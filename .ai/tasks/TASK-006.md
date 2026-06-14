# TASK-006: 数据导出（JSON 备份 + CSV 成交记录）

## 状态
- [ ] 待开始  [ ] 进行中  [x] 已完成  [ ] 已验收
- 创建者: claude
- 当前执行账号: codex-guominghu
- 创建时间: 2026-06-13

## 背景

系统目前所有数据存在 `state.json` + localStorage，用户无法：
1. 方便地备份数据（防止服务器文件丢失）
2. 把成交记录导出给财务/老板看（Excel 可读格式）
3. 在不同设备间手动迁移数据

## 目标

在 topbar 增加「导出」下拉菜单，提供两种导出：
1. **导出完整备份（JSON）**：下载 `procurement-backup-YYYYMMDD.json`，包含完整 state（variants/actions/suppliers/transactions/reviewNotes）
2. **导出成交记录（CSV）**：下载 `transactions-YYYY.csv`，当前年度成交记录，Excel 直接可读

## 技术约束

- 零依赖，用 `Blob` + `URL.createObjectURL` + `<a download>` 实现纯前端下载
- 不能动 `procurement_server.py`
- CSV 用 UTF-8 BOM（`﻿`）开头，保证 Excel 中文不乱码

## 拆解步骤

### 步骤 1：topbar 增加导出入口

在 topbar 右侧工具区加一个 `<button class="btn" onclick="toggleExportMenu()">导出 ▾</button>`，
点击展开一个小下拉菜单（绝对定位），包含两个选项：
- 「📦 备份数据（JSON）」→ `exportJSON()`
- 「📊 成交记录（CSV）」→ `exportCSV()`

点击选项后菜单收起。点击菜单外区域也收起（`document.onclick` 全局监听）。

### 步骤 2：实现 `exportJSON()`

```js
function exportJSON() {
  const blob = new Blob([JSON.stringify(state, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `procurement-backup-${new Date().toISOString().slice(0,10).replace(/-/g,'')}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
```

### 步骤 3：实现 `exportCSV()`

列顺序：`日期,变体名,供应商,规格,数量,单位,单价,金额,合同号,备注`

```js
function exportCSV() {
  const year = new Date().getFullYear();
  const txs = (state.transactions||[]).filter(t => t.year === year);
  const varMap = Object.fromEntries((state.variants||[]).map(v=>[v.id,v.name]));
  const rows = [['日期','变体名','供应商','规格','数量','单位','单价(元)','金额(元)','合同号','备注']];
  txs.sort((a,b)=>String(a.date).localeCompare(String(b.date))).forEach(t=>{
    rows.push([t.date, varMap[t.variantId]||t.variantId, t.supplierName||'',
               t.specGrade||'', t.quantity||0, t.unit||'', t.unitPrice||0,
               t.totalAmount||0, t.contractNumber||'', t.notes||'']);
  });
  const csv = '﻿' + rows.map(r=>r.map(cell=>
    `"${String(cell).replace(/"/g,'""')}"`).join(',')).join('\r\n');
  const blob = new Blob([csv], {type:'text/csv;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `transactions-${year}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
```

### 步骤 4：工作日志 + handoff 更新

## 验收标准

- [ ] topbar 出现「导出 ▾」按钮，点击展开两个选项
- [ ] 点击「备份数据」触发 JSON 文件下载，文件名含今日日期
- [ ] 点击「成交记录」触发 CSV 下载，Excel 打开中文不乱码
- [ ] CSV 列顺序正确，金额/数量为数字（非字符串）
- [ ] 下拉菜单点击外部区域可关闭
- [ ] 无 console error

## 潜在风险

1. **Excel BOM**：CSV 必须以 `﻿` 开头，否则 Excel 中文乱码
2. **引号转义**：CSV 单元格值含逗号或换行时需用双引号包裹并转义内部引号
3. **下拉菜单 z-index**：确保菜单层级高于其他元素（`z-index:100`）

## 执行日志

- [2026-06-14 10:44 | codex-guominghu] 完成 topbar「导出 ▾」下拉菜单，包含「备份数据（JSON）」和「成交记录（CSV）」两项；实现 `exportJSON()` / `exportCSV()`，JSON 文件名为 `procurement-backup-YYYYMMDD.json`，CSV 文件名为 `transactions-YYYY.csv`，CSV 使用 UTF-8 BOM、固定列顺序和双引号转义；点击外部区域可关闭菜单。已完成内嵌 JSON 校验、脚本语法校验、CSV BOM/列顺序/引号转义校验、浏览器菜单打开/关闭和当前页 console error 检查。应用内浏览器不支持真实 download 事件，因此下载触发后的文件保存由等价脚本与源码路径验证。
