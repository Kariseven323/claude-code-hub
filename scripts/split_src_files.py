#!/usr/bin/env python3
"""
将 project_files.md 中 src/ 目录下的文件按每 5 份一组分割，
生成用于分析 KarisCode 重写完整性的请求句子。
"""

import re
from pathlib import Path


def parse_project_files(content: str) -> dict[str, list[str]]:
    """解析 project_files.md，提取 src/ 目录下的文件列表。"""
    directories = {}
    current_dir = None

    lines = content.split('\n')
    for line in lines:
        # 匹配目录标题：## 📁 src/xxx
        dir_match = re.match(r'^## 📁 (src/.*)$', line)
        if dir_match:
            current_dir = dir_match.group(1)
            directories[current_dir] = []
            continue

        # 匹配文件行：- filename：`path` (xxx lines)
        if current_dir and current_dir.startswith('src/'):
            file_match = re.match(r'^- (.+?)：`(.+?)`\s*\((\d+) lines\)', line)
            if file_match:
                filename = file_match.group(1)
                filepath = file_match.group(2)
                lines_count = file_match.group(3)
                # 保留原始格式
                directories[current_dir].append(f"- {filename}：`{filepath}` ({lines_count} lines)")

    # 只保留 src/ 开头的目录
    return {k: v for k, v in directories.items() if k.startswith('src/')}


def chunk_list(lst: list, chunk_size: int = 5) -> list[list]:
    """将列表按指定大小分割。"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def generate_analysis_requests(directories: dict[str, list[str]]) -> list[str]:
    """生成分析请求句子。"""
    requests = []

    for dir_path, files in directories.items():
        if not files:
            continue

        chunks = chunk_list(files, 5)

        for chunk in chunks:
            file_list = '\n'.join(chunk)
            request = f"""请你分析当前项目：
{file_list}
这些文件在KarisCode文件夹内的重写是否1:1复刻的完整实现，然后更新文档docs/contrast.md，详细列出语义一致的部分和语义不一致的部分"""
            requests.append(request)

    return requests


def main():
    # 读取 project_files.md
    project_files_path = Path(__file__).parent.parent / 'docs' / 'project_files.md'

    if not project_files_path.exists():
        print(f"错误：找不到文件 {project_files_path}")
        return

    content = project_files_path.read_text(encoding='utf-8')

    # 解析文件
    directories = parse_project_files(content)

    # 生成分析请求
    requests = generate_analysis_requests(directories)

    # 输出结果
    print(f"共找到 {len(directories)} 个 src/ 目录")
    print(f"共生成 {len(requests)} 个分析请求\n")
    print("=" * 60)

    for i, request in enumerate(requests, 1):
        print(f"\n【请求 {i}】\n")
        print(request)
        print("\n" + "-" * 60)

    # 同时写入到输出文件
    output_path = Path(__file__).parent.parent / 'docs' / 'analysis_requests.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 代码重写分析请求\n\n")
        f.write(f"共 {len(requests)} 个分析请求\n\n")
        for i, request in enumerate(requests, 1):
            f.write(f"## 请求 {i}\n\n")
            f.write(f"```\n{request}\n```\n\n")

    print(f"\n结果已保存到：{output_path}")


if __name__ == '__main__':
    main()
