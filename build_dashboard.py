# -*- coding: utf-8 -*-
"""生成 AI_Projects 探险手记 HTML。读取 dashboard_data.json，输出自包含单文件看板。
风格：日常记录感，不是简历。数据随扫描自动更新。"""
import json, datetime, html, math, re, statistics, os
from collections import Counter, defaultdict

data = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_data.json"), encoding="utf-8"))
projs = sorted(data["projects"], key=lambda p: -p["mb"])
cats = data["categories"]
tl = data["timeline"]
langs = data["langs"]
tiers = data["tiers"]

total_mb = sum(p["mb"] for p in projs)
total_files = sum(p["f"] for p in projs)
mts = [p["m"] for p in projs if p["m"]]
first_d = datetime.datetime.fromtimestamp(min(mts)).strftime("%Y.%m")
last_d = datetime.datetime.fromtimestamp(max(mts)).strftime("%Y.%m")
N = len(projs)

# ---- 类别配色（与原版一致） ----
CAT_COLORS = {
    "AI编程工具": "#6366f1", "素材归档": "#94a3b8", "模型测试": "#f59e0b",
    "效率工具": "#10b981", "视频音频处理": "#ec4899", "比赛项目": "#ef4444",
    "学习教育": "#14b8a6", "Web应用": "#8b5cf6", "命理玄学": "#f97316",
    "内容创作": "#06b6d4", "游戏娱乐": "#eab308", "股票财经": "#059669",
}
LANG_COLORS = {
    "Python": "#3776ab", "HTML": "#e34c26", "Markdown": "#083fa1", "TypeScript": "#3178c6",
    "JavaScript": "#f7df1e", "Shell": "#4eaa25", "PowerShell": "#012456", "Batch": "#4eaa25",
    "Jupyter": "#f37626", "Swift": "#fa7343", "Java": "#b07219", "Rust": "#dea584", "其他": "#64748b",
}

def fmt_mb(mb):
    if mb >= 1024: return f"{mb/1024:.1f}GB"
    if mb >= 1: return f"{mb:.0f}MB"
    return f"{mb*1024:.0f}KB"

# ---- 新增角度 1：年份截面 ----
yr_counter = Counter()
for p in projs:
    if p["m"]:
        yr_counter[datetime.datetime.fromtimestamp(p["m"]).year] += 1
    else:
        yr_counter["未知"] += 1
years = ["2024", "2025", "2026"]
year_html = ""
for y in years:
    n = yr_counter.get(int(y), 0)
    w = n / N * 100
    year_html += f'''<div class="hbar-row"><div class="hbar-label">{y} 年</div><div class="hbar-track"><div class="hbar-fill" style="width:{w}%;background:#7c3aed"></div></div><div class="hbar-val">{n}</div></div>'''

# ---- 新增角度 2：最近 90 天还在动的项目 ----
NOW = datetime.datetime(2026, 9, 20).timestamp()
recent = [p for p in projs if p["m"] and NOW - p["m"] < 90 * 86400]
recent_sorted = sorted(recent, key=lambda p: -p["m"])
recent_html = "".join(
    f'''<div class="stat-chip"><b>{html.escape(p['n'])}</b><span>{datetime.datetime.fromtimestamp(p['m']).strftime('%m-%d')} · {p['c']}</span></div>'''
    for p in recent_sorted
)

# ---- 新增角度 3：几点收工（最后修改时间的小时分布） ----
hr_counter = Counter()
for p in projs:
    if p["m"]:
        hr_counter[datetime.datetime.fromtimestamp(p["m"]).hour] += 1
peak_hour = max(hr_counter.items(), key=lambda x: x[1])[0]
night_count = sum(v for h, v in hr_counter.items() if h >= 22 or h <= 2)

# ---- 平均 vs 中位数 ----
sizes = [p["mb"] for p in projs]
median_mb = statistics.median(sizes)

