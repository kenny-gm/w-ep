"""
利润核算模块
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date
from typing import List, Optional
from pydantic import BaseModel
import io

from app.database import get_db
from app.models.profit_models import (
    ShopCostConfig, ProductCostHistory, SalesReport, ReportProductDetail,
    ExchangeRateRecord, PaymentRecord, FixedCost
)
from app.models.models import Shop, Product, Order, OrderItem
from app.routers.auth import get_current_user
from app.services.wb_api import WBAPIClient

router = APIRouter(prefix="/api/profit", tags=["利润核算"])


# ========== Pydantic模型 ==========

class ShopConfigUpdate(BaseModel):
    vat_rate: Optional[float] = None
    sales_fee_rate: Optional[float] = None
    income_tax_rate: Optional[float] = None
    fbw_warehouse_fee: Optional[float] = None
    fbs_warehouse_fee: Optional[float] = None
    warehouse_fee_by_weight: Optional[list] = None
    monthly_fixed_cost: Optional[float] = None
    monthly_fixed_cost_note: Optional[str] = None
    auto_use_cost_threshold: Optional[float] = None
    cost_alert_threshold: Optional[float] = None
    loss_threshold: Optional[float] = None
    default_cost_rate: Optional[float] = None
    cost_rate_source: Optional[str] = None
    income_rate_source: Optional[str] = None


class ProductCostUpdate(BaseModel):
    purchase_cost_cny: Optional[float] = None
    domestic_logistics_cny: Optional[float] = None
    cross_border_logistics_cny: Optional[float] = None
    fbw_warehouse_rub: Optional[float] = None
    fbs_warehouse_rub: Optional[float] = None


class SyncReportRequest(BaseModel):
    shop_id: int
    period_start: str  # YYYY-MM-DD
    period_end: str    # YYYY-MM-DD


class FixedCostCreate(BaseModel):
    cost_type: str
    name: str
    amount_cny: float
    allocation_method: str = "daily"
    effective_date: Optional[str] = None
    note: Optional[str] = None


class PaymentRecordCreate(BaseModel):
    payment_date: str
    settlement_amount_rub: float
    received_cny: float
    exchange_rate: float
    bank_name: Optional[str] = None
    transaction_id: Optional[str] = None


# ========== 1. 店铺费用配置 ==========

@router.get("/shops/{shop_id}/config")
def get_shop_config(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取店铺费用配置"""
    config = db.query(ShopCostConfig).filter(ShopCostConfig.shop_id == shop_id).first()
    if not config:
        config = ShopCostConfig(shop_id=shop_id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/shops/{shop_id}/config")
def update_shop_config(
    shop_id: int,
    config_data: ShopConfigUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新店铺费用配置"""
    config = db.query(ShopCostConfig).filter(ShopCostConfig.shop_id == shop_id).first()
    if not config:
        config = ShopCostConfig(shop_id=shop_id)
        db.add(config)
    
    for key, value in config_data.model_dump(exclude_unset=True).items():
        if hasattr(config, key) and value is not None:
            setattr(config, key, value)
    
    config.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "配置已保存", "config": config}


# ========== 2. 报告列表查询 ==========

@router.get("/reports")
def get_reports(
    shop_id: int = Query(...),
    status: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取销售报告列表"""
    query = db.query(SalesReport).filter(SalesReport.shop_id == shop_id)
    
    if status:
        query = query.filter(SalesReport.status == status)
    if period_start:
        query = query.filter(SalesReport.period_start >= period_start)
    if period_end:
        query = query.filter(SalesReport.period_end <= period_end)
    
    total = query.count()
    reports = query.order_by(SalesReport.period_start.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": r.id,
                "period_start": r.period_start,
                "period_end": r.period_end,
                "total_settlement_rub": r.total_settlement_rub,
                "total_orders": r.total_orders,
                "status": r.status,
                "net_profit_cny": r.net_profit_cny,
                "profit_margin": r.profit_margin
            }
            for r in reports
        ]
    }


# ========== 3. 报告详情 ==========

