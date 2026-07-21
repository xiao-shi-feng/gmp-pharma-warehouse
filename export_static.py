"""
GMP 知识库数据导出器 — 将知识库导出为静态 JSON
用于 GitHub Pages 静态部署
"""
import json
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))
from kb_search import kb


def export_static_data(output_dir: str = "static-data"):
    """导出所有知识库数据为静态 JSON"""
    os.makedirs(output_dir, exist_ok=True)

    # 1. 导出所有模块
    modules_data = []
    for name in kb.get_modules():
        entries = kb.get_module_entries(name)
        modules_data.append({
            "name": name,
            "count": len(entries),
            "entries": entries
        })

    with open(os.path.join(output_dir, "modules.json"), "w", encoding="utf-8") as f:
        json.dump({"modules": modules_data}, f, ensure_ascii=False, indent=2)

    # 2. 导出扁平搜索索引
    all_entries = []
    for entry in kb.entries:
        all_entries.append(entry.to_dict())

    with open(os.path.join(output_dir, "entries.json"), "w", encoding="utf-8") as f:
        json.dump({"entries": all_entries, "total": len(all_entries)},
                  f, ensure_ascii=False, indent=2)

    # 3. 导出概览统计
    overview = {
        "total_modules": len(kb.get_modules()),
        "total_entries": len(kb.entries),
        "modules": kb.get_modules()
    }
    with open(os.path.join(output_dir, "overview.json"), "w", encoding="utf-8") as f:
        json.dump(overview, f, ensure_ascii=False, indent=2)

    print(f"✅ 静态数据已导出到 {output_dir}/")
    print(f"   模块: {len(modules_data)}")
    print(f"   条目: {len(all_entries)}")
    return output_dir


if __name__ == "__main__":
    export_static_data()
