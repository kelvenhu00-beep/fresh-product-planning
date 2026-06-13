# TASK-005: 淡季看板 `#/offseason`

## 状态
- [ ] 待开始  [ ] 进行中  [x] 已完成  [ ] 已验收
- 创建者: claude
- 当前执行账号: codex-guominghu
- 创建时间: 2026-06-12

## 背景

节庆档 (`#/festivals`) 解决的是「什么时候该买入」，
淡季看板解决的是**「什么时候该收手」**——两者是采购节奏管理的一对。

采购员目前没有系统性的方式知道：
- 哪些品种旺季刚结束，应该开始减量
- 哪些品种再过 1-2 周就要下市，现在是最后补货窗口
- 哪些品种进入完全停采期（下市到下次上市之间）

这些信息分散在 104 个变体的 Section A 里，没有聚合视图。

## 目标

新增 `#/offseason` 淡季看板页，基于**当前 ISO 周**，自动聚合需要「收手」的品种，
分区显示采购行动建议，帮助采购员管理季末库存和停采节奏。

## 技术约束

- **框架/库**：零依赖单 HTML 文件，纯 JS/CSS
- **数据来源**：`state.variants`（season 字段）+ `state.transactions`（本季成交情况）
- **路由位置**：`ROUTES` 在 `#/festivals` 后、`#/review` 前插入 `['#/offseason', '淡季']`
- **不能动的文件**：`procurement_server.py`、多设备同步逻辑
- **仅展示，无需编辑**：本页全部只读，无编辑态

## 页面设计

### 顶部说明栏
```
当前第 W{n} 周 · {month}月{day}日
共 {N} 个品种需要关注
```

### 分区（从紧急到缓）

---

#### 🔴 区块一：最后补货窗口（下市倒计时 ≤ 2 周）

触发条件：`currentWeek >= endWeek - 2 && currentWeek <= endWeek`
（跨年品种需要处理 endWeek < earliestWeek 的情况）

卡片内容：
- 变体名 + 品类
- `距离下市还有 N 周`（红色倒计时）
- 本季成交笔数（从 state.transactions 取，若为 0 显示「本季无成交记录」橙色警告）
- 参考采购价（low ~ high）
- [去详情] 跳转 #/variants

**采购建议文案**：「本品种即将下市，如需补货请尽快下单，错过后需等待下年上市」

---

#### 🟡 区块二：旺季结束，建议减量（旺季结束后 1–4 周）

触发条件：`currentWeek > peakEndWeek && currentWeek <= peakEndWeek + 4`
（跨年 peak 同样需要特殊处理）

卡片内容：
- 变体名 + 品类
- `旺季已于 W{peakEndWeek} 结束，已过 {N} 周`（黄色）
- 本季成交总量 + 总额（有数据则展示，无则显示「暂无成交记录」）
- [去详情]

**采购建议文案**：「大量上市期已过，价格可能开始回升，建议减少订货量，消化现有库存」

---

#### ⬜ 区块三：采购空窗期（已下市，距下次上市 > 4 周）

触发条件：品种已下市（`currentWeek > endWeek`）且距下次 `earliestWeek` 超过 4 周
（此处以当年 earliestWeek 推算；若已过则用明年）

不展示单个卡片，改为**折叠列表**（默认收起）：
`⬜ 采购空窗品种（N 个）——当前完全停采，预计 W{earliestWeek} 前后重新上市`
展开后每品种一行：变体名 / 预计下次上市 W{n} / [详情]

---

#### 📊 底部：本周淡季品类分布（小图）

按 8 大品类分组，展示各品类内当前处于「减量」和「停采」状态的品种数量，
以小型 bar 或数字方块形式展示，让采购员快速看到哪个品类这周需要重点清仓。

---

### 空状态

若当前周所有品种都在旺季或未上市（通常不存在），显示：
`✅ 当前周无需特别关注的淡季品种`

## 拆解步骤

### 步骤 1：路由 + 基础框架

- [ ] `ROUTES` 插入 `['#/offseason', '淡季']`（在 #/festivals 后、#/review 前）
- [ ] `renderOffseason()` 函数框架 + `document.getElementById('view').innerHTML = ...` 渲染入口

### 步骤 2：核心分类函数