@router.get("/reports/{report_id}")
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取报告详情和产品明细"""
    report = db.query(SalesReport).filter(SalesReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    details = db.query(ReportProductDetail).filter(
        ReportProductDetail.report_id == report_id
    ).all()
    
    config = db.query(ShopCostConfig).filter(ShopCostConfig.shop_id == report.shop_id).first()
    
    return {
        "report": {
            "id": report.id,
            "shop_id": report.shop_id,
            "period_start": report.period_start,
            "period_end": report.period_end,
            "total_sales_rub": report.total_sales_rub,
            "total_commission_rub": report.total_commission_rub,
            "total_logistics_rub": report.total_logistics_rub,
            "total_ad_cost_rub": report.total_ad_cost_rub,
            "total_settlement_rub": report.total_settlement_rub,
            "total_orders": report.total_orders,
            "fbw_order_count": report.fbw_order_count,
            "fbs_order_count": report.fbs_order_count,
            "income_exchange_rate": report.income_exchange_rate,
            "cost_exchange_rate": report.cost_exchange_rate,
            "total_received_cny": report.total_received_cny,
            "total_product_cost_cny": report.total_product_cost_cny,
            "total_warehouse_cost_cny": report.total_warehouse_cost_cny,
            "vat_cny": report.vat_cny,
            "sales_fee_cny": report.order_sum_fee_cny,
            "other_cost_cny": report.other_cost_cny,
            "profit_before_tax_cny": report.profit_before_tax_cny,
            "profit_after_tax_cny": report.profit_after_tax_cny,
            "net_profit_cny": report.net_profit_cny,
            "profit_margin": report.profit_margin,
            "status": report.status,
            "created_at": report.created_at,
            "calculated_at": report.calculated_at
        },
        "details": [
            {
                "id": d.id,
                "product_id": d.product_id,
                "sku": d.sku,
                "product_name": d.product_name,
                "quantity": d.quantity,
                "sales_rub": d.order_sum_rub,
                "purchase_cost_cny": d.purchase_cost_cny,
                "domestic_logistics_cny": d.domestic_logistics_cny,
                "cross_border_logistics_cny": d.cross_border_logistics_cny,
                "fbw_warehouse_rub": d.fbw_warehouse_rub,
                "fbs_warehouse_rub": d.fbs_warehouse_rub,
                "product_cost_rub": d.product_cost_rub,
                "profit_rub": d.profit_rub,
                "profit_margin": d.profit_margin,
                "is_loss": d.is_loss,
                "loss_reason": d.loss_reason
            }
            for d in details
        ],
        "config": {
            "vat_rate": config.vat_rate if config else 8,
            "sales_fee_rate": config.order_sum_fee_rate if config else 4,
            "income_tax_rate": config.income_tax_rate if config else 20,
            "fbw_warehouse_fee": config.fbw_warehouse_fee if config else 50,
            "fbs_warehouse_fee": config.fbs_warehouse_fee if config else 80,
            "default_cost_rate": config.default_cost_rate if config else 12.5,
            "loss_threshold": config.loss_threshold if config else 0
        }
    }


# ========== 4. 更新产品成本 ==========

@router.put("/reports/{report_id}/details/{detail_id}")
def update_product_cost(
    report_id: int,
    detail_id: int,
    cost_data: ProductCostUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新单个产品成本"""
    detail = db.query(ReportProductDetail).filter(
        ReportProductDetail.id == detail_id,
        ReportProductDetail.report_id == report_id
    ).first()
    
    if not detail:
        raise HTTPException(status_code=404, detail="产品明细不存在")
    
    # 更新成本
    for key, value in cost_data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(detail, key, value)
    
    detail.updated_at = datetime.utcnow()
    
    # 保存到历史记录（如果成本有变化）
    if any([cost_data.purchase_cost_cny, cost_data.domestic_logistics_cny, 
            cost_data.cross_border_logistics_cny]):
        history = ProductCostHistory(
            product_id=detail.product_id,
            sku=detail.sku,
            product_name=detail.product_name,
            purchase_cost_cny=detail.purchase_cost_cny or 0,
            domestic_logistics_cny=detail.domestic_logistics_cny or 0,
            cross_border_logistics_cny=detail.cross_border_logistics_cny or 0,
            fbw_warehouse_rub=detail.fbw_warehouse_rub or 0,
            fbs_warehouse_rub=detail.fbs_warehouse_rub or 0,
            effective_date=datetime.now().strftime("%Y-%m-%d"),
            source="manual"
        )
        db.add(history)
    
    db.commit()
    
    # 重新计算利润
    calculate_report_profit(report_id, db)
    
    return {"message": "成本已更新", "detail_id": detail_id}


