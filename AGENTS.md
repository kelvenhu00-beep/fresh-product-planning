# Codex 工作规范 (AGENTS.md)

> 这份文件是 Codex 在本项目的"宪法"。每次开工前必读。

## 你的角色
你是**执行者**。规划工作由 Claude Code 在 `.ai/tasks/` 中完成。
你的职责是：读任务卡 → 写代码 → 更新进度 → 提交。

## 标准工作流

### 1. 开工前
```bash
git pull --rebase
cat .ai/handoff.md   # 看当前要做什么任务
```

### 2. 读任务卡
打开 `.ai/tasks/TASK-XXX.md`，理解：
- 目标
- 技术约束
- 拆解步骤
- 验收标准

### 3. 干活时的铁律
- **每完成一个可验证的小步骤，立即 commit** (防 token 耗尽丢进度)
- **每次 commit 前更新任务卡的"执行日志"**
- 不动任务卡里明确说"不要改"的文件
- 遇到模糊需求，**写到 `.ai/questions.md` 让 Claude 回答**，不要自己脑补

### 4. Commit 规范
格式：
```
[TASK-XXX][codex-<账号标识>] 简短描述

- 详细说明改了什么
- 为什么这么改
```

示例：
```
[TASK-001][codex-A] 实现用户登录接口

- 新增 /api/auth/login
- 用 bcrypt 校验密码
- 加了单元测试
```

### 5. 完工
- 任务卡状态改为 ✅ 已完成
- 更新 `.ai/handoff.md` 指向下一个任务
- `git push`

## 断点续传协议 (换账号时必读)

如果你是新接手的账号 (前一个账号 token 用完了):
1. `git pull --rebase`
2. 读 `.ai/handoff.md` 找当前任务
3. 读对应任务卡的"执行日志"了解前任进度
4. 在日志末尾追加 `[账号X] 接手，当前理解：...` 再继续
5. **不要重做前任已完成的步骤**

## 禁忌
- ❌ 不要修改 `CLAUDE.md`、`AGENTS.md` (除非用户明确要求)
- ❌ 不要直接 push 到 main 分支 (用 feature 分支 + PR)
- ❌ 不要把 secrets / token / 密码写进代码
- ❌ 不要跳过 commit 直接干一大堆活
