wb-erp/
├── backend/                    # 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 主入口
│   │   ├── config.py          # 配置文件
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py        # 用户
│   │   │   ├── shop.py        # 店铺
│   │   │   ├── product.py     # 产品
│   │   │   ├── order.py       # 订单
│   │   │   ├── inventory.py   # 库存
│   │   │   ├── ad.py          # 广告数据
│   │   │   └── finance.py     # 财务数据
│   │   ├── routers/           # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 登录认证
│   │   │   ├── dashboard.py   # 销售看板
│   │   │   ├── products.py   # 产品管理
│   │   │   ├── orders.py     # 订单管理
│   │   │   ├── inventory.py  # 库存管理
│   │   │   ├── ads.py         # 广告分析
│   │   │   ├── finance.py    # 利润分析
│   │   │   └── admin.py      # 后台管理
│   │   ├── services/         # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── wb_api.py     # WB API 对接
│   │   │   ├── sync.py        # 数据同步任务
│   │   │   └── calculator.py  # 利润计算
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── security.py   # 安全工具
│   ├── requirements.txt       # Python 依赖
│   └── Dockerfile
├── frontend/                  # 前端
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/           # 路由
│   │   ├── views/            # 页面
│   │   │   ├── Dashboard.vue    # 销售看板
│   │   │   ├── Ads.vue          # 广告分析
│   │   │   ├── Products.vue     # 产品管理
│   │   │   ├── Inventory.vue    # 库存管理
│   │   │   ├── Finance.vue      # 利润分析
│   │   │   └── admin/           # 后台管理
│   │   │       ├── Users.vue
│   │   │       ├── Shops.vue
│   │   │       └── Settings.vue
│   │   ├── components/       # 组件
│   │   ├── stores/           # 状态管理
│   │   └── styles/           # 样式
│   ├── index.html
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml         # 容器编排
├── nginx.conf               # Nginx 配置
└── README.md
