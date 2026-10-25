from pathlib import Path
import json,re,html
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]; BOOK=ROOT/'reader/fingerprint'; BASE='https://solomonforjesus.org'; esc=html.escape
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,d):self.parts.append(d)
def plain(s):
 p=Text();p.feed(s);return ' '.join(' '.join(p.parts).split())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode('utf-8'))
book=json.loads((BOOK/'book.json').read_text(encoding='utf-8')); chapters=[s for s in book['sections'] if re.fullmatch(r'chapter-\d\d',s['id'])]
links=''.join(f'<li><a href="/reader/fingerprint/{s["id"]}/">{esc(s["label"])}</a></li>' for s in chapters)
for n,s in enumerate(chapters):
 body=(BOOK/s['file']).read_text(encoding='utf-8'); title=plain(re.search(r'<h1[^>]*>(.*?)</h1>',body,re.S).group(1)); url=f'{BASE}/reader/fingerprint/{s["id"]}/'
 desc=f'Read Chapter {n+1}, {title}, from Fingerprint of Reality by Gary Dearing. Full chapter, free online, with reading and sharing controls.'
 schema={'@context':'https://schema.org','@type':'Chapter','@id':url+'#chapter','name':title,'position':n+1,'url':url,'description':desc,'inLanguage':'en','isAccessibleForFree':True,'author':{'@type':'Person','name':'Gary Dearing'},'isPartOf':{'@type':'Book','@id':BASE+'/reader/fingerprint/#book','name':book['title'],'url':BASE+'/reader/fingerprint/'}}
 crumbs={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Solomon Christian Publishing','item':BASE+'/'},{'@type':'ListItem','position':2,'name':book['title'],'item':BASE+'/reader/fingerprint/'},{'@type':'ListItem','position':3,'name':s['label'],'item':url}]}
 prev=f'../{chapters[n-1]["id"]}/' if n else '../#prologue'; nxt=f'../{chapters[n+1]["id"]}/' if n+1<len(chapters) else '../#afterword'
 head=f'<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} — Chapter {n+1} | Fingerprint of Reality</title><meta name="description" content="{esc(desc)}"><meta name="author" content="Gary Dearing"><meta name="robots" content="index, follow"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{esc(title)} — Fingerprint of Reality"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}/fingerprint-front-hires.png"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script><script type="application/ld+json">{json.dumps(crumbs,ensure_ascii=False)}</script><link rel="stylesheet" href="../reader.css"><link rel="stylesheet" href="../chapters.css"><script defer src="../chapters.js"></script>'
 header='<a class="skip-link" href="#chapter-text">Skip to chapter</a><header class="topbar"><a class="home-link" href="/">← Publisher</a><div class="brand"><strong>Solomon Reader</strong><span>Fingerprint of Reality · Gary Dearing</span></div><div class="controls"><a class="home-link" href="../">Book cover</a><a class="home-link" href="#chapter-contents">Contents</a><button id="fontDown" aria-label="Decrease text size">A−</button><button id="fontUp" aria-label="Increase text size">A+</button><button id="themeBtn" aria-label="Toggle dark mode">◐</button><button id="shareChapter">Share chapter</button><span id="shareStatus" role="status"></span></div></header>'
 page=f'<!doctype html><html lang="en"><head>{head}</head><body>{header}<main class="reader-shell"><article id="chapter-text" class="book-content">{body}</article><nav class="chapter-nav" aria-label="Chapter navigation"><a href="{prev}">← Previous</a><a href="{nxt}">Next →</a></nav><nav id="chapter-contents" class="chapter-directory" aria-label="Book chapters"><h2>Chapters in Fingerprint of Reality</h2><ol>{links}</ol></nav></main><footer class="chapter-footer">By <a href="/authors/gary-dearing/">Gary Dearing</a> · Solomon Christian Publishing</footer></body></html>'
 write(BOOK/s['id']/'index.html',page)
index=BOOK/'index.html';text=index.read_text(encoding='utf-8');directory='<nav class="chapter-directory" aria-label="Browse book chapters"><h2>Read by chapter</h2><ol>'+links+'</ol></nav>'
text=re.sub(r'\s*<!-- CHAPTER DIRECTORY START -->.*?<!-- CHAPTER DIRECTORY END -->','',text,flags=re.S)
text=text.replace('</main>','</main>\n<!-- CHAPTER DIRECTORY START -->'+directory+'<!-- CHAPTER DIRECTORY END -->')
if 'href="chapters.css"' not in text:text=text.replace('</head>','<link rel="stylesheet" href="chapters.css">\n</head>')
write(index,text)
p=ROOT/'sitemap.xml';text=p.read_text(encoding='utf-8');text=re.sub(r'\s*<url><loc>https://solomonforjesus.org/reader/fingerprint/chapter-\d\d/</loc>.*?</url>','',text,flags=re.S)
text=text[:text.index('</urlset>')].rstrip()+'</urlset>';text=text.replace('</urlset>','\n'+''.join(f'<url><loc>{BASE}/reader/fingerprint/{s["id"]}/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n' for s in chapters)+'</urlset>');write(p,text)
print(f'Built {len(chapters)} complete chapter pages.')
