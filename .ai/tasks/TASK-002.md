# TASK-002: Section H 补全编辑 + 删除 Section F 冗余面板

## 状态
- [ ] 待开始  [ ] 进行中  [ ] 已完成  [ ] 已验收
- 创建者: claude
- 当前执行账号: (Codex 接手时填写)
- 创建时间: 2026-06-12

## 背景

当前变体详情页底部有一个 `<details>` 折叠面板「完整字段编辑」（即 `renderFallbackSection`），
它是早期临时方案，用来编辑那些尚未分配专属 Section 的字段。
随着 TASK-001 完成后所有业务 Section 已独立实现，这个面板存在两个问题：

1. **Section F 冗余且暴露开发态字段**：
   - 里面的「基础」tab 直接显示字段名如 `originType`、`categoryId`、「标签，逗号分隔」等开发命名，
     用户看到会困惑。
   - 「上市期」tab 与 Section A 完全重叠；「价格规格/风险与储存/谈判要点/行动」tab
     与 Section B/C/D/E 完全重叠。功能全面冗余。

2. **Section H（详情头部）没有编辑入口**：
   - `name`（变体名）、`variety`（品种）、`originType`（国产/进口/混合）、
     `origin`（country/province/city/county）、`coreOrigin`（region/reason）、
     `tags`（标签）、`priority`（优先级）、`dataConfidence`（数据可信度）、`notes`（备注）
     这 9 类字段目前**只能**通过 Section F 的「基础」tab 修改。
   - 删掉 Section F 之前，必须先在 Section H 提供干净的编辑 UI。

## 目标

给 Section H 头部加上「编辑」模式，覆盖全部基础字段；
然后从 `renderVariantDetail` 中移除 `renderFallbackSection` 调用。

## 技术约束

- **框架/库**：零依赖单 HTML 文件，纯 JS/CSS（与现状一致）
- **不能动的文件**：`procurement_server.py`、`.ai/`、多设备同步逻辑
- **编辑模式**：复用现有 `startSectionEdit / saveSectionEdit / cancelSectionEdit` 机制，key 用 `'header'`
- **`field()` 辅助函数**：现有 `field(path, label, value, type, options, wide)` 已满足需求，直接复用
- **`bindVariantInputs`**：已处理任意 `data-path` 写入，header Section 的字段改动自动走现有通道
- **性能/兼容**：macOS Safari 17+ / Chrome 120+，桌面优先

## 当前代码位置

- `renderVariantDetail(v)` 末尾调用 `renderFallbackSection(v)` ← 要删这行
- `renderDetailHeader(v, c)` ← 要在这里加编辑按钮和编辑态 HTML
- `renderFallbackSection(v)` + `renderVariantTab(v)` ← 待删（先确认没有其他调用者再删）
- `ui.variantTab` 状态 ← 待确认是否还被其他地方使用，若仅被 Section F 引用则一并清理

## 拆解步骤

### 步骤 1：给 Section H 加编辑态

修改 `renderDetailHeader(v, c)`：

**展示态**（当前）：
- 面包屑 + 大标题 + 副标题 + coreOrigin + chip-row + linkedSuppliers + 工具按钮（联网补全/复制/删除）

**展示态新增**：工具按钮区右侧加一个 `<button class="btn" onclick="startSectionEdit('header')">编辑</button>`

**编辑态**（新增，当 `ui.editingSection === 'header'` 时渲染）：
返回包含以下 form-grid 的区域，使用现有 `field()` 辅助：

| 字段路径 | 中文标签 | 类型 | 备注 |
|---|---|---|---|
| `name` | 变体名 | text | |
| `variety` | 品种 | text | |
| `originType` | 产地类型 | select | 国产/进口/混合 |
| `origin.country` | 国家 | text | 进口品填写 |
| `origin.province` | 省份 | text | 国产品填写 |
| `origin.city` | 城市 | text | |
| `origin.county` | 县区 | text | |
| `coreOrigin.region` | 核心产区 | text | |
| `coreOrigin.reason` | 核心产区说明 | textarea | wide |
| `tags` | 标签（逗号分隔） | text | 存为 string，save 时 split(',').map(trim).filter(Boolean) 写回数组；`bindVariantInputs` 中对 `path==='tags'` 特殊处理 |
| `priority` | 优先级 | select | 1/2/3 |
| `dataConfidence` | 数据可信度 | select | 高/中/低 |
| `notes` | 备注 | textarea | wide |

