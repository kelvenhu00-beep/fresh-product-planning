.PHONY: sync status handoff new-task help

help:
	@echo "AI 协同项目 - 快捷命令"
	@echo ""
	@echo "  make sync       - git pull --rebase && push"
	@echo "  make status     - 查看当前任务和进度"
	@echo "  make handoff    - 查看交接信息"
	@echo "  make new-task   - 创建新任务卡 (会提示输入编号)"
	@echo ""

sync:
	@git pull --rebase && git push

status:
	@echo "===== 当前交接状态 ====="
	@cat .ai/handoff.md 2>/dev/null || echo "(无 handoff.md)"
	@echo ""
	@echo "===== 未完成任务 ====="
	@grep -L "已完成" .ai/tasks/TASK-*.md 2>/dev/null | sed 's|.ai/tasks/||' || echo "(无)"
	@echo ""
	@echo "===== 最近 5 个 commit ====="
	@git log --oneline -5 2>/dev/null

handoff:
	@cat .ai/handoff.md

new-task:
	@read -p "任务编号 (如 001): " n; \
	read -p "任务标题: " t; \
	cp .ai/tasks/_TEMPLATE.md .ai/tasks/TASK-$$n.md; \
	sed -i.bak "s|TASK-XXX: <任务标题>|TASK-$$n: $$t|" .ai/tasks/TASK-$$n.md && rm .ai/tasks/TASK-$$n.md.bak; \
	echo "✅ 已创建 .ai/tasks/TASK-$$n.md，请编辑后 commit"
