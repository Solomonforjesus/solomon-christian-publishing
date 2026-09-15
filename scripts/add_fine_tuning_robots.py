from pathlib import Path
p=Path('articles/fine-tuning-is-only-the-beginning/index.html')
s=p.read_text(encoding='utf-8')
if 'name="robots"' not in s:
    marker='  <meta name="description" content="Does the universe point toward purpose? Explore cosmic fine-tuning and the wider investigation of science, design, and faith in Fingerprint of Reality.">\n'
    addition=marker+'  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">\n'
    if marker not in s:
        raise SystemExit('description marker not found')
    p.write_text(s.replace(marker, addition, 1), encoding='utf-8')
print('Fine-tuning article explicitly indexable.')
