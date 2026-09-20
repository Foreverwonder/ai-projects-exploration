# -*- coding: utf-8 -*-
r"""人工精确定类 + 组装看板数据。读 raw_scan.json，输出 dashboard_data.json。

分类是逐个核对项目文件特征手工定的，不靠关键词猜。新增项目就在这里补一行。
"""
import json, os, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

MANUAL = {
    # 命理玄学
    "baziK线图": "命理玄学", "baZitest": "命理玄学", "baZi—test": "命理玄学",
    "claude4.7算命": "命理玄学", "DeepSeekv4flash转录视频八字": "命理玄学",
    "六爻起卦": "命理玄学", "印占软件": "命理玄学", "爬问真八字": "命理玄学",
    "算命提示词优化": "命理玄学",
    "双圆环命理八字奇门紫薇": "命理玄学", "双环圆盘八字紫薇六爻奇门": "命理玄学",
    # 股票财经
    "251120compare_price": "股票财经", "DeepSeek转录视频炒股": "股票财经",
    "stock-monitor": "股票财经", "中国黄金股市研究": "股票财经",
    # 视频音频处理
    "251012同声传译": "视频音频处理", "251125神速TTS": "视频音频处理",
    "AI分镜拆解": "视频音频处理", "AI换脸": "视频音频处理", "MP3转MP4": "视频音频处理",
    "gif录屏": "视频音频处理", "小兔的舞蹈": "视频音频处理", "春节滤镜": "视频音频处理",
    "胖东来三轮大清洗视频AI处理": "视频音频处理", "铃芽之旅音频hook": "视频音频处理",
    "zhy": "视频音频处理",
    # AI 编程 / Agent 工具
    "0729房源归档Agent": "AI编程工具", "antigravityCLI": "AI编程工具",
    "Antigravity反向代理": "AI编程工具", "AutoGLM": "AI编程工具",
    "claude-code": "AI编程工具", "claudecode泄露源码": "AI编程工具",
    "coze工作流导出动画1": "AI编程工具", "deepseekv4": "AI编程工具",
    "deepseekv4flash正式版": "AI编程工具", "DouBao_MarsCode": "AI编程工具",
    "everything-claude-code": "AI编程工具", "github免费API": "AI编程工具",
    "Hermes Agent": "AI编程工具", "mcp-servers": "AI编程工具", "n8nChinese": "AI编程工具",
    "new_API": "AI编程工具", "openclaw": "AI编程工具", "opencode": "AI编程工具",
    "qwen3.5": "AI编程工具", "腾讯Marvis": "AI编程工具", "苏苏cow-coze": "AI编程工具",
    "老金的元Agent架构": "AI编程工具", "魔搭api": "AI编程工具",
    "DeepSeekHarness": "AI编程工具", "JEV测试——硬盘体检": "AI编程工具",
    "小米桌面Agent": "AI编程工具",
    # 模型与接口测试
    "25_200wTokenTest": "模型测试", "251230M2.1": "模型测试", "251231skill": "模型测试",
    "claude4.7kiro测试": "模型测试", "codex测试": "模型测试",
    "deepseekv4前端后端测试": "模型测试", "LongCat_test": "模型测试",
    "Longcat2601": "模型测试", "M2.1test": "模型测试", "mimo-v2.5-pro": "模型测试",
    "minimaxM2.5test": "模型测试", "step3.7": "模型测试", "test1023": "模型测试",
    "Ox测试": "模型测试", "璞嗗寘Test": "模型测试", "豆包Test": "模型测试",
    # 比赛项目
    "202508全球攻防": "比赛项目", "24AI攻防生图赛道一": "比赛项目",
    "251017_modelscope_AIgame": "比赛项目", "251114魔搭2": "比赛项目",
    "251114魔搭AI小说提交版": "比赛项目", "251114魔搭AI小说黄总优化版": "比赛项目",
    "2603amd比赛": "比赛项目", "26黄总比赛": "比赛项目", "核聚变比赛": "比赛项目",
    "魔搭游戏工具": "比赛项目",
    # 效率工具
    "251124m2.1文件粉碎机": "效率工具", "251124窗口半透明工具": "效率工具",
    "MD2img": "效率工具", "m3u8下载器": "效率工具", "rust_monitor": "效率工具",
    "rust_终端监控": "效率工具", "修复本地tun网络": "效率工具", "找回环境变量": "效率工具",
    "耳机检测": "效率工具", "耳機检测": "效率工具", "释放法软件": "效率工具",
    "迁移系统": "效率工具",
    # 游戏娱乐
    "gemini3.5flash小球": "游戏娱乐", "M2.1八分音符酱复刻": "游戏娱乐",
    "M2.1曼陀罗绘画": "游戏娱乐", "M2.1赛车游戏": "游戏娱乐", "AI互动小说": "游戏娱乐",
    "预测世界杯": "游戏娱乐",
    # 学习教育
    "0614钟慧瑜课件": "学习教育", "202509中石化": "学习教育", "Coding": "学习教育",
    "homework_app": "学习教育", "改作业程序文件夹": "学习教育", "毕设研究": "学习教育",
    "英语试卷作文拍照": "学习教育", "钟慧瑜的教学函数动画代码": "学习教育",
    "可以成功运行的例子": "学习教育", "c-coding": "学习教育",
    # Web 应用
    "0804": "Web应用", "251023": "Web应用", "251028": "Web应用", "251110": "Web应用",
    "bilihong-app": "Web应用", "M2.1springboot": "Web应用", "mdNoteApp": "Web应用",
    "AI黑板": "Web应用", "新春秒哒": "Web应用",
    # 内容创作
    "2025AI播客": "内容创作", "AI图片0106": "内容创作", "分镜大师设计文档": "内容创作",
    "爬取小说": "内容创作", "台湾竖排文字解读器": "内容创作", "好看的": "内容创作",
    "RSSHub": "内容创作", "大批量蒸馏神学书": "内容创作", "豆包做的高速发展历程": "内容创作",
    # 素材与个人归档
    "0613": "素材归档", "0713": "素材归档", "0804_1": "素材归档", "0806袋鼠大佬": "素材归档",
    "2024AI项目": "素材归档", "251004": "素材归档", "251011": "素材归档", "251115": "素材归档",
    "DuMate": "素材归档", "Obsidian": "素材归档", "skills": "素材归档",
    "一泽的WebAcessSkill": "素材归档", "天工龙虾SkyClaw": "素材归档", "甘总头像": "素材归档",
    "ZZZZZ杂文件": "素材归档", "截止26年0108桌面文件": "素材归档",
    "并行运行三个Agent截图记录": "素材归档", "旅游前夕准备open-code": "素材归档",
    "_github_publish": "素材归档", "logs": "素材归档",
    "懿笑倾城0904结营分享会": "素材归档", "懿笑倾城0913直播分享会": "素材归档",
    "懿笑倾城260827结营分享会": "素材归档", "懿笑倾城9001直播": "素材归档",
    "梵公子经验": "素材归档",
}

