# 当前任务交接

> 这是 AI 之间的"接力棒"。每次切换账号 / 切换 AI 前，必须更新这里。

## 正在进行
- **TASK-004** 节庆档动态化（农历）：✅ 已验收通过（2026-06-13）

## ⬇️ Codex 下一步：按顺序执行

### 第 1 步（立即开始）：重新内嵌变体 JSON
`数据_variants.json` 已由 Claude 扩充（104 → 179 个变体，覆盖销售清单全品类）。
**Codex 需把更新后的 `数据_variants.json` 重新内嵌到 `index.html` 的 `<script id="data-variants">` 标签内。**
操作与之前内嵌 coreOrigin 数据完全相同：读取 JSON 文件，替换 script 标签内容，保持其他代码不变。
完成后验证：179 个变体全部包含 `name` 和 `coreOrigin.region` 字段，三段内嵌 JSON 解析正常，无 console error。
commit 格式：`[data-embed][codex-X] 重新内嵌 179 变体到 index.html`

### 第 2 步：实现 TASK-003 季后复盘 `#/review`
见 `.ai/tasks/TASK-003.md`，实现完成后 commit 并更新任务卡执行日志。

### 第 3 步：实现 TASK-005 淡季看板 `#/offseason`
见 `.ai/tasks/TASK-005.md`，实现完成后 commit 并更新任务卡执行日志。

## 队列中
1. TASK-006：销售数据 CSV 导入（用户整理好数据后规划）
2. (后续) 价格年度趋势图 / 供应商绩效分析（方向D，待 TASK-003 积累数据后）
3. (后续) 直连 Claude API（方向B，待用户确认）

## 已完成 (最近 5 个)
- TASK-002 Section H 编辑补全 + Section F 清理（2026-06-12 Codex 完成，Claude 验收通过）
- TASK-001 实际成交价格录入 + 供应商档案（2026-06-11 Codex 完成，2026-06-12 Claude 验收通过）

---
最后更新: 2026-06-12 by Codex（TASK-004 已完成，等待 Claude 验收）
