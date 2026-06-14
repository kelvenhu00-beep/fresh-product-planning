# TASK-007: 仪表盘增强 + 数据质量提示

## 状态
- [ ] 待开始  [ ] 进行中  [x] 已完成  [ ] 已验收
- 创建者: claude
- 当前执行账号: codex-guominghu
- 创建时间: 2026-06-13

## 背景

仪表盘目前显示「本周必做行动」和采购雷达，但有两个明显缺口：
1. **数据质量不透明**：系统里有 179 个变体，很多是 dataConfidence=「低」或「中」的 AI 填写数据，采购员不知道哪些数据需要人工核实
2. **淡季看板和复盘页上线后，仪表盘还没有把这两个页面的关键信息聚合进来**：采购员进门第一眼看不到「当前有几个品种即将下市」「今年成交了多少钱」

## 目标

对仪表盘进行两处增强：

### 增强 A：新增「数据质量」提示卡

在仪表盘底部（全年覆盖分析之后）增加一个折叠卡：
`🔍 数据质量待核实（N 个变体）`

展开后按 dataConfidence 分组显示：
- 🔴 可信度「低」：N 个（需要优先核实）
- 🟡 可信度「中」：N 个（建议抽查）
- ✅ 可信度「高」：N 个（已核实）

每组显示变体名列表（chip 形式，点击跳转详情），方便采购员逐步用联网补全功能校对数据。

### 增强 B：顶部新增「快捷入口」行

在「本周必做」红色卡片上方，增加一行 3 个快捷数字卡：

| 卡片 | 数据来源 | 点击行为 |
|---|---|---|
| 🔴 即将下市 N 个 | 淡季看板最后补货窗口品种数 | 跳转 `#/offseason` |
| 📊 本年成交 ¥X | state.transactions 当年总额 | 跳转 `#/review` |
| ⚠️ 零成交品种 N 个 | priority≤2 且本年无成交的品种数 | 跳转 `#/review` |

## 技术约束

- 零依赖，纯 JS/CSS
- 不改动其他页面逻辑
- 快捷卡复用现有 `.kpi-card` 或 `.stat-card` 样式，不新增大量 CSS

## 拆解步骤

### 步骤 1：快捷入口行

在 `renderDashboard()` 顶部（本周必做卡之前）插入三个数字卡 HTML。
数据计算：
- 即将下市：复用 `classifyVariants(state.variants, nowInfo().week).lastWindow.length`
- 本年成交：`(state.transactions||[]).filter(t=>t.year===nowInfo().year).reduce((s,t)=>s+(t.totalAmount||0),0)`
- 零成交品种：`state.variants.filter(v=>Number(v.priority)<=2).filter(v=>!(state.transactions||[]).some(t=>t.variantId===v.id&&t.year===nowInfo().year)).length`

### 步骤 2：数据质量折叠卡

在 `renderDashboard()` 末尾插入 `<details>` 块：
- 计算各 dataConfidence 等级的变体数和列表
- chip 样式复用现有 `.chip` 类
- 默认折叠（`<details>` 不加 `open` 属性）

### 步骤 3：工作日志 + handoff 更新

## 验收标准

- [ ] 仪表盘顶部出现 3 个快捷数字卡，数字与实际数据一致
- [ ] 点击快捷卡分别跳转 `#/offseason` 和 `#/review`
- [ ] 底部出现数据质量折叠卡，三个可信度等级数字正确
- [ ] 展开后 chip 点击可跳转对应变体详情
- [ ] 其他页面不受影响，无 console error

## 潜在风险

1. **`classifyVariants` 依赖**：TASK-005 已实现此函数，确认函数名正确后直接复用
2. **dashboard 重渲染**：快捷卡数据是实时计算的，切换页面回仪表盘时自动刷新

## 执行日志

- [2026-06-14 10:57 | codex-guominghu] 完成仪表盘增强：在「本周必做」前新增 3 个快捷数字卡，分别跳转 `#/offseason`、`#/review`、`#/review`；在仪表盘底部新增「数据质量待核实」折叠卡，按 `dataConfidence` 的「低 / 中 / 高」分组展示数量和 chip，chip 可跳转水果详情。已完成内嵌 JSON 校验、脚本语法校验、浏览器渲染验证、快捷卡跳转验证、数据质量折叠卡展开与 chip 跳转验证，当前页无 console error。
