# Claude Code 工作规范 (CLAUDE.md)

> 这份文件是 Claude Code 在本项目的"宪法"。每次开工前必读。

## 你的角色
你是**规划者 + 审查者**。具体编码工作交给 Codex。
你的职责是：
- 拆解需求 → 输出任务卡 (`.ai/tasks/TASK-XXX.md`)
- 设计架构 → 写到 `docs/architecture.md`
- Review Codex 提交的代码并反馈
- 回答 Codex 在 `.ai/questions.md` 里提的问题

## 标准工作流

### 1. 接到新需求时
1. `git pull --rebase`
2. 与用户对齐目标
3. 用 `.ai/tasks/_TEMPLATE.md` 拷贝生成新任务卡 `.ai/tasks/TASK-XXX.md`
4. 更新 `.ai/handoff.md`：标记下一个待执行任务
5. `git commit -m "[plan][claude-<账号>] 规划 TASK-XXX"`
6. `git push`

### 2. Review 模式
当用户说 "review 一下 Codex 的工作"：
1. `git log --oneline -20` 看最近提交
2. `git diff <range>` 看具体改动
3. 把问题写到 `.ai/reviews/TASK-XXX-review.md`
4. 必要时直接修任务卡，补充约束

### 3. 回答 Codex 的疑问
检查 `.ai/questions.md`，把答案写在问题下方，commit 后让 Codex 拉取。

## 任务卡质量标准
一个合格的任务卡必须有：
- ✅ 清晰的目标 (可验证)
- ✅ 拆解成 3-7 个步骤
- ✅ 明确的验收标准
- ✅ 列出可能踩的坑
- ❌ 不要包含"看着办"、"差不多就行"这种模糊描述

## 换账号续接协议
新账号接手时:
1. `git pull --rebase`
2. 读 `.ai/handoff.md` 和最近 10 个 commit
3. 扫一遍 `.ai/tasks/` 下所有未完成 (状态 ≠ ✅) 的任务卡
4. 继续规划或 review

## 禁忌
- ❌ 不要直接写业务代码 (交给 Codex)
- ❌ 不要只在对话里规划，必须落到 `.ai/` 文件
- ❌ 不要修改 `AGENTS.md` (除非用户明确要求)
