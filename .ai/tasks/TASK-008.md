# TASK-008: 修复节庆档退步（恢复完整 11 节庆 + 动态周次）

## 状态
- [ ] 待开始  [ ] 进行中  [x] 已完成  [ ] 已验收
- 创建者: claude
- 当前执行账号: codex-guominghu
- 创建时间: 2026-06-13
- **优先级：P0，阻断，先于 TASK-006/007 执行**

## 问题描述（人工检测发现）

TASK-004 的实现引入了严重退步：

| 对比项 | 旧版（正确）| 新版（TASK-004 后，错误）|
|---|---|---|
| 节庆数量 | 11 个（元旦/春节/元宵/清明/五一/端午/中秋/国庆/双11/双12/圣诞）| ❌ 只剩 3 个（春节/端午/中秋）|
| 档内高峰变体 | ✅ 按节庆窗口筛选匹配变体，显示品类 | ❌ 改成标签匹配，逻辑错误 |
| 建议提前4周锁货 | ✅ 完整展示 | ❌ 整个区域消失 |
| 卡片布局 | ✅ 两段式（高峰变体 + 锁货建议）| ❌ 简化成单段，信息量大减 |

## 正确目标

保留 TASK-004 的成果（动态农历计算），同时恢复旧版的完整 UI 和功能。

## 需要恢复的代码

### 1. FESTIVALS 常量改为动态构建

用 TASK-004 的日期表替换旧的硬编码周次，其余结构不变：

```js
function buildFestivals(year) {
  const sf = SPRING_FESTIVAL[year] || SPRING_FESTIVAL[2026];
  const db = DRAGON_BOAT[year]    || DRAGON_BOAT[2026];
  const ma = MID_AUTUMN[year]     || MID_AUTUMN[2026];
  const sfW  = dateToIsoWeek(sf);
  const ltnW = dateToIsoWeek(addDays(sf, 14));   // 元宵 = 春节+14天
  const qmW  = dateToIsoWeek(qingmingDate(year)); // 清明公式
  const dbW  = dateToIsoWeek(db);
  const maW  = dateToIsoWeek(ma);

  return [
    {id:'newyear',   name:'元旦', emoji:'🎊', startWeek:1,                endWeek:1},
    {id:'spring',    name:'春节', emoji:'🧧', startWeek:normalizeWeek(sfW-1),  endWeek:normalizeWeek(sfW+2)},
    {id:'lantern',   name:'元宵', emoji:'🏮', startWeek:normalizeWeek(ltnW-1), endWeek:normalizeWeek(ltnW+1)},
    {id:'qingming',  name:'清明', emoji:'🌿', startWeek:normalizeWeek(qmW-1),  endWeek:normalizeWeek(qmW+1)},
    {id:'labor',     name:'五一', emoji:'🛠',  startWeek:17,               endWeek:19},
    {id:'dragon-boat',name:'端午',emoji:'🐲', startWeek:normalizeWeek(dbW-1),  endWeek:normalizeWeek(dbW+1)},
    {id:'mid-autumn',name:'中秋', emoji:'🥮', startWeek:normalizeWeek(maW-1),  endWeek:normalizeWeek(maW+1)},
    {id:'national',  name:'国庆', emoji:'🇨🇳',startWeek:40,               endWeek:41},
    {id:'double11',  name:'双11', emoji:'🛒', startWeek:44,               endWeek:45},
    {id:'double12',  name:'双12', emoji:'🛒', startWeek:49,               endWeek:50},
    {id:'christmas', name:'圣诞', emoji:'🎄', startWeek:52,               endWeek:52},
  ];
}
```

每次 `renderFestivals()` 调用时执行 `buildFestivals(nowInfo().year)` 获取当年节庆列表。

### 2. 恢复 renderFestivalCard（双区域布局）

完整恢复旧版实现：

