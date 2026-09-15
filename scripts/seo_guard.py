from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys

HOST = "solomonforjesus.org"
BASE = f"https://{HOST}"
SITEMAP_URL = BASE + "/sitemap.xml"
ORG_ID = BASE + "/#organization"
AUTHOR_ID = BASE + "/authors/gary-dearing/#person"
BOOK_ID = BASE + "/reader/fingerprint/#book"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title = []
        self.description = None
        self.robots = None
        self.canonical = None
        self.in_jsonld = False
        self.buffer = []
        self.jsonld = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attrs.get("name", "").lower()
            if name == "description":
                self.description = attrs.get("content", "").strip()
            elif name == "robots":
                self.robots = attrs.get("content", "").strip().lower()
        elif tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonical = attrs.get("href", "").strip()
        elif tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.buffer = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_jsonld:
            self.in_jsonld = False
            self.jsonld.append("".join(self.buffer).strip())
            self.buffer = []

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.in_jsonld:
            self.buffer.append(data)


def local_file(url):
    path = urlparse(url).path
    return Path("index.html") if path == "/" else Path(path.strip("/")) / "index.html"


def walk(value, types, ids):
    if isinstance(value, dict):
        t = value.get("@type")
        if isinstance(t, str):
            types.add(t)
        elif isinstance(t, list):
            types.update(x for x in t if isinstance(x, str))
        if isinstance(value.get("@id"), str):
            ids.add(value["@id"])
        for child in value.values():
            walk(child, types, ids)
    elif isinstance(value, list):
        for child in value:
            walk(child, types, ids)


def finish(errors):
    if errors:
        print("PUBLISHING SEO GUARD FAILED")
        for error in errors:
            print(" -", error)
        sys.exit(1)
    print("Publishing SEO guard passed: sitemap pages, canonicals, indexability, book/author/publisher entities, breadcrumbs, JSON-LD, and robots directives are consistent.")


def main():
    errors = []
    sitemap_path = Path("sitemap.xml")
    robots_path = Path("robots.txt")
    if not sitemap_path.exists() or not robots_path.exists():
        finish(["Missing sitemap.xml or robots.txt"])

    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", sitemap_path.read_text(encoding="utf-8"))
    if not urls:
        errors.append("Sitemap contains no URLs")
    if len(urls) != len(set(urls)):
        errors.append("Sitemap contains duplicate URLs")

    for url in urls:
        parsed_url = urlparse(url)
        if parsed_url.scheme != "https" or parsed_url.netloc != HOST:
            errors.append(f"Sitemap URL outside canonical host: {url}")
            continue
        file_path = local_file(url)
        if not file_path.exists():
            errors.append(f"Sitemap URL has no static page: {url} -> {file_path}")
            continue

        parser = PageParser()
        parser.feed(file_path.read_text(encoding="utf-8"))
        if not " ".join("".join(parser.title).split()):
            errors.append(f"Missing title: {file_path}")
        if not parser.description:
            errors.append(f"Missing description: {file_path}")
        if parser.canonical != url:
            errors.append(f"Canonical mismatch: {file_path} expected {url!r}, found {parser.canonical!r}")
        if parser.robots is None or "noindex" in parser.robots:
            errors.append(f"Public sitemap page is not explicitly indexable: {file_path}")

        parsed_json = []
        for block in parser.jsonld:
            if not block:
                continue
            try:
                parsed_json.append(json.loads(block))
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON-LD in {file_path}: {exc}")
        if not parsed_json:
            errors.append(f"Missing JSON-LD: {file_path}")
            continue

        types, ids = set(), set()
        for data in parsed_json:
            walk(data, types, ids)

        path = parsed_url.path
        if path == "/":
            if "Organization" not in types or "WebSite" not in types:
                errors.append("Publishing homepage must define Organization and WebSite")
            if ORG_ID not in ids:
                errors.append("Publishing homepage missing canonical organization @id")
        elif path == "/reader/fingerprint/":
            for required in ("Book", "BreadcrumbList"):
                if required not in types:
                    errors.append(f"Fingerprint reader missing {required} schema")
            for required_id in (BOOK_ID, AUTHOR_ID, ORG_ID):
                if required_id not in ids:
                    errors.append(f"Fingerprint reader missing entity reference {required_id}")
        elif path == "/authors/gary-dearing/":
            for required in ("ProfilePage", "Person", "BreadcrumbList"):
                if required not in types:
                    errors.append(f"Gary Dearing profile missing {required} schema")
            if AUTHOR_ID not in ids:
                errors.append("Gary Dearing profile missing canonical Person @id")
        elif path.startswith("/articles/"):
            for required in ("Article", "BreadcrumbList"):
                if required not in types:
                    errors.append(f"Publishing article missing {required} schema: {file_path}")

    robots = robots_path.read_text(encoding="utf-8")
    if "User-agent: OAI-SearchBot" not in robots:
        errors.append("robots.txt no longer explicitly allows OAI-SearchBot")
    if f"Sitemap: {SITEMAP_URL}" not in robots:
        errors.append("robots.txt sitemap declaration is missing or incorrect")

    finish(errors)


if __name__ == "__main__":
    main()
