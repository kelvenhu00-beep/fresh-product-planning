# 项目当前状态总览

> 用途：新接手会话开工前必读。包含项目定位、文件清单、已上线功能、技术约束、协同时间线。
> 维护：Claude 在每个里程碑后更新。

最后更新：2026-06-10 by claude-A

---

## 一、产品定位

「全年水果采购计划系统」—— 给**连锁商超采购同事**日常使用的本地工具。

- 形态：**单 HTML 文件** + 一个 70 行 Python 服务器，macOS Safari/Chrome 双开即用
- 当前规模：46 品类 / 104 变体 / 自动生成 520 条采购行动 / 全部含核心产区
- 核心价值：从「采购凭经验」变成「全年节奏 + 关键节点 + 历史沉淀」

## 二、文件清单

### 业务源代码
| 路径 | 大小 | 说明 |
|---|---|---|
| `index.html` | 274KB | 主应用，单文件，内嵌 3 段 JSON + 全部 CSS/JS |
| `procurement_server.py` | 70 行 | 局域网同步 HTTP 服务器，提供 /state GET/POST + 静态文件 |

### 数据
| 路径 | 内容 |
|---|---|
| `数据_categories.json` | 46 个水果品类（8 大组 + 其他） |
| `数据_variants.json` | 104 个变体的完整字段（产区 × 品种），含 coreOrigin |
| `数据_actionTemplates.json` | 5 个标准采购动作模板（关注天气 / 联系产地 / 收集报价 / 产地走访 / 锁价签合同） |
| `数据_schema.md` | 字段定义规范（v1.1 含 coreOrigin） |

### 设计文档
| 路径 | 内容 |
|---|---|
| `重新规划方案_v1.md` | 总体方案 + 决策记录 |
| `设计_页面布局.md` | 5 个页面 wireframe + 配色 + 技术约束 |
| `设计_水果管理详情页_v2.md` | 详情页 v2 改造（展示态 + Section 编辑） |
| `初始数据_v1_品类变体清单.md` | 144 个变体目录（已填 104，priority 3 剩 ~46） |
| `协作_分工与协议.md` | 早期 Claude/Codex 协作规约（已被 CLAUDE.md/AGENTS.md/.ai/ 替代） |

### 历史
| 路径 | 内容 |
|---|---|
| `采购调研问卷_全年水果采购计划系统.md` | 项目早期阶段调研问卷（已被 v1 取代） |
| `采购调研填写系统_使用说明.md` | 调研问卷使用说明 |

### 协同日志
| 路径 | 内容 |
|---|---|
| `工作日志.md` | Claude × Codex 协同的全部 timeline（2026-06-09 至 06-10） |

## 三、已上线功能

### 1. 仪表盘 `#/dashboard`
- 红色「本周必做」聚合卡（按紧急度 + lock-price 优先 Top 5）
- 4 个 KPI 卡（本月即上市 / 本月待办 / 已逾期 / 锁价待签）
- 「本周采购雷达」4 个洞察卡（大量上市开始 / 价格洼地 / 品质稳定窗口 / 4 周内下市）
- 即将上市未来 4 周列表
- 本周行动建议列表
- 「已逾期」可折叠
- 底部「全年覆盖与风险分析」三栏（52 周品类密度 / 风险类型分布 / 国产-进口占比）

### 2. 全年日历 `#/calendar`
- 横向 52 周 × 100+ 行变体色带
- 自动定位当前周到视口中央
- 阶段着色：peak 实色 / pre/post 浅色 / 价格洼地金线 / 品质稳定绿线 / 当前周红色竖线
- 过滤：分组 / 国产-进口 / 优先级 / 标签 / 排序
- 跨年 peak (`peakStartWeek > peakEndWeek`) 正确渲染

### 3. 水果管理 `#/variants`
- 左侧品类树 + 搜索过滤 + 滚动位置保持
- 右侧详情页 6 Section：
  - **H 头部**：大标题 + 徽章组（国产/进口/优先级/可信度/标签）+ coreOrigin 显示
  - **A 上市周期**：迷你 52 周时间轴 + 5 行 emoji 摘要 + 跨年标注
  - **B 规格价格**：分级卡 + 动态 price-bar marker + 毛利率 gauge + 损耗
  - **C 风险与储存**：按类型上色风险卡 + 冷藏 4 属性块
  - **D 谈判要点 + 价格趋势 timeline**
  - **E 行动计划**：横向时间线 + 5 标准动作节点
  - **F 完整字段编辑**：折叠兜底面板（注：已被多个 Section 级编辑取代，待清理）
- 每 Section 独立编辑切换（保存 / 取消，cancel 完整回滚到 backup）
- 联网补全：详情头部「🔍 联网补全」(merge 模式)

### 4. 行动清单 `#/actions`
- 4 视图：本周 / 未来 4 周 / 全部 / 按水果
- 紧急度 / 类型 / 状态筛选
- 单条操作：完成 / 改期 / 跳过 / 恢复
- 批量完成本页待处理
- 自动行动按 peakYear 智能跨年（避免新增 peak 已过变体时出现一堆过期行动）

### 5. 节庆档 `#/festivals`
- 11 个销售档：元旦 / 春节 / 元宵 / 清明 / 五一 / 端午 / 中秋 / 国庆 / 双 11 / 双 12 / 圣诞
- 每档卡：窗口期 + 该窗口内进入 peak 的变体 + 建议提前 4 周锁货品类
- 当前周落入档窗口时红边框高亮
- **当前局限**：节庆周次写死（春节用 W4-W8 概数），未根据农历每年动态计算

