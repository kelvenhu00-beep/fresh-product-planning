# TASK-004 Review：节庆档动态化（农历计算）

- 审查者: claude
- 审查时间: 2026-06-13
- 结论: **✅ 验收通过**

## 验收核查

| 验收项 | 结论 | 说明 |
|---|---|---|
| 2026 年春节 ≈ W7-W10 | ✅ | 页面显示 W7-W10，2026-02-17 = W8，窗口前1后2 正确 |
| 2026 年端午 ≈ W24-W26 | ✅ | DRAGON_BOAT[2026]='2026-06-19'=W25，窗口±1 正确 |
| 2026 年中秋 ≈ W38-W40 | ✅ | MID_AUTUMN[2026]='2026-09-25'=W39，窗口±1 正确 |
| 查表缺失年份有 fallback | ✅ | `lunarDate` 函数 clamp 到 2025-2035 范围 |
| 节庆页高亮逻辑正常 | ✅ | 当前周落入窗口时红边框高亮（目测正常） |
| 节庆周次动态化（无硬编码） | ✅ | 全文检测无 `weeks:[N,M]` 硬编码 |
| normalizeWeek 跨年处理 | ✅ | `while(w<1)w+=52; while(w>52)w-=52;` |
| qingmingDate 公式计算 | ✅ | 天文算法，2026 清明=4月4日=W14 正确 |
| 无 console error | ✅ | Playwright 验证 0 errors |
| 其他页面不受影响 | ✅ | 未动其他页面逻辑 |

## 关键函数确认

- `SPRING_FESTIVAL / DRAGON_BOAT / MID_AUTUMN` 查表覆盖 2025-2035 ✅
- `dateToIsoWeek` 复用现有 `isoWeek()` ✅
- `addDays` 处理日期偏移（元宵=春节+14天）✅
- `lunarDate(table, year)` fallback 安全 ✅
- `festivalDef` 统一构建节庆定义，替代原先硬编码 ✅
