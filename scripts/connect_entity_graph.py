from pathlib import Path
import json, re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

org = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': 'https://solomonforjesus.org/#organization',
    'name': 'Solomon Christian Publishing',
    'url': 'https://solomonforjesus.org/',
    'logo': 'https://solomonforjesus.org/BannerPublishingForJesus.png',
    'description': 'Solomon Christian Publishing produces thoughtful Christian books and serious written work in service to truth, wisdom, and the Gospel of Jesus Christ.',
    'parentOrganization': {'@id': 'https://www.solomonforjesus.com/#organization'}
}
website = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': 'https://solomonforjesus.org/#website',
    'url': 'https://solomonforjesus.org/',
    'name': 'Solomon Christian Publishing',
    'description': 'Thoughtful Christian books and serious written work in service to truth, wisdom, and the Gospel of Jesus Christ.',
    'publisher': {'@id': 'https://solomonforjesus.org/#organization'}
}

first_pattern = r'<script type="application/ld\+json">\s*\{.*?"publishingPrinciples".*?\}\s*</script>'
first_replacement = '<script type="application/ld+json">\n  ' + json.dumps(org, separators=(',', ':')) + '\n  </script>'
s2, count1 = re.subn(first_pattern, first_replacement, s, count=1, flags=re.S)
if count1 != 1:
    raise SystemExit('Could not locate Publishing Organization schema block')

second_pattern = r'<script id="publishing-website-schema" type="application/ld\+json">.*?</script>'
second_replacement = '<script id="publishing-website-schema" type="application/ld+json">' + json.dumps(website, separators=(',', ':')) + '</script>'
s3, count2 = re.subn(second_pattern, second_replacement, s2, count=1, flags=re.S)
if count2 != 1:
    raise SystemExit('Could not locate Publishing WebSite schema block')

p.write_text(s3, encoding='utf-8')
print('Connected Solomon Christian Publishing to Solomon For Jesus parent entity.')