### 6. 联网补全（输入驱动 4 步弹窗）
- 入口 1：水果管理顶部「🔍 联网补全新水果」(create 模式)
- 入口 2：变体详情头部「🔍 联网补全」(merge 模式)
- Step 1 输入产品名 / 品类 / 品种 / 产地 / 优先级
- Step 2 生成结构化 prompt → 复制
- Step 3 粘贴 LLM JSON
  - 容错：markdown 代码块 / 中文弯引号 / 同时粘贴 prompt+输出（自动截最后一个 JSON 对象）
- Step 4 diff 预览 + 应用（仅填空 / 全部覆盖；id/categoryId/name 锁定）

### 7. 多设备同步（局域网，2026-06-10 新增）
- `procurement_server.py` 提供 /state GET/POST，state.json 共享存储
- topbar `syncBadge` 显示同步状态（绿=已同步 / 金=离线）
- bootstrap LWW（比较 lastSavedAt ISO 时间戳）
- 每 10s pollSync 拉取远程改动（编辑态/弹窗态自动跳过避免误覆盖）
- 离线时 localStorage 兜底，恢复后下次保存自动重连

## 四、数据特征

- **品类层级**：8 大组 + 其他，每组 2-9 个品类
  - 仁果（2）/ 核果（5）/ 柑橘（6）/ 浆果（3）/ 热带亚热带（11，含杨桃/番石榴/椰枣等扩充）/ 瓜类（3）/ 时令特色（8，含黄皮/无花果/雪莲果）/ 进口高端（4）/ 其他（3，含木瓜/桑葚/红毛丹）
- **优先级分布**：priority 1 = 30 个核心商超必备 / priority 2 = 74 个次要 / priority 3 = 0（剩约 46 个未填）
- **核心产区**：全部 104 个含 `coreOrigin: { region, reason }`，具体到县/乡/镇级（如「烟台栖霞富士 → 栖霞市庙后乡 / 寺口镇 / 杨础镇 | 胶东低山丘陵海拔 200-400m，昼夜温差 12°C+，土壤富钾」）
- **价格、损耗、毛利、风险、储存**：均按中国连锁商超采购视角填写
- **进口品**：按国家组织 origin.country，国产按 province/city/county

## 五、技术约束

- **零依赖**：单 HTML 文件、纯 stdlib Python 服务器，无 npm 包 / 无 CDN
- **浏览器**：macOS Safari 17+ / Chrome 120+，桌面优先（≥1280px 流畅）
- **数据存储**：
  - 浏览器 localStorage（兜底，离线可用）
  - 服务器 state.json（多设备共享主存储）
- **同步模型**：LWW（last-write-wins）按 ISO 时间戳

## 六、协同时间线

| 日期 | 里程碑 |
|---|---|
| 06-09 上午 | Claude 完成产品规划、schema、初始 30 变体数据 |
| 06-09 下午 | Codex 实现 index.html v1（MVP 4 页） |
| 06-09 晚 | Codex 修复 3 处优化（scheduleSave 失焦 / loadState fallback / 日历宽度） |
| 06-09 晚 | Claude 扩充至 104 变体 + 46 品类（加 6 新品类） |
| 06-09 夜 | Codex 实现详情页 v2（展示态 + Section 编辑） |
| 06-10 凌晨 | Codex 实现 Phase A（本周必做 + 按水果聚合） |
| 06-10 上午 | Codex 实现 Phase B′（雷达 + 节庆档 + 全年分析 + coreOrigin UI） |
| 06-10 上午 | Claude 填充 104 变体的 coreOrigin 数据 + Codex 重新内嵌 |
| 06-10 中午 | Codex 实现联网补全（输入驱动 4 步）+ 容错解析 |
| 06-10 下午 | Codex 全量测试 + 修复模板残留 + 打部署包 |
| 06-10 下午 | Claude 实现局域网多设备同步（procurement_server.py + index.html 同步逻辑） |
| 06-10 晚 | 用户引入 AI 协同环境（CLAUDE.md / AGENTS.md / .ai/） |

## 七、当前已知技术债

1. **Section F 冗余** —— 详情页底部「完整字段编辑」折叠面板已被各 Section 独立编辑取代，但仍存在；展开会出现一堆开发态字段标签（如 `originType`、`categoryId`、「标签，逗号分隔」）
2. **Section H 编辑缺失** —— 头部 name / variety / origin / tags / priority / dataConfidence / notes / coreOrigin 等字段目前只能通过 Section F 编辑；删 Section F 前需补头部编辑
3. **节庆档静态** —— 春节/中秋/清明等农历节日周次写死，每年实际不同
4. **Priority 3 变体未填** —— 144 计划 - 104 已填 = ~46 个长尾品种未补
5. **复盘模块未做** —— `设计_页面布局.md` 中 v3 规划过，目前没入口

## 八、git 状态

- 远程：`https://github.com/kelvenhu00-beep/fresh-product-planning.git`
- 分支：`main` 跟踪 `origin/main`
- 历史：项目源码刚由 claude-A 沉淀入 git（在本 commit 之前仅有「初始化 AI 协同环境」一个 commit）

## 九、运行方式

```bash
# 启动服务器（局域网共享数据）
python3 procurement_server.py

# 访问
http://<host-ip>:8765/index.html

# 备份数据
cp state.json state.json.backup.$(date +%Y%m%d)
```

state.json 是真实用户数据所在（多设备共享）。备份它就备份了全部。
