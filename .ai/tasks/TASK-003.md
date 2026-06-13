# TASK-003: 季后复盘模块 `#/review`

## 状态
- [ ] 待开始  [ ] 进行中  [x] 已完成  [ ] 已验收
- 创建者: claude
- 当前执行账号: codex-guominghu
- 创建时间: 2026-06-12

## 背景

TASK-001 实现了实际成交录入和供应商档案，数据已经在系统里了，但目前没有任何地方能**回头看**：
- 这一年某品种买了多少次？总花了多少钱？均价是否高于参考价？
- 哪些供应商用得最多？哪家给的价格最好？
- 哪些品种压根没有成交记录（漏采？未到季？）
- 行动计划完成率怎样？
- 有什么经验要记录给下一年？

这是把工具从「采购计划」升级为「采购管理闭环」的关键一步：
**计划 → 执行（行动/成交）→ 复盘 → 优化下一年计划**

## 目标

新增 `#/review` 复盘页，让采购员在一个年度结束（或季中）时：
1. 按年份汇总本年全部成交，看整体采购执行情况
2. 逐品种看：计划参考价 vs 实际均价、成交时序 vs 上市窗口
3. 逐供应商看：使用频次、供货总量、均价表现
4. 记录品种维度的「本年复盘笔记」（给下年采购参考）
5. 快速识别「零成交品种」（计划了但没有记录的品种）

## 技术约束

- **框架/库**：零依赖单 HTML 文件，纯 JS/CSS（与现状一致）
- **数据来源**：`state.transactions`、`state.suppliers`、`state.variants`、`state.actions`（均已有）
- **新增存储字段**：`state.reviewNotes: { [variantId]: { [year]: string } }` —— 复盘笔记，旧 state 加载时默认 `{}`
- **不能动的文件**：`procurement_server.py`、多设备同步逻辑
- **路由位置**：`ROUTES` 在 `#/festivals` 后追加 `['#/review', '复盘']`
- **性能**：全量遍历 transactions（< 1000 条）无需虚拟化

## 拆解步骤

### 步骤 1：schema 扩展 + 路由

- [ ] `loadState()` 加：`state.reviewNotes = (typeof saved.reviewNotes === 'object' && !Array.isArray(saved.reviewNotes)) ? saved.reviewNotes : {}`
- [ ] `ROUTES` 末尾加 `['#/review', '复盘']`

### 步骤 2：复盘页主框架 `renderReview()`

页面结构（从上到下）：

```
[ 顶部筛选栏 ]
  年份 select（从 transactions 的 year 字段枚举去重，降序；若无成交则只显示当前年）
  默认选中最新有成交记录的年份

[ 年度总览卡片行 ]  ← 4 个 KPI 卡
  - 总成交笔数
  - 总采购金额（¥X）
  - 涉及品种数 / 全部 priority≤2 品种数（如 18/30）
  - 涉及供应商数

[ 品种复盘列表 ]  ← 按优先级+名称排序
  每个有成交记录的品种一行（见下方细节）
  末尾单独一组「零成交品种」折叠区域

[ 供应商排行 ]  ← 按本年成交总金额降序 Top 10
```

### 步骤 3：品种复盘行 `renderVariantReviewRow(v, txList, year)`

每行展示：

**左侧（~40%）**
- 变体名（大）+ 品类名（小）
- 成交统计：`N 笔 · X 斤/件/箱 · ¥Y 均价 · ¥Z 总额`
- 价格偏差 badge：`均价 vs 参考典型价`
  - 均价 < 参考 low → `🟢 低于参考区间`
  - low ≤ 均价 ≤ high → `🟡 在参考区间内`
  - 均价 > high → `🔴 高于参考区间`

**中间（~35%）：成交时序迷你图**
- 复用全年日历的 52 周色带思路（缩小版，高度约 12px）
- 绿色底条 = peakStartWeek ~ peakEndWeek（大量上市窗口）
- 每笔成交用金色竖线标注在对应 ISO 周位置
- 若某笔成交落在 peak 窗口外，竖线改为红色（提示抢购或错过）

**右侧（~25%）：复盘笔记**
- 单行 `<textarea>` 展示，点击进入编辑，失焦自动保存到 `state.reviewNotes[v.id][year]`
- placeholder：「记录本年采购经验，供下年参考…」

**行末**：`[详情 →]` 按钮 → 跳转 `#/variants` 并选中该变体

### 步骤 4：供应商排行 `renderSupplierRanking(txList)`

取本年 txList，按 `supplierName` 聚合：

| 供应商名 | 成交笔数 | 总量 | 总额 | 均价 | 供过品种数 |
|---|---|---|---|---|---|

- Top 10 显示，超出可「展开全部」
- 每行点击：跳转 `#/suppliers` 并选中该供应商（若有 supplierId）

