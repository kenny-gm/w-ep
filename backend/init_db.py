"""初始化数据库表"""
from app.database import Base, engine
from app.models import models  # 导入整个模块

# 创建所有表
Base.metadata.create_all(bind=engine)
print("数据库表创建完成!")

# 列出所有表
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"创建的表: {tables}")
