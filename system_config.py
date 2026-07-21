"""
GMP 药品仓库管理 AI 系统 — 系统配置模块
包含配置管理、日志记录、系统健康检查
"""
import os
import sys
import json
import socket
import sqlite3
from datetime import datetime


# ==================== 系统配置 ====================

class SystemConfig:
    """系统配置管理"""

    DEFAULT_CONFIG = {
        "app_name": "GMP 药品仓库管理 AI 系统",
        "version": "1.0.0",
        "author": "时煜源创科技",
        "description": "GMP/GSP 药品仓库合规知识库与智能检索系统",
        "server": {
            "host": "127.0.0.1",
            "port": 5000,
            "debug": True
        },
        "database": {
            "path": "data/gmp_data.db",
            "backup_enabled": True,
            "backup_interval_hours": 24
        },
        "knowledge_base": {
            "modules_count": 14,
            "entries_count": 30,
            "search_top_k": 10
        },
        "alarm": {
            "notify_persons": 3,
            "check_interval_seconds": 300,
            "temperature_warning_threshold": 1.0,
            "temperature_critical_threshold": 3.0
        },
        "validation": {
            "cold_storage_annual_due": True,
            "transport_validation_months": 12,
            "calibration_cycle_months": 12
        },
        "compliance": {
            "gmp_version": "2010修订",
            "gsp_version": "2016年总局令第28号",
            "gb_standard": "GB/T 34399-2025"
        }
    }

    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "data", "system_config.json"
        )
        self.config = self._load()

    def _load(self) -> dict:
        """加载配置文件"""
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return dict(self.DEFAULT_CONFIG)
        return dict(self.DEFAULT_CONFIG)

    def save(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        """获取配置项（支持点号分隔）"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value):
        """设置配置项（支持点号分隔）"""
        keys = key.split(".")
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()

    def to_dict(self) -> dict:
        """导出配置"""
        return {
            "app_name": self.get("app_name"),
            "version": self.get("version"),
            "server": self.get("server"),
            "database": self.get("database"),
            "knowledge_base": self.get("knowledge_base"),
            "alarm": self.get("alarm"),
            "validation": self.get("validation"),
            "compliance": self.get("compliance")
        }


# ==================== 系统日志 ====================

class SystemLogger:
    """系统日志记录器"""

    LOG_LEVELS = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4
    }

    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(
            os.path.dirname(__file__), "data", "logs"
        )
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_log = None

    def _get_log_file(self) -> str:
        """获取当天日志文件路径"""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"system_{today}.log")

    def log(self, level: str, module: str, message: str):
        """写入日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = self._get_log_file()
        log_line = f"[{timestamp}] [{level:8s}] [{module:20s}] {message}\n"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception:
            pass

    def info(self, module: str, message: str):
        self.log("INFO", module, message)

    def warning(self, module: str, message: str):
        self.log("WARNING", module, message)

    def error(self, module: str, message: str):
        self.log("ERROR", module, message)

    def debug(self, module: str, message: str):
        self.log("DEBUG", module, message)


# ==================== 系统健康检查 ====================

def health_check(db_path: str = None) -> dict:
    """系统健康检查"""
    checks = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "checks": []
    }

    # 检查 Python 版本
    py_version = sys.version
    checks["checks"].append({
        "name": "Python 运行环境",
        "status": "pass",
        "detail": f"Python {py_version.split()[0]}"
    })

    # 检查数据库
    db_path = db_path or os.path.join(
        os.path.dirname(__file__), "data", "gmp_data.db"
    )
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM warehouse_zones")
            zone_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM temperature_logs")
            log_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM material_batches")
            batch_count = cursor.fetchone()[0]
            conn.close()
            checks["checks"].append({
                "name": "数据库状态",
                "status": "pass",
                "detail": f"数据库正常 (区域={zone_count}, 记录={log_count}, 批次={batch_count})"
            })
        except Exception as e:
            checks["checks"].append({
                "name": "数据库状态",
                "status": "fail",
                "detail": f"数据库异常: {str(e)}"
            })
            checks["status"] = "degraded"
    else:
        checks["checks"].append({
            "name": "数据库状态",
            "status": "fail",
            "detail": "数据库文件不存在，请启动应用初始化"
        })
        checks["status"] = "degraded"

    # 检查端口可用性
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(("127.0.0.1", port))
        if result == 0:
            checks["checks"].append({
                "name": f"端口 {port}",
                "status": "pass",
                "detail": f"端口 {port} 已在监听"
            })
        else:
            checks["checks"].append({
                "name": f"端口 {port}",
                "status": "warn",
                "detail": f"端口 {port} 未监听（应用未启动）"
            })
    finally:
        sock.close()

    # 检查磁盘空间
    try:
        stat = os.statvfs(os.path.dirname(__file__) or ".")
        free_gb = (stat.f_frsize * stat.f_bavail) / (1024 ** 3)
        if free_gb < 1:
            checks["checks"].append({
                "name": "磁盘空间",
                "status": "fail",
                "detail": f"剩余空间不足: {free_gb:.1f}GB"
            })
            checks["status"] = "degraded"
        else:
            checks["checks"].append({
                "name": "磁盘空间",
                "status": "pass",
                "detail": f"剩余空间: {free_gb:.1f}GB"
            })
    except Exception:
        pass

    return checks


def get_system_info() -> dict:
    """获取系统信息"""
    import platform
    return {
        "app": "GMP 药品仓库管理 AI 系统",
        "version": "1.0.0",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": time.tzname if hasattr(time, 'tzname') else "UTC"
    }


# 全局实例
config = SystemConfig()
logger = SystemLogger()
