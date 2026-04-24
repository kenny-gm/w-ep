// 店铺列表
export const mockShops = [
  { id: 1, name: '俄罗斯旗舰店', currency: 'RUB' },
  { id: 2, name: '白俄罗斯分店', currency: 'RUB' },
]

// 产品列表
export const mockProducts = [
  { id: 101, name: '女士羊毛大衣', shop_id: 1, product_id: 'WB-12345-67890', sku: 'SKU-WO-001' },
  { id: 102, name: '男士羽绒服', shop_id: 1, product_id: 'WB-12345-67891', sku: 'SKU-DJ-002' },
  { id: 103, name: '儿童棉服', shop_id: 2, product_id: 'WB-12345-67892', sku: 'SKU-KD-003' },
]

// 核心指标
export const mockCoreMetrics = {
  total_sales: 1285000,
  total_sales_trend: 15,
  total_orders: 342,
  total_orders_trend: 8,
  natural_orders: 256,
  natural_orders_ratio: 74.9,
  natural_orders_ratio_trend: 2.1,
}

// 销售趋势数据（最近7天）
export const mockSalesTrend = {
  dates: ['2026-03-14', '2026-03-15', '2026-03-16', '2026-03-17', '2026-03-18', '2026-03-19', '2026-03-20'],
  values: [152000, 168000, 184000, 172000, 196000, 210000, 228000],
}

// 广告效果指标（卢布）
export const mockAdMetrics = {
  ad_spend: 128000,
  ad_spend_trend: 5.2,
  roas: 2.4,
  roas_trend: -0.3,
  acos: 9.9,
  acos_trend: 1.2,
  ad_orders: 86,
  ad_orders_trend: 8.5,
  ad_orders_ratio: 25.1,
  ctr: 0.0215,
  ctr_trend: 0.3,
}

// 流量来源分解
export const mockTrafficSource = {
  natural_ratio: 73,
  ad_ratio: 25,
  other_ratio: 2,
  natural_visitors: 7300,
  ad_visitors: 2500,
  other_visitors: 200,
  total_visitors: 10000,
  ad_clicks: 2500,
  ad_impressions: 50000,
  ad_spend: 15000,
  total_orders: 100,
  ad_orders: 30,
  natural_orders: 70
}

// 广告vs自然流量趋势
export const mockTrafficTrend = {
  dates: ['2026-03-14', '2026-03-15', '2026-03-16', '2026-03-17', '2026-03-18', '2026-03-19', '2026-03-20'],
  ad_traffic: [22, 23, 24, 25, 24, 23, 22],
  natural_traffic: [78, 77, 76, 75, 76, 77, 78],
}

// 广告活动数据（带时间列，卢布）
export const mockAdCampaigns = [
  // CPM搜索 - 每日数据
  { date: '2026-03-20', type: 'cpm_search', type_name: 'CPM搜索', impressions: 15420, clicks: 386, ctr: 0.0250, add_to_cart: 42, cart_rate: 0.1088, orders: 15, conversion_rate: 0.0389, spend: 15420, sales: 69300, cpc: 40, cpm: 1000, acos: 0.222, roas: 4.5 },
  { date: '2026-03-19', type: 'cpm_search', type_name: 'CPM搜索', impressions: 14800, clicks: 370, ctr: 0.0250, add_to_cart: 40, cart_rate: 0.1081, orders: 14, conversion_rate: 0.0378, spend: 14800, sales: 66600, cpc: 40, cpm: 1000, acos: 0.222, roas: 4.5 },
  { date: '2026-03-18', type: 'cpm_search', type_name: 'CPM搜索', impressions: 16200, clicks: 405, ctr: 0.0250, add_to_cart: 45, cart_rate: 0.1111, orders: 16, conversion_rate: 0.0395, spend: 16200, sales: 72900, cpc: 40, cpm: 1000, acos: 0.222, roas: 4.5 },
  { date: '2026-03-17', type: 'cpm_search', type_name: 'CPM搜索', impressions: 15600, clicks: 390, ctr: 0.0250, add_to_cart: 43, cart_rate: 0.1103, orders: 15, conversion_rate: 0.0385, spend: 15600, sales: 70200, cpc: 40, cpm: 1000, acos: 0.222, roas: 4.5 },
  
  // CPM推荐
  { date: '2026-03-20', type: 'cpm_recommend', type_name: 'CPM推荐', impressions: 9800, clicks: 137, ctr: 0.0140, add_to_cart: 18, cart_rate: 0.1314, orders: 5, conversion_rate: 0.0365, spend: 19600, sales: 39200, cpc: 143, cpm: 2000, acos: 0.500, roas: 2.0 },
  { date: '2026-03-19', type: 'cpm_recommend', type_name: 'CPM推荐', impressions: 9200, clicks: 128, ctr: 0.0139, add_to_cart: 16, cart_rate: 0.1250, orders: 4, conversion_rate: 0.0313, spend: 18400, sales: 36800, cpc: 144, cpm: 2000, acos: 0.500, roas: 2.0 },
  
  // CPC搜索
  { date: '2026-03-20', type: 'cpc_search', type_name: 'CPC搜索', impressions: 5200, clicks: 114, ctr: 0.0219, add_to_cart: 22, cart_rate: 0.1930, orders: 8, conversion_rate: 0.0702, spend: 34200, sales: 102600, cpc: 300, cpm: 6577, acos: 0.333, roas: 3.0 },
  { date: '2026-03-19', type: 'cpc_search', type_name: 'CPC搜索', impressions: 4800, clicks: 106, ctr: 0.0221, add_to_cart: 20, cart_rate: 0.1887, orders: 7, conversion_rate: 0.0660, spend: 31800, sales: 95400, cpc: 300, cpm: 6625, acos: 0.333, roas: 3.0 },
]

