import re

with open('/opt/wb-erp/backend/app/services/wb_api.py', 'r') as f:
    content = f.read()

# Fix 1: Update API endpoint
content = content.replace(
    '"/api/analytics/v3/sales-funnel/products/history"',
    '"/api/analytics/v3/sales-funnel/products"'
)

# Fix 2: Update docstring
content = content.replace(
    '接口：POST /api/analytics/v3/sales-funnel/products/history',
    '接口：POST /api/analytics/v3/sales-funnel/products'
)

# Fix 3: Update response parsing - handle new structure
old_parsing = '''            # 按产品组织数据
            product_data = {}
            for product in response:
                nm_id = product.get("product", {}).get("nmId")
                if not nm_id:
                    continue
                
                product_data[nm_id] = {}
                for day in product.get("history", []):
                    date = day.get("date")
                    product_data[nm_id][date] = {
                        "visitors": day.get("openCount", 0),
                        "cart_count": day.get("cartCount", 0),
                        "order_count": day.get("orderCount", 0),
                        "order_sum": day.get("orderSum", 0)
                    }
            
            return product_data'''

new_parsing = '''            # 按产品组织数据
            product_data = {}
            products = response.get("data", {}).get("products", [])
            
            for product in products:
                nm_id = str(product.get("product", {}).get("nmId"))
                if not nm_id:
                    continue
                
                stat = product.get("statistic", {}).get("selected", {})
                period = stat.get("period", {})
                date = period.get("start", date_from)
                
                product_data[nm_id] = {
                    date: {
                        "visitors": stat.get("openCount", 0),
                        "cart_count": stat.get("cartCount", 0),
                        "order_count": stat.get("orderCount", 0),
                        "order_sum": stat.get("orderSum", 0)
                    }
                }
            
            return product_data'''

content = content.replace(old_parsing, new_parsing)

with open('/opt/wb-erp/backend/app/services/wb_api.py', 'w') as f:
    f.write(content)

print('Fixed wb_api.py')
