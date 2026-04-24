// 货币格式化工具

/**
 * 格式化金额为卢布
 * @param {number} amount - 金额
 * @param {boolean} showSymbol - 是否显示₽符号
 * @returns {string} 格式化后的金额
 */
export function formatRuble(amount, showSymbol = true) {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return showSymbol ? '₽ 0' : '0'
  }
  
  const formatted = amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
  
  return showSymbol ? `₽ ${formatted}` : formatted
}

/**
 * 格式化百分比
 * @param {number} value - 数值（0-1）
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的百分比
 */
export function formatPercent(value, decimals = 2) {
  if (value === null || value === undefined || isNaN(value)) {
    return '0%'
  }
  return `${(value * 100).toFixed(decimals)}%`
}

/**
 * 格式化数字（千位分隔）
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num) {
  if (num === null || num === undefined || isNaN(num)) {
    return '0'
  }
  return num.toLocaleString('zh-CN')
}

// 默认汇率（人民币转卢布）
export const DEFAULT_EXCHANGE_RATE = 12.5

/**
 * 人民币转卢布
 * @param {number} cny - 人民币金额
 * @param {number} rate - 汇率
 * @returns {number} 卢布金额
 */
export function cnyToRuble(cny, rate = DEFAULT_EXCHANGE_RATE) {
  if (!cny || isNaN(cny)) return 0
  return cny * rate
}