# ========== 5. 批量更新产品成本 ==========

@router.post("/reports/{report_id}/details/batch")
def batch_update_costs(
    report_id: int,
    details: List[ProductCostUpdate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """批量更新产品成本"""
    # 需要同时传入detail_id
    # 这个接口需要配合前端发送包含id的批量数据
    return {"message": "批量更新功能开发中"}


# ========== 6. 利润计算函数 ==========

def calculate_report_profit(report_id: int, db: Session):
    """计算报告利润"""
    report = db.query(SalesReport).filter(SalesReport.id == report_id).first()
    if not report:
        return
    
    details = db.query(ReportProductDetail).filter(
        ReportProductDetail.report_id == report_id
    ).all()
    
    config = db.query(ShopCostConfig).filter(ShopCostConfig.shop_id == report.shop_id).first()
    
    # 获取汇率
    income_rate = report.income_exchange_rate or 0.08
    cost_rate = report.cost_exchange_rate or 12.5
    
    # 计算人民币收入
    report.total_received_cny = report.total_settlement_rub * income_rate
    
    # 计算各项成本
    total_product_cost_cny = 0
    total_warehouse_cost_cny = 0
    
    loss_count = 0
    
    for detail in details:
        # 单品成本 (RUB)
        cny_cost = (detail.purchase_cost_cny or 0 + 
                    detail.domestic_logistics_cny or 0 + 
                    detail.cross_border_logistics_cny or 0)
        rub_cost = cny_cost * cost_rate
        
        # 海外仓费用
        warehouse_cost = 0
        if detail.quantity and detail.quantity > 0:
            if detail.fbw_warehouse_rub:
                warehouse_cost = detail.fbw_warehouse_rub * detail.quantity
            elif detail.fbs_warehouse_rub:
                warehouse_cost = detail.fbs_warehouse_rub * detail.quantity
        
        detail.product_cost_rub = rub_cost + warehouse_cost
        detail.profit_rub = (detail.order_sum_rub or 0) - detail.product_cost_rub
        
        if detail.order_sum_rub and detail.order_sum_rub > 0:
            detail.profit_margin = detail.profit_rub / detail.order_sum_rub * 100
        else:
            detail.profit_margin = 0
        
        # 标记亏损
        threshold = (config.loss_threshold / 100) if config and config.loss_threshold else 0
        if detail.profit_margin < threshold * 100:
            detail.is_loss = True
            detail.loss_reason = f"利润率 {detail.profit_margin:.1f}% 低于阈值 {threshold*100}%"
            loss_count += 1
        else:
            detail.is_loss = False
            detail.loss_reason = None
        
        total_product_cost_cny += cny_cost
        total_warehouse_cost_cny += warehouse_cost * income_rate
    
    report.total_product_cost_cny = total_product_cost_cny
    report.total_warehouse_cost_cny = total_warehouse_cost_cny
    
    # 税费计算
    if config:
        report.vat_cny = (report.total_sales_rub or 0) * (config.vat_rate / 100) * income_rate
        report.order_sum_fee_cny = report.total_received_cny * (config.order_sum_fee_rate / 100)
    else:
        report.vat_cny = (report.total_sales_rub or 0) * 0.08 * income_rate
        report.order_sum_fee_cny = report.total_received_cny * 0.04
    
    # 固定费用
    fixed_costs = db.query(FixedCost).filter(
        FixedCost.shop_id == report.shop_id,
        FixedCost.report_id == report_id
    ).all()
    total_fixed_cost = sum(fc.amount_cny for fc in fixed_costs)
    report.other_cost_cny = total_fixed_cost
    
    # 利润计算
    report.profit_before_tax_cny = (report.total_received_cny - 
                                    report.total_product_cost_cny - 
                                    report.total_warehouse_cost_cny - 
                                    report.other_cost_cny)
    
    report.profit_after_tax_cny = report.profit_before_tax_cny - report.vat_cny - report.order_sum_fee_cny
    
    if report.profit_after_tax_cny > 0 and config and config.income_tax_rate:
        income_tax = report.profit_after_tax_cny * (config.income_tax_rate / 100)
        report.net_profit_cny = report.profit_after_tax_cny - income_tax
    else:
        report.net_profit_cny = report.profit_after_tax_cny
    
    if report.total_received_cny and report.total_received_cny > 0:
        report.profit_margin = report.net_profit_cny / report.total_received_cny * 100
    else:
        report.profit_margin = 0
    
    report.status = "calculated"
    report.calculated_at = datetime.utcnow()
    
    db.commit()


# ========== 7. WB销售报告同步 ==========

@router.post("/reports/sync")
def sync_wb_report(
    request: SyncReportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """从WB API同步销售报告"""
    shop = db.query(Shop).filter(Shop.id == request.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    if not shop.api_token:
        raise HTTPException(status_code=400, detail="店铺未配置API Token")
    
    # 解析日期
    period_start = request.period_start  # 直接使用字符串 YYYY-MM-DD
    period_end = request.period_end  # 直接使用字符串 YYYY-MM-DD
    
    # 检查是否已存在报告
    existing = db.query(SalesReport).filter(
        and_(
            SalesReport.shop_id == request.shop_id,
            SalesReport.period_start == period_start,
            SalesReport.period_end == period_end
        )
    ).first()
    
    if existing:
        report = existing
    else:
        # 创建新报告
        report = SalesReport(
            shop_id=request.shop_id,
            period_start=period_start,
            period_end=period_end,
            status="pending"
        )
        db.add(report)
        db.flush()
    
    # 获取店铺配置
    config = db.query(ShopCostConfig).filter(
        ShopCostConfig.shop_id == request.shop_id
    ).first()
    
    # 从数据库获取销售数据
    orders = db.query(Order).filter(
        and_(
            Order.shop_id == request.shop_id,
            Order.order_date >= period_start,
            Order.order_date <= period_end
        )
    ).all()
    
    # 汇总数据
    total_sales = sum(o.total_amount or 0 for o in orders)
    total_orders = len(orders)
    
    # FBW/FBS统计
    # FBW/FBS统计 (简化版 - 假设所有订单都是FBW)
    fbw_count = total_orders
    fbs_count = 0
    
    # 获取产品销售明细
    order_ids = [o.id for o in orders]
    order_items = db.query(OrderItem).filter(
        OrderItem.order_id.in_(order_ids)
    ).all() if order_ids else []
    
    # 按产品汇总
    product_sales = {}
    for item in order_items:
        key = f"{item.product_id}_{item.sku}"
        if key not in product_sales:
            product_sales[key] = {
                "product_id": item.product_id,
                "sku": item.sku,
                "product_name": item.sku or "",
                "quantity": 0,
                "sales_rub": 0
            }
        product_sales[key]["quantity"] += item.quantity or 0
        product_sales[key]["sales_rub"] += item.total_price or 0
    
    # 更新报告数据
    report.total_sales_rub = total_sales
    report.total_orders = total_orders
    report.fbw_order_count = fbw_count
    report.fbs_order_count = fbs_count
    
    # 估算平台费用（简化版）
    report.total_commission_rub = total_sales * 0.05  # 5% 佣金
    report.total_logistics_rub = total_orders * 30     # 30 RUB/单物流费
    report.total_ad_cost_rub = 0                      # 广告费需要单独获取
    
    # 结算金额 = 销售额 - 佣金 - 物流
    report.total_settlement_rub = total_sales - report.total_commission_rub - report.total_logistics_rub
    
    # 汇率
    if config:
        report.income_exchange_rate = 1 / config.default_cost_rate if config.default_cost_rate else 0.08
    else:
        report.income_exchange_rate = 0.08
    report.cost_exchange_rate = config.default_cost_rate if config else 12.5
    
    db.commit()
    
    # 删除旧的明细
    db.query(ReportProductDetail).filter(
        ReportProductDetail.report_id == report.id
    ).delete()
    
    # 创建新的产品明细
    for key, data in product_sales.items():
        detail = ReportProductDetail(
            report_id=report.id,
            product_id=data["product_id"],
            sku=data["sku"],
            product_name=data["product_name"],
            quantity=data["quantity"],
            sales_rub=data["sales_rub"]
        )
        db.add(detail)
    
    # 自动计算利润
    calculate_report_profit(report.id, db)
    db.refresh(report)
    
    return {
        "message": "报告同步成功",
        "report": {
            "id": report.id,
            "period_start": report.period_start,
            "period_end": report.period_end,
            "total_orders": report.total_orders,
            "total_sales_rub": report.total_sales_rub,
            "total_settlement_rub": report.total_settlement_rub,
            "net_profit_cny": report.net_profit_cny,
            "profit_margin": report.profit_margin,
            "status": report.status
        }
    }


# ========== 8. 固定费用管理 ==========

@router.get("/shops/{shop_id}/fixed-costs")
def get_fixed_costs(
    shop_id: int,
    report_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取固定费用列表"""
    query = db.query(FixedCost).filter(FixedCost.shop_id == shop_id)
    if report_id:
        query = query.filter(FixedCost.report_id == report_id)
    costs = query.all()
    return {"items": [
        {
            "id": c.id,
            "cost_type": c.cost_type,
            "name": c.name,
            "amount_cny": c.amount_cny,
            "allocation_method": c.allocation_method,
            "effective_date": c.effective_date,
            "note": c.note
        }
        for c in costs
    ]}


@router.post("/shops/{shop_id}/fixed-costs")
def create_fixed_cost(
    shop_id: int,
    cost_data: FixedCostCreate,
    report_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建固定费用"""
    cost = FixedCost(
        shop_id=shop_id,
        cost_type=cost_data.cost_type,
        name=cost_data.name,
        amount_cny=cost_data.amount_cny,
        allocation_method=cost_data.allocation_method,
        effective_date=cost_data.effective_date,
        note=cost_data.note,
        report_id=report_id
    )
    db.add(cost)
    db.commit()
    return {"message": "固定费用已创建", "cost": cost}


@router.delete("/fixed-costs/{cost_id}")
def delete_fixed_cost(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除固定费用"""
    cost = db.query(FixedCost).filter(FixedCost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="费用记录不存在")
    db.delete(cost)
    db.commit()
    return {"message": "费用已删除"}


# ========== 9. 收款记录管理 ==========

@router.get("/shops/{shop_id}/payments")
def get_payment_records(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取收款记录"""
    records = db.query(PaymentRecord).filter(
        PaymentRecord.shop_id == shop_id
    ).order_by(PaymentRecord.payment_date.desc()).all()
    return {"items": [
        {
            "id": p.id,
            "payment_date": p.payment_date,
            "settlement_amount_rub": p.settlement_amount_rub,
            "received_cny": p.received_cny,
            "exchange_rate": p.exchange_rate,
            "bank_name": p.bank_name,
            "transaction_id": p.transaction_id
        }
        for p in records
    ]}


@router.post("/shops/{shop_id}/payments")
def create_payment_record(
    shop_id: int,
    payment_data: PaymentRecordCreate,
    report_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建收款记录"""
    payment = PaymentRecord(
        shop_id=shop_id,
        report_id=report_id,
        payment_date=payment_data.payment_date,
        settlement_amount_rub=payment_data.settlement_amount_rub,
        received_cny=payment_data.received_cny,
        exchange_rate=payment_data.exchange_rate,
        bank_name=payment_data.bank_name,
        transaction_id=payment_data.transaction_id
    )
    db.add(payment)
    db.commit()
    return {"message": "收款记录已创建", "payment": payment}


# ========== 10. 汇率管理 ==========

@router.get("/exchange-rates")
def get_exchange_rates(
    rate_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取汇率记录"""
    query = db.query(ExchangeRateRecord)
    if rate_type:
        query = query.filter(ExchangeRateRecord.rate_type == rate_type)
    records = query.order_by(ExchangeRateRecord.effective_date.desc()).limit(30).all()
    return {"items": [
        {
            "id": r.id,
            "rate_type": r.rate_type,
            "base_currency": r.base_currency,
            "target_currency": r.target_currency,
            "rate": r.rate,
            "effective_date": r.effective_date,
            "source": r.source
        }
        for r in records
    ]}


@router.post("/exchange-rates")
def create_exchange_rate(
    rate_type: str,
    base_currency: str,
    target_currency: str,
    rate: float,
    effective_date: str,
    source: str = "manual",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建汇率记录"""
    record = ExchangeRateRecord(
        rate_type=rate_type,
        base_currency=base_currency,
        target_currency=target_currency,
        rate=rate,
        effective_date=effective_date,
        source=source
    )
    db.add(record)
    db.commit()
    return {"message": "汇率已记录", "record": record}


# ========== 11. 多期汇总 ==========

@router.post("/reports/summary")
def get_reports_summary(
    report_ids: List[int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """多期利润汇总"""
    if not report_ids:
        raise HTTPException(status_code=400, detail="请选择报告")
    
    reports = db.query(SalesReport).filter(SalesReport.id.in_(report_ids)).all()
    
    if not reports:
        raise HTTPException(status_code=404, detail="未找到报告")
    
    # 汇总数据
    total_settlement_rub = sum(r.total_settlement_rub or 0 for r in reports)
    total_received_cny = sum(r.total_received_cny or 0 for r in reports)
    total_product_cost_cny = sum(r.total_product_cost_cny or 0 for r in reports)
    total_warehouse_cost_cny = sum(r.total_warehouse_cost_cny or 0 for r in reports)
    total_vat_cny = sum(r.vat_cny or 0 for r in reports)
    total_sales_fee_cny = sum(r.order_sum_fee_cny or 0 for r in reports)
    total_other_cost_cny = sum(r.other_cost_cny or 0 for r in reports)
    total_net_profit_cny = sum(r.net_profit_cny or 0 for r in reports)
    total_orders = sum(r.total_orders or 0 for r in reports)
    
    # 按产品汇总
    details = db.query(ReportProductDetail).filter(
        ReportProductDetail.report_id.in_(report_ids)
    ).all()
    
    product_summary = {}
    for d in details:
        sku = d.sku or "unknown"
        if sku not in product_summary:
            product_summary[sku] = {
                "sku": sku,
                "product_name": d.product_name,
                "total_quantity": 0,
                "total_sales_rub": 0,
                "total_profit_rub": 0
            }
        product_summary[sku]["total_quantity"] += d.quantity or 0
        product_summary[sku]["total_sales_rub"] += d.order_sum_rub or 0
        product_summary[sku]["total_profit_rub"] += d.profit_rub or 0
    
    for sku in product_summary:
        p = product_summary[sku]
        p["profit_margin"] = (p["total_profit_rub"] / p["total_sales_rub"] * 100 
                            if p["total_sales_rub"] > 0 else 0)
    
    # 排序
    sorted_products = sorted(
        product_summary.values(),
        key=lambda x: x["total_profit_rub"],
        reverse=True
    )
    
    return {
        "summary": {
            "report_count": len(reports),
            "period_start": min(r.period_start for r in reports),
            "period_end": max(r.period_end for r in reports),
            "total_orders": total_orders,
            "total_settlement_rub": total_settlement_rub,
            "total_received_cny": total_received_cny,
            "total_product_cost_cny": total_product_cost_cny,
            "total_warehouse_cost_cny": total_warehouse_cost_cny,
            "total_vat_cny": total_vat_cny,
            "total_sales_fee_cny": total_sales_fee_cny,
            "total_other_cost_cny": total_other_cost_cny,
            "total_net_profit_cny": total_net_profit_cny,
            "avg_profit_margin": (total_net_profit_cny / total_received_cny * 100 
                                if total_received_cny > 0 else 0)
        },
        "products": sorted_products[:50]  # 最多返回50个产品
    }