// 关键词数据（卢布）
export const mockKeywords = [
  { keyword: '羊毛大衣女冬季', impressions: 8500, clicks: 280, ctr: 0.0329, spend: 8500, sales: 29750, roas: 3.5, cpc: 30, position: 2.3, suggestion: '✅ 加大投放，提高出价10%', suggestion_type: 'increase' },
  { keyword: '女士毛呢大衣', impressions: 6200, clicks: 186, ctr: 0.0300, spend: 6200, sales: 21700, roas: 3.5, cpc: 33, position: 3.1, suggestion: '✅ 保持当前出价', suggestion_type: 'maintain' },
  { keyword: '韩版毛呢外套', impressions: 4800, clicks: 120, ctr: 0.0250, spend: 4800, sales: 14400, roas: 3.0, cpc: 40, position: 4.2, suggestion: '✅ 保持当前出价', suggestion_type: 'maintain' },
  { keyword: '冬季加厚外套', impressions: 3500, clicks: 70, ctr: 0.0200, spend: 3500, sales: 7000, roas: 2.0, cpc: 50, position: 5.5, suggestion: '⚠️ 点击率偏低，优化广告创意', suggestion_type: 'optimize' },
  { keyword: '保暖毛呢大衣', impressions: 2800, clicks: 56, ctr: 0.0200, spend: 2800, sales: 5040, roas: 1.8, cpc: 50, position: 6.2, suggestion: '⚠️ ROAS偏低，优化关键词', suggestion_type: 'optimize' },
  { keyword: '修身毛呢外套', impressions: 1800, clicks: 36, ctr: 0.0200, spend: 1800, sales: 2880, roas: 1.6, cpc: 50, position: 7.1, suggestion: '❌ ROAS过低，暂停或降低出价50%', suggestion_type: 'pause' },
]

// AI优化建议
export const mockOptimizationAdvice = {
  overall: 'ROAS 2.4，低于行业平均（3.5），建议优化关键词和出价策略',
  by_type: {
    cpm_search: '✅ 关键词"羊毛大衣女冬季"表现优异，ROAS 3.5，建议提高出价10%\n⚠️ 关键词"冬季加厚外套"点击率偏低(2.0%)，建议优化广告图\n❌ 关键词"修身毛呢外套"ROAS仅1.6，建议暂停或降低出价50%',
    cpm_recommend: '⚠️ 点击率仅1.4%，低于CPM搜索的2.5%，建议优化商品主图和标题\n✅ 转化率表现良好，可适当增加预算',
    cpc_search: '✅ 转化率0.07%为最高，但CPC偏高(₽300)，建议优化关键词匹配方式\n⚠️ 建议降低出价或寻找更低竞争关键词',
  },
  budget_allocation: '建议将35%预算分配给CPM搜索，15%给CPC搜索，50%给表现稳定的CPM推荐',
}
