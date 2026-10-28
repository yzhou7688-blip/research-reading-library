"""Local literature library helpers. Python standard library only."""

import argparse
import csv
import io
import json
import os
import re
import shutil
from pathlib import Path
from string import Template
from urllib.parse import quote


PACKAGE = Path(__file__).resolve().parents[1]
CATALOG = Path('00_目录/文献目录.csv')
FIELDS = next(csv.reader((PACKAGE / 'assets/catalog.csv').read_text(encoding='utf-8').splitlines()))
STAGES = {'unread', 'abstract', 'partial', 'full_text'}
RELATIONS = {'支持', '限定', '相反发现', '概念依据', '启发'}


def read_catalog(root):
    path = root / CATALOG
    if not path.exists():
        return []
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError('目录字段与模板不一致，请先映射已有字段。')
        rows = list(reader)
    ids = [row['paper_id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('目录中存在重复paper_id。')
    return rows


def write_catalog(root, rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    (root / CATALOG).write_text(stream.getvalue(), encoding='utf-8-sig')


def local_path(root, value):
    """Catalog paths are relative, so the whole library can be relocated."""
    path = (root / value).resolve()
    if Path(value).is_absolute() or not path.is_relative_to(root):
        raise ValueError(f'库内路径必须相对于文献库：{value}')
    return path


def link(label, target, source, anchor=''):
    relative = Path(os.path.relpath(target, source.parent)).as_posix()
    url = quote(relative, safe='/.-_')
    return f'[{label}]({url}' + (f'#{anchor}' if anchor else '') + ')'


def cell(value):
    return str(value).replace('\r', ' ').replace('\n', ' ').replace('|', '&#124;')


def table(headers, rows):
    lines = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    lines += ['| ' + ' | '.join(cell(value) for value in row) + ' |' for row in rows]
    return '\n'.join(lines) + '\n'


def safe_name(value):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', value).strip(' .')[:75]
    if not name:
        raise ValueError('文件名或分类不能为空。')
    if re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', name, re.I):
        name = '_' + name
    return name


def canonical_doi(value):
    value = re.sub(r'^(https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value.strip(), flags=re.I)
    return value.casefold()


def init_library(root):
    for name in ['00_目录', '01_PDF原文', '02_精读卡', '03_补充材料']:
        (root / name).mkdir(parents=True, exist_ok=True)
    if not (root / CATALOG).exists():
        write_catalog(root, [])
    classification = root / '00_目录/分类说明.md'
    if not classification.exists():
        classification.write_text('# 文献分类\n\n根据当前研究问题维护主分类及辅助标签。\n', encoding='utf-8')


def register(root, record, pdf=None, create_card=False):
    unknown = set(record) - set(FIELDS)
    if unknown or any(not isinstance(v, str) for v in record.values()):
        raise ValueError(f'记录应为字符串字段，未知字段：{sorted(unknown)}')
    paper_id = record.get('paper_id', '')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', paper_id):
        raise ValueError('paper_id应以字母开头，仅含ASCII字母、数字、下划线或连字符。')
    rows = read_catalog(root)
    existing = next((row for row in rows if row['paper_id'] == paper_id), None)
    row = {key: '' for key in FIELDS}
    if existing:
        row.update(existing)
    row.update(record)
    if not row['title'].strip():
        raise ValueError('必须提供title。')
    doi = canonical_doi(row['doi'])
    if doi and not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
        raise ValueError('DOI格式不正确；未核验可留空并记录状态。')
    for other in rows:
        if doi and other['paper_id'] != paper_id and canonical_doi(other['doi']) == doi:
            raise ValueError(f'DOI已登记为{other["paper_id"]}，请使用已有编号。')
    if existing and existing['doi'] and doi != canonical_doi(existing['doi']):
        raise ValueError('已有编号对应另一DOI，请先核对文献身份。')
    for key in ['pdf_path', 'card_path']:
        if existing and key in record and record[key] != existing[key]:
            raise ValueError('路径迁移请先更新文件及链接，再在目录中同步。')
    category = row['category'] or '待归类'
    row['category'] = category
    stem = safe_name('_'.join([paper_id, row['authors'].split(';')[0] or '作者待核', row['year'] or '年份待核', row['title'][:40]]))
    if not row['human_reading']:
        row['human_reading'] = '未确认'
    if not row['ai_reading']:
        row['ai_reading'] = '未读'
    source = Path(pdf).resolve() if pdf else None
    if source and (not source.is_file() or source.suffix.casefold() != '.pdf'):
        raise ValueError('PDF来源文件不存在或扩展名不是.pdf。')
    if source:
        row['pdf_path'] = row['pdf_path'] or f'01_PDF原文/{safe_name(category)}/{stem}.pdf'
    if source or create_card:
        row['card_path'] = row['card_path'] or f'02_精读卡/{safe_name(category)}/{stem}_精读卡.md'
    pdf_target = local_path(root, row['pdf_path']) if row['pdf_path'] else None
    card_target = local_path(root, row['card_path']) if row['card_path'] else None
    if source and pdf_target.exists() and source != pdf_target:
        raise ValueError('规范PDF已存在；核对版本后再更新，不覆盖已有原文。')
    if row['card_path'] and not row['pdf_path'] and not (source or create_card):
        raise ValueError('卡片路径需要实际卡片或明确建卡请求。')
    if source:
        pdf_target.parent.mkdir(parents=True, exist_ok=True)
        if source != pdf_target:
            shutil.copy2(source, pdf_target)
        row['original_path'] = row['original_path'] or str(source)
        row['fulltext_status'] = '已获取'
    elif not row['fulltext_status']:
        row['fulltext_status'] = '待获取'
    if card_target:
        card_target.parent.mkdir(parents=True, exist_ok=True)
        if not card_target.exists():
            metadata = json.dumps({'paper_id': paper_id, 'title': row['title'], 'reading_stage': 'unread'}, ensure_ascii=False, indent=2)
            citation = row['citation'] or '题录待核验：' + row['title']
            content = Template((PACKAGE / 'assets/reading-card.md').read_text(encoding='utf-8')).substitute(
                metadata=metadata, paper_id=paper_id, title=row['title'], citation=citation,
                doi=('https://doi.org/' + doi) if doi else '待核验', category=category,
                pdf_link=link('PDF原文', pdf_target, card_target) if pdf_target else '待获取')
            card_target.write_text(content, encoding='utf-8')
        elif source:
            content = card_target.read_text(encoding='utf-8')
            pending_link = '- PDF原文：待获取'
            if pending_link in content:
                content = content.replace(pending_link, '- PDF原文：' + link('PDF原文', pdf_target, card_target), 1)
                card_target.write_text(content, encoding='utf-8')
        row['card_status'] = '已建档'
    if existing:
        rows[rows.index(existing)] = row
    else:
        rows.append(row)
    write_catalog(root, rows)
    return row


def read_card(path, paper_id):
    text = path.read_text(encoding='utf-8-sig')
    front = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not front:
        raise ValueError(f'{paper_id}卡片缺少JSON frontmatter。')
    metadata = json.loads(front.group(1))
    if metadata.get('paper_id') != paper_id or metadata.get('reading_stage') not in STAGES:
        raise ValueError(f'{paper_id}卡片编号或reading_stage不正确。')
    blocks = re.findall(r'^```reading-index\s*\n(.*?)^```\s*$', text, re.M | re.S)
    if len(blocks) != 1:
        raise ValueError(f'{paper_id}应包含一个reading-index块。')
    payload = json.loads(blocks[0])
    if set(payload) != {'judgments', 'methods'} or any(not isinstance(v, list) for v in payload.values()):
        raise ValueError(f'{paper_id}索引应包含judgments和methods数组。')
    anchors = re.findall(r'<a\s+id=[\'"]([A-Za-z][A-Za-z0-9_-]*)[\'"]\s*></a>', text)
    if len(anchors) != len(set(anchors)):
        raise ValueError(f'{paper_id}正文锚点重复。')
    used = set()
    for kind, entries in payload.items():
        fields = (['judgment_id', 'judgment', 'relation', 'evidence', 'conditions', 'locator', 'anchor', 'stage']
                  if kind == 'judgments' else ['task', 'method', 'reusable_step', 'data', 'conditions', 'locator', 'anchor', 'stage'])
        for entry in entries:
            if not isinstance(entry, dict) or any(not isinstance(entry.get(k), str) or not entry[k].strip() for k in fields):
                raise ValueError(f'{paper_id}的{kind}条目字段缺失。')
            if entry['anchor'] not in anchors:
                raise ValueError(f'{paper_id}索引缺少正文锚点：{entry["anchor"]}')
            key = (kind, entry['anchor'], entry.get('judgment_id', entry.get('task')))
            if key in used:
                raise ValueError(f'{paper_id}存在重复索引条目。')
            used.add(key)
            if entry['stage'] not in {'abstract', 'full_text'} or metadata['reading_stage'] == 'unread':
                raise ValueError(f'{paper_id}索引证据阶段与阅读状态不符。')
            if metadata['reading_stage'] == 'abstract' and entry['stage'] != 'abstract':
                raise ValueError(f'{paper_id}摘要卡不能生成全文证据。')
            if kind == 'judgments' and (entry['relation'] not in RELATIONS or not re.fullmatch(r'J\d+', entry['judgment_id'])):
                raise ValueError(f'{paper_id}判断编号或证据关系不正确。')
    return payload


def render(root, write=True):
    rows = read_catalog(root)
    navigation, judgments, methods = [], [], []
    judgment_names = {}
    for row in sorted(rows, key=lambda x: x['paper_id']):
        paper_id = row['paper_id']
        destinations = {}
        for key in ['pdf_path', 'card_path']:
            if row[key]:
                path = local_path(root, row[key])
                if not path.is_file():
                    raise ValueError(f'{paper_id}文件不存在：{row[key]}')
                destinations[key] = path
        nav_path = root / '00_目录/阅读导航.md'
        navigation.append([paper_id, row['title'], row['category'], row['fulltext_status'], row['ai_reading'], row['human_reading'],
                           link('PDF', destinations['pdf_path'], nav_path) if 'pdf_path' in destinations else '待获取',
                           link('卡片', destinations['card_path'], nav_path) if 'card_path' in destinations else '待建档'])
        if 'card_path' not in destinations:
            continue
        payload = read_card(destinations['card_path'], paper_id)
        for entry in payload['judgments']:
            jid = entry['judgment_id']
            if jid in judgment_names and judgment_names[jid] != entry['judgment']:
                raise ValueError(f'{jid}对应多个不同判断，请统一判断文字。')
            judgment_names[jid] = entry['judgment']
            ref = link(paper_id + ' 卡片', destinations['card_path'], root / '00_目录/研究判断与证据索引.md', entry['anchor'])
            judgments.append([jid, entry['judgment'], ref, entry['relation'], entry['evidence'], entry['conditions'], entry['locator'], '摘要线索' if entry['stage'] == 'abstract' else '全文依据'])
        for entry in payload['methods']:
            ref = link(paper_id + ' 卡片', destinations['card_path'], root / '00_目录/方法用途索引.md', entry['anchor'])
            methods.append([entry['task'], ref, entry['method'], entry['reusable_step'], entry['data'], entry['conditions'], entry['locator'], '摘要线索' if entry['stage'] == 'abstract' else '全文依据'])
    outputs = {
        '阅读导航.md': '# 阅读导航\n\n' + table(['编号', '题名', '主分类', '全文', 'AI阅读', '用户阅读', 'PDF', '卡片'], navigation),
        '研究判断与证据索引.md': '# 研究判断与证据索引\n\n从卡片生成；修改卡片后重建。\n\n' + table(['判断编号', '研究判断', '文献', '关系', '具体依据', '条件', '原文位置', '来源阶段'], sorted(judgments)),
        '方法用途索引.md': '# 方法用途索引\n\n从卡片生成；修改卡片后重建。\n\n' + table(['方法用途', '文献', '方法', '可借鉴步骤', '数据', '条件', '原文位置', '来源阶段'], sorted(methods)),
    }
    if write:
        for name, content in outputs.items():
            (root / '00_目录' / name).write_text(content, encoding='utf-8')
    return {'records': len(rows), 'judgments': len(judgments), 'methods': len(methods)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'register', 'index', 'check'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--record', type=Path, help='单条题录JSON；键名与catalog.csv相同，值均为字符串。')
    parser.add_argument('--pdf', type=Path)
    parser.add_argument('--card', action='store_true', help='无PDF时也创建待阅读卡片。')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == 'init':
            init_library(root)
        elif args.command == 'register':
            if not args.record:
                parser.error('register需要--record。')
            if not (root / CATALOG).exists():
                parser.error('先执行init。')
            record = json.loads(args.record.read_text(encoding='utf-8-sig'))
            if not isinstance(record, dict):
                raise ValueError('record必须是JSON对象。')
            register(root, record, args.pdf, args.card)
        if args.command == 'check':
            if not (root / CATALOG).exists():
                raise ValueError('文献目录不存在。')
            result = render(root, write=False)
        else:
            result = render(root)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