### 步骤 5：零成交品种折叠区 + 行动完成率

**零成交品种（`<details>` 折叠，默认收起）**
- 筛选：priority ≤ 2 的变体中，当年无任何成交记录的品种
- 每个品种一个 chip（点击跳到该变体详情）
- 标题：`⚠️ 零成交品种（N 个）—— 计划了但本年无记录，请确认是否漏记`

**行动完成率（小卡，放在年度总览右侧或下方）**
- 筛选本年（`action.year === selectedYear`）的所有 action
- 显示：`完成 X / 共 Y（Z%）` + 简单进度条
- 分紧急度拆分：高/中/低各自的完成率

### 步骤 6：复盘笔记自动保存

- `<textarea>` `oninput` → debounce 500ms → 写入 `state.reviewNotes[variantId][year]`
- 随后调用 `persistNow()`（走现有 localStorage + POST /state 同步通道）
- 无需 Section 编辑态（笔记随时自动保存，不需要保存/取消按钮）

### 步骤 7：工作日志 + handoff 更新

- `工作日志.md` 追加 `[2026-06-12 HH:MM | Codex] TASK-003 交付：...`
- `.ai/handoff.md` 更新状态
- 本任务卡执行日志追加每步完成时间

## 验收标准

- [ ] **路由可用**：侧边栏出现「复盘」，点击进入 `#/review` 无报错
- [ ] **年份筛选**：有成交数据时默认选最新年份；切换年份时列表联动刷新
- [ ] **年度 KPI**：4 个汇总卡数字与 `state.transactions` 中本年数据一致
- [ ] **品种复盘行**：有成交的品种均显示，均价/总额/笔数正确；价格偏差 badge 颜色正确
- [ ] **成交时序图**：peak 窗口底色正确；金色竖线落在对应 ISO 周；peak 外成交竖线变红
- [ ] **复盘笔记**：输入后 500ms 内自动保存；刷新页面后文字保留；多年笔记互不干扰
- [ ] **零成交品种**：priority ≤ 2 且本年无成交的品种均列出，chip 可跳转
- [ ] **供应商排行**：按本年总额降序，数字正确；点击可跳转供应商页
- [ ] **行动完成率**：本年行动的完成数/总数正确，三个紧急度分拆正确
- [ ] **其他页面不受影响**：仪表盘/日历/水果管理/供应商/行动清单均正常
- [ ] **无 console error**

## 潜在风险 / 踩坑提示

1. **`reviewNotes` 序列化**：`loadState` 里要用 `typeof saved.reviewNotes === 'object' && !Array.isArray(...)` 判断，
   防止旧 state 里该字段不存在或被意外序列化成 `null`。

2. **ISO 周计算**：成交记录的 `date` 字段（YYYY-MM-DD）需转成 ISO 周编号才能在时序图上定位。
   复用现有 `isoWeek(date)` 函数（或等价实现）；若函数名不同，先 grep 确认。

3. **跨年 peak 渲染**：`peakStartWeek > peakEndWeek` 时（如榴莲 W48 ~ W10），
   底色色带要分两段渲染（W48-W52 + W1-W10），不要直接用 `left: startW/52*100%` 单段。

4. **成交落在当年 vs variant 跨年 peak**：
   成交时序图的 52 周坐标系以「日历年 1-52」为基准，不随 peak 跨年偏移。
   成交在 peak 窗口外的判定：`week < peakStartWeek && week > peakEndWeek`（跨年 peak 时逻辑取反）。

5. **零成交品种**：只检查 priority ≤ 2，priority 3 长尾品种不列入，避免噪音太多。

6. **供应商聚合用 supplierName 不用 supplierId**：
   部分成交可能没有 supplierId（手填了 supplierName 但未建档），按 name 聚合才不会漏掉。

7. **复盘笔记 debounce**：不要用 `scheduleSave` / `saveTimer`（它们是变体编辑用的），
   给笔记 textarea 单独维护一个 `reviewNoteTimer` 变量，避免定时器互相覆盖。

## 执行日志

> Codex 每完成一步追加一行，格式: `YYYY-MM-DD HH:MM [账号X] 完成步骤 N: 说明`

- 2026-06-13 23:05 [codex-guominghu] 完成步骤 1-2: 扩展 `reviewNotes` 存储字段、补 `#/review` 路由与 `renderReview()` 主框架。
- 2026-06-13 23:05 [codex-guominghu] 完成步骤 3-6: 实现品种复盘行、52 周成交时序、零成交折叠区、年度行动完成率、供应商排行与复盘笔记 500ms 自动保存。
- 2026-06-13 23:05 [codex-guominghu] 完成验证: 三段内嵌 JSON 解析正常，页面脚本语法通过，Node 最小 DOM 冒烟通过 `renderReview()` 与复盘笔记 debounce。
