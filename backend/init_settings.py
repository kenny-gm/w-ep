#!/usr/bin/env python3
"""初始化系统默认设置"""
from app.database import SessionLocal
from app.models.models import SystemSetting

db = SessionLocal()

# 默认系统设置
default_settings = [
    {"key": "cny_to_rub", "value": "12.5", "description": "人民币转卢布汇率"},
    {"key": "ad_ratio_warning", "value": "0.03", "description": "广告占比警告阈值"},
    {"key": "ad_ratio_danger", "value": "0.05", "description": "广告占比危险阈值"},
    {"key": "profit_rate_warning", "value": "0.10", "description": "利润率警告阈值"},
    {"key": "sync_enabled", "value": "true", "description": "是否启用自动同步"},
    {"key": "sync_hour", "value": "3", "description": "自动同步时间（小时）"},
]

print("=== 初始化系统设置 ===")

existing = db.query(SystemSetting).count()
print(f"现有设置数量: {existing}")

if existing == 0:
    for setting_data in default_settings:
        setting = SystemSetting(**setting_data)
        db.add(setting)
        print(f"创建设置: {setting_data['key']} = {setting_data['value']}")
    
    db.commit()
    print("\n✅ 设置初始化完成")
else:
    print("设置已存在，跳过初始化")

# 显示所有设置
print("\n当前系统设置:")
settings = db.query(SystemSetting).all()
for s in settings:
    print(f"  {s.key}: {s.value} ({s.description})")

db.close()
