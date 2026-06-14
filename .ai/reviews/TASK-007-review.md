# TASK-007 Review：仪表盘增强 + 数据质量提示

- 审查者: claude
- 审查时间: 2026-06-14
- 结论: **✅ 验收通过**

## 验收核查

| 验收项 | 结论 | 说明 |
|---|---|---|
| 顶部 3 个快捷数字卡 | ✅ | 即将下市(5) / 本年成交(¥0) / 零成交品种(104) 均正确渲染 |
| 即将下市点击跳转 | ✅ | `location.hash='#/offseason'` |
| 本年成交/零成交跳转 | ✅ | `location.hash='#/review'` |
| 数据与淡季看板一致 | ✅ | 5 个即将下市与 TASK-005 数据吻合 |
| 数据质量折叠卡 | ✅ | 「🔍 数据质量待核实（41 个变体）」位于底部 |
| dataConfidence 分组 | ✅ | 低/中/高三组分别显示数量和 chip |
| chip 点击跳转变体 | ✅ | `openVariant(v.id)` |
| classifyVariants 复用 | ✅ | 直接调用 TASK-005 实现的函数 |
| 无阻断 console error | ✅ | 仅 favicon 404 |
