# AI_Projects 探险手记

D 盘那个 AI 项目文件夹，两年攒了 **149 个项目**。周末闲着没事翻了一遍，顺手做了个数据画像，记在这里。

- 149 个项目 · 13.6GB · 49,486 个文件
- 2025 年新增 59 个、2026 年到 9 月又添 75 个 —— 上头是 2025 年下半年开始的
- 项目大小中位数只有 0.70MB —— 一堆小实验，偶尔憋个大的
- 命理玄学浓度意外地高（八字、六爻、印占、算命提示词……）
- 比赛没停过：核聚变、AMD、魔搭、全球攻防，从 2025 一路比到 2026

点开 [index.html](index.html) 看全图，或直接访问 **https://foreverwonder.github.io/ai-projects-exploration/**

## 这文件夹里都有啥

| 主题 | 项目数 | 占用 |
|---|---|---|
| AI编程工具 | 26 | 1.32GB |
| 素材归档 | 25 | 1.22GB |
| 模型测试 | 16 | 6.22GB |
| 效率工具 | 12 | 42MB |
| 视频音频处理 | 11 | 2.57GB |
| 命理玄学 | 11 | 768MB |
| 比赛项目 | 10 | 707MB |
| 学习教育 | 10 | 15MB |
| 内容创作 | 9 | 287MB |
| Web应用 | 9 | 17MB |
| 游戏娱乐 | 6 | 4MB |
| 股票财经 | 4 | 530MB |

数据是 2026-09-20 用只读脚本重扫的，一个字节没动。

## 生成方式

```bash
python scan_ai_projects.py     # 只读扫描 D:\AI_Projects → raw_scan.json
python classify.py             # 读 raw_scan.json，人工分类表定类 → dashboard_data.json
python build_dashboard.py      # 读 dashboard_data.json → index.html
```

- `scan_ai_projects.py` —— 只读遍历目录，收集文件数 / 体积 / 语言 / 最后修改时间（可传目标目录）
- `classify.py` —— 分类表 `MANUAL` 是逐个核对文件特征手工定的，不靠关键词猜；新增项目手动补一行，脚本会提示漏掉的
- `build_dashboard.py` —— 生成自包含单文件 HTML，无外部依赖、不联网

想更新数字就按上面顺序重跑三遍。
