#!/usr/bin/env python3
"""列出项目所有文件，按目录分组输出到docs/project_files.md"""

import os
from collections import defaultdict
from pathlib import Path

def count_lines(file_path: Path) -> int:
    """计算文件行数，二进制文件返回 -1"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return -1


def list_project_files(root_dir: str = ".", exclude_dirs: set = None) -> str:
    """
    列出项目文件，按目录分组

    Args:
        root_dir: 项目根目录
        exclude_dirs: 要排除的目录名集合

    Returns:
        格式化的文件列表字符串
    """
    if exclude_dirs is None:
        exclude_dirs = {"KarisCode", ".git", "node_modules", ".next", "dist"}

    root = Path(root_dir).resolve()
    files_by_dir = defaultdict(list)

    for dirpath, dirnames, filenames in os.walk(root):
        # 排除指定目录
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        if filenames:
            rel_dir = os.path.relpath(dirpath, root)
            rel_dir = "." if rel_dir == "." else rel_dir
            for f in sorted(filenames):
                files_by_dir[rel_dir].append(f)

    # 生成输出
    lines = ["# 项目文件列表\n"]
    separator = "-" * 60

    for dir_path in sorted(files_by_dir.keys()):
        lines.append(f"\n## 📁 {dir_path}\n")
        for filename in files_by_dir[dir_path]:
            full_path = os.path.join(dir_path, filename)
            abs_path = root / full_path
            line_count = count_lines(abs_path)
            line_str = f" ({line_count} lines)" if line_count >= 0 else ""
            lines.append(f"- {filename}：`{full_path}`{line_str}")
        lines.append(f"\n{separator}\n")

    return "\n".join(lines)


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    output = list_project_files(project_root)

    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    output_file = docs_dir / "project_files.md"
    output_file.write_text(output, encoding="utf-8")

    print(f"文件列表已生成：{output_file}")


if __name__ == "__main__":
    main()
