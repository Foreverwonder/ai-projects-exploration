# -*- coding: utf-8 -*-
r"""只读扫描目录，收集项目元数据。不改动任何文件。

用法：  python scan_ai_projects.py [目标目录]
默认扫 D:\AI_Projects，结果写到同目录 raw_scan.json。

Windows 上的坑（都踩过）：
  - 一律 os.scandir，不要 os.stat(路径)，慢 8 倍
  - junction 用 st_file_attributes & 0x400 判断，os.path.islink 对 junction 返回 False
  - NTFS 存在负时间戳，time.localtime 会直接抛 OSError；判据 m < 0 or m > 253402300799，
    并且必须在 min/max 聚合「之前」过滤，否则会污染结果
"""
import os, json, time, sys

SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build",
             ".next", ".nuxt", ".cache", "target", "site-packages", ".obsidian",
             ".trash", ".gitbook", "vendor", "Pods", ".idea", ".vscode", ".pnpm-store",
             ".mypy_cache", ".pytest_cache", ".ruff_cache", "coverage"}
SKIP_FILES = {"desktop.ini", "thumbs.db", ".ds_store"}
MT_MAX = 253402300799.0

LANG_MAP = {".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
            ".ts": "TypeScript", ".tsx": "TypeScript", ".jsx": "JavaScript", ".java": "Java",
            ".go": "Go", ".c": "C", ".cpp": "C++", ".h": "C", ".rs": "Rust",
            ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".vue": "Vue", ".svelte": "Svelte",
            ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
            ".sh": "Shell", ".bat": "Batch", ".ps1": "PowerShell", ".php": "PHP",
            ".rb": "Ruby", ".swift": "Swift", ".kt": "Kotlin", ".sql": "SQL",
            ".ipynb": "Jupyter", ".cs": "C#", ".lua": "Lua", ".toml": "TOML"}
DOC_EXTS = (".md", ".json", ".yaml", ".yml", ".toml", ".txt")


def good(m):
    return m is not None and 0 <= m <= MT_MAX


def scan_dir(path, depth=0, max_depth=14):
    files = size = 0
    langs, latest, readmes, top_names = {}, 0.0, [], []
    try:
        it = os.scandir(path)
    except (PermissionError, OSError):
        return dict(files=0, size=0, langs={}, latest=0.0, readmes=[], top_names=[])
    with it as entries:
        for e in entries:
            try:
                if e.is_dir(follow_symlinks=False):
                    try:
                        if e.stat(follow_symlinks=False).st_file_attributes & 0x400:
                            continue          # 重解析点（junction）
                    except (OSError, AttributeError):
                        pass
                    if e.name in SKIP_DIRS or e.name.startswith(".") or depth >= max_depth:
                        continue
                    sub = scan_dir(e.path, depth + 1, max_depth)
                    files += sub["files"]
                    size += sub["size"]
                    for k, v in sub["langs"].items():
                        langs[k] = langs.get(k, 0) + v
                    if good(sub["latest"]):
                        latest = max(latest, sub["latest"])
                    readmes.extend(sub["readmes"])
                    if depth == 0:
                        top_names.append((e.name, sub["files"], sub["size"]))
                else:
                    nm = e.name.lower()
                    if nm in SKIP_FILES:
                        continue
                    try:
                        st = e.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    files += 1
                    size += st.st_size
                    if good(st.st_mtime):
                        latest = max(latest, st.st_mtime)
                    ext = os.path.splitext(nm)[1]
                    if ext:
                        langs[ext] = langs.get(ext, 0) + 1
                    if nm.startswith("readme") and depth <= 2:
                        readmes.append(e.path)
                    if depth == 0:
                        top_names.append((e.name, 1, st.st_size))
            except OSError:
                continue
    return dict(files=files, size=size, langs=langs, latest=latest,
                readmes=readmes, top_names=top_names)


def read_readme_title(path):
    try:
        raw = open(path, "r", encoding="utf-8", errors="replace").read(4000)
    except OSError:
        return None, None
    title = desc = None
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if title is None and s.startswith("#"):
            title = s.lstrip("#").strip()
            continue
        if title is not None and not s.startswith(("#", "!", "[", "|", "<", "-", "*", ">", "`")) and len(s) > 4:
            desc = s[:110]
            break
    return title, desc


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else r"D:\AI_Projects"
    here = os.path.dirname(os.path.abspath(__file__))
    items, t0 = [], time.time()
    for e in sorted(os.scandir(root), key=lambda x: x.name.lower()):
        try:
            if e.is_dir(follow_symlinks=False):
                if e.name.startswith("."):
                    continue
                sub = scan_dir(e.path)
                title = desc = None
                for rp in sub["readmes"][:3]:
                    t, d = read_readme_title(rp)
                    if t:
                        title, desc = t, d
                        break
                code = {k: v for k, v in sub["langs"].items() if k not in DOC_EXTS}
                main_lang = "其他"
                if code:
                    main_lang = LANG_MAP.get(max(code, key=code.get), "其他")
                elif sub["langs"]:
                    main_lang = LANG_MAP.get(max(sub["langs"], key=sub["langs"].get), "其他")
                items.append(dict(name=e.name, kind="dir", files=sub["files"], size=sub["size"],
                                  latest=sub["latest"], readme_title=title, readme_desc=desc,
                                  main_lang=main_lang, readme_count=len(sub["readmes"]),
                                  top_children=[{"n": n, "f": f, "s": s} for n, f, s in
                                                sorted(sub["top_names"], key=lambda x: -x[2])[:6]]))
            else:
                if e.name.lower() in SKIP_FILES:
                    continue
                st = e.stat(follow_symlinks=False)
                items.append(dict(name=e.name, kind="file", files=1, size=st.st_size,
                                  latest=st.st_mtime, readme_title=None, readme_desc=None,
                                  main_lang="文件", readme_count=0, top_children=[]))
        except OSError:
            continue
    out = dict(root=root, items=items, scanned_at=time.strftime("%Y-%m-%d %H:%M:%S"),
               elapsed_s=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(here, "raw_scan.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    d = [x for x in items if x["kind"] == "dir"]
    print("扫描完成：%d 个目录 / %d 个文件 / %.1f MB / %.1fs" % (
        len(d), sum(x["files"] for x in d), sum(x["size"] for x in d) / 1048576, out["elapsed_s"]))


if __name__ == "__main__":
    main()
