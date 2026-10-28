# research-reading-library

**文献目录与阅读卡管理 skill**，用于 Codex 中的文献整理与研究阅读。连接候选文献、实际下载的 PDF、摘要归档、独立精读卡与证据索引，方便持续补充文献，并在研究论证和方法设计时调用阅读成果。

## 功能

| 阶段 | 工作内容 | 主要产物 |
|---|---|---|
| 寻找文献 | 汇入检索结果、用户自行发现的文献和引文追踪结果 | 可更新的候选目录与全文获取入口 |
| 同步下载 | 核对实际文件、题录身份、重复条目及关联版本 | 实际持有情况与规范 PDF 入口 |
| 摘要归档 | 提取对象、问题、方法和阅读用途 | 主分类、辅助标签、归类理由和阅读顺序 |
| 卡片建档 | 分配稳定编号，建立 PDF 与卡片对应关系 | 独立存放的精读卡框架 |
| 逐篇精读 | 重建研究逻辑，记录证据定位和研究关联 | 四部分精读卡 |
| 调用成果 | 按研究判断或方法用途查找材料 | 两张可重建的索引表 |

研究主题、项目路径、分类及筛选条件由当前任务决定。候选目录持续接收用户补充，并根据实际下载和阅读情况更新。整理建档与全文精读可以分别执行。

## 安装到 Codex

在 Codex 中调用内置的 `skill-installer`，发送：

```text
请使用 skill-installer，从 https://github.com/yzhou7688-blip/research-reading-library
安装仓库根目录中的 skill，名称为 research-reading-library。
```

也可以将仓库内容复制到 Codex 的 skills 目录，形成以下结构：

```text
<CODEX_HOME>/skills/research-reading-library/SKILL.md
```

`CODEX_HOME` 未设置时，默认位置为用户目录下的 `.codex`。保留 `agents/`、`assets/`、`references/` 和 `scripts/` 的相对关系。安装完成后，在下一轮对话中调用技能。

## 快速开始

在 Codex 中说明文献库位置、当前任务，以及需要参考的研究问题或分类文件。

**寻找候选文献：**

```text
使用 $research-reading-library，结合 ARS，围绕我提供的研究问题建立候选文献目录。
保留我自行补充文献的入口，提供完整题录、推荐理由和全文获取途径。
```

**整理下载文件并建卡：**

```text
使用 $research-reading-library，整理指定文件夹中的 PDF。
读取我提供的分类说明，核对题录、按摘要归档，并在独立文件夹建立精读卡。
本次做到建档阶段。
```

**精读指定文献：**

```text
使用 $research-reading-library，精读目录中的 L001。
完成四部分卡片，解释关键概念，说明问题与方法的对应关系，并附原文位置。
```

**查找证据或方法：**

```text
使用 $research-reading-library，查找哪些已读文献能够支持、限定或修正以下研究判断：……
```

```text
使用 $research-reading-library，根据我现有的数据和分析任务，查找可借鉴的方法步骤及迁移条件。
```

## 四部分精读卡

1. **研究背景与问题形成**：已有研究做了什么、关注什么，作者提出何种不足，本文补充什么；复杂概念结合简短示例解释。
2. **研究问题、数据与方法**：连接问题、数据、变量、方法及其选择依据，解释方法如何产生答案，记录比较设计、识别条件与验证方式。
3. **结论、贡献与后续问题**：对应问题整理发现，说明贡献、作者自述局限、阅读分析发现的问题，以及作者和阅读者分别提出的后续方向。
4. **与当前研究的关联**：提取可引用论述、可借鉴方法环节、所需数据与适用条件，记录促使当前研究重新考虑的问题。

关键发现和方法附 PDF 页码、章节、图表或补充材料位置。作者报告、阅读分析、解释性示例及待检验想法分别标明。

## 文献库结构

```text
文献库/
├─ 00_目录/
│  ├─ 文献目录.csv
│  ├─ 阅读导航.md
│  ├─ 分类说明.md
│  ├─ 研究判断与证据索引.md
│  └─ 方法用途索引.md
├─ 01_PDF原文/
│  └─ <主分类>/<编号_作者_年份_短标题>.pdf
├─ 02_精读卡/
│  └─ <主分类>/<编号_作者_年份_短标题>_精读卡.md
└─ 03_补充材料/
   └─ <文献编号>/
```

