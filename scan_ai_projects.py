# -*- coding: utf-8 -*-
"""只读扫描 D:\AI_Projects，收集项目元数据用于统计分析。不做任何修改。"""
import os, json, time
from collections import Counter, defaultdict

ROOT = r"D:\AI_Projects"

# 跳过的大目录（避免扫描 node_modules 等海量文件）
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build",
             ".next", ".nuxt", ".cache", "target", "site-packages", ".obsidian",
             ".trash", ".gitbook", "vendor", "Pods", ".idea", ".vscode"}
SKIP_EXTS = {".pyc", ".pyo", ".class", ".o", ".so", ".dll", ".exe", ".png", ".jpg",
             ".jpeg", ".gif", ".mp4", ".mp3", ".zip", ".rar", ".7z", ".webp", ".ico",
             ".woff", ".woff2", ".ttf", ".map", ".lock"}

def is_skip_dir(name):
    return name in SKIP_DIRS or name.startswith(".")

def scan_dir(path, depth=0, max_depth=12):
    """返回 (文件数, 总大小, 语言计数, 最近修改时间戳, 扩展名Top)"""
    file_count = 0
    total_size = 0
    lang_counter = Counter()
    ext_counter = Counter()
    latest_mtime = 0
    readme_found = False
    max_files = 200000  # 安全阀
    try:
        entries = os.scandir(path)
    except (PermissionError, OSError):
        return file_count, total_size, {}, latest_mtime, ext_counter, readme_found, {}
    with entries as it:
        for e in it:
            if file_count >= max_files:
                break
            try:
                if e.is_dir(follow_symlinks=False):
                    if is_skip_dir(e.name) or depth >= max_depth:
                        continue
                    fc, ts, lc, lm, extc, rf, sub_meta = scan_dir(e.path, depth+1, max_depth)
                    file_count += fc
                    total_size += ts
                    lang_counter.update(lc)
                    ext_counter.update(extc)
                    latest_mtime = max(latest_mtime, lm)
                    readme_found = readme_found or rf
                else:
                    name_l = e.name.lower()
                    if name_l in ("desktop.ini", "thumbs.db"):
                        continue
                    try:
                        st = e.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    file_count += 1
                    total_size += st.st_size
                    latest_mtime = max(latest_mtime, st.st_mtime)
                    ext = os.path.splitext(name_l)[1]
                    if ext and ext not in SKIP_EXTS:
                        ext_counter[ext] += 1
                    if name_l.startswith("readme") or "readme" in name_l:
                        readme_found = True
                    if ext in (".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go",
                               ".c", ".cpp", ".rs", ".html", ".css", ".vue", ".md",
                               ".json", ".yaml", ".yml", ".sh", ".bat", ".ps1",
                               ".php", ".rb", ".swift", ".kt", ".sql", ".ipynb", ".mjs"):
                        lang_counter[ext] += 1
            except OSError:
                continue
    return file_count, total_size, dict(lang_counter), latest_mtime, dict(ext_counter), readme_found, {}

def lang_name(ext):
    m = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
         ".jsx": "JavaScript", ".java": "Java", ".go": "Go", ".c": "C", ".cpp": "C++",
         ".rs": "Rust", ".html": "HTML", ".css": "CSS", ".vue": "Vue", ".md": "Markdown",
         ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".sh": "Shell", ".bat": "Batch",
         ".ps1": "PowerShell", ".php": "PHP", ".rb": "Ruby", ".swift": "Swift",
         ".kt": "Kotlin", ".sql": "SQL", ".ipynb": "Jupyter", ".mjs": "JavaScript"}
    return m.get(ext, ext.lstrip(".").upper())

def main():
    results = []
    total_start = time.time()
    for e in sorted(os.scandir(ROOT), key=lambda x: x.name.lower()):
        if e.is_dir(follow_symlinks=False):
            if e.name in (".obsidian", "logs") or e.name.startswith("."):
                continue
            fc, ts, lc, lm, extc, rf, _ = scan_dir(e.path)
            if fc == 0:
                # 空目录也算
                pass
            total_ext = sum(extc.values())
            # 主语言 = 出现最多的代码/文档扩展名（排除json/md优先选代码）
            code_priority = [k for k in lc if k not in (".md", ".json", ".yaml", ".yml")]
            if code_priority:
                main_lang = lang_name(max(code_priority, key=lc.get))
            elif lc:
                main_lang = lang_name(max(lc, key=lc.get))
            else:
                main_lang = "其他"
            results.append({
                "name": e.name,
                "type": "dir",
                "file_count": fc,
                "size_bytes": ts,
                "latest_mtime": lm,
                "langs": lc,
                "main_lang": main_lang,
                "readme": rf,
                "top_exts": dict(sorted(extc.items(), key=lambda x: -x[1])[:5]),
            })
        else:
            try:
                st = e.stat(follow_symlinks=False)
                if e.name.lower() == "desktop.ini":
                    continue
                results.append({
                    "name": e.name, "type": "file", "file_count": 1,
                    "size_bytes": st.st_size, "latest_mtime": st.st_mtime,
                    "langs": {}, "main_lang": "文件",
                    "readme": False, "top_exts": {}
                })
            except OSError:
                continue

    out = {
        "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "root": ROOT,
        "elapsed_s": round(time.time() - total_start, 1),
        "projects": results,
    }
    with open(r"C:\Users\71976\WorkBuddy\2026-08-11-23-35-59\ai_projects_scan.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"扫描完成: {len(results)} 个条目, 耗时 {out['elapsed_s']}s")
    # 打印概览
    total_files = sum(r["file_count"] for r in results if r["type"] == "dir")
    total_size = sum(r["size_bytes"] for r in results if r["type"] == "dir")
    print(f"目录数: {sum(1 for r in results if r['type']=='dir')}, 总文件数: {total_files}, 总大小: {total_size/1024/1024:.1f} MB")

if __name__ == "__main__":
    main()