编辑态底部：`保存` / `取消` 按钮（复用现有 `saveSectionEdit()` / `cancelSectionEdit()`）

> **注意**：`tags` 字段在 `bindVariantInputs` 里需要特殊处理，因为 `field()` 把它渲染为逗号字符串，
> 但 variant 里存的是 `string[]`。需要在 `path === 'tags'` 时执行
> `v.tags = val.split(',').map(s=>s.trim()).filter(Boolean)` 而不是直接赋值。
> 检查现有 `bindVariantInputs` 是否已有此处理（查 TASK-001 之前 Codex 是否加过），
> 若无则补充。

### 步骤 2：删除 Section F

1. 从 `renderVariantDetail(v)` 末尾删除 `${renderFallbackSection(v)}`
2. 确认 `renderFallbackSection` 和 `renderVariantTab` 没有被其他地方调用（grep 确认）
3. 若确认无引用，删除 `renderFallbackSection` 和 `renderVariantTab` 两个函数定义
4. 检查 `ui.variantTab` 状态：若只有这两个函数使用，从 `ui` 初始化对象里删掉 `variantTab`

### 步骤 3：工作日志 + handoff 更新

- `工作日志.md` 追加 `[2026-06-12 HH:MM | Codex] TASK-002 交付：...`
- `.ai/handoff.md` 更新状态
- 本任务卡执行日志追加每步完成时间

## 验收标准

- [ ] **Section H 有编辑入口**：详情头部右上角出现「编辑」按钮，点击后进入编辑态
- [ ] **全字段可编辑**：name / variety / originType / origin (4 子字段) / coreOrigin (2 子字段) / tags / priority / dataConfidence / notes 均有对应 input/select/textarea
- [ ] **tags 正确处理**：逗号分隔字符串 ↔ string[] 双向转换，保存后 chip-row 正确更新
- [ ] **保存 / 取消均正常**：保存后头部立即刷新显示新值；取消后回到保存前的值（backup 恢复）
- [ ] **Section F 已消失**：详情页底部不再出现「完整字段编辑」折叠面板
- [ ] **其他 Section 不受影响**：A/B/C/D/E/Transaction Section 的展示与编辑功能正常
- [ ] **无 console error**

## 潜在风险 / 踩坑提示

1. **`tags` path 处理**：`field('tags', ...)` 输出的 input value 是逗号字符串（如 `"大宗,稳定"`），
   而 `bindVariantInputs` 通用逻辑直接 `v[path] = val` 会把 string 赋给数组字段。
   务必在 `path === 'tags'` 时 split 处理，否则 chip-row 会渲染出「大宗,稳定」这种单标签。

2. **`coreOrigin` 初始化**：部分旧变体可能没有 `coreOrigin` 字段，`field('coreOrigin.region', ...)` 
   取值时 `v.coreOrigin?.region||''` 已有 `?.` 防护，但 `bindVariantInputs` 写入时要确保
   `if(!v.coreOrigin) v.coreOrigin = {}` 再赋值，否则 `v.coreOrigin.region = val` 会 TypeError。
   检查现有 `bindVariantInputs` 是否已做嵌套路径安全处理（若有则直接复用）。

3. **`name` 修改后左侧树未刷新**：保存 Section H 编辑（修改了 `name`）时，
   `saveSectionEdit` 调用 `renderVariants()`，左侧品类树会全量重渲染，
   这应该已经能刷新变体名。但要验证一下树中变体名是否同步更新。

4. **删 Section F 后 `ui.variantTab` 废弃**：如果其他地方有 `ui.variantTab` 的读取
   （如 `renderVariants` 条件分支），需一并清理，避免孤儿状态。

5. **`renderVariantTab` 调用 `renderPriceEditor / renderRiskEditor / renderNegotiationEditor`**：
   这三个函数本身不删，它们仍被对应 Section 的编辑态使用，只需删掉 `renderVariantTab`
   作为调用入口即可。

## 执行日志

> Codex 每完成一步追加一行，格式: `YYYY-MM-DD HH:MM [账号X] 完成步骤 N: 说明`

-
