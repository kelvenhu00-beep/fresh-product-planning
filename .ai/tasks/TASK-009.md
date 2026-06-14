# TASK-009: Topbar 整理 + 全局 UX 小优化

## 状态
- [ ] 待开始  [x] 进行中  [ ] 已完成  [ ] 已验收
- 创建者: claude
- 当前执行账号: codex-guominghu
- 创建时间: 2026-06-14

## 背景

随着功能不断增加，topbar 现在有些混乱：
- 旧的「导入 JSON」「导出 JSON」「重置初始数据」按钮和新的「导出 ▾」下拉并存，功能重叠
- `#/review` 编辑模式下「编辑」按钮在编辑中仍然可见（TASK-002 review 记录的遗留问题）
- 侧边栏路由顺序可以更符合使用频率（仪表盘→水果管理→行动清单→节庆档→淡季→复盘→供应商）

## 目标

三处小优化，工作量轻，但对日常使用体验有明显提升：

### 优化 A：Topbar 按钮整理

**现状**：topbar 有「导出 ▾」「导入 JSON」「导出 JSON」「重置初始数据」四个按钮
**目标**：
- 把「导入 JSON」合并进「导出 ▾」下拉菜单（重命名为「⚙️ 数据管理 ▾」），添加第三项「📥 导入备份（JSON）」
- 删除独立的「导入 JSON」「导出 JSON」按钮（功能已在下拉菜单里）
- 保留「重置初始数据」按钮（危险操作，单独显示更醒目）

导入逻辑：触发 `<input type="file" accept=".json">` → 读取文件 → JSON.parse → 写入 state → persistNow() → render()，失败时 toast 错误信息

### 优化 B：Section H 编辑中隐藏「编辑」按钮

在 `renderDetailHeader(v, c)` 中，当 `editing=true` 时，工具栏的「编辑」按钮改为不渲染：
```js
// 把
`<button class="btn" onclick="startSectionEdit('header')">编辑</button>`
// 改为
`${editing ? '' : '<button class="btn" onclick="startSectionEdit(\'header\')">编辑</button>'}`
```

### 优化 C：侧边栏导航顺序调整

`ROUTES` 调整为更符合使用频率的顺序：
```js
const ROUTES = [
  ['#/dashboard', '仪表盘'],
  ['#/variants',  '水果管理'],
  ['#/actions',   '行动清单'],
  ['#/calendar',  '全年日历'],
  ['#/festivals', '节庆档'],
  ['#/offseason', '淡季'],
  ['#/review',    '复盘'],
  ['#/suppliers', '供应商'],
];
```

## 技术约束

- 零依赖，纯 JS/CSS
- 不改动任何页面的核心业务逻辑

## 验收标准

- [ ] **topbar 整洁**：只有「⚙️ 数据管理 ▾」下拉（含导出JSON/导出CSV/导入备份）+ 「重置初始数据」
- [ ] **导入备份**：选择 .json 文件后，state 正确更新并渲染，失败时有 toast 错误提示
- [ ] **Section H 编辑态无「编辑」按钮**：点击编辑后，编辑按钮消失，只剩保存/取消
- [ ] **侧边栏顺序**：仪表盘→水果管理→行动清单→全年日历→节庆档→淡季→复盘→供应商
- [ ] **无 console error**

## 潜在风险

1. **导入 JSON 覆盖校验**：导入前检查文件是否有 `schemaVersion` 字段，无则 toast「文件格式不正确，请使用系统导出的备份文件」
2. **隐藏编辑按钮时保存/取消位置**：确认编辑态下保存/取消按钮在 `.section-edit-form` 里，不依赖工具栏按钮

## 执行日志

- [2026-06-14 11:06 | codex-guominghu] 已完成优化 A/C：topbar 改为「⚙️ 数据管理 ▾」下拉，包含备份 JSON、成交记录 CSV、导入备份 JSON；移除 topbar 独立导入/导出按钮；侧边栏路由顺序已调整。执行优化 B 时发现当前 `index.html` 内不存在任务卡指定的 `renderDetailHeader` / `startSectionEdit('header')` / `saveSectionEdit` / `cancelSectionEdit` 精确结构，已写入 `.ai/questions.md` 等 Claude 确认，不自行脑补改动。
