"""视频流程命令行。"""
import argparse
import json
from pathlib import Path
from tiebanshenshu.methods.video import VideoMethodCalculator
from tiebanshenshu.methods.video_corpus import load_comparison_verses

def main(argv=None):
    parser=argparse.ArgumentParser(description='按泽方视频四柱复算，未核验条文不自动定刻')
    parser.add_argument('--pillars',nargs=4,required=True,metavar=('年','月','日','时'))
    parser.add_argument('--output',type=Path,help='保存JSON演算记录')
    parser.add_argument('--basis-number',type=int,help='仅作连续演算，不代表已核验事实')
    parser.add_argument('--fortune-pillar',help='视频大运算例运柱，例如壬午')
    args=parser.parse_args(argv)
    try:
        result=VideoMethodCalculator(load_comparison_verses()).calculate(dict(zip(('year','month','day','time'),args.pillars)),basis_number=args.basis_number,fortune_pillar=args.fortune_pillar)
    except ValueError as exc:
        parser.error(str(exc))
    content=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(content,encoding='utf-8')
    else:
        print(content)
