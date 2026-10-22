"""泽方 o3mkGBcPkrI 白板配数；数表含义不同，不与十四表混用。"""
STEM_GUA = dict(zip('甲乙丙丁戊己庚辛壬癸', '乾坤艮兑坎离震巽乾坤'))
BRANCH_GUA = dict(zip('子丑寅卯辰巳午未申酉戌亥', '坎坤震乾兑离离艮艮乾巽坎'))
STEM_CODE = dict(zip('甲丙戊庚壬乙丁己辛癸', range(1, 11)))
STEM_CODE['癸'] = 0
STEM_CODE['月'] = 0
# 22:50 左下字幕；顺序为上卦、下卦。
TRIGRAM_SUM = {'坤': (33,42), '艮': (42,42), '坎': (26,26), '巽': (39,39),
               '震': (45,45), '离': (45,45), '兑': (26,26), '乾': (39,48)}
# 爻从下向上；纳支时反转为视频的自上向下。
LINES = {'乾': (1,1,1), '坤': (0,0,0), '震': (1,0,0), '巽': (0,1,1),
         '坎': (0,1,0), '离': (1,0,1), '艮': (0,0,1), '兑': (1,1,0)}
ANNUAL_STEM = {**dict.fromkeys('甲己乙庚',4), **dict.fromkeys('丙辛',6), **dict.fromkeys('丁壬戊癸',3)}
ANNUAL_BRANCH = {**dict.fromkeys('亥子',(1,6)), **dict.fromkeys('巳午',(2,7)),
                 **dict.fromkeys('寅卯',(3,8)), **dict.fromkeys('申酉',(4,9)),
                 **dict.fromkeys('辰戌丑未',(5,10))}

# 独立收录视频配数，不从十四表或旧考刻引擎导入。
TIAN_GAN_TAI_XUAN = dict(zip('甲乙丙丁戊己庚辛壬癸', (9,8,7,6,5,9,8,7,6,5)))
DI_ZHI_TAI_XUAN = dict(zip('子丑寅卯辰巳午未申酉戌亥', (9,8,7,6,5,4,9,8,7,6,5,4)))
BA_GUA_XIAN_TIAN = dict(zip('乾兑离震巽坎艮坤', range(1,9)))
BA_GUA_HOU_TIAN = dict(zip('坎坤震巽乾兑艮离', (1,2,3,4,6,7,8,9)))
BA_GUA_BY_XIAN_TIAN_NUM = {v:k for k,v in BA_GUA_XIAN_TIAN.items()}
BA_GUA_BY_HOU_TIAN_NUM = {v:k for k,v in BA_GUA_HOU_TIAN.items()}
STEM_CODE['支'] = 0
# 视频11:30起的两张表，与《铁板神数十九法秘解》乾/坤宫甲流度对照。
PARENT_BASES = {
    '父亲': dict(zip('鼠牛虎兔龙蛇马羊猴鸡狗猪', range(9003,9603,50))),
    '母亲': dict(zip('鼠牛虎兔龙蛇马羊猴鸡狗猪', range(9605,10205,50))),
}
PARENT_TABLE_SOURCE = 'https://vr-d.com/pdf-file/命理/铁板神数十九法秘解_陈鼎龙.pdf'

# 29:16叠加表：只给化神配数，不代替判断合化是否成立。
HUA_SHEN = {'甲己':('土',5), '乙庚':('金',4), '丙辛':('水',1),
            '丁壬':('木',3), '戊癸':('火',2)}

def reference_tables():
    """将视频叠加表单独呈现，和白板推导记录区分。"""
    tables = [
        ('先天卦数',441,BA_GUA_XIAN_TIAN,'已用于月上年下考刻与前卦'),
        ('天干配卦',926,{k:f'{v}{BA_GUA_HOU_TIAN[v]}' for k,v in STEM_GUA.items()},'已用于四柱八卦加则'),
        ('地支配卦',926,{k:f'{v}{BA_GUA_HOU_TIAN[v]}' for k,v in BRANCH_GUA.items()},'已用于四柱八卦加则'),
        ('爻位配数',1200,dict(zip(('子丑','寅卯','辰巳','午未','申酉','戌亥'),(30,60,90,120,150,180))),'已按阴阳分别从上往下使用'),
        ('上下卦合计',1400,TRIGRAM_SUM,'已按上卦/下卦列分别使用'),
        ('化神五行数',1756,HUA_SHEN,'表格已转录；合化成立条件未全部核实'),
        ('流年天干配数',1840,ANNUAL_STEM,'已用于未合化流年分支'),
        ('流年地支配数',1840,ANNUAL_BRANCH,'已用于未合化流年分支'),
    ]
    return [{'title':title,'source_seconds':[seconds],
             'rows':[{'key':key,'value':value} for key,value in data.items()],
             'usage':usage} for title,seconds,data,usage in tables]

VIDEO_TEXT_EVIDENCE = {4381: {'sentence':'黄莺出谷，载迁乔木。', 'source_seconds':[1350]}}
