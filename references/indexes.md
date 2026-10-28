# 从卡片生成两张索引

## 信息来源

卡片正文维护分析；卡片末尾的`reading-index` JSON块保存对应的结构化检索条目。目录维护题录及文件路径。生成器据二者生成索引，索引不作为独立编辑源。修改分析时同步对应JSON条目，再重建索引；删除旧条目后重建即可消除旧入口。

## 研究判断索引

围绕当前研究中需要文献依据的判断设置稳定编号，如J001。同一编号使用同一判断文字，可对应多篇文献，支持、限定、相反发现、概念依据和启发分别记录。判断的待检验/已采用性质在项目上下文及卡片正文记录；索引中的论文数量不替代证据评价。

条目字段：`judgment_id`、`judgment`、`relation`、`evidence`、`conditions`、`locator`、`anchor`、`stage`。

## 方法用途索引

按任务组织，如“分析结果随时间变化”“比较群体差异”，再记录方法名及可借鉴步骤。相同任务可对应多种方法。字段：`task`、`method`、`reusable_step`、`data`、`conditions`、`locator`、`anchor`、`stage`。

## 精度与链接

- `stage`为abstract或full_text，表示该条目的证据来源。摘要线索在索引中明确显示。卡片整体阅读程度不能自动提升每条证据。
- 正文在相应分析段落前加显式锚点，如`<a id="evidence-e01"></a>`；条目`anchor`填`evidence-e01`。使用字母开头的ASCII字母、数字、下划线或连字符。
- `locator`填正文或补充材料的实际位置，`conditions`填具体条件或有依据的“通用概念定义”等说明。
- `unread`卡片的两组条目保持空数组。abstract卡片不添加full_text条目。
- 每次更新卡片重建两张索引和阅读导航。重建按编号排序；检查重复编号、冲突判断文字、缺失锚点及丢失链接。

JSON结构示例（字段说明，不作为文献事实）：

```json
{
  "judgments": [{
    "judgment_id": "J001", "judgment": "当前研究准备论证的具体判断",
    "relation": "限定", "evidence": "本文提供的具体发现",
    "conditions": "适用人群和情境", "locator": "正文 PDF p.3，图1",
    "anchor": "evidence-e01", "stage": "full_text"
  }],
  "methods": [{
    "task": "拟解决的研究任务", "method": "方法名称",
    "reusable_step": "可借鉴的具体步骤", "data": "需要的数据",
    "conditions": "迁移和验证条件", "locator": "方法章节 PDF p.5",
    "anchor": "method-m01", "stage": "full_text"
  }]
}
```

查询时返回相关条目、证据关系、适用条件及原卡片链接。用户需要判断证据整体是否充分时，读取关联卡片和必要原文，再使用ARS或综述技能综合。
