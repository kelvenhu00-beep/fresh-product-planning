# TASK-010: P0 修復水果管理詳情頁完整功能

## 狀態
- [ ] 待開始  [ ] 進行中  [ ] 已完成  [ ] 已驗收
- 創建者: claude
- 當前執行賬號: (Codex 接手時填寫)
- 創建時間: 2026-06-14
- **優先級：P0，阻斷，先於其他任務執行**

## 問題描述

TASK-005（commit 47ff252）实现淡季看板时意外把水果管理详情页完整重写为简化版
`renderVariantDetailView`，导致以下功能全部丢失：

| 丢失功能 | 原函数 | 首次实现于 |
|---|---|---|
| 成交记录 Section | `renderTransactionSection` | TASK-001 |
| 供应商双向链接 | `renderLinkedSuppliers` | TASK-001 |
| price-bar 成交散点 | `priceRangeView` 内 scatter | TASK-001 |
| Section 编辑系统 | `startSectionEdit/saveSectionEdit/cancelSectionEdit` | TASK-002 |
| Section H 头部编辑 | `renderDetailHeader`（含 editing 态） | TASK-002 |
| 上市周期 Section | `renderSeasonSection` | 原始版 |
| 规格价格 Section | `renderPriceSection` | 原始版 |
| 风险储存 Section | `renderRiskSection` | 原始版 |
| 谈判要点 Section | `renderNegotiationSection` | 原始版 |
| 行动计划 Section | `renderActionPlanSection` | 原始版 |
| detailSection 辅助函数 | `detailSection(key,title,view,edit)` | 原始版 |
| 变体徽章组 | `variantChips(v)` | 原始版 |

## 修復目標

從 commit `28731fa`（TASK-002 完成狀態，所有功能齊全）恢復水果詳情頁的完整函數集，同時保留此後各任務（TASK-003/005/006/007）添加的新功能。

## 修復方案

### 方式：從 git 精準提取並替換

1. 用 `git show 28731fa:index.html` 提取 TASK-002 版本
2. 從中提取以下所有函數的完整定義（它們在 TASK-005 中被整體丟棄）：
   - `renderVariantDetail(v)` ← 主入口（替換現在的 renderVariantDetailView）
   - `renderDetailHeader(v, c)`
   - `renderSeasonSection(v, c)`
   - `renderPriceSection(v)`
   - `renderRiskSection(v)`
   - `renderTransactionSection(v)`
   - `renderNegotiationSection(v)`
   - `renderActionPlanSection(v)`
   - `detailSection(key, title, viewHtml, editHtml)`
   - `startSectionEdit(section)`
   - `saveSectionEdit()`
   - `cancelSectionEdit()`
   - `variantChips(v)`
   - `renderLinkedSuppliers(v)`
   - `linkedSuppliersForVariant(v)`
   - `priceRangeView(label, range, v)` ← 含成交散點
   - `renderTransactionSection` 依賴的輔助：`addTransaction`, `removeTransaction`, `bindTransactionInputs`, `transactionById`, `recentTransactions`, `variantTransactions`, `reviewQuantityText`（若 renderTransactionSection 需要）

3. 在 index.html 中：
   - 刪除 `renderVariantDetailView` 函數定義
   - 插入上述提取的完整函數集
   - 找到 `renderVariantDetailView` 的調用處，替換為 `renderVariantDetail`

4. 調用處確認：在 `renderVariants()` 函數中找到水果管理詳情的渲染調用，確保改為 `renderVariantDetail(v)` 

### 注意事項

- **不要改動** TASK-003/005/006/007 新增的函數（復盤/淡季/導出/儀表盤）
- **不要改動** ROUTES、sidebar、topbar 等結構
- 如果 `28731fa` 版本中有部分函數與新版本衝突（重名），以 `28731fa` 版本為準（它是經過驗收的完整版本）
- `bindTransactionInputs`、`addTransaction` 等 TASK-001 函數在 `28731fa` 中都已存在，直接恢複即可

## 驗收標準

- [ ] 水果管理詳情頁顯示完整 Section 結構：H 頭部 → A 上市 → B 規格价格 → C 風險 → D 成交記錄 → E 談判 → F 行動計划
- [ ] 每個 Section 有「✎ 編輯」按鈕，點擊後進入編輯態，有保存/取消
- [ ] Section H 頭部有「編輯」按鈕，點擊展開 13 個字段編輯表單
- [ ] 成交記錄 Section 可新增/刪除成交行，totalAmount 自動計算
- [ ] 採購價 price-bar 上方有成交散點（錄入成交後可見）
- [ ] 供應商 chip 顯示在頭部，可跳轉供應商頁
- [ ] 其他所有頁面（仪表盘/日历/节庆/淡季/复盘/供应商）不受影響
- [ ] 無 console error

## 執行日誌

-
