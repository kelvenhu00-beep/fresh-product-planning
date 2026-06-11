# TASK-001: 实际成交价格录入 + 供应商档案

## 状态
- [ ] 待开始  [x] 进行中  [ ] 已完成  [ ] 已验收
- 创建者: claude-A
- 当前执行账号: Codex
- 创建时间: 2026-06-11

## 背景

当前系统只有「采购参考价格区间」（procurementPrice.low/typical/high），但没有实际成交记录。日常采购痛点：

1. 谈判前找供应商联系方式 → 翻外部记录
2. 谈完合同后想记录一笔实际成交（日期 / 数量 / 单价 / 合同号）→ 无处可记
3. 想看「这个变体过去 3 年的实际成交价曲线」用来给下次议价做锚点 → 没有
4. 想知道「张总（某供应商）以前都给我们供过什么、合作几年了」→ 没有

这是把工具从「采购计划工具」升级为「轻 ERP」的关键功能。

## 目标

用户在变体详情页能：
1. 录入一笔实际成交（日期 / 供应商 / 规格 / 数量 / 单价 / 合同号 / 备注），金额自动计算
2. 看到该变体的成交历史 + 在采购 price-bar 上叠加最近 6 个月成交散点
3. 通过新页面「供应商档案」(`#/suppliers`) CRUD + 搜索所有供应商
4. 从变体详情看到关联供应商小卡，点击跳转到该供应商档案

## 技术约束

- **框架/库**：保持零依赖单 HTML 文件，纯 stdlib（与现状一致）
- **schema 向后兼容**：旧 `state.json` / localStorage 无 `suppliers` / `transactions` 字段时必须能正常加载，新字段默认空数组
- **不能动的文件**：
  - `procurement_server.py`（已稳定运行的同步服务）
  - 现有 6 Section 的渲染顺序（H/A/B/C/D/E）—— 新「实际成交」Section 插在 C 之后、D 之前
  - 多设备同步逻辑（`bootstrapSync` / `pollSync` / `persistNow`）不动，新数据自然走同步通道
- **性能要求**：成交记录数 < 1000 条时无明显卡顿
- **兼容性**：macOS Safari 17+ / Chrome 120+，桌面优先

## 数据 schema

**两个新顶级字段**进 `state`：

```ts
state.suppliers: Array<Supplier>
state.transactions: Array<Transaction>   // 全局存，不嵌套到 variant，便于跨变体查询
```

### Supplier 字段

```ts
type Supplier = {
  id: string;                  // "sup-" + timestamp36
  name: string;                // 公司/合作社/个人名
  contactPerson: string;
  phone: string;
  wechat?: string;
  province: string;
  city?: string;
  variantIds?: string[];       // 主供应的变体（用户标记，可选；成交记录会自动反向计算）
  rating: 1 | 2 | 3 | 4 | 5;
  yearsCooperated: number;     // 合作年数
  status: 'active' | 'dormant';
  notes?: string;
  createdAt: string;           // ISO
};
```

### Transaction 字段

```ts
type Transaction = {
  id: string;                  // "tx-" + timestamp36
  variantId: string;           // 关联变体
  supplierId?: string;         // 关联供应商（可空，允许手填 supplierName 不入档）
  supplierName: string;        // 冗余存一份，方便没建档时也能记
  date: string;                // YYYY-MM-DD
  year: number;                // 单独存，便于年度统计
  specGrade?: string;          // 如 "80#" / "L" / "标品"
  quantity: number;
  unit: string;                // "斤" / "件" / "箱" / "个"
  unitPrice: number;
  totalAmount: number;         // 自动 = quantity * unitPrice，不让用户改
  contractNumber?: string;
  notes?: string;
  createdAt: string;           // ISO
};
```

`数据_schema.md` 同步补充这两段定义。

## 拆解步骤

### 1. schema 扩展 + 兼容性兜底
- [ ] `数据_schema.md` 增加 Supplier / Transaction 段落
- [ ] `loadState()` 中加入：`state.suppliers = Array.isArray(saved.suppliers) ? saved.suppliers : []`，`state.transactions` 同理
- [ ] `blankVariantTemplate()` 不需要改（transactions 是全局，不嵌入变体）
- [ ] 导入导出 JSON 自然涵盖（state 整体序列化）

### 2. 供应商档案页 `#/suppliers`
- [ ] `ROUTES` 新增 `['#/suppliers', '供应商']` 放在 `#/variants` 后
- [ ] sidebar nav 自动渲染（基于 ROUTES）
- [ ] `renderSuppliers()`：
  - 左侧筛选条：搜索框（按 name/phone/province 模糊匹配）/ 按省份 select / 按 rating select / [+ 新增供应商]
  - 右侧网格卡列表：每卡 name（大）/ contactPerson + phone / province·city / ⭐ rating / 合作 N 年 / 关联变体数 / [详情]
- [ ] 点卡片打开侧滑详情面板（复用 modal 样式），表单字段全部可编辑
- [ ] 删除供应商时：若存在关联 transactions（按 supplierId），弹 confirm「已有 N 条成交记录，确认删除（成交记录中的 supplierName 保留）」

### 3. 变体详情新增「实际成交」Section
- [ ] 在 `renderVariantDetail` 中，把 `${renderRiskSection(v)}` 之后插入 `${renderTransactionSection(v)}`
- [ ] `renderTransactionSection(v)`：用 `detailSection('transactions', '实际成交记录', viewHtml, editorHtml)` 包裹
- [ ] **View 态**（按 date desc 取最近 5 条）：
  - mini-table：日期 / 供应商 / 规格 / 数量·单位 / 单价 / 金额 / 合同号
  - 表下小结：「共 N 条成交，累计金额 ¥X，加权均价 ¥Y/单位」
  - 若 > 5 条：「展开全部」按钮
