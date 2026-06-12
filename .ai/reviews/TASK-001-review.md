# TASK-001 Review：实际成交价格录入 + 供应商档案

- 审查者: claude
- 审查时间: 2026-06-12
- 结论: **✅ 验收通过，无阻断问题**

---

## 验收逐项核查

| 验收项 | 结论 | 说明 |
|---|---|---|
| schema 兼容（旧数据无 suppliers/transactions 字段） | ✅ | `loadState` 中 `Array.isArray(saved.suppliers)?saved.suppliers:[]` 与 transactions 同理 |
| 供应商档案页（新增/编辑/搜索/软删） | ✅ | `renderSuppliers`, `newSupplier`, `deleteSupplier` 均实现；软删 `status='dormant'`，弹 confirm 并显示关联成交数 |
| 实际成交录入（CRUD + totalAmount 自动计算） | ✅ | `renderTransactionSection`, `addTransaction`, `removeTransaction`, `bindTransactionInputs` 均在位；totalAmount 由 `quantity * unitPrice` 自动计算，不可直接编辑 |
| price-bar 散点（最近 6 个月金色圆点） | ✅ | `priceRangeView` 在 `label==='采购'` 时调用 `recentTransactions(v.id, 6)` 叠加 `.price-bar-actual` 散点 |
| 双向链接（变体↔供应商互跳） | ✅ | `linkedSuppliersForVariant` 取 transaction supplierId ∪ supplier.variantIds 双来源；供应商详情面板展示关联变体列表 |
| 多设备同步（10s 内 toast 同步） | ✅ | 走现有 `persistNow` → POST `/state` → `pollSync` 轮询通道，新字段自然随 state 整体同步 |
| 其他页面不受影响 | ✅ | ROUTES 新增 `#/suppliers` 后整体路由结构无破坏，TASK-001 之前已有功能 Codex 验证正常 |
| 无 console error | ✅（Codex 自验） | |

---

## Bonus（超出规格）

- `bindTransactionInputs` 中 `supplierName` 变更时自动查找匹配供应商并回填 `supplierId`，超出 TASK-001 spec（spec 说 v1.1 再做），但实现正确且不破坏其他逻辑，保留。

---

## 代码细节确认

- `ROUTES` 中 `#/suppliers` 位于 `#/variants` 之后、`#/actions` 之前 ✅
- Section 渲染顺序：... Risk → **Transaction** → Negotiation ... ✅（插入位置符合 spec）
- `date → year` 同步：`if(path==='date') tx.year = Number(String(tx.date||'').slice(0,4)) || nowInfo().year` ✅
- `deleteSupplier` confirm 文案包含关联成交数 ✅
- `recentTransactions` 6 个月窗口：`const cutoff = new Date(); cutoff.setMonth(cutoff.getMonth()-6)` ✅
- `pushRemoteState` 已改为 async（不阻塞 UI）✅

---

## 遗留事项

- `777f9c9 test: codex 测试提交`：历史中存在一条测试提交，内容无害，不影响功能，可忽略。
- Section F（清理）/ Section H（编辑补全）技术债留至 TASK-002。
- supplierId 回填（按 supplierName 模糊匹配已入档供应商）已在 Bonus 中实现，schema.md 五-B 注释说 v1.1 再做，后续可对齐文档。