EXCLUDE = {"_github_homepage"}


def main():
    scan = json.load(open(os.path.join(HERE, "raw_scan.json"), encoding="utf-8"))
    raw = [x for x in scan["items"] if x.get("kind", "dir") == "dir" and x["name"] not in EXCLUDE]

    miss = [p["name"] for p in raw if p["name"] not in MANUAL]
    if miss:
        print("!! 未分类（先补 MANUAL）:", miss)

    projects = []
    for p in raw:
        projects.append(dict(n=p["name"], c=MANUAL.get(p["name"], "素材归档"),
                             mb=round(p["size"] / 1048576, 1), f=p["files"],
                             l=p["main_lang"], m=p["latest"] if p["files"] else 0,
                             r=p["readme_count"] > 0))
    projects.sort(key=lambda x: -x["mb"])

    cats = {}
    for p in projects:
        c = cats.setdefault(p["c"], dict(count=0, mb=0.0, files=0))
        c["count"] += 1
        c["mb"] += p["mb"]
        c["files"] += p["f"]

    tl = Counter()
    for p in projects:
        if p["m"]:
            d = datetime.datetime.fromtimestamp(p["m"])
            tl["%d-%02d" % (d.year, d.month)] += 1

    langs = Counter(p["l"] for p in projects if p["f"] > 0)
    tiers = Counter()
    for p in projects:
        mb = p["mb"]
        tiers["微小" if mb < 1 else "小" if mb < 10 else "中" if mb < 100 else "大" if mb < 1000 else "巨大"] += 1

    out = dict(projects=projects, categories=cats,
               timeline={k: tl[k] for k in sorted(tl)},
               langs=dict(langs.most_common()), tiers=dict(tiers))
    json.dump(out, open(os.path.join(HERE, "dashboard_data.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("分类完成：%d 个项目 / %d 类 / %.1fGB" % (
        len(projects), len(cats), sum(p["mb"] for p in projects) / 1024))


if __name__ == "__main__":
    main()
