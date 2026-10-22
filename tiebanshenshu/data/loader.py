"""按基础表、本命、流年和语料分别加载数据。"""
import os
from tiebanshenshu.data.csv_reader import CsvTableReader


class TieBanDataLoader(CsvTableReader):
    def __init__(self, db_folder=None):
        super().__init__(db_folder)
        self.tables = {} 
        self.rule_tables = []

        # 卦象映射表 - 支持按 (刻别, 本命数) 查找卦名
        self.HEXAGRAM_MAP = {}          # 兼容原有逻辑：仅按本命数查找（取优先匹配）
        self.HEXAGRAM_DETAIL_MAP = {}   # 完整映射：(刻别, 本命数) -> 卦名

        self.DESTINY_DATA = {}
        self.LIUNIAN_START = {}
        self.LIUNIAN_SEQ = {}
        self.MARKER_TABLE = {}
        self.LETTER_TABLE = {}
        self.SECRET_NUM_TABLE = {}

        # 14-14相关映射表
        self.DATA_BY_LETTER = {}        # (字母, 岁数) -> (基数, 加数, 条文校正数)
        self.DATA_BY_CORRECTION = {}    # (条文校正数, 岁数) -> (基数, 加数) 用于校正后查找
        self.CORRECTION_TO_LETTER = {}  # (条文校正数, 岁数) -> 字母 反向映射

        # 新增：条文断词映射表
        self.FORTUNE_DUANYU_MAP = {}    # 条文数字 -> (断语, 对应年龄)
        self.FORTUNE_DUANYU_RAW = []    # 原始断词数据

        print(f">>> 正在加载数据库 ({os.path.abspath(self.db_folder)})...")
        if os.path.exists(self.db_folder):
            self._load_all()
        else:
            print("【错误】数据库文件夹不存在！")

    def _load_all(self):
        self._load_basic_tables()
        self._load_hexagrams()
        self._load_destiny()
        self._load_annual_rules()
        self._load_annual_verses()
        self._load_verses()
        self._load_secret_numbers()
        self._load_names()


    def _load_basic_tables(self):
        # 1. 基础表 (14-1 ~ 14-6)
        self.tables['14-1'] = {self._clean_key(r.get('农历月份')): int(r.get('数值', 0)) for r in self._read_csv_as_dicts("14-1.csv")}
        self.tables['14-2'] = {self._clean_key(r.get('时支')): int(r.get('数值', 0)) for r in self._read_csv_as_dicts("14-2.csv")}
        for r in self._read_csv_as_dicts("14-3.csv"):
            if r.get('先天命数'):
                for n in r['先天命数'].split('|'): self.tables.setdefault('14-3', {})[int(n)] = {self._clean_key(k): v for k, v in r.items()}
        self.tables['14-4'] = {self._clean_key(r.get('五音')): int(r.get('数值', 0)) for r in self._read_csv_as_dicts("14-4.csv")}
        for r in self._read_csv_as_dicts("14-5.csv"):
            nayin = self._clean_key(r.get('日柱纳音'))
            self.tables.setdefault('14-5', {})[nayin] = {self._clean_key(k): int(v) for k, v in r.items() if k.strip() != '日柱纳音'}
        self.tables['14-6'] = {self._clean_key(r.get('时柱纳音')): int(r.get('数值', 0)) for r in self._read_csv_as_dicts("14-6.csv")}

        # 14-7 规则表
        self.rule_tables = self._read_csv_as_dicts("14-7.csv")

    def _load_hexagrams(self):
        # 2. 卦象表加载 (14-9.csv)
        df_14_9 = self._read_csv_robust("14-9.csv", header_option=None)
        if df_14_9 is not None and not df_14_9.empty:
            col_count = len(df_14_9.columns)
            print(f"  > 加载 14-9.csv 成功，共 {len(df_14_9)} 条数据，列数：{col_count}")

            if col_count >= 3:
                invalid_rows = 0
                valid_rows = 0

                for idx, row in df_14_9.iterrows():
                    try:
                        # 第一列：刻别（初刻/正刻）
                        kebie = self._clean_key(row[0])
                        if kebie not in ["初刻", "正刻"]:
                            invalid_rows += 1
                            if invalid_rows <= 3:
                                print(f"    提示: 第 {idx+1} 行刻别无效 ({kebie})，已跳过")
                            continue

                        # 第二列：本命数
                        benming_num = row[1]
                        if not self._is_numeric(benming_num):
                            invalid_rows += 1
                            if invalid_rows <= 3:
                                print(f"    提示: 第 {idx+1} 行本命数非数值 ({benming_num})，已跳过")
                            continue
                        num = int(float(benming_num))

                        # 第三列：卦名
                        hex_name = self._clean_key(row[2])
                        if not hex_name or hex_name == 'nan':
                            invalid_rows += 1
                            if invalid_rows <= 3:
                                print(f"    提示: 第 {idx+1} 行卦名为空，已跳过")
                            continue

                        # 构建映射
                        self.HEXAGRAM_DETAIL_MAP[(kebie, num)] = hex_name
                        if num not in self.HEXAGRAM_MAP:
                            self.HEXAGRAM_MAP[num] = hex_name

                        valid_rows += 1
                        if valid_rows <= 10:
                            print(f"    调试: {kebie} {num} -> {hex_name}")

                    except Exception as e:
                        invalid_rows += 1
                        continue

                print(f"  > 14-9.csv 解析完成：有效行数 {valid_rows}，无效行数 {invalid_rows}")
                print(f"  > 成功解析 {len(self.HEXAGRAM_DETAIL_MAP)} 条详细卦象数据")
                if len(self.HEXAGRAM_DETAIL_MAP) == 0:
                    print("  [警告] 14-9.csv 中未找到有效卦象数据！")
        else:
            print("  [警告] 无法读取 14-9.csv，请检查文件是否存在！")

    def _load_destiny(self):
        # 14-10: 卦象详情
        df_14_10 = self._read_csv_robust("14-10.csv", header_option=0)
        if df_14_10 is not None and not df_14_10.empty:
            print(f"  > 加载 14-10.csv 成功，共 {len(df_14_10)} 条数据")

            columns = [self._clean_key(col) for col in df_14_10.columns]
            print(f"    14-10.csv 列名: {columns}")

            col_map = {}
            for idx, col in enumerate(columns):
                if '辟卦' in col or '卦名' in col:
                    col_map['gua'] = idx
                elif '基数' in col:
                    col_map['base'] = idx
                elif '初刻' in col:
                    col_map['initial'] = idx
                elif '正刻' in col:
                    col_map['main'] = idx
                elif '序数' in col:
                    col_map['seq'] = idx
                elif '性格' in col:
                    col_map['xingge'] = idx
                elif '才能' in col:
                    col_map['caineng'] = idx
                elif '财运' in col:
                    col_map['caiyun'] = idx
                elif '兄弟' in col:
                    col_map['xiongdi'] = idx

            required_cols = ['gua', 'base', 'initial', 'main', 'seq', 'xingge', 'caineng', 'caiyun', 'xiongdi']
            missing_cols = [col for col in required_cols if col not in col_map]
            if missing_cols:
                print(f"    [警告] 14-10.csv 缺少必要列: {missing_cols}")
            else:
                valid_count = 0
                for idx, row in df_14_10.iterrows():
                    try:
                        gua = self._clean_key(row.iloc[col_map['gua']])
                        base = int(float(row.iloc[col_map['base']]))
                        seq = int(float(row.iloc[col_map['seq']]))

                        def parse_offsets(s):
                            return [int(x) for x in str(s).replace('，','|').replace('\n','|').split('|') if x.strip().isdigit()]

                        offsets = {
                            "性格": parse_offsets(row.iloc[col_map['xingge']]),
                            "才能前程": parse_offsets(row.iloc[col_map['caineng']]),
                            "财运": parse_offsets(row.iloc[col_map['caiyun']]),
                            "兄弟个数": parse_offsets(row.iloc[col_map['xiongdi']])
                        }

                        data_pack = {"base": base, "seq": seq, "offsets": offsets}

                        initial_nums = str(row.iloc[col_map['initial']]).split('|')
                        for n in initial_nums:
                            if n.strip().isdigit():
                                self.DESTINY_DATA[(gua, "Initial", int(n.strip()))] = data_pack

                        main_nums = str(row.iloc[col_map['main']]).split('|')
                        for n in main_nums:
                            if n.strip().isdigit():
                                self.DESTINY_DATA[(gua, "Main", int(n.strip()))] = data_pack

                        valid_count += 1

                    except Exception as e:
                        continue

                print(f"    成功加载 {valid_count} 条本命条文数据")
                print(f"    成功解析 {len(self.DESTINY_DATA)} 条本命映射")
                if len(self.DESTINY_DATA) > 0:
                    print(f"    示例映射: {list(self.DESTINY_DATA.keys())[:5]}")
        else:
            print("  [警告] 无法读取 14-10.csv，请检查文件是否存在！")

    def _load_annual_rules(self):
        # 3. 流年相关 (14-11 ~ 14-14)
        for r in self._read_csv_as_dicts("14-11-1.csv"):
            try:
                num = int(r['先天命数']) if '先天命数' in r else 'generic'
                if r.get('年支组') and r.get('性别'):
                    self.LIUNIAN_START[(num, self._clean_key(r['年支组']), self._clean_key(r['性别']))] = int(r.get('起始数', 0))
            except: pass

        for r in self._read_csv_as_dicts("14-11-2.csv"):
            try:
                num = int(r.get('先天命数', 0))
                gan = self._clean_key(r.get('天干') or r.get('年干组'))
                seq = []
                if '1' in r and '12' in r:
                    seq = [self._clean_key(r.get(str(i))) for i in range(1, 13)]
                elif '原始序列' in r:
                    seq = [x.strip() for x in r['原始序列'].replace(',', '|').replace(' ', '|').split('|') if x.strip()]
                if num and gan and seq: self.LIUNIAN_SEQ[(num, gan)] = seq
            except: pass

        for r in self._read_csv_as_dicts("14-12.csv"):
            try:
                zhi = self._clean_key(r.get('流年地支'))
                num = int(r.get('后天命数', 0))
                marker = self._clean_key(r.get('流年标记'))
                if zhi and num and marker: self.MARKER_TABLE.setdefault(zhi, {})[num] = marker
            except: pass

        for r in self._read_csv_as_dicts("14-13.csv"):
            try:
                moment = self._clean_key(r.get('考刻'))
                parity = self._clean_key(r.get('日命数加时运数的奇偶性'))
                tone_val = self._clean_key(r.get('流年天四声'))
                marker = self._clean_key(r.get('流年标记'))
                letter = self._clean_key(r.get('流年字母'))
                if moment and parity and tone_val and marker and letter:
                     self.LETTER_TABLE[(moment, parity, tone_val, marker)] = letter
            except: pass

    def _load_annual_verses(self):
        # 14-14 流年条文表
        df_14_14 = self._read_csv_robust("14-14.csv", header_option=0)
        if df_14_14 is not None and not df_14_14.empty:
            print(f"  > 加载 14-14.csv 成功，共 {len(df_14_14)} 条数据")

            # 获取列名并清洗
            columns = [self._clean_key(col) for col in df_14_14.columns]
            print(f"    14-14.csv 列名: {columns}")

            # 查找关键列的索引
            col_mapping = {}
            for idx, col in enumerate(columns):
                if '流年字母' in col:
                    col_mapping['letter'] = idx
                elif '流年岁数' in col:
                    col_mapping['age'] = idx
                elif '基数' in col:
                    col_mapping['base'] = idx
                elif '加数' in col:
                    col_mapping['add'] = idx
                elif '条文校正数' in col or '流年叫正文' in col:
                    col_mapping['correction'] = idx

            # 验证必要列是否存在
            required_cols = ['letter', 'age', 'base', 'add', 'correction']
            missing_cols = [col for col in required_cols if col not in col_mapping]
            if missing_cols:
                print(f"    [警告] 14-14.csv 缺少必要列: {missing_cols}")
            else:
                # 读取数据
                for idx, row in df_14_14.iterrows():
                    try:
                        letter = self._clean_key(row.iloc[col_mapping['letter']])
                        age = int(float(row.iloc[col_mapping['age']]))
                        base = int(float(row.iloc[col_mapping['base']]))
                        add = int(float(row.iloc[col_mapping['add']]))
                        correction = int(float(row.iloc[col_mapping['correction']]))

                        if letter and age > 0:
                            # 主映射：(字母, 岁数) -> (基数, 加数, 条文校正数)
                            self.DATA_BY_LETTER[(letter, age)] = (base, add, correction)
                            # 校正映射：(条文校正数, 岁数) -> (基数, 加数)
                            self.DATA_BY_CORRECTION[(correction, age)] = (base, add)
                            # 反向映射：(条文校正数, 岁数) -> 字母
                            self.CORRECTION_TO_LETTER[(correction, age)] = letter

                    except Exception as e:
                        continue

                print(f"    成功加载 {len(self.DATA_BY_LETTER)} 条流年条文数据")
        else:
            print("  [警告] 无法读取 14-14.csv，请检查文件是否存在！")

    def _load_verses(self):
        # 新增：加载铁板神数-条文断词.csv (DB目录下的List.csv)
        duanyu_file = "List.csv"
        df_duanyu = self._read_csv_robust(duanyu_file, header_option=0)
        if df_duanyu is not None and not df_duanyu.empty:
            print(f"  > 加载 {duanyu_file} 成功，共 {len(df_duanyu)} 条数据")

            # 获取列名并清洗
            columns = [self._clean_key(col) for col in df_duanyu.columns]
            print(f"    {duanyu_file} 列名: {columns}")

            # 查找关键列的索引
            col_mapping = {}
            for idx, col in enumerate(columns):
                if '条文数字' in col or '条文数' in col or '数字' in col:
                    col_mapping['num'] = idx
                elif '断语' in col or '断词' in col or '内容' in col:
                    col_mapping['duanyu'] = idx
                elif '年龄' in col or '对应年龄' in col or '岁数' in col:
                    col_mapping['age'] = idx

            # 读取数据
            valid_count = 0
            for idx, row in df_duanyu.iterrows():
                try:
                    # 获取条文数字
                    if 'num' in col_mapping:
                        fortune_num = row.iloc[col_mapping['num']]
                        if self._is_numeric(fortune_num):
                            fortune_num = int(float(fortune_num))
                        else:
                            continue
                    else:
                        continue

                    # 获取断语
                    duanyu = ""
                    if 'duanyu' in col_mapping:
                        duanyu = self._clean_key(row.iloc[col_mapping['duanyu']])

                    # 获取对应年龄
                    duanyu_age = ""
                    if 'age' in col_mapping:
                        duanyu_age = self._clean_key(row.iloc[col_mapping['age']])

                    # 构建映射
                    if fortune_num > 0:
                        self.FORTUNE_DUANYU_MAP[fortune_num] = (duanyu, duanyu_age)
                        self.FORTUNE_DUANYU_RAW.append({
                            'num': fortune_num,
                            'duanyu': duanyu,
                            'age': duanyu_age
                        })
                        valid_count += 1

                except Exception as e:
                    continue

            print(f"    成功加载 {valid_count} 条条文断语数据")
            if valid_count > 0:
                # 打印前5条作为示例
                print(f"    示例数据: {list(self.FORTUNE_DUANYU_MAP.items())[:5]}")
        else:
            print(f"  [警告] 无法读取 {duanyu_file}，断语功能将不可用！")

    def _load_secret_numbers(self):
        # 加载秘数表
        secret_file = "秘数表.csv"
        df_secret = self._read_csv_robust(secret_file, header_option=0)
        if df_secret is not None and not df_secret.empty:
            print(f"  > 加载 {secret_file} 成功，共 {len(df_secret)} 条数据")

            self.SECRET_NUMBER_TABLE = {}
            for idx, row in df_secret.iterrows():
                try:
                    topic = self._clean_key(row.get('事项', ''))
                    secret_num = int(float(row.get('秘数', 0)))
                    if topic:
                        self.SECRET_NUMBER_TABLE[topic] = secret_num
                except Exception as e:
                    continue

            print(f"    成功加载 {len(self.SECRET_NUMBER_TABLE)} 条秘数数据: {self.SECRET_NUMBER_TABLE}")
        else:
            print(f"  [提示] 未找到 {secret_file}，使用默认秘数表")
            self.SECRET_NUMBER_TABLE = {
                "流年": 0,
                "社交": 10,
                "家庭": 30,
                "运势": 50,
                "财运": 80,
                "本命": 120
            }

    def _load_names(self):
        baijia_file = "chinese_surnames.csv"
        self.BAIJIA_XING = {"木": [], "火": [], "土": [], "金": [], "水": []}
        df_baijia = self._read_csv_robust(baijia_file, header_option=0)
        if df_baijia is not None and not df_baijia.empty:
            print(f"  > 加载 {baijia_file} 成功，共 {len(df_baijia)} 条数据")
            for idx, row in df_baijia.iterrows():
                try:
                    xing = str(row.get('surname', '')).strip()
                    wuxing = str(row.get('wuxing', '')).strip()
                    if xing and wuxing in self.BAIJIA_XING:
                        self.BAIJIA_XING[wuxing].append(xing)
                except Exception as e:
                    continue
            for wx, xing_list in self.BAIJIA_XING.items():
                self.BAIJIA_XING[wx] = list(set(xing_list))
            print(f"    成功加载百家姓数据: 木{len(self.BAIJIA_XING['木'])}火{len(self.BAIJIA_XING['火'])}土{len(self.BAIJIA_XING['土'])}金{len(self.BAIJIA_XING['金'])}水{len(self.BAIJIA_XING['水'])}")
        else:
            print(f"  [提示] 未找到 {baijia_file}")

        common_names_file = "common_names.csv"
        self.COMMON_NAMES = {"木": [], "火": [], "土": [], "金": [], "水": []}
        df_names = self._read_csv_robust(common_names_file, header_option=0)
        if df_names is not None and not df_names.empty:
            print(f"  > 加载 {common_names_file} 成功，共 {len(df_names)} 条数据")
            for idx, row in df_names.iterrows():
                try:
                    hanzi = str(row.get('character', '')).strip()
                    wuxing = str(row.get('wuxing', '')).strip()
                    if hanzi and wuxing in self.COMMON_NAMES:
                        self.COMMON_NAMES[wuxing].append(hanzi)
                except Exception as e:
                    continue
            for wx, ming_list in self.COMMON_NAMES.items():
                self.COMMON_NAMES[wx] = list(set(ming_list))
            print(f"    成功加载常用名字数据: 木{len(self.COMMON_NAMES['木'])}火{len(self.COMMON_NAMES['火'])}土{len(self.COMMON_NAMES['土'])}金{len(self.COMMON_NAMES['金'])}水{len(self.COMMON_NAMES['水'])}")
        else:
            print(f"  [提示] 未找到 {common_names_file}")