# ---- 生成项目卡片网格 ----
cat_count = {c: v["count"] for c, v in cats.items()}
cards = []
for p in projs:
    c = p["c"]
    col = CAT_COLORS.get(c, "#94a3b8")
    name = html.escape(p["n"])
    badge = "📖" if p["r"] else ""
    cards.append(f'''<div class="pcard" data-cat="{c}" data-lang="{html.escape(p['l'])}">
      <div class="pc-name"><span class="dot" style="background:{col}"></span>{name}{badge}</div>
      <div class="pc-meta"><span>{fmt_mb(p['mb'])}</span><span>{p['f']} 文件</span><span>{html.escape(p['l'])}</span></div>
      <div class="pc-bar"><div style="width:{min(100, max(2, p['mb']/2000*100))}%;background:{col}"></div></div>
    </div>''')
cards_html = "\n".join(cards)

# ---- 时间线 ----
tl_pairs = sorted(tl.items())
tl_labels = ",".join(f'"{k}"' for k, _ in tl_pairs)
tl_values = ",".join(str(v) for _, v in tl_pairs)

# ---- 语言 ----
lang_top = sorted(langs.items(), key=lambda x: -x[1])[:10]
lang_total = sum(langs.values())
lang_bars = ""
for l, n in lang_top:
    w = n / lang_total * 100
    col = LANG_COLORS.get(l, "#64748b")
    lang_bars += f'''<div class="hbar-row"><div class="hbar-label">{l}</div><div class="hbar-track"><div class="hbar-fill" style="width:{w}%;background:{col}"></div></div><div class="hbar-val">{n}</div></div>'''

# ---- 规模分档 ----
tier_order = ["微小", "小", "中", "大", "巨大"]
tier_bars = ""
for t in tier_order:
    n = tiers.get(t, 0)
    w = n / N * 100
    tier_bars += f'''<div class="hbar-row"><div class="hbar-label">{t}</div><div class="hbar-track"><div class="hbar-fill tier-{t}" style="width:{w}%"></div></div><div class="hbar-val">{n}</div></div>'''

# ---- 类别 top 列表（按数量） ----
cat_sorted = sorted(cats.items(), key=lambda x: -x[1]["count"])
cat_list = ""
for c, v in cat_sorted:
    col = CAT_COLORS.get(c, "#94a3b8")
    w = v["count"] / N * 100
    cat_list += f'''<div class="hbar-row"><div class="hbar-label">{c} <span class="sub">{fmt_mb(v['mb'])}</span></div><div class="hbar-track"><div class="hbar-fill" style="width:{w}%;background:{col}"></div></div><div class="hbar-val">{v['count']}</div></div>'''

# ---- 最大项目 top10 ----
big10 = projs[:10]
big_bars = ""
max_mb = big10[0]["mb"] if big10 else 1
for i, p in enumerate(big10):
    w = p["mb"] / max_mb * 100
    col = CAT_COLORS.get(p["c"], "#94a3b8")
    big_bars += f'''<div class="hbar-row"><div class="hbar-label">{i+1}. {html.escape(p['n'])} <span class="sub">{p['c']}</span></div><div class="hbar-track"><div class="hbar-fill" style="width:{w}%;background:{col}"></div></div><div class="hbar-val">{fmt_mb(p['mb'])}</div></div>'''