- [ ] `classifyVariants(variants, currentWeek)` → 返回 `{ lastWindow, postPeak, offSeason, inSeason }`
  - 注意跨年品种（`peakStartWeek > peakEndWeek` 或 `earliestWeek > endWeek`）的周次比较需要处理环形逻辑
  - 只处理 priority ≤ 2 的品种（priority 3 长尾暂不纳入）

跨年周次比较辅助函数（关键逻辑）：
```js
// 判断 week 是否在 [start, end] 窗口内（支持跨年，即 start > end 的情况）
function inSeasonRange(week, start, end) {
  if (start <= end) return week >= start && week <= end;
  return week >= start || week <= end; // 跨年
}
```

### 步骤 3：卡片渲染

- [ ] `renderOffseasonCard(v, zone, currentWeek, txList)` —— 通用卡片组件
  - zone: `'last' | 'postpeak' | 'offseason'`
  - txList: 该变体本年成交记录（从 state.transactions 筛选）
- [ ] 三个区块各自调用，拼 HTML

### 步骤 4：底部品类分布图

- [ ] 按 `categoryId` → `category.group` 聚合，统计各品类减量/停采数量
- [ ] 渲染为简单数字方块（不需要 canvas，纯 CSS）

### 步骤 5：工作日志 + handoff 更新

- [ ] `工作日志.md` 追加
- [ ] `.ai/handoff.md` 更新（TASK-004 和 TASK-005 并行，各自更新自己的状态）
- [ ] 本任务卡执行日志追加

## 验收标准

- [ ] **路由可用**：侧边栏出现「淡季」，点击进入无报错
- [ ] **三分区正确分类**：用当前 W24（2026-06）验证：苹果（旺季未到）/ 草莓（已下市）/ 荔枝（大量上市中）/ 西瓜（旺季）应分布在正确区块
- [ ] **跨年品种不崩溃**：苹果（`peakStartWeek > peakEndWeek`）/ 砂糖橘（冬季跨年）在淡季看板中判断正确
- [ ] **成交数据联动**：本季有成交记录的品种显示成交汇总；无成交显示橙色提醒
- [ ] **空窗折叠正常**：点击展开折叠区域，各品种的预计下次上市周次正确
- [ ] **[去详情] 跳转正确**：点击后进入 #/variants 并选中对应变体
- [ ] **其他页面不受影响**
- [ ] **无 console error**

## 潜在风险 / 踩坑提示

1. **跨年品种的环形周次比较**（最易出错）：
   - 苹果旺季 peakStartWeek=40, peakEndWeek=12（跨年），当前 W24 是淡季
   - 砂糖橘 endWeek=8（下一年 2 月才下市），当前 W24 也是停采期
   - 必须用 `inSeasonRange(week, start, end)` 处理，不能直接比大小

2. **「本季」成交范围**：本季 = 当年，用 `tx.year === currentYear` 过滤即可；
   对于跨年品种（如苹果 10 月起上市），本季可能跨两个自然年，
   v1 允许只看当年记录（简化），不做跨年季度计算。

3. **品种「下市后下次上市」计算**：
   - 若 `endWeek < currentWeek`，说明本年已下市；下次上市 = 明年 `earliestWeek`
   - 若 `earliestWeek <= currentWeek`（还没到旺季），下次上市 = 今年 `earliestWeek`
   - 空窗判定：`distanceToNextSeason(currentWeek, earliestWeek) > 4`

4. **priority 3 排除**：只处理 priority ≤ 2，否则 ~46 个未完善品种会产生噪音。

5. **与节庆档 CSS 共享**：淡季看板的卡片样式可复用节庆档的 `.festival-card` 或 `.card` 类，
   不需要大量新增 CSS，避免样式膨胀。

## 执行日志

> Codex 每完成一步追加一行，格式: `YYYY-MM-DD HH:MM [账号X] 完成步骤 N: 说明`

- 2026-06-13 23:32 [codex-guominghu] 完成步骤 1-4: 新增 `#/offseason` 淡季看板路由、跨年周次分类、最后补货/旺季后减量/采购空窗三分区、成交记录联动和品类分布图；只处理 priority <= 2 变体。
- 2026-06-13 23:32 [codex-guominghu] 完成步骤 5: 修复当前文件缺失的页面入口函数导致的启动错误，补齐只读版水果管理/供应商/节庆档入口及 `money`/`percent` 工具，确保淡季页详情跳转和全路由冒烟无 console error。
