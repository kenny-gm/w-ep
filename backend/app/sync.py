"""
数据同步服务
支持：
1. 新店铺：自动同步90天历史数据（按天分批）
2. 已存在店铺：增量同步（只拉取新数据）
3. 数据去重：存在则更新，不存在则插入
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.models import (
    Shop, Product, Order, OrderItem, InventorySnapshot,
    AdRecord, SyncLog, InventoryRecord
)
from app.services.wb_api import WBAPIClient
import logging

logger = logging.getLogger("sync")


class SyncService:
    """数据同步服务"""
    
    # 新店铺同步历史天数
    HISTORY_DAYS = 90
    
    # 每批请求间隔（秒），避免限流
    BATCH_INTERVAL = 1.0
    
    def __init__(self, db: Session, shop: Shop):
        self.db = db
        self.shop = shop
        self.client = WBAPIClient(shop.api_token)
        self.shop_id = shop.id
    
    def is_new_shop(self) -> bool:
        """判断是否为新店铺（从未同步过）"""
        return self.shop.last_sync_at is None
    
    def _create_sync_log(self, sync_type: str) -> SyncLog:
        """创建同步日志"""
        sync_log = SyncLog(
            shop_id=self.shop_id,
            sync_type=sync_type,
            status="running"
        )
        self.db.add(sync_log)
        self.db.commit()
        return sync_log
    
    def _finish_sync_log(self, sync_log: SyncLog, success: bool, count: int = 0, message: str = ""):
        """完成同步日志"""
        sync_log.status = "success" if success else "failed"
        sync_log.records_count = count
        sync_log.message = message
        sync_log.finished_at = datetime.now(ZoneInfo("Asia/Shanghai"))
        self.db.commit()
    
    # ==================== 商品同步 ====================
    
    def sync_products(self, limit: int = 1000, overwrite: bool = False) -> dict:
        """
        同步商品
        
        Args:
            limit: 每批获取数量
            overwrite: 是否覆盖已存在的商品
        
        Returns:
            {"success": bool, "count": int, "updated": int}
        """
        sync_log = self._create_sync_log("products")
        
        try:
            count = 0
            updated = 0
            offset = 0
            
            while True:
                cards = self.client.get_products(limit=limit, offset=offset)
                
                if not cards:
                    break
                
                for card in cards:
                    nm_id = str(card.get("nmId", ""))
                    if not nm_id:
                        continue
                    
                    # 查找已存在商品
                    existing = self.db.query(Product).filter(
                        Product.nm_id == nm_id,
                        Product.shop_id == self.shop_id
                    ).first()
                    
                    if existing:
                        if overwrite:
                            # 更新已存在商品
                            existing.name = card.get("title", existing.name)
                            existing.sku = card.get("sku", existing.sku)
                            existing.weight = card.get("weight", 0) / 1000 if card.get("weight") else existing.weight
                            existing.length = card.get("length", 0) / 10 if card.get("length") else existing.length
                            existing.width = card.get("width", 0) / 10 if card.get("width") else existing.width
                            existing.height = card.get("height", 0) / 10 if card.get("height") else existing.height
                            updated += 1
                        continue  # 不覆盖则跳过
                    else:
                        # 创建新商品
                        product = Product(
                            nm_id=nm_id,
                            sku=card.get("sku", ""),
                            shop_id=self.shop_id,
                            name=card.get("title", ""),
                            custom_name=card.get("title", ""),
                            weight=card.get("weight", 0) / 1000 if card.get("weight") else None,
                            length=card.get("length", 0) / 10 if card.get("length") else None,
                            width=card.get("width", 0) / 10 if card.get("width") else None,
                            height=card.get("height", 0) / 10 if card.get("height") else None,
                        )
                        self.db.add(product)
                        count += 1
                
                offset += limit
                self.db.commit()
                
                if len(cards) < limit:
                    break
            
            # 更新同步时间
            self.shop.last_sync_at = datetime.now(ZoneInfo("Asia/Shanghai"))
            self.db.commit()
            
            self._finish_sync_log(sync_log, True, count, f"新增 {count} 个，更新 {updated} 个")
            
            return {"success": True, "count": count, "updated": updated}
            
        except Exception as e:
            logger.error(f"同步商品失败: {e}")
            self._finish_sync_log(sync_log, False, 0, str(e))
            return {"success": False, "error": str(e)}
    
    # ==================== 订单同步 ====================
    
    def sync_orders(self, days: Optional[int] = None, incremental: bool = True) -> dict:
        """
        同步订单 - 使用get_new_orders API
        
        Args:
            days: 同步天数（None表示自动判断）
            incremental: 是否增量同步
        
        Returns:
            {"success": bool, "count": int, "updated": int}
        """
        sync_log = self._create_sync_log("orders")
        
        try:
            # 获取新订单
            orders = self.client.get_new_orders()
            
            count = 0
            updated = 0
            
            for order_data in orders:
                result = self._upsert_order(order_data)
                if result == "created":
                    count += 1
                elif result == "updated":
                    updated += 1
            
            sync_log.status = "success"
            sync_log.records_count = count
            sync_log.finished_at = datetime.now(ZoneInfo("Asia/Shanghai"))
            sync_log.message = f"新增 {count} 个订单，更新 {updated} 个"
            self.db.commit()
            
            return {"success": True, "count": count, "updated": updated}
            
        except Exception as e:
            logger.error(f"同步订单失败: {e}")
            self._finish_sync_log(sync_log, False, 0, str(e))
            return {"success": False, "error": str(e)}
    
    def _upsert_order(self, order_data: dict) -> str:
        """
        插入或更新订单 - 使用get_new_orders返回的数据格式
        
        Returns:
            "created" | "updated" | "skipped"
        """
        # get_new_orders返回的订单字段：orderUid, id, nmId, price, salePrice, createdAt等
        order_uid = str(order_data.get("orderUid", ""))
        order_id = str(order_data.get("id", ""))
        
        if not order_uid and not order_id:
            return "skipped"
        
        # 使用orderUid作为唯一标识（如果存在）
        unique_id = order_uid if order_uid else f"wb_{order_id}"
        
        order_date = None
        if order_data.get("createdAt"):
            try:
                order_date = datetime.fromisoformat(
                    order_data["createdAt"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
            except:
                order_date = None
        
        # 查找已存在订单
        existing = self.db.query(Order).filter(
            Order.order_id == unique_id,
            Order.shop_id == self.shop_id
        ).first()
        
        if existing:
            # 更新已存在订单
            existing.status = "new"
            existing.total_amount = order_data.get("salePrice", 0) or existing.total_amount
            existing.updated_at = datetime.now(ZoneInfo("Asia/Shanghai"))
            if order_date:
                existing.order_date = order_date
            return "updated"
        else:
            # 创建新订单
            order = Order(
                order_id=unique_id,
                shop_id=self.shop_id,
                status="new",
                total_amount=order_data.get("salePrice", 0) or 0,
                commission=0,
                logistics_fee=0,
                order_date=order_date or datetime.now(ZoneInfo("Asia/Shanghai"))
            )
            self.db.add(order)
            self.db.flush()  # 获取 order.id
            
            # 创建订单明细
            nm_id = str(order_data.get("nmId", ""))
            sku = order_data.get("article", "") or order_data.get("skus", [""])[0] if order_data.get("skus") else ""
            
            # 查找产品
            product = self.db.query(Product).filter(
                Product.nm_id == nm_id,
                Product.shop_id == self.shop_id
            ).first()
            
            item_obj = OrderItem(
                order_id=order.id,
                product_id=product.id if product else None,
                nm_id=nm_id,
                sku=sku,
                quantity=1,
                price=order_data.get("price", 0) or 0,
                total_price=order_data.get("salePrice", 0) or 0
            )
            self.db.add(item_obj)
            
            return "created"
    
    # ==================== 库存同步 ====================
    
    def sync_inventory(self) -> dict:
        """
        同步库存快照
        
        Returns:
            {"success": bool, "count": int}
        """
        sync_log = self._create_sync_log("inventory")
        
        try:
            warehouses = self.client.get_warehouses()
            
            count = 0
            for wh in warehouses:
                wh_id = str(wh.get("id", ""))
                wh_name = wh.get("name", "")
                
                stocks = self.client.get_stock(wh_id)
                
                for stock in stocks:
                    nm_id = str(stock.get("nmId", ""))
                    if not nm_id:
                        continue
                    
                    product = self.db.query(Product).filter(
                        Product.nm_id == nm_id,
                        Product.shop_id == self.shop_id
                    ).first()
                    
                    if not product:
                        continue
                    
                    # 创建库存快照（每次同步都是新快照）
                    snapshot = InventorySnapshot(
                        product_id=product.id,
                        warehouse_id=wh_id,
                        warehouse_name=wh_name,
                        quantity=stock.get("amount", 0) or 0
                    )
                    self.db.add(snapshot)
                    count += 1
            
            self.shop.last_sync_at = datetime.now(ZoneInfo("Asia/Shanghai"))
            self.db.commit()
            
            self._finish_sync_log(sync_log, True, count)
            
            return {"success": True, "count": count}
            
        except Exception as e:
            logger.error(f"同步库存失败: {e}")
            self._finish_sync_log(sync_log, False, 0, str(e))
            return {"success": False, "error": str(e)}
    
    # ==================== 广告同步 ====================
    
    def sync_ads(self, days: Optional[int] = None) -> dict:
        """
        同步广告数据 - 使用fullstats API
        
        Args:
            days: 同步天数（None表示自动判断）
        
        Returns:
            {"success": bool, "count": int, "updated": int}
        """
        sync_log = self._create_sync_log("ads")
        
        try:
            date_to = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
            
            if days:
                date_from = (datetime.now(ZoneInfo("Asia/Shanghai")) - timedelta(days=days)).strftime("%Y-%m-%d")
            elif self.shop.last_sync_at:
                date_from = (self.shop.last_sync_at - timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                date_from = (datetime.now(ZoneInfo("Asia/Shanghai")) - timedelta(days=self.HISTORY_DAYS)).strftime("%Y-%m-%d")
            
            stats = self.client.get_ad_stats(date_from=date_from, date_to=date_to)
            
            count = 0
            updated = 0
            
            for stat in stats:
                # fullstats返回的数据结构
                nm_id = str(stat.get("nmId", ""))
                if not nm_id:
                    continue
                
                record_date = None
                if stat.get("date"):
                    try:
                        record_date = datetime.fromisoformat(stat["date"].replace("Z", "+00:00")).replace(tzinfo=None)
                    except:
                        record_date = datetime.now(ZoneInfo("Asia/Shanghai"))
                else:
                    record_date = datetime.now(ZoneInfo("Asia/Shanghai"))
                
                # 查找产品
                product = self.db.query(Product).filter(
                    Product.nm_id == nm_id,
                    Product.shop_id == self.shop_id
                ).first()
                
                if not product:
                    continue
                
                # 创建或更新广告记录
                ad_record = AdRecord(
                    product_id=product.id,
                    shop_id=self.shop_id,
                    ad_type=stat.get("type", "promotion"),
                    impressions=stat.get("views", 0) or 0,
                    clicks=stat.get("clicks", 0) or 0,
                    cost=stat.get("sum", 0) or 0,
                    orders=stat.get("orders", 0) or 0,
                    sales=stat.get("sum_orders", 0) or 0,
                    record_date=record_date
                )
                self.db.add(ad_record)
                count += 1
            
            self.shop.last_sync_at = datetime.now(ZoneInfo("Asia/Shanghai"))
            self.db.commit()
            
            self._finish_sync_log(sync_log, True, count, f"新增 {count} 条广告记录")
            
            return {"success": True, "count": count, "updated": updated}
            
        except Exception as e:
            logger.error(f"同步广告失败: {e}")
            self._finish_sync_log(sync_log, False, 0, str(e))
            return {"success": False, "error": str(e)}
    
    # ==================== 全量同步 ====================
    
    def sync_all(self, history: bool = False) -> dict:
        """
        全量同步
        
        Args:
            history: 是否同步历史数据（新店铺用）
        
        Returns:
            各模块同步结果
        """
        results = {}
        
        # 1. 先同步商品（必须先执行，订单依赖商品）
        logger.info("开始同步商品...")
        results["products"] = self.sync_products(overwrite=True)
        
        if not results["products"]["success"]:
            return results
        
        # 2. 同步订单
        logger.info("开始同步订单...")
        results["orders"] = self.sync_orders()
        
        # 3. 同步库存
        logger.info("开始同步库存...")
        results["inventory"] = self.sync_inventory()
        
        # 4. 同步广告
        logger.info("开始同步广告...")
        if history or self.is_new_shop():
            results["ads"] = self.sync_ads(days=self.HISTORY_DAYS)
        else:
            results["ads"] = self.sync_ads()
        
        logger.info("全量同步完成!")
        return results


# ==================== 订单利润计算 ====================

def calculate_order_profit(db: Session, order: Order) -> Order:
    """计算订单利润"""
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    total_product_cost = 0
    
    for item in items:
        if item.product_id:
            # FIFO 计算产品成本
            records = db.query(InventoryRecord).filter(
                InventoryRecord.product_id == item.product_id,
                InventoryRecord.remaining_quantity > 0
            ).order_by(InventoryRecord.inbound_at).all()
            
            remaining_qty = item.quantity
            item_cost = 0
            
            for record in records:
                if remaining_qty <= 0:
                    break
                
                take_qty = min(remaining_qty, record.remaining_quantity)
                item_cost += take_qty * record.product_cost
                record.remaining_quantity -= take_qty
                remaining_qty -= take_qty
            
            item.product_cost = item_cost
            total_product_cost += item_cost
    
    # 计算利润
    order.product_cost = total_product_cost
    order.profit = (
        order.total_amount 
        - order.commission 
        - order.logistics_fee 
        - order.product_cost 
        - order.ad_cost 
        - order.other_cost
    )
    
    # 计算利润率
    if order.total_amount > 0:
        order.profit_rate = order.profit / order.total_amount
    
    return order
