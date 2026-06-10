# 数据 Schema 定义 v1

> 维护：Claude
> 用途：定义系统所有数据的字段约定。Codex 实现 `index.html` 时按此为准。

---

## 一、核心实体

```
Category  品类（如「苹果」）
  └─ Variant  变体（如「烟台栖霞富士」） ← 采购计划单元
       └─ Action  采购行动（自动按上市期生成 + 用户手工补充）
       └─ Supplier  供应商记录（v1.1 启用）
       └─ PriceHistory  历史价格（v1.1 启用）
```

v1 数据文件仅含 `categories[]` 与 `variants[]` 与 `actionTemplates[]`。

---

## 二、Category 字段

```ts
type Category = {
  id: string;            // kebab-case，如 "apple", "cherry"
  name: string;          // 中文名，如 "苹果"
  group: string;         // 大类，如 "仁果类"
  description?: string;
};
```

八个 group 取值：`仁果类 | 核果类 | 柑橘类 | 浆果类 | 热带亚热带 | 瓜类 | 时令特色 | 进口高端`。

---

## 三、Variant 字段（核心）

```ts
type Variant = {
  // 基础
  id: string;              // kebab-case，如 "apple-yantai-fuji"
  categoryId: string;      // 关联 Category.id
  name: string;            // 变体名，如 "烟台栖霞富士"
  variety: string;         // 品种，如 "红富士"
  originType: "国产" | "进口" | "混合";

  // 产地（行政归属）
  origin: {
    country?: string;      // 进口品填，国产留空
    province?: string;     // 国产品填
    city?: string;
    county?: string;
  };

  // 核心产区（最佳子产地 + 地理/气候/品种优势说明）
  // v1.1 新增字段。所有 104 个 v1 变体已填充
  coreOrigin?: {
    region: string;        // 具体到县/乡/镇/进口产区
    reason: string;        // 一两句话说明为何是核心产区（terroir）
  };

  // 上市周期（ISO 周编号 1-53）
  // 跨年时 end < start，渲染时按"年末折返"处理
  season: {
    earliestWeek: number;        // 最早上市
    peakStartWeek: number;       // 大量上市开始
    peakEndWeek: number;         // 大量上市结束
    lowPriceWeekStart: number;   // 价格洼地开始
    lowPriceWeekEnd: number;     // 价格洼地结束
    stableQualityWeekStart: number;
    stableQualityWeekEnd: number;
    endWeek: number;             // 下市
  };

  // 规格 / 等级
  specs: Array<{
    grade: string;         // 如 "80#", "L", "AA"
    description?: string;  // 如 "果径 80mm 以上"
  }>;

  // 价格（采购到货价 / 终端零售价，均为参考区间）
  procurementPrice: PriceRange;   // 采购价
  retailPrice: PriceRange;        // 零售参考价

  // 供应商类型
  supplierTypes: string[];        // 如 ["产地合作社","一级批发商","代办","进口贸易商"]

  // 常见风险
  risks: Array<{
    type: "天气" | "品质" | "价格" | "履约" | "物流" | "政策";
    description: string;
  }>;

  // 冷藏 / 储存
  coldStorage: {
    tempRange: string;          // 如 "0~4°C"
    humidity: string;           // 如 "85-90%"
    shelfLife: string;          // 如 "冷库 6-8 个月"
    notes?: string;
  };

  // 损耗参考（仓 / 卖场，0-1 小数）
  lossRate: {
    warehouse: number;
    retail: number;
  };

  // 毛利参考（0-1 小数）
  grossMargin: {
    low: number;
    typical: number;
    high: number;
  };

  // 谈判要点（要点 bullet）
  negotiationTips: string[];

  // 历史价格趋势（一句话简述 + 近 3 年关键事件）
  priceTrend: {
    summary: string;              // 一句话
    notableEvents?: string[];     // 可选
  };

  // 标签
  tags: string[];                 // 如 ["大宗","稳定","高出货","礼品装"]

  // 行动模板覆写（默认沿用全局 5 个标准动作，特殊变体可覆写）
  actionsOverride?: ActionTemplateRef[];

  // 备注（手工自由文本）
  notes?: string;

  // 元数据
  priority: 1 | 2 | 3;            // 1=高优先级（v1）, 2=中, 3=低
  dataConfidence: "高" | "中" | "低";  // AI 填写时的可信度自评
};

type PriceRange = {
  unit: string;        // "元/斤" | "元/件" | "元/箱(10kg)"
  low: number;         // 区间下限
  typical: number;     // 常见价
  high: number;        // 区间上限
};
```

### 价格单位约定

| 品类倾向 | 默认单位 |
|---|---|
| 散装大宗（苹果/梨/橙/西瓜） | `元/斤` |
| 礼品装（车厘子/草莓/葡萄高端品） | `元/斤` 或 `元/盒(500g)` |
| 进口大箱（榴莲/牛油果） | `元/件` 或 `元/箱` |
| 论个销售（椰青/榴莲果） | `元/个` |

填写时以「采购最常用的报价单位」为准，统一在 `unit` 字段标注。

---

## 四、ActionTemplate 字段

```ts
type ActionTemplate = {
  id: string;              // "watch-weather", "contact-origin", ...
  name: string;            // 中文动作名
  defaultOffsetWeeks: number;  // 距 peakStartWeek 的偏移（负数=之前）
  urgency: "高" | "中" | "低";
  description: string;     // 操作说明
  checklist?: string[];    // 操作清单
};
```

五个全局标准动作（详见 `数据_actionTemplates.json`）：

| 动作 | 默认偏移 | 紧急度 |
|---|---|---|
| 关注天气 | peak 前 8 周 | 中 |
| 联系产地 | peak 前 6 周 | 中 |
| 收集报价 | peak 前 4 周 | 高 |
| 产地走访 | peak 前 2 周 | 高 |
| 锁价 / 签合同 | peak 前 1 周 | 高 |

每个变体上线时，系统按 `peakStartWeek` + 模板自动生成 5 条 Action。用户可手工增删。

---

## 五、Action 字段（用户实例）

```ts
type Action = {
  id: string;
  variantId: string;
  templateId?: string;           // 来源模板（手工添加可为空）
  name: string;
  week: number;                  // ISO 周
  year: number;                  // 年份
  urgency: "高" | "中" | "低";
  status: "pending" | "done" | "skipped";
  notes?: string;
  createdAt: string;             // ISO timestamp
  completedAt?: string;
};
```

---

## 六、文件清单与加载顺序

```
1. 数据_categories.json     // Category[]
2. 数据_variants.json        // Variant[]
3. 数据_actionTemplates.json // ActionTemplate[]
```

`index.html` 内嵌或 `fetch()` 加载。用户在浏览器内的所有修改通过 localStorage 持久化（key = `procurement-plan-v1`），结构如下：

```ts
type Storage = {
  schemaVersion: 1;
  variants: Variant[];     // 用户修改后的覆盖版本（与初始 JSON 合并时以此为准）
  actions: Action[];       // 用户的行动实例
  suppliers?: Supplier[];  // v1.1
  priceHistory?: any[];    // v1.1
  meta: {
    lastSavedAt: string;
    user?: string;
  };
};
```

---

## 七、版本

- v1 schema 定稿：2026-06-09
- 后续若有破坏性改动，递增 `schemaVersion`，并提供迁移函数