```js
function renderFestivalCard(f, currentWeek) {
  const active = inRange(currentWeek, normalizeWeek(f.startWeek - 4), f.endWeek);
  const peakHits = state.variants.filter(v =>
    festivalWeeks(f).some(w => inRange(w, v.season.peakStartWeek, v.season.peakEndWeek))
  ).sort((a,b) => (a.priority||3)-(b.priority||3) || a.name.localeCompare(b.name));
  const lockHits = state.variants.filter(v =>
    inRange(v.season.peakStartWeek, normalizeWeek(f.startWeek - 4), f.startWeek)
  ).sort((a,b) => (a.priority||3)-(b.priority||3) || a.name.localeCompare(b.name));
  return `<section class="festival-card ${active?'active':''}">
    <h3>${f.emoji} ${esc(f.name)}</h3>
    <div class="meta">W${f.startWeek}${f.endWeek!==f.startWeek?'-W'+f.endWeek:''} · ${weekMonthText(f.startWeek,f.endWeek)}</div>
    <div class="festival-section">
      <h4>档内高峰变体 · ${peakHits.length}</h4>
      <div class="list">${peakHits.slice(0,8).map(v=>variantRow(v,esc(catOf(v).name))).join('')||empty('暂无')}</div>
    </div>
    <div class="festival-section">
      <h4>建议提前 4 周锁货 · ${lockHits.length}</h4>
      <div class="list">${lockHits.slice(0,8).map(v=>variantRow(v,`W${v.season.peakStartWeek} 大量上市`)).join('')||empty('暂无')}</div>
    </div>
  </section>`;
}
```

### 3. 恢复 renderFestivals（调用 buildFestivals）

```js
function renderFestivals() {
  const currentWeek = nowInfo().week;
  const festivals = buildFestivals(nowInfo().year);
  document.getElementById('view').innerHTML =
    `<div class="festival-grid">${festivals.map(f => renderFestivalCard(f, currentWeek)).join('')}</div>`;
}
```

### 4. 恢复 festivalWeeks 辅助函数

```js
function festivalWeeks(f) {
  const out = [];
  for (let w = f.startWeek; ; w = normalizeWeek(w+1)) {
    out.push(w);
    if (w === f.endWeek) break;
  }
  return out;
}
```

## 保留 TASK-004 的成果

- ✅ 保留 `SPRING_FESTIVAL` / `DRAGON_BOAT` / `MID_AUTUMN` 查表
- ✅ 保留 `dateToIsoWeek` / `addDays` / `qingmingDate` / `lunarDate` 辅助函数
- ✅ 保留 `normalizeWeek` 函数
- ❌ 删除新版错误的 `renderFestivals` 实现

## 验收标准

- [ ] 节庆档显示**完整 11 个节庆**（元旦/春节/元宵/清明/五一/端午/中秋/国庆/双11/双12/圣诞）
- [ ] 每个节庆卡片有**两个区域**：「档内高峰变体」+ 「建议提前 4 周锁货」
- [ ] 2026 年春节窗口 ≈ W7-W10（动态计算，非硬编码）
- [ ] 当前周（W24）落入端午窗口附近时卡片高亮
- [ ] 档内高峰变体数量合理（如春节显示 20+ 个，而非旧的 26 个，因为现在有 179 变体）
- [ ] 无 console error

## 潜在风险

1. `festivalWeeks(f)` 的 for 循环：当 startWeek > endWeek（跨年情况）时需要能跳出；
   现有 normalizeWeek 只会把 >52 的数绕回来，但若 startWeek=52,endWeek=1，循环会陷入死循环。
   **修复方式**：循环最多跑 52 次，超出则强制退出：
   ```js
   function festivalWeeks(f) {
     const out = [];
     let w = f.startWeek;
     for (let i = 0; i < 53; i++) {
       out.push(w);
       if (w === f.endWeek) break;
       w = normalizeWeek(w + 1);
     }
     return out;
   }
   ```

## 执行日志

- 2026-06-14 10:24 [codex-guominghu] 完成步骤 1-4: 将节庆档恢复为 `buildFestivals(year)` 动态构建 11 个节庆，恢复 `renderFestivalCard` 双区域布局、`festivalWeeks` 跨年安全循环和 `weekMonthText` 周次日期文案。
- 2026-06-14 10:24 [codex-guominghu] 验证: 内嵌 JSON 与脚本语法通过；2026 节庆数 11，春节窗口 W7-W10，端午窗口 W24-W26 且 W24 高亮；浏览器验证 11 张卡、22 个 `festival-section`、无当前页 console error。
