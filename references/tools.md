# 标准库工具

`scripts/library.py`使用Python标准库，无外部服务或额外包。选择当前环境已配置的解释器，执行`<解释器> <skill路径>/scripts/library.py ...`。遵循用户指定的解释器路径，不为本工具新建环境。

## 命令

```text
library.py init --root <文献库>
library.py register --root <文献库> --record <单条题录.json>
library.py register --root <文献库> --record <单条题录.json> --pdf <已下载.pdf>
library.py register --root <文献库> --record <单条题录.json> --card
library.py index --root <文献库>
library.py check --root <文献库>
```

`init`创建四个目录和目录模板，保留已有文件。`register`按paper_id更新提供的字段；同DOI的不同编号提示使用已有编号。提供PDF时复制到规范位置并创建卡片；单独登记候选时只更新目录。`--card`可为未获取全文的条目先建卡。

`index`从目录与全部卡片重建导航、判断索引和方法索引。`check`检查文件、元数据和索引关系，不写入文献库。工具不联网核验题录，也不自动判断文章内容。

题录JSON最少包含`paper_id`、`title`；正式使用补齐authors、year、venue、doi、citation、discovery_source、source_url、category等已核字段。键名见目录模板，值均为字符串；作者多名可用分号分隔，标签也可用分号分隔。未核信息保留空值及相应状态。

已有文献库先映射原字段和编号。`pdf_path`、`card_path`为相对库根目录的路径；来源路径存original_path。分类不必成为编号的一部分。已有卡片导入时使用本技能的JSON frontmatter和reading-index块，保留正文及用户笔记。不要用register覆盖原有卡片。

## 编辑与同步

1. 精读后编辑卡片正文和reading-index块，更新frontmatter中的reading_stage。
2. 更新目录的ai_reading及其他实际变化字段；只有用户明确确认才更新human_reading。
3. 执行index生成两张索引与导航，再按结果检查本次变更。

卡片初次创建后，register不会改写已有卡片正文。新增PDF到已有待获取卡片时，登记后将卡片的“PDF原文”链接更新为目录中的规范路径。题名/DOI修订也同步卡片头部及参考文献。

涉及分类路径迁移、文件重命名时由当前代理根据实际库结构处理，随后同步目录、卡片链接和索引。本工具聚焦登记、建卡和索引生成，不自动搬动整个现有文献库。
