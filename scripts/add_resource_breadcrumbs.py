from pathlib import Path
import json

resources = [
    (Path('reader/fingerprint/index.html'), 'Fingerprint of Reality', 'https://solomonforjesus.org/reader/fingerprint/'),
    (Path('authors/gary-dearing/index.html'), 'Gary Dearing', 'https://solomonforjesus.org/authors/gary-dearing/'),
    (Path('articles/fine-tuning-is-only-the-beginning/index.html'), 'Fine-Tuning Is Only the Beginning', 'https://solomonforjesus.org/articles/fine-tuning-is-only-the-beginning/'),
]
for path, name, url in resources:
    text = path.read_text(encoding='utf-8')
    if 'id="publishing-breadcrumb-schema"' in text:
        print(f'Skipping existing breadcrumb schema: {path}')
        continue
    data = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Solomon Christian Publishing', 'item': 'https://solomonforjesus.org/'},
            {'@type': 'ListItem', 'position': 2, 'name': name, 'item': url},
        ],
    }
    script = '<script id="publishing-breadcrumb-schema" type="application/ld+json">' + json.dumps(data, separators=(',', ':')) + '</script>\n'
    marker = '</head>'
    if marker not in text:
        raise SystemExit(f'No head closing tag: {path}')
    path.write_text(text.replace(marker, script + marker, 1), encoding='utf-8')
    print(f'Added breadcrumb schema: {path}')
