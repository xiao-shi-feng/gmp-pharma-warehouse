"""
GMP 药品仓库管理 AI 系统 — 数据管理模块
包含数据库模型、温度数据模拟、报表生成
"""
import sqlite3
import os
import json
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "gmp_data.db")


def get_db():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 仓库区域表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_name TEXT NOT NULL,
            zone_type TEXT NOT NULL,
            color_mark TEXT NOT NULL,
            temperature_min REAL,
            temperature_max REAL,
            humidity_min REAL,
            humidity_max REAL,
            capacity INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 温湿度记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER,
            temperature REAL NOT NULL,
            humidity REAL,
            recorded_at TIMESTAMP NOT NULL,
            device_id TEXT,
            is_alarm INTEGER DEFAULT 0,
            FOREIGN KEY (zone_id) REFERENCES warehouse_zones(id)
        )
    """)

    # 物料批次表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS material_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_no TEXT NOT NULL UNIQUE,
            material_name TEXT NOT NULL,
            supplier TEXT,
            quantity INTEGER,
            unit TEXT,
            manufacture_date DATE,
            expiry_date DATE,
            status TEXT DEFAULT 'pending',
            zone_id INTEGER,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zone_id) REFERENCES warehouse_zones(id)
        )
    """)

    # 温度验证记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            validation_type TEXT NOT NULL,
            facility_name TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            result TEXT,
            report_path TEXT,
            verified_by TEXT,
            next_due_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 不合格品记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nonconformance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER,
            issue_type TEXT,
            description TEXT,
            severity TEXT,
            reported_by TEXT,
            reported_at TIMESTAMP,
            disposition TEXT,
            closed_at TIMESTAMP,
            status TEXT DEFAULT 'open',
            FOREIGN KEY (batch_id) REFERENCES material_batches(id)
        )
    """)

    # 报警规则表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarm_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL,
            zone_id INTEGER,
            temperature_min REAL,
            temperature_max REAL,
            humidity_min REAL,
            humidity_max REAL,
            notify_persons TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (zone_id) REFERENCES warehouse_zones(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_demo_data():
    """生成演示数据"""
    conn = get_db()
    cursor = conn.cursor()

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM warehouse_zones")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # 仓库区域
    zones = [
        ("常温库A区", "storage", "绿色", 10, 30, 35, 75, 5000, "常温药品及原辅料存储区"),
        ("阴凉库B区", "storage", "绿色", 2, 20, 35, 75, 3000, "阴凉储存要求的药品"),
        ("冷藏库C区", "cold_storage", "绿色", 2, 8, 35, 75, 1000, "冷藏药品（2~8℃）"),
        ("冷冻库D区", "freezer", "绿色", -25, -18, None, None, 500, "冷冻药品存储"),
        ("待验区", "quarantine", "黄色", 10, 30, 35, 75, 200, "待检验药品临时存放"),
        ("不合格品区", "rejected", "红色", 10, 30, 35, 75, 100, "不合格品隔离存放，双锁管理"),
        ("退货区", "return", "黄色", 10, 30, 35, 75, 150, "退货药品暂存待评估"),
        ("发货区", "shipping", "绿色", 10, 30, 35, 75, 300, "出库发货暂存区"),
    ]

    zone_ids = []
    for z in zones:
        cursor.execute("""
            INSERT INTO warehouse_zones (zone_name, zone_type, color_mark,
                temperature_min, temperature_max, humidity_min, humidity_max,
                capacity, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, z)
        zone_ids.append(cursor.lastrowid)

    # 模拟温湿度数据（过去24小时）
    now = datetime.now()
    temp_ranges = [
        (22, 26), (18, 20), (4, 7), (-20, -18),
        (22, 26), (22, 26), (22, 26), (22, 26)
    ]
    for zi, (tmin, tmax) in enumerate(temp_ranges):
        for h in range(24):
            t = round(random.uniform(tmin, tmax), 1)
            h_val = round(random.uniform(40, 65), 1)
            ts = now - timedelta(hours=23 - h)
            device = f"TH-{zi+1:03d}-{h+1:02d}"
            is_alarm = 1 if (t < tmin - 2 or t > tmax + 2) else 0
            cursor.execute("""
                INSERT INTO temperature_logs (zone_id, temperature, humidity,
                    recorded_at, device_id, is_alarm)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (zi + 1, t, h_val, ts.strftime("%Y-%m-%d %H:%M:%S"), device, is_alarm))

    # 模拟物料批次
    materials = [
        ("BATCH-2026001", "阿莫西林胶囊", "华北制药", 5000, "盒", "2026-01-15", "2028-01-14", "approved", 1),
        ("BATCH-2026002", "头孢克肟片", "石药集团", 3000, "盒", "2026-02-20", "2028-02-19", "approved", 1),
        ("BATCH-2026003", "胰岛素注射液", "通化东宝", 200, "支", "2026-03-01", "2027-09-01", "approved", 3),
        ("BATCH-2026004", "人血白蛋白", "华兰生物", 500, "瓶", "2026-03-10", "2027-03-09", "approved", 3),
        ("BATCH-2026005", "布洛芬缓释胶囊", "中美史克", 10000, "盒", "2026-04-01", "2028-03-31", "approved", 1),
        ("BATCH-2026006", "阿托伐他汀钙片", "辉瑞制药", 8000, "盒", "2026-04-15", "2027-10-14", "quarantine", 5),
        ("BATCH-2026007", "盐酸二甲双胍片", "上海医药", 12000, "盒", "2026-05-01", "2027-04-30", "approved", 2),
        ("BATCH-2026008", "注射用青霉素钠", "华北制药", 1500, "支", "2026-05-10", "2027-11-09", "rejected", 6),
        ("BATCH-2026009", "藿香正气水", "太极集团", 6000, "盒", "2026-06-01", "2028-05-31", "approved", 2),
        ("BATCH-2026010", "破伤风疫苗", "武汉生物", 1000, "支", "2026-06-15", "2027-06-14", "approved", 3),
    ]

    batch_ids = []
    for m in materials:
        cursor.execute("""
            INSERT INTO material_batches (batch_no, material_name, supplier,
                quantity, unit, manufacture_date, expiry_date, status, zone_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, m)
        batch_ids.append(cursor.lastrowid)

    # 不合格品记录
    cursor.execute("""
        INSERT INTO nonconformance_records (batch_id, issue_type, description,
            severity, reported_by, reported_at, disposition, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (batch_ids[7], "温度超标",
          "该批次在运输途中温度记录显示最高达到12℃，超出冷藏要求2~8℃范围",
          "critical", "质检员_张三", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
          "拒收，退回供应商处理", "open"))

    # 验证记录
    cursor.execute("""
        INSERT INTO validation_records (validation_type, facility_name,
            start_time, end_time, result, verified_by, next_due_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ("满载温度分布验证", "冷藏库C区",
          (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M"),
          (now - timedelta(days=28)).strftime("%Y-%m-%d %H:%M"),
          "通过", "质量部_李四",
          (now + timedelta(days=335)).strftime("%Y-%m-%d"),
          "最热点：出风口右侧1.5m处（6.8℃）；最冷点：回风口下方（3.2℃）"))

    # 报警规则
    cursor.execute("""
        INSERT INTO alarm_rules (rule_name, zone_id, temperature_min,
            temperature_max, humidity_min, humidity_max, notify_persons, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ("冷藏库C区超温报警", 3, 2, 8, 35, 75, "张三,李四,王五", 1))

    conn.commit()
    conn.close()
    print("演示数据已生成")


# ==================== 数据查询接口 ====================

def get_zone_status():
    """获取各区域实时状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wz.*,
            (SELECT temperature FROM temperature_logs
             WHERE zone_id = wz.id ORDER BY recorded_at DESC LIMIT 1) as current_temp,
            (SELECT humidity FROM temperature_logs
             WHERE zone_id = wz.id ORDER BY recorded_at DESC LIMIT 1) as current_humidity,
            (SELECT COUNT(*) FROM material_batches WHERE zone_id = wz.id) as batch_count
        FROM warehouse_zones wz
        ORDER BY wz.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_logs(zone_id=None, limit=50):
    """获取最近的温湿度记录"""
    conn = get_db()
    cursor = conn.cursor()
    if zone_id:
        cursor.execute("""
            SELECT tl.*, wz.zone_name
            FROM temperature_logs tl
            JOIN warehouse_zones wz ON tl.zone_id = wz.id
            WHERE tl.zone_id = ?
            ORDER BY tl.recorded_at DESC LIMIT ?
        """, (zone_id, limit))
    else:
        cursor.execute("""
            SELECT tl.*, wz.zone_name
            FROM temperature_logs tl
            JOIN warehouse_zones wz ON tl.zone_id = wz.id
            ORDER BY tl.recorded_at DESC LIMIT ?
        """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_alarms(limit=20):
    """获取最近的报警记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tl.*, wz.zone_name
        FROM temperature_logs tl
        JOIN warehouse_zones wz ON tl.zone_id = wz.id
        WHERE tl.is_alarm = 1
        ORDER BY tl.recorded_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_batches_by_status(status=None):
    """获取物料批次"""
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute("""
            SELECT mb.*, wz.zone_name
            FROM material_batches mb
            JOIN warehouse_zones wz ON mb.zone_id = wz.id
            WHERE mb.status = ?
            ORDER BY mb.expiry_date ASC
        """, (status,))
    else:
        cursor.execute("""
            SELECT mb.*, wz.zone_name
            FROM material_batches mb
            JOIN warehouse_zones wz ON mb.zone_id = wz.id
            ORDER BY mb.expiry_date ASC
        """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_near_expiry(days=90):
    """获取近效期批次"""
    conn = get_db()
    cursor = conn.cursor()
    from datetime import date
    target = date.today() + timedelta(days=days)
    cursor.execute("""
        SELECT mb.*, wz.zone_name
        FROM material_batches mb
        JOIN warehouse_zones wz ON mb.zone_id = wz.id
        WHERE mb.expiry_date <= ? AND mb.status = 'approved'
        ORDER BY mb.expiry_date ASC
    """, (target.isoformat(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_stats():
    """获取仪表盘统计数据"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM material_batches")
    total_batches = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM material_batches WHERE status = 'approved'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM material_batches WHERE status = 'rejected'")
    rejected = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM nonconformance_records WHERE status = 'open'")
    open_nc = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM temperature_logs WHERE is_alarm = 1 AND recorded_at >= datetime('now', '-24 hours')")
    recent_alarms = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM material_batches
        WHERE expiry_date <= date('now', '+90 days')
        AND expiry_date > date('now')
        AND status = 'approved'
    """)
    near_expiry = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM validation_records")
    validations = cursor.fetchone()[0]

    conn.close()
    return {
        "total_batches": total_batches,
        "approved_batches": approved,
        "rejected_batches": rejected,
        "open_nc_count": open_nc,
        "recent_alarms_24h": recent_alarms,
        "near_expiry_90d": near_expiry,
        "total_validations": validations
    }


# 启动时初始化
init_db()
seed_demo_data()


# ==================== 报表与分析 ====================

def generate_temperature_report(days=7):
    """生成温湿度分析报表"""
    conn = get_db()
    cursor = conn.cursor()
    from datetime import date, timedelta
    start_date = (date.today() - timedelta(days=days)).isoformat()

    # 各区域平均温度
    cursor.execute("""
        SELECT wz.zone_name,
               ROUND(AVG(tl.temperature), 1) as avg_temp,
               ROUND(MAX(tl.temperature), 1) as max_temp,
               ROUND(MIN(tl.temperature), 1) as min_temp,
               ROUND(AVG(tl.humidity), 1) as avg_humidity,
               COUNT(CASE WHEN tl.is_alarm = 1 THEN 1 END) as alarm_count,
               COUNT(*) as record_count
        FROM temperature_logs tl
        JOIN warehouse_zones wz ON tl.zone_id = wz.id
        WHERE tl.recorded_at >= ?
        GROUP BY wz.zone_name
        ORDER BY wz.id
    """, (start_date,))
    rows = cursor.fetchall()
    zone_report = [dict(r) for r in rows]

    # 超温趋势（按天统计）
    cursor.execute("""
        SELECT DATE(tl.recorded_at) as log_date,
               COUNT(CASE WHEN tl.is_alarm = 1 THEN 1 END) as alarm_count,
               ROUND(AVG(tl.temperature), 1) as avg_temp
        FROM temperature_logs tl
        WHERE tl.recorded_at >= ?
        GROUP BY DATE(tl.recorded_at)
        ORDER BY log_date
    """, (start_date,))
    trend_data = [dict(r) for r in rows]
    conn.close()

    return {
        "period_days": days,
        "period_start": start_date,
        "zone_report": zone_report,
        "trend_data": trend_data,
        "total_records": sum(r["record_count"] for r in zone_report),
        "total_alarms": sum(r["alarm_count"] for r in zone_report)
    }


def generate_inventory_report():
    """生成库存分析报表"""
    conn = get_db()
    cursor = conn.cursor()

    # 按状态统计
    cursor.execute("""
        SELECT status, COUNT(*) as count, SUM(quantity) as total_qty
        FROM material_batches
        GROUP BY status
    """)
    status_stats = [dict(r) for r in cursor.fetchall()]

    # 按供应商统计
    cursor.execute("""
        SELECT supplier, COUNT(*) as batch_count,
               SUM(quantity) as total_qty,
               GROUP_CONCAT(DISTINCT status) as statuses
        FROM material_batches
        GROUP BY supplier
        ORDER BY batch_count DESC
    """)
    supplier_stats = [dict(r) for r in cursor.fetchall()]

    # 按区域统计
    cursor.execute("""
        SELECT wz.zone_name, COUNT(mb.id) as batch_count,
               SUM(mb.quantity) as total_qty
        FROM warehouse_zones wz
        LEFT JOIN material_batches mb ON wz.id = mb.zone_id
        GROUP BY wz.zone_name
        ORDER BY batch_count DESC
    """)
    zone_stats = [dict(r) for r in cursor.fetchall()]

    # 近效期分布
    from datetime import date, timedelta
    today = date.today()
    expiry_ranges = [
        ("30天内到期", 30),
        ("31-90天到期", 90),
        ("91-180天到期", 180),
        ("180天以上", 9999),
    ]
    expiry_dist = []
    for label, days in expiry_ranges:
        if days == 9999:
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(quantity) as total_qty
                FROM material_batches
                WHERE expiry_date > ? AND status = 'approved'
            """, ((today + timedelta(days=180)).isoformat(),))
        else:
            prev_days = expiry_ranges[expiry_ranges.index((label, days)) - 1][1] if expiry_ranges.index((label, days)) > 0 else 0
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(quantity) as total_qty
                FROM material_batches
                WHERE expiry_date BETWEEN ? AND ?
                AND expiry_date > date('now')
                AND status = 'approved'
            """, ((today + timedelta(days=prev_days)).isoformat(),
                  (today + timedelta(days=days)).isoformat()))
        row = cursor.fetchone()
        expiry_dist.append({
            "range": label,
            "count": row[0] or 0,
            "total_qty": row[1] or 0
        })

    conn.close()
    return {
        "total_batches": sum(s["count"] for s in status_stats),
        "status_stats": status_stats,
        "supplier_stats": supplier_stats,
        "zone_stats": zone_stats,
        "expiry_distribution": expiry_dist
    }


def generate_compliance_checklist():
    """生成 GMP/GSP 合规检查清单"""
    checklist = [
        {
            "category": "仓储条件",
            "items": [
                {"check": "温湿度记录是否完整（每天两次含节假日）", "standard": "每天记录，保存≥5年"},
                {"check": "计量器具是否在有效校准期内", "standard": "每年校准一次，有证书"},
                {"check": "防虫防鼠设施是否完好", "standard": "纱窗、挡鼠板≥50cm"},
                {"check": "仓库温湿度是否在标准范围内", "standard": "常温10~30℃/阴凉≤20℃/冷库2~8℃"},
            ]
        },
        {
            "category": "色标与分区",
            "items": [
                {"check": "各区色标标识是否清晰完整", "standard": "绿/黄/红三色对应合格/待验/不合格"},
                {"check": "不合格品区是否上锁管理", "standard": "物理隔离+双锁"},
                {"check": "退货区是否独立设置", "standard": "黄色标识，待评估"},
            ]
        },
        {
            "category": "物料管理",
            "items": [
                {"check": "物料是否按批号管理", "standard": "每批唯一批号，全程追溯"},
                {"check": "近效期物料是否有预警标识", "standard": "≤6个月贴警示标签"},
                {"check": "发放是否执行FIFO/FEFO", "standard": "先进先出+近效期先出"},
                {"check": "双人复核是否执行", "standard": "一人发一人核，签字确认"},
            ]
        },
        {
            "category": "记录与台账",
            "items": [
                {"check": "货位卡是否实时更新", "standard": "一货一卡，动态更新"},
                {"check": "记录修改是否符合规范", "standard": "横线划改，签名日期，不得涂改"},
                {"check": "计算机化系统是否有权限管理", "standard": "分级权限，密码定期更换"},
                {"check": "数据是否定期备份", "standard": "每日增量+每周全量，异地保存"},
            ]
        },
        {
            "category": "验证管理",
            "items": [
                {"check": "冷库是否按时完成年度验证", "standard": "每年满载验证，夏季+冬季各一次"},
                {"check": "冷藏车是否在验证有效期内", "standard": "停用超3个月须重新验证"},
                {"check": "温湿度监测系统是否年度验证", "standard": "每年至少一次"},
                {"check": "验证报告是否完整", "standard": "含布点图、数据、结论、校准证书"},
            ]
        },
        {
            "category": "偏差与 CAPA",
            "items": [
                {"check": "偏差是否及时记录和调查", "standard": "48h内启动调查"},
                {"check": "CAPA是否闭环管理", "standard": "措施有效验证后关闭"},
                {"check": "不合格品是否隔离处置", "standard": "红色标识+物理隔离"},
            ]
        },
    ]
    return checklist


def get_alarm_rules():
    """获取报警规则列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ar.*, wz.zone_name
        FROM alarm_rules ar
        JOIN warehouse_zones wz ON ar.zone_id = wz.id
        ORDER BY ar.is_active DESC, ar.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_batches(keyword: str):
    """搜索物料批次"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mb.*, wz.zone_name
        FROM material_batches mb
        JOIN warehouse_zones wz ON mb.zone_id = wz.id
        WHERE mb.batch_no LIKE ? OR mb.material_name LIKE ? OR mb.supplier LIKE ?
        ORDER BY mb.expiry_date
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_validation_summary():
    """验证计划摘要"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM validation_records ORDER BY next_due_date ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    from datetime import date, timedelta
    today = date.today()
    summary = {
        "total": len(rows),
        "overdue": 0,
        "due_soon": 0,
        "valid": 0,
        "records": [dict(r) for r in rows]
    }
    for r in rows:
        due = r["next_due_date"]
        if due:
            due_date = date.fromisoformat(due) if isinstance(due, str) else due
            if due_date < today:
                summary["overdue"] += 1
            elif (due_date - today).days <= 90:
                summary["due_soon"] += 1
            else:
                summary["valid"] += 1
    return summary