每篇使用稳定编号。主分类用于存放，辅助标签用于跨主题查找。PDF 与卡片共享文件名主体，并通过目录及卡片链接对应。已有编号优先沿用。

题录核验、全文获取、摘要归档、卡片建档、AI 阅读及用户阅读分别记录；用户亲自阅读的状态根据其确认更新。

## 两张索引

- **研究判断与证据索引**：按判断编号汇总相关文献，显示支持、限定、相反发现、概念依据或启发，以及具体依据和适用条件。
- **方法用途索引**：按拟解决的任务查找方法，显示可借鉴步骤、所需数据和迁移条件。

卡片正文保存详细分析；末尾的 `reading-index` JSON 块保存检索条目。更新正文及对应条目后，运行 `index` 重建索引和阅读导航。索引链接到卡片的具体段落，卡片提供原文定位。摘要条目显示为“摘要线索”。格式见 [索引规则](references/indexes.md)。

## 本地工具

[`scripts/library.py`](scripts/library.py) 使用 Python 标准库，由 Codex 按当前环境已配置的解释器执行，无需安装第三方包。以下 `<Python解释器>` 和路径替换为实际值；用户指定了解释器时沿用该路径。

```text
<Python解释器> scripts/library.py init --root <文献库路径>
<Python解释器> scripts/library.py register --root <文献库路径> --record <题录.json>
<Python解释器> scripts/library.py register --root <文献库路径> --record <题录.json> --pdf <已下载.pdf>
<Python解释器> scripts/library.py register --root <文献库路径> --record <题录.json> --card
<Python解释器> scripts/library.py index --root <文献库路径>
<Python解释器> scripts/library.py check --root <文献库路径>
```

| 命令 | 行为 |
|---|---|
| `init` | 创建文献库目录、空目录表及分类说明 |
| `register` | 按编号登记或更新题录；提供 PDF 时复制到规范路径并建立卡片 |
| `register --card` | 为尚未获取全文的条目先建立卡片 |
| `index` | 根据目录和卡片生成导航及两张索引 |
| `check` | 检查文件、卡片元数据和索引关系，保持文献库内容不变 |

题录 JSON 最少包含字符串类型的 `paper_id` 和 `title`。以下仅为字段示意，使用时替换为实际文献信息：

```json
{
  "paper_id": "L001",
  "title": "文献完整题名",
  "authors": "作者姓名",
  "year": "发表年份",
  "category": "主分类名称",
  "discovery_source": "用户补充或实际检索来源"
}
```

完整字段见 [目录模板](assets/catalog.csv)。工具负责登记、文件对应及索引生成；题录核验、摘要理解和精读分析由 Codex 结合可访问的来源完成。已有卡片的正文与用户笔记在更新登记时保留。更新流程见 [工具用法](references/tools.md)。

## 与其他技能协作

| 技能 | 协作职责 |
|---|---|
| ARS / `academic-research-suite` | 按需检索、核验题录、分析单篇研究和讨论方法 |
| `literature-review-skills` | 综述问题细化、主题组织、方法比较和矛盾综合 |
| PDF 技能 | 读取 PDF 正文、图表及补充材料 |
| `research-reading-library` | 维护目录、归档、卡片、阅读状态和检索索引 |

各阶段按任务调用相应能力。检索兼顾 OA 与非 OA，筛选条件遵循用户要求。文献内容以实际读取范围为依据，阅读启发在卡片中积累，随后结合研究讨论形成采用决定。

## 仓库文件

| 文件或目录 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 技能入口与阶段选择 |
| [agents/openai.yaml](agents/openai.yaml) | Codex 展示信息与调用策略 |
| [assets/](assets/) | 目录及精读卡模板 |
| [references/catalog-and-filing.md](references/catalog-and-filing.md) | 目录、下载同步与摘要归档 |
| [references/close-reading.md](references/close-reading.md) | 四部分精读要求 |
| [references/indexes.md](references/indexes.md) | 判断和方法用途索引格式 |
| [references/tools.md](references/tools.md) | 工具命令与更新方式 |
| [scripts/library.py](scripts/library.py) | 本地登记、建卡、索引和检查工具 |