# ---- 命名风格 ----
names = [p["n"] for p in projs]
date_n = sum(1 for n in names if re.match(r"^\d{4,6}", n))
cn_n = sum(1 for n in names if re.search(r"[\u4e00-\u9fff]", n) and not re.match(r"^\d{4,6}", n))
en_n = sum(1 for n in names if re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", n))
mix_n = max(0, N - date_n - cn_n - en_n)

def donut_arcs(parts, colors, total):
    r = 90; cx = 120; cy = 120
    seg = []
    start = -90
    for v, col in zip(parts, colors):
        frac = v / total
        a1 = start; a2 = start + frac * 360
        seg.append((col, a1, a2))
        start = a2
    paths = []
    for col, a1, a2 in seg:
        if a2 - a1 >= 359.9:
            paths.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="34"/>')
            continue
        x1 = cx + r * math.cos(math.radians(a1)); y1 = cy + r * math.sin(math.radians(a1))
        x2 = cx + r * math.cos(math.radians(a2)); y2 = cy + r * math.sin(math.radians(a2))
        large = 1 if (a2 - a1) > 180 else 0
        paths.append(f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{col}" stroke-width="34"/>')
    return "".join(paths)

cat_cols = [CAT_COLORS.get(c, "#94a3b8") for c, v in cat_sorted]
cat_vals = [v["count"] for c, v in cat_sorted]
donut_cat = donut_arcs(cat_vals, cat_cols, sum(cat_vals))

name_parts = [date_n, cn_n, en_n, mix_n]
name_cols = ["#f59e0b", "#ef4444", "#3b82f6", "#94a3b8"]
donut_name = donut_arcs(name_parts, name_cols, N)

# ---- 趣味事实（数据驱动，自动更新） ----
readme_n = sum(1 for p in projs if p["r"])
readme_pct = round(readme_n / N * 100)
top = projs[0]
top_pct = round(top["mb"] / total_mb * 100)
comp_cats = ["比赛项目", "模型测试", "AI编程工具", "命理玄学", "视频音频处理", "游戏娱乐"]
model_words = ["deepseek", "claude", "minimax", "mimo", "qwen", "gemini", "longcat", "m2.1"]
model_hits = [p["n"] for p in projs if any(w in p["n"].lower() for w in model_words)]

facts = [
    ("👑", "空间之王", f"「{top['n']}」现在占 {fmt_mb(top['mb'])}，一个人顶掉了全部空间的 {top_pct}%"),
    ("📅", "两年发力", f"{N} 个项目里，{yr_counter.get(2025,0)} 个落在 2025 年、{yr_counter.get(2026,0)} 个落在 2026 年 —— 大部分都是这两年折腾出来的"),
    ("🧪", "小实验体质", f"{N} 个项目的中位数只有 {fmt_mb(median_mb)}，平均却有 {fmt_mb(total_mb/N)} —— 一堆小实验，偶尔憋个大的"),
    ("🕐", "深夜收工", f"最后修改时间分布在 {peak_hour} 点最集中，0 点到 2 点之间收尾的项目有 {night_count} 个 —— 懂的都懂"),
    ("🔮", "玄学浓度", f"{cats.get(chr(21629)+chr(29702)+chr(29572)+chr(23398),{}).get(chr(99)+chr(111)+chr(117)+chr(110)+chr(116),0)} 个命理项目：八字、六爻、印占、算命提示词……AI 时代照样给老祖宗打工"),
    ("📚", "README 覆盖率", f"只有 {readme_n}/{N} 个项目写了 README（{readme_pct}%）—— 好项目值得写个说明书"),
    ("🏁", "比赛没停过", "核聚变、AMD、魔搭、全球攻防……从 2025 年一路比到 2026 年，文件夹就是战绩"),
    ("🔥", "最近还热着", f"近 90 天还有 {len(recent)} 个项目在动：{html.escape(recent_sorted[0]['n'])}、{html.escape(recent_sorted[1]['n'])}……没停过"),
]

facts_html = "".join(f'''<div class="fact-card"><div class="fact-emoji">{e}</div><div class="fact-body"><h4>{t}</h4><p>{d}</p></div></div>''' for e, t, d in facts)

HTML_DOC = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI_Projects 探险手记 · {N} 个项目的两年</title>
<style>
  :root {{
    --bg: #f6f7fb; --card: #ffffff; --ink: #1e2433; --sub: #6b7280;
    --line: #e5e7eb; --accent: #6366f1;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--ink); font-family:"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif; line-height:1.6; }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:32px 20px 80px; }}

  /* 头部 */
  .hero {{ background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 55%,#db2777 100%); border-radius:20px; padding:44px 40px; color:#fff; position:relative; overflow:hidden; }}
  .hero::after {{ content:""; position:absolute; right:-60px; top:-60px; width:280px; height:280px; border-radius:50%; background:rgba(255,255,255,.08); }}
  .hero::before {{ content:""; position:absolute; right:60px; bottom:-90px; width:200px; height:200px; border-radius:50%; background:rgba(255,255,255,.06); }}
  .hero h1 {{ font-size:30px; font-weight:800; letter-spacing:1px; }}
  .hero p {{ opacity:.9; margin-top:8px; font-size:15px; }}
  .hero .scan-meta {{ margin-top:14px; font-size:13px; opacity:.75; }}
  .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-top:22px; }}
  .stat {{ background:rgba(255,255,255,.14); backdrop-filter:blur(6px); border-radius:14px; padding:14px 16px; }}
  .stat b {{ display:block; font-size:26px; font-weight:800; }}
  .stat span {{ font-size:12.5px; opacity:.85; }}

  section {{ margin-top:34px; }}
  .sec-head {{ display:flex; align-items:baseline; gap:10px; margin-bottom:14px; }}
  .sec-head h2 {{ font-size:20px; font-weight:800; }}
  .sec-head .tag {{ font-size:12px; color:var(--accent); background:#eef2ff; padding:3px 10px; border-radius:20px; font-weight:600; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:22px; }}
  .card h3 {{ font-size:15px; margin-bottom:14px; display:flex; align-items:center; gap:8px; }}
  .sub {{ color:var(--sub); font-size:12px; font-weight:400; margin-left:4px; }}

  /* 条形图 */
  .hbar-row {{ display:grid; grid-template-columns:150px 1fr 44px; align-items:center; gap:10px; margin:9px 0; }}
  .hbar-label {{ font-size:13px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .hbar-track {{ background:#f1f3f7; border-radius:8px; height:16px; overflow:hidden; }}
  .hbar-fill {{ height:100%; border-radius:8px; min-width:2px; }}
  .hbar-val {{ font-size:12.5px; color:var(--sub); text-align:right; }}

  /* 环形图 */
  .donut-wrap {{ display:flex; align-items:center; gap:26px; }}
  .donut-legend {{ flex:1; }}
  .dl-row {{ display:flex; align-items:center; gap:8px; font-size:13px; margin:6px 0; }}
  .dl-dot {{ width:10px; height:10px; border-radius:3px; flex-shrink:0; }}
  .dl-row b {{ margin-left:auto; }}

  /* 项目网格 */
  .pfilter {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; }}
  .pbtn {{ border:1px solid var(--line); background:#fff; padding:6px 14px; border-radius:20px; font-size:12.5px; cursor:pointer; transition:.15s; color:var(--ink); }}
  .pbtn:hover {{ border-color:var(--accent); }}
  .pbtn.on {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .pgrid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:12px; }}
  .pcard {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 14px; transition:.15s; }}
  .pcard:hover {{ transform:translateY(-2px); box-shadow:0 8px 20px rgba(0,0,0,.06); border-color:#c7d2fe; }}
  .pc-name {{ font-size:13.5px; font-weight:700; display:flex; align-items:center; gap:7px; }}
  .dot {{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }}
  .pc-meta {{ display:flex; gap:10px; font-size:11.5px; color:var(--sub); margin-top:5px; }}
  .pc-bar {{ height:4px; background:#f1f3f7; border-radius:3px; margin-top:8px; overflow:hidden; }}
  .pc-bar div {{ height:100%; border-radius:3px; }}
  .empty-tip {{ color:var(--sub); text-align:center; padding:30px; display:none; }}

  /* 趣味事实 */
  .facts {{ display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }}
  .fact-card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 18px; display:flex; gap:14px; align-items:flex-start; }}
  .fact-emoji {{ font-size:26px; }}
  .fact-body h4 {{ font-size:14.5px; margin-bottom:3px; }}
  .fact-body p {{ font-size:13px; color:var(--sub); }}

  .stat-chip {{ background:#f8fafc; border:1px solid var(--line); border-radius:10px; padding:10px 14px; font-size:12.5px; display:inline-block; margin:0 8px 8px 0; }}
  .stat-chip b {{ display:block; font-size:13px; }}

  .foot {{ text-align:center; color:var(--sub); font-size:12px; margin-top:40px; }}
  @media (max-width:760px) {{ .grid2,.facts {{ grid-template-columns:1fr; }} .stats {{ grid-template-columns:repeat(2,1fr); }} }}
</style>
</head>
<body>
<div class="wrap">

  <div class="hero">
    <h1>🧭 AI_Projects 探险手记</h1>
    <p>D 盘那个 {N} 个项目的「AI 大杂烩」，翻了个底朝天。全是这两年玩出来的，顺手记一笔。</p>
    <div class="scan-meta">记录时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} · 跨度 {first_d} → {last_d} · 纯只读翻的，一个字节没动</div>
    <div class="stats">
      <div class="stat"><b>{N}</b><span>个项目</span></div>
      <div class="stat"><b>{fmt_mb(total_mb)}</b><span>总占用空间</span></div>
      <div class="stat"><b>{total_files:,}</b><span>个文件</span></div>
      <div class="stat"><b>{len(cats)}</b><span>大主题分类</span></div>
    </div>
  </div>

  <!-- 主题分布 -->
  <section>
    <div class="sec-head"><h2>📊 都在玩什么</h2><span class="tag">谁最能占地方 vs 谁数量最多</span></div>
    <div class="grid2">
      <div class="card">
        <h3>按项目数量</h3>
        {cat_list}
      </div>
      <div class="card">
        <h3>环形占比</h3>
        <div class="donut-wrap">
          <svg viewBox="0 0 240 240" width="190" height="190">
            {donut_cat}
            <text x="120" y="114" text-anchor="middle" font-size="26" font-weight="800" fill="#1e2433">{N}</text>
            <text x="120" y="134" text-anchor="middle" font-size="11" fill="#6b7280">个项目</text>
          </svg>
          <div class="donut-legend">
            {''.join(f'<div class="dl-row"><span class="dl-dot" style="background:{CAT_COLORS.get(c,"#94a3b8")}"></span>{c}<b>{v["count"]}</b></div>' for c,v in cat_sorted)}
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- 年份截面 + 活跃时间线 -->
  <section>
    <div class="sec-head"><h2>📈 什么时候在搞</h2><span class="tag">按最后修改时间算</span></div>
    <div class="grid2">
      <div class="card">
        <h3>年份截面 <span class="sub">谁留下过痕迹</span></h3>
        {year_html}
        <p class="sub" style="margin-top:10px">2024 年只是踩了踩水，真正上头是 2025 年往后——{yr_counter.get(2025,0)} + {yr_counter.get(2026,0)} 个项目都是这两年搞的。</p>
      </div>
      <div class="card">
        <h3>按月活跃</h3>
        <svg viewBox="0 0 480 150" width="100%" style="display:block">
          <rect x="0" y="0" width="480" height="150" fill="none"/>
          {''.join(f'<text x="{20+i*32}" y="142" font-size="8.5" fill="#6b7280" text-anchor="middle">{lbl}</text>' for i,lbl in enumerate(tl_labels.split(",")) if i % 2 == 0)}
          {''.join(f'<rect x="{14+i*32}" y="{138-v*5}" width="18" height="{max(2,v*5)}" rx="2" fill="{ "#6366f1" if i%2==0 else "#a5b4fc" }"><title>{lbl}: {v} 个项目</title></rect>' for i,(lbl,v) in enumerate(zip(tl_labels.split(","), map(int, tl_values.split(",")))) if v >= 1)}
        </svg>
        <p class="sub" style="margin-top:8px">2025 下半年开始明显发力，之后基本没停过。</p>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-head"><h2>💻 技术画像</h2><span class="tag">主语言 + 规模</span></div>
    <div class="grid2">
      <div class="card">
        <h3>主语言分布 <span class="sub">按项目</span></h3>
        {lang_bars}
      </div>
      <div class="card">
        <h3>项目规模分档</h3>
        {tier_bars}
        <p class="sub" style="margin-top:10px">「微小」= 1MB 以下，「巨大」= 1GB 以上。中位数只有 {fmt_mb(median_mb)}，但偶尔也会憋个大的。</p>
      </div>
    </div>
  </section>

  <!-- 命名风格 -->
  <section>
    <div class="sec-head"><h2>🏷️ 命名风格</h2><span class="tag">{N} 个名字里有性格</span></div>
    <div class="card">
      <div class="donut-wrap">
        <svg viewBox="0 0 240 240" width="190" height="190">
          {donut_name}
          <text x="120" y="114" text-anchor="middle" font-size="26" font-weight="800" fill="#1e2433">{N}</text>
          <text x="120" y="134" text-anchor="middle" font-size="11" fill="#6b7280">种取名姿势</text>
        </svg>
        <div class="donut-legend">
          <div class="dl-row"><span class="dl-dot" style="background:#f59e0b"></span>日期开头（251125…）<b>{date_n}</b></div>
          <div class="dl-row"><span class="dl-dot" style="background:#ef4444"></span>中文名（命理/游戏/工具…）<b>{cn_n}</b></div>
          <div class="dl-row"><span class="dl-dot" style="background:#3b82f6"></span>英文名（Hermes Agent…）<b>{en_n}</b></div>
          <div class="dl-row"><span class="dl-dot" style="background:#94a3b8"></span>混合/其他<b>{mix_n}</b></div>
        </div>
      </div>
    </div>
  </section>

  <!-- 空间榜 -->
  <section>
    <div class="sec-head"><h2>🚀 空间消耗榜 Top10</h2><span class="tag">硬盘都给了谁</span></div>
    <div class="card">
      {big_bars}
    </div>
  </section>

  <!-- 最近活跃 -->
  <section>
    <div class="sec-head"><h2>🕑 近 90 天还在动的</h2><span class="tag">没吃灰的项目</span></div>
    <div class="card">
      {recent_html}
      <p class="sub" style="margin-top:6px">上面这些是最近三个月还有文件改动的，一共 {len(recent)} 个。剩下的在吃灰，但说不定哪天又捡起来。</p>
    </div>
  </section>

  <!-- 趣味事实 -->
  <section>
    <div class="sec-head"><h2>🎯 这文件夹的 8 个隐藏事实</h2><span class="tag">翻出来的彩蛋</span></div>
    <div class="facts">
      {facts_html}
    </div>
  </section>

  <!-- 项目全表 -->
  <section>
    <div class="sec-head"><h2>🗂️ 全部 {N} 个项目</h2><span class="tag">点分类筛选 · 📖=有README</span></div>
    <div class="pfilter">
      <button class="pbtn on" data-f="all">全部</button>
      {''.join(f'<button class="pbtn" data-f="{c}">{c} ({v})</button>' for c,v in cat_count.items())}
    </div>
    <div class="pgrid" id="pgrid">
      {cards_html}
    </div>
    <div class="empty-tip" id="emptyTip">这个分类下暂时没项目～</div>
  </section>

  <div class="foot">AI_Projects 探险手记 · 记于 {datetime.datetime.now().strftime("%Y-%m-%d")} · 翻的是自己的文件夹，没动任何东西</div>
</div>

<script>
  const btns = document.querySelectorAll('.pbtn');
  const cards = document.querySelectorAll('.pcard');
  const tip = document.getElementById('emptyTip');
  btns.forEach(b => b.addEventListener('click', () => {{
    btns.forEach(x => x.classList.remove('on'));
    b.classList.add('on');
    const f = b.dataset.f;
    let shown = 0;
    cards.forEach(c => {{
      const ok = f === 'all' || c.dataset.cat === f;
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    tip.style.display = shown === 0 ? 'block' : 'none';
  }}));
</script>
</body>
</html>
"""

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML_DOC)
print("已生成:", out_path)
print(f"HTML 大小: {len(HTML_DOC)/1024:.0f} KB")
