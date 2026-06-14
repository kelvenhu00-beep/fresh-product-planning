# TASK-006 Review：数据导出（JSON + CSV）

- 审查者: claude
- 审查时间: 2026-06-14
- 结论: **✅ 验收通过**

## 验收核查

| 验收项 | 结论 | 说明 |
|---|---|---|
| topbar「导出 ▾」按钮 | ✅ | 按钮存在，点击展开下拉菜单 |
| 下拉菜单展开/收起 | ✅ | `toggleExportMenu(e)` + `e.stopPropagation()` 防冒泡 |
| 点外部区域关闭 | ✅ | `document.addEventListener('click', e=>!e.target.closest('.export-wrap')&&closeExportMenu())` |
| JSON 备份选项 | ✅ | 「📦 备份数据（JSON）」→ `exportJSON()` |
| CSV 导出选项 | ✅ | 「📊 成交记录（CSV）」→ `exportCSV()` |
| JSON 文件名含日期 | ✅ | `procurement-backup-YYYYMMDD.json` |
| CSV 文件名 | ✅ | `transactions-YYYY.csv` |
| UTF-8 BOM | ✅ | `'﻿'` 开头（Unicode 转义，Excel 中文防乱码）|
| CSV 列顺序正确 | ✅ | 日期/变体名/供应商/规格/数量/单位/单价/金额/合同号/备注 |
| 引号转义 | ✅ | `String(cell).replace(/"/g,'""')` |
| 无阻断 console error | ✅ | 仅 favicon 404 |

## 备注
topbar 有既有「导入 JSON」「导出 JSON」「重置初始数据」按钮，与新「导出 ▾」下拉并存，不影响功能。
