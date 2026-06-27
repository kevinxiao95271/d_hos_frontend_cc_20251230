/**
 * 将前端持有的 timeDimension + timeValue 转换为后端计算接口所需的 startDate / endDate
 *
 * timeDimension | timeValue   | startDate   | endDate
 * YEAR          | 2020        | 2020-01-01  | 2020-12-31
 * MONTH         | 2025-01     | 2025-01-01  | 2025-01-31
 * QUARTER       | 2025-Q1     | 2025-01-01  | 2025-03-31
 * DAY           | 2025-01-15  | 2025-01-15  | 2025-01-15
 */
export function toDateRange(timeDimension, timeValue) {
  if (!timeDimension || !timeValue) {
    throw new Error(`缺少必填参数：timeDimension=${timeDimension}, timeValue=${timeValue}`)
  }

  const dim = String(timeDimension).toUpperCase()

  if (dim === 'YEAR') {
    const year = String(timeValue).trim()
    return { startDate: `${year}-01-01`, endDate: `${year}-12-31` }
  }

  if (dim === 'MONTH') {
    const [year, month] = String(timeValue).split('-').map(Number)
    const lastDay = new Date(year, month, 0).getDate()
    const mm = String(month).padStart(2, '0')
    const dd = String(lastDay).padStart(2, '0')
    return { startDate: `${year}-${mm}-01`, endDate: `${year}-${mm}-${dd}` }
  }

  if (dim === 'QUARTER') {
    const [yearStr, qStr] = String(timeValue).split('-')
    const year = Number(yearStr)
    const q = Number(String(qStr).replace('Q', ''))
    const quarterMap = {
      1: { start: '01-01', end: '03-31' },
      2: { start: '04-01', end: '06-30' },
      3: { start: '07-01', end: '09-30' },
      4: { start: '10-01', end: '12-31' },
    }
    const { start, end } = quarterMap[q] || {}
    if (!start) throw new Error(`非法季度值：${timeValue}`)
    return { startDate: `${year}-${start}`, endDate: `${year}-${end}` }
  }

  if (dim === 'DAY') {
    const day = String(timeValue).trim()
    return { startDate: day, endDate: day }
  }

  throw new Error(`不支持的 timeDimension：${timeDimension}`)
}