- [ ] **Edit 态**：arrayTable 列：date / supplierName (input + datalist 从 state.suppliers 联想) / specGrade / quantity / unit / unitPrice / contractNumber / notes
  - quantity 或 unitPrice 任一变化 → 实时刷新该行 totalAmount 显示（不允许直接编辑 totalAmount）
  - 新增行：日期默认今天，unit 默认上一次输入

### 4. price-bar 叠加最近 6 个月实际成交散点
- [ ] `priceRangeView` 增强：若是采购价（label === '采购'）且有该变体最近 6 个月 transactions，在 price-bar 上叠加散点：
  - 每个 transaction 一个 `.price-bar-actual` 小圆点
  - 横向位置 = `(tx.unitPrice - low) / (high - low) * 100%`，clamp [0, 100]
  - 颜色：金色，加 title 显示 「W?·N斤@¥X·供应商Y」
- [ ] CSS 新增 `.price-bar-actual{position:absolute;width:8px;height:8px;border-radius:50%;background:var(--gold);border:2px solid #fff;top:2px;transform:translateX(-50%);box-shadow:0 1px 2px rgba(0,0,0,.2)}`

### 5. 变体↔供应商双向链接
- [ ] 在变体详情 Section H（头部）的徽章组下方追加「关联供应商」小卡区域
  - 数据来源：① 在 state.transactions 中出现过 supplierId 的供应商 ∪ ② state.suppliers 中 variantIds 包含本变体的
  - 每个供应商一个 chip：name + phone + ⭐ rating + onclick 跳转 `#/suppliers` 并选中该供应商
- [ ] 供应商档案详情面板增加「关联变体」列表（同样双向计算）

### 6. 多设备同步联调
- [ ] 录入一笔成交 → `persistNow()` 自动 POST 到 server.state.json → 另一设备 ≤10s 同步
- [ ] 在 A 设备删除供应商 → B 设备 10s 内同步删除
- [ ] 在 A / B 同时编辑同一供应商时 LWW（最后保存的赢，符合现状）

### 7. 工作日志 + handoff 更新
- [ ] 在 `工作日志.md` 追加 `[YYYY-MM-DD HH:MM | Codex] TASK-001 交付：...`
- [ ] 在 `.ai/handoff.md` 更新状态
- [ ] 在本任务卡的「执行日志」追加每步完成时间

## 验收标准

- [ ] **schema 兼容**：旧 state.json（无 suppliers/transactions 字段）加载后无 console error，新字段自动为空数组
- [ ] **供应商档案页**：可新增 / 编辑 / 搜索 / 软删（保留成交关联）
- [ ] **实际成交录入**：在任一变体详情页可新增 / 编辑 / 删除成交记录，totalAmount 自动计算
- [ ] **price-bar 散点**：录入一笔成交后，price-bar 上立即出现金色圆点 marker
- [ ] **双向链接**：在变体详情看到关联供应商 → 点击跳转到供应商页且高亮该供应商；反之亦然
- [ ] **多设备同步**：设备 A 录入成交后，设备 B 在 10 秒内 toast「已同步」并显示新数据
- [ ] **其他页面不受影响**：仪表盘 / 全年日历 / 行动清单 / 节庆档 / 联网补全 均正常运行
- [ ] **无 console error**

## 潜在风险 / 踩坑提示

1. **跨年日期**：成交记录的 `date` 字段如果跨年（12 月底登记 1 月发生），`year` 字段需单独存而不是从 date 截取（避免之后改 date 时 year 不同步）。约定：录入时 `year = parseInt(date.slice(0, 4))`，每次 date 变更同步刷新 year。
2. **supplierId 软关联**：成交记录可只有 supplierName（用户没建供应商档案直接手填），后续建档时按 name 模糊匹配回填 supplierId（v1.1 增量，TASK-001 不做匹配，仅保证 supplierName 字段存在）。
3. **删除供应商**：默认软删（status='dormant'），保留成交记录中的 supplierName 显示。
4. **price-bar 散点重叠**：6 个月内可能有多笔同价位成交，散点会重叠。v1 允许重叠，hover 用 title 显示全部。后续可叠加抖动或聚合。
5. **datalist 性能**：state.suppliers 大于 200 个时联想可能卡顿。当前可忽略。
6. **移动端响应式**：5-7 列 mini-table 在窄屏挤压。v1 接受横向滚动。
7. **金额数值溢出**：unitPrice × quantity 在大宗采购（如 10 吨 × 5 元 = 50000）下用 Number 没问题，但要避免 unitPrice 用户填错单位（元/吨当元/斤），UI 上单位字段醒目。
8. **导入导出 JSON 向后兼容**：导入旧 v1 JSON 仍可加载（state.suppliers / transactions 自动为空）；导出 v2 JSON 在旧版打开会忽略新字段（无破坏）。

## 执行日志

> Codex 每完成一步追加一行，格式: `YYYY-MM-DD HH:MM [账号X] 完成步骤 N: 说明`

- 2026-06-11 21:29 [Codex] 完成步骤 1-2: 扩展 Supplier / Transaction schema 与旧数据兼容兜底；新增 `#/suppliers` 供应商档案页、筛选、卡片、详情编辑面板与软删。
