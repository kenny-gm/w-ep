from zoneinfo import ZoneInfo
# backend/app/models/profit_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ShopCostConfig(Base):
    """店铺费用配置表 - 用户可手动设置"""
    __tablename__ = "shop_cost_configs"
    
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    # 税费设置
    vat_rate = Column(Float, default=8.0)           # 增值税率 (%)
    sales_fee_rate = Column(Float, default=4.0)     # 销售费用率 (%)
    income_tax_rate = Column(Float, default=20.0)   # 所得税率 (%)
    
    # 海外仓费用设置
    fbw_warehouse_fee = Column(Float, default=50.0)  # FBW单均费用 (RUB)
    fbs_warehouse_fee = Column(Float, default=80.0)  # FBS单均费用 (RUB)
    warehouse_fee_by_weight = Column(JSON, default=list)  # 重量阶梯费用
    
    # 固定费用
    monthly_fixed_cost = Column(Float, default=0)     # 月固定成本 (CNY)
    monthly_fixed_cost_note = Column(String(200))     # 备注
    
    # 自动化阈值
    auto_use_cost_threshold = Column(Float, default=10.0)   # 成本自动复用阈值 (%)
    cost_alert_threshold = Column(Float, default=15.0)      # 成本预警阈值 (%)
    loss_threshold = Column(Float, default=0)               # 亏损订单标记阈值 (%)
    
    # 汇率设置
    default_cost_rate = Column(Float, default=12.5)   # 默认成本汇率 (CNY→RUB)
    cost_rate_source = Column(String(20), default="manual")  # manual/auto/fixed
    income_rate_source = Column(String(20), default="manual") # manual/payment_record/market
    
    created_at = Column(String(10), default=datetime.utcnow)
    updated_at = Column(String(10), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    shop_id = Column(Integer, ForeignKey("shops.id"))
    shop = relationship("Shop")


class ProductCostHistory(Base):
    """产品成本历史表 - 用户可手动录入/导入"""
    __tablename__ = "product_cost_histories"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku = Column(String(100))
    product_name = Column(String(200))
    
    # 成本数据 (CNY)
    purchase_cost_cny = Column(Float, default=0)      # 采购成本
    domestic_logistics_cny = Column(Float, default=0) # 国内物流
    cross_border_logistics_cny = Column(Float, default=0)  # 跨境物流
    
    # 海外仓费用 (RUB)
    fbw_warehouse_rub = Column(Float, default=0)
    fbs_warehouse_rub = Column(Float, default=0)
    
    # 汇率
    exchange_rate = Column(Float, default=12.5)
    
    # 生效周期
    effective_date = Column(String(10), nullable=False)
    expire_date = Column(String(10), nullable=True)
    
    # 来源
    source = Column(String(50), default="manual")  # manual/import/auto
    
    created_at = Column(String(10), default=datetime.utcnow)
    
    product = relationship("Product", back_populates="cost_histories")


class SalesReport(Base):
    """销售报告表 - WB API自动导入，只读"""
    __tablename__ = "sales_reports"
    
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    # 报告周期
    period_start = Column(String(10), nullable=False)
    period_end = Column(String(10), nullable=False)
    
    # WB平台数据 (API自动导入，只读)
    total_sales_rub = Column(Float, default=0)           # 总销售额
    total_commission_rub = Column(Float, default=0)      # 平台佣金
    total_logistics_rub = Column(Float, default=0)       # 平台物流费
    total_ad_cost_rub = Column(Float, default=0)         # 广告费
    total_settlement_rub = Column(Float, default=0)      # WB结算金额
    total_orders = Column(Integer, default=0)            # 总订单数
    
    # FBW/FBS订单数
    fbw_order_count = Column(Integer, default=0)
    fbs_order_count = Column(Integer, default=0)
    
    # 汇率 (用户可设置)
    income_exchange_rate = Column(Float, default=0.08)   # 收入汇率 (RUB→CNY)
    cost_exchange_rate = Column(Float, default=12.5)     # 成本汇率 (CNY→RUB)
    
    # 成本数据汇总
    total_product_cost_cny = Column(Float, default=0)
    total_domestic_logistics_cny = Column(Float, default=0)
    total_cross_border_logistics_cny = Column(Float, default=0)
    total_warehouse_cost_cny = Column(Float, default=0)
    
    # 费用
    vat_cny = Column(Float, default=0)
    sales_fee_cny = Column(Float, default=0)
    other_cost_cny = Column(Float, default=0)
    
    # 利润计算结果
    total_received_cny = Column(Float, default=0)        # 人民币收入
    profit_before_tax_cny = Column(Float, default=0)     # 税前利润
    profit_after_tax_cny = Column(Float, default=0)      # 税后利润
    net_profit_cny = Column(Float, default=0)            # 净利润
    profit_margin = Column(Float, default=0)             # 利润率
    
    # 状态
    status = Column(String(20), default="pending")       # pending/calculating/calculated/confirmed
    
    created_at = Column(String(10), default=datetime.utcnow)
    calculated_at = Column(String(10), nullable=True)
    confirmed_at = Column(String(10), nullable=True)
    
    shop_id = Column(Integer, ForeignKey("shops.id"))
    shop = relationship("Shop")
    details = relationship("ReportProductDetail", back_populates="report", cascade="all, delete-orphan")


class ReportProductDetail(Base):
    """报告产品明细表"""
    __tablename__ = "report_product_details"
    
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("sales_reports.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    sku = Column(String(100))
    product_name = Column(String(200))
    
    # 销售数据
    quantity = Column(Integer, default=0)           # 销售数量
    sales_rub = Column(Float, default=0)           # 销售额 (RUB)
    
    # 成本数据 (用户可编辑)
    purchase_cost_cny = Column(Float, default=0)
    domestic_logistics_cny = Column(Float, default=0)
    cross_border_logistics_cny = Column(Float, default=0)
    fbw_warehouse_rub = Column(Float, default=0)
    fbs_warehouse_rub = Column(Float, default=0)
    
    # 计算结果
    product_cost_rub = Column(Float, default=0)
    profit_rub = Column(Float, default=0)
    profit_margin = Column(Float, default=0)
    
    # 标记
    is_loss = Column(Boolean, default=False)
    loss_reason = Column(String(200), nullable=True)
    
    created_at = Column(String(10), default=datetime.utcnow)
    updated_at = Column(String(10), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    report = relationship("SalesReport", back_populates="details")
    product = relationship("Product")


class ExchangeRateRecord(Base):
    """汇率记录表"""
    __tablename__ = "exchange_rate_records"
    
    id = Column(Integer, primary_key=True)
    rate_type = Column(String(20))                 # cost/income
    base_currency = Column(String(10), default="CNY")
    target_currency = Column(String(10), default="RUB")
    rate = Column(Float, nullable=False)
    effective_date = Column(String(10), nullable=False)
    source = Column(String(50), default="manual")
    created_at = Column(String(10), default=datetime.utcnow)


class PaymentRecord(Base):
    """收款记录表"""
    __tablename__ = "payment_records"
    
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("sales_reports.id"), nullable=True)
    
    payment_date = Column(String(10), nullable=False)
    settlement_amount_rub = Column(Float, nullable=False)
    received_cny = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    bank_name = Column(String(100))
    transaction_id = Column(String(100))
    
    created_at = Column(String(10), default=datetime.utcnow)
    
    shop = relationship("Shop")
    report = relationship("SalesReport")


class FixedCost(Base):
    """固定费用表"""
    __tablename__ = "fixed_costs"
    
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    
    cost_type = Column(String(50))
    name = Column(String(100), nullable=False)
    amount_cny = Column(Float, nullable=False)
    allocation_method = Column(String(20), default="daily")
    effective_date = Column(String(10), nullable=True)
    report_id = Column(Integer, ForeignKey("sales_reports.id"), nullable=True)
    note = Column(String(200))
    
    created_at = Column(String(10), default=datetime.utcnow)
    
    shop = relationship("Shop")
    report = relationship("SalesReport")
