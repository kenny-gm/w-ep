# Add to ai_config.py

# ========== 报告存储表 ==========
class AIReport(Base):
    __tablename__ = "ai_reports"
    
    id = Column(Integer, primary_key=True)
    type = Column(String(20))  # day, week, month
    date_range = Column(String(100))  # "2026-04-01" or "2026年第14周" or "2026年3月"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class AIReportResponse(BaseModel):
    id: int
    type: str
    date_range: str
    content: str
    created_at: Optional[datetime]

class AIScheduleSettings(BaseModel):
    daily_enabled: bool = False
    daily_time: str = "06:00"
    weekly_enabled: bool = False
    weekly_time: str = "06:00"
    monthly_enabled: bool = False
    monthly_time: str = "06:00"


@router.get("/reports", response_model=List[AIReportResponse])
def get_reports(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """获取AI报告列表"""
    reports = db.query(AIReport).order_by(AIReport.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/reports/{report_id}", response_model=AIReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """获取单个报告"""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report


@router.delete("/reports/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """删除报告"""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    db.delete(report)
    db.commit()
    return {"message": "已删除"}


@router.get("/schedule-settings")
def get_schedule_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """获取调度设置"""
    settings = {}
    for key in ["daily_enabled", "daily_time", "weekly_enabled", "weekly_time", "monthly_enabled", "monthly_time"]:
        s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if s:
            if s.value == "true":
                settings[key] = True
            elif s.value == "false":
                settings[key] = False
            else:
                settings[key] = s.value
        else:
            if "enabled" in key:
                settings[key] = False
            else:
                settings[key] = "06:00"
    return settings


@router.put("/schedule-settings")
def update_schedule_settings(
    data: AIScheduleSettings,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """更新调度设置"""
    for key, value in data.model_dump().items():
        s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if s:
            s.value = str(value)
        else:
            db.add(SystemSetting(key=key, value=str(value)))
    db.commit()
    return {"message": "调度设置已更新"}


@router.post("/generate-report")
async def generate_ai_report(
    type: str = "day",  # day, week, month
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """生成AI报告"""
    from datetime import datetime, timedelta
    
    # 获取日期范围
    today = datetime.now().date()
    if type == "day":
        start_date = today - timedelta(days=1)
        end_date = start_date
        date_range = start_date.strftime("%Y-%m-%d")
    elif type == "week":
        today_weekday = today.weekday()
        last_monday = today - timedelta(days=today_weekday + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_date = last_monday
        end_date = last_sunday
        date_range = start_date.strftime("%Y年%m月%d日") + " - " + end_date.strftime("%m月%d日")
    else:  # month
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        start_date = first_day_last_month
        end_date = last_day_last_month
        date_range = start_date.strftime("%Y年%m月")
    
    # 获取提示词
    config_key = type + "_summary"
    config = db.query(AIConfig).filter(AIConfig.config_key == config_key, AIConfig.is_active == True).first()
    if not config:
        raise HTTPException(status_code=400, detail="未找到提示词配置")
    
    # 获取仪表板数据
    from app.routers.dashboard import get_dashboard_data, DashboardProductsRequest
    from app.database import get_db as get_db_orig
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    db2 = next(get_db_orig())
    try:
        req = DashboardProductsRequest(start_date=start_str, end_date=end_str, shop_ids=None, product_id=None)
        result = get_dashboard_data(req, db2, current_user)
        
        summary = result.get("summary", {})
        items = result.get("items", [])
        
        # 构建数据摘要
        if type == "day":
            data_text = "日期: " + date_range + "\n"
            data_text += "销售额: " + str(summary.get('sales_amount', 0)) + "元\n"
            data_text += "访客数: " + str(summary.get('visitors', 0)) + "\n"
            data_text += "订单数: " + str(summary.get('order_count', 0)) + "\n"
            data_text += "转化率: " + str(summary.get('conversion_rate', 0)) + "%\n"
            data_text += "加购率: " + str(summary.get('add_to_cart_rate', 0)) + "%\n"
            data_text += "广告费: " + str(summary.get('ad_cost', 0)) + "元\n"
            data_text += "广告占比: " + str(summary.get('ad_ratio', 0)) + "%\n\n"
            data_text += "单品数据:\n"
            for item in items[:10]:
                nm_id = item.get('nm_id', item.get('product_id', 'N/A'))
                data_text += "- " + str(nm_id) + ": 销售额" + str(item.get('sales', 0)) + "元, 转化率" + str(item.get('conversion_rate', 0)) + "%\n"
        elif type == "week":
            data_text = "周报数据 (" + date_range + ")\n"
            data_text += "销售额: " + str(summary.get('sales_amount', 0)) + "元\n"
            data_text += "订单数: " + str(summary.get('order_count', 0)) + "\n"
        else:
            data_text = "月报数据 (" + date_range + ")\n"
            data_text += "销售额: " + str(summary.get('sales_amount', 0)) + "元\n"
            data_text += "订单数: " + str(summary.get('order_count', 0)) + "\n"
        
        # 替换提示词变量
        prompt = config.prompt_template.replace("{" + config.variables + "}", data_text)
        
        # 调用AI
        ai_response = await call_ai(prompt, db)
        
        # 保存报告
        report = AIReport(
            type=type,
            date_range=date_range,
            content=ai_response,
            created_at=datetime.now()
        )
        db.add(report)
        db.commit()
        
        return {"id": report.id, "message": "报告生成成功"}
    finally:
        db2.close()
