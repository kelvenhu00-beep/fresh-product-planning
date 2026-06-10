# `.ai/` 目录说明

这是 Claude Code 和 Codex 协同工作的"共享大脑"。

## 文件用途

| 文件 | 谁写 | 谁读 | 作用 |
|---|---|---|---|
| `handoff.md` | 两者都写 | 两者都读 | 当前任务接力棒 |
| `tasks/TASK-XXX.md` | Claude 创建，Codex 更新日志 | 两者 | 任务卡 |
| `tasks/_TEMPLATE.md` | - | Claude | 新建任务时拷贝 |
| `questions.md` | Codex 提问 | Claude 回答 | 异步答疑 |
| `progress/` | Codex | Claude review | 长任务的详细日志 |
| `reviews/` | Claude | Codex 修改 | 代码 review 意见 |

## 工作流示意

```
用户 → Claude (规划) → 写任务卡 → git push
                                      ↓
用户 → Codex (执行)  ← git pull ← 读任务卡 → 写代码 → 更新日志 → git push
                                      ↓
用户 → Claude (review) ← git pull ← 看代码 → 写 review → git push
```

## 换账号 SOP

**Codex 账号 A token 耗尽时:**
```
> 请把当前进度更新到任务卡的执行日志，然后 commit & push。
> /exit

$ codex-use B    # 切换账号 (用你的 shell 函数)
$ codex          # 重启

> 我是新接手的账号B。请 git pull，然后读 .ai/handoff.md 续接工作。
```

**Claude 账号同理。**
