"""
GMP 药品仓库管理 AI 系统 — Flask Web 应用
提供知识搜索、分类浏览、智能问答、数据管理 API
"""
import os
import re
import json
from flask import Flask, render_template, request, jsonify, send_from_directory

from kb_search import kb
from data_manager import (
    get_zone_status, get_recent_logs, get_alarms,
    get_batches_by_status, get_near_expiry, get_dashboard_stats
)

app = Flask(__name__, template_folder="templates", static_folder="static")


# ==================== 页面路由 ====================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ==================== 知识库 API ====================

@app.route("/api/modules")
def get_modules():
    modules = []
    for name in kb.get_modules():
        entries = kb.get_module_entries(name)
        modules.append({"name": name, "count": len(entries), "entries": entries})
    return jsonify({"modules": modules})


@app.route("/api/module/<module_name>")
def get_module(module_name):
    entries = kb.get_module_entries(module_name)
    return jsonify({"module": module_name, "entries": entries})


@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": [], "suggestions": []})
    results = kb.search(query)
    suggestions = kb.suggest(query)
    return jsonify({
        "query": query, "results": results,
        "suggestions": suggestions, "total": len(results)
    })


@app.route("/api/ask")
def ask():
    question = request.args.get("q", "").strip()
    if not question:
        return jsonify({"answer": "", "sources": []})

    results = kb.search(question, top_k=5)
    if not results:
        return jsonify({
            "answer": "抱歉，知识库中没有找到与您问题相关的内容。请尝试换个说法提问。",
            "sources": []
        })

    primary = results[0]
    secondary = results[1] if len(results) > 1 else None

    answer_parts = [f"根据《{primary['module']}》相关规定："]
    answer_parts.append(primary["content"][:500])

    if secondary and secondary["module"] != primary["module"]:
        answer_parts.append(f"\n\n另可参考《{secondary['module']}》相关内容。")

    if "GMP" in primary["content"] or "GSP" in primary["content"]:
        gmp_refs = re.findall(r'GMP\s*第\s*\d+\s*条', primary["content"])
        if gmp_refs:
            answer_parts.append(f"\n\n📋 引用法规：{', '.join(set(gmp_refs))}")

    return jsonify({"answer": "".join(answer_parts), "sources": results[:3]})


@app.route("/api/overview")
def overview():
    modules = kb.get_modules()
    return jsonify({
        "total_modules": len(modules),
        "total_entries": len(kb.entries),
        "total_chars": sum(len(e.content) for e in kb.entries),
        "modules": modules
    })


# ==================== 数据管理 API ====================

@app.route("/api/dashboard/stats")
def dashboard_stats():
    """仪表盘统计数据"""
    return jsonify(get_dashboard_stats())


@app.route("/api/dashboard/zones")
def dashboard_zones():
    """仓库区域实时状态"""
    return jsonify({"zones": get_zone_status()})


@app.route("/api/dashboard/logs")
def dashboard_logs():
    """温湿度记录"""
    zone_id = request.args.get("zone_id", type=int)
    limit = request.args.get("limit", 50, type=int)
    return jsonify({"logs": get_recent_logs(zone_id, limit)})


@app.route("/api/dashboard/alarms")
def dashboard_alarms():
    """报警记录"""
    return jsonify({"alarms": get_alarms()})


@app.route("/api/dashboard/batches")
def dashboard_batches():
    """物料批次"""
    status = request.args.get("status")
    return jsonify({"batches": get_batches_by_status(status)})


@app.route("/api/dashboard/near-expiry")
def dashboard_near_expiry():
    """近效期物料"""
    days = request.args.get("days", 90, type=int)
    return jsonify({"batches": get_near_expiry(days), "days": days})


# ==================== 静态文件 ====================

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


# ==================== 启动 ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*50}")
    print(f"  GMP 药品仓库管理 AI 系统")
    print(f"  知识库: {len(kb.entries)} 条 / {len(kb.get_modules())} 个模块")
    print(f"  服务地址: http://127.0.0.1:{port}")
    print(f"  仪表盘: http://127.0.0.1:{port}/dashboard")
    print(f"{'='*50}\n")
    app.run(host="127.0.0.1", port=port, debug=True)
