#!/usr/bin/env python3
"""修改数据库字段约束"""
import sqlite3

# 尝试两个数据库文件
for db_file in ["/app/wberp.db", "/app/wb_erp.db"]:
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 检查是否有shops表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shops'")
        if cursor.fetchone():
            print(f"修改数据库: {db_file}")
            
            # 创建新表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS shops_new (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                api_token VARCHAR(500),
                currency VARCHAR(10) DEFAULT 'RUB',
                exchange_rate FLOAT DEFAULT 12.5,
                sync_enabled BOOLEAN DEFAULT 1,
                sync_interval_hours INTEGER DEFAULT 24,
                last_sync_at DATETIME,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME,
                updated_at DATETIME
            )
            """)
            
            # 复制数据
            cursor.execute("INSERT INTO shops_new SELECT * FROM shops")
            
            # 删除旧表
            cursor.execute("DROP TABLE shops")
            
            # 重命名
            cursor.execute("ALTER TABLE shops_new RENAME TO shops")
            
            conn.commit()
            print(f"✅ {db_file} 修改完成")
        
        conn.close()
    except Exception as e:
        print(f"处理 {db_file} 错误: {e}")

print("\n所有数据库修改完成")
