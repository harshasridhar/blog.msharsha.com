#!/usr/bin/env python3
"""
Build the blog HTML from Markdown sources. Zero dependencies (stdlib only).

Each post is a Markdown file with YAML-ish frontmatter in /content/<slug>.md.
This generates posts/<slug>.html plus index.html, sitemap.xml and feed.xml.
Those outputs are git-ignored and rebuilt on deploy — the repo carries only
the Markdown sources, templates (in this script), style.css and components.js.

Local preview:   python3 scripts/build-site.py
"""
import os, re, glob, json, html
from datetime import datetime
from email.utils import formatdate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
POSTS = os.path.join(ROOT, "posts")
SITE = "https://blog.msharsha.com"


# ─────────────────────────── helpers ───────────────────────────
def esc(s):
    return html.escape(str(s), quote=False)

def attr(s):
    return html.escape(str(s), quote=True)

def fmt_date(iso):
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
        return f"{d.strftime('%B')} {d.day}, {d.year}"
    except ValueError:
        return iso

def rfc822(iso):
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
        return formatdate(d.timestamp())
    except ValueError:
        return iso


# ─────────────────────── frontmatter parser ────────────────────
def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    fm, body = text[3:end].strip("\n"), text[end + 4:].lstrip("\n")
    meta, key = {}, None
    for raw in fm.split("\n"):
        if not raw.strip():
            continue
        if re.match(r"^\s*-\s+", raw) and key:           # block list item
            meta.setdefault(key, [])
            meta[key].append(_unquote(re.sub(r"^\s*-\s+", "", raw).strip()))
            continue
        if ":" in raw:
            k, v = raw.split(":", 1)
            key, v = k.strip(), v.strip()
            if v == "":
                meta[key] = []
            elif v.startswith("[") and v.endswith("]"):
                meta[key] = [_unquote(x.strip()) for x in v[1:-1].split(",") if x.strip()]
            else:
                meta[key] = _unquote(v)
    return meta, body

def _unquote(s):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


# ───────────────────────── markdown render ─────────────────────
def _inline(text):
    codes = []
    text = re.sub(r"`([^`]+)`", lambda m: codes.append(esc(m.group(1))) or f"\x00{len(codes)-1}\x00", text)
    text = esc(text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">', text)
    def link(m):
        label, url = m.group(1), m.group(2)
        ext = " target=\"_blank\" rel=\"noopener\"" if url.startswith("http") else ""
        return f'<a href="{url}"{ext}>{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\*\w])\*([^*]+)\*(?![\*\w])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![_\w])_([^_]+)_(?![_\w])", r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)
    return text

def _is_block(line):
    return (line.startswith("```") or re.match(r"^#{2,3}\s", line)
            or re.match(r"^(\*\s*\*\s*\*|-{3,}|\*{3,})\s*$", line)
            or line.startswith(">") or re.match(r"^(\-|\*|\+)\s+", line)
            or re.match(r"^\d+\.\s+", line) or line.lstrip().startswith("<")
            or re.match(r"^!\[[^\]]*\]\([^)]+\)\s*$", line))

def render_markdown(md):
    lines = md.split("\n")
    out, i, n = [], 0, len(md.split("\n"))
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            i += 1
            code = []
            while i < n and not lines[i].startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + esc("\n".join(code)) + "</code></pre>")
        elif line.strip() == "":
            i += 1
        elif re.match(r"^(\*\s*\*\s*\*|-{3,}|\*{3,})\s*$", line):
            out.append('<div class="divider">* * *</div>'); i += 1
        elif re.match(r"^#{2,3}\s", line):
            m = re.match(r"^(#{2,3})\s+(.*)$", line)
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2).strip())}</h{lvl}>"); i += 1
        elif line.startswith(">"):
            q = []
            while i < n and lines[i].startswith(">"):
                q.append(lines[i].lstrip(">").strip()); i += 1
            out.append('<div class="pull-quote">' + _inline(" ".join(q)) + "</div>")
        elif re.match(r"^(\-|\*|\+)\s+", line) or re.match(r"^\d+\.\s+", line):
            ordered = bool(re.match(r"^\d+\.\s+", line))
            items = []
            while i < n and (re.match(r"^(\-|\*|\+)\s+", lines[i]) or re.match(r"^\d+\.\s+", lines[i])):
                items.append("<li>" + _inline(re.sub(r"^(\-|\*|\+|\d+\.)\s+", "", lines[i]).strip()) + "</li>")
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
        elif line.lstrip().startswith("<"):
            block = []
            while i < n and lines[i].strip() != "":
                block.append(lines[i]); i += 1
            out.append("\n".join(block))
        elif re.match(r"^!\[[^\]]*\]\([^)]+\)\s*$", line):
            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
            cap = f"<figcaption>{esc(m.group(1))}</figcaption>" if m.group(1) else ""
            out.append(f'<figure><img src="{m.group(2)}" alt="{attr(m.group(1))}" loading="lazy" decoding="async">{cap}</figure>'); i += 1
        else:
            para = []
            while i < n and lines[i].strip() != "" and not _is_block(lines[i]):
                para.append(lines[i].strip()); i += 1
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
    return "\n".join(out)


# ─────────────────────────── templates ─────────────────────────
def cover_picture(cover, alt, klass="cover-wrap", sizes="(max-width:760px) 92vw, 650px",
                  webp_widths=(480, 800, 1200), img_class="cover", extra=""):
    srcset = ", ".join(f"/images/{cover}-{w}.webp {w}w" for w in webp_widths)
    pcls = f' class="{klass}"' if klass else ""
    icls = f' class="{img_class}"' if img_class else ""
    return (f'<picture{pcls}>\n'
            f'    <source type="image/webp" srcset="{srcset}" sizes="{sizes}">\n'
            f'    <img{icls} src="/images/{cover}-1200.jpg" alt="{attr(alt)}" width="1200" height="630"{extra}>\n'
            f'  </picture>')

def render_post(meta, body_html, slug):
    tags = meta.get("tags", [])
    desc = meta.get("description") or meta.get("subtitle", "")
    cover = meta.get("cover")
    og_image = f"{SITE}/images/{cover}-1200.jpg" if cover else "https://msharsha.com/og-image.jpg"
    crosspost = ""
    if meta.get("medium"):
        crosspost = (f'\n  <p class="crosspost">A shorter version of this piece is on '
                     f'<a href="{attr(meta["medium"])}" target="_blank" rel="noopener">Medium</a>. '
                     f'This is the full article.</p>\n')
    cover_html = ("\n  " + cover_picture(cover, f'{meta.get("title","")} — cover') + "\n") if cover else "\n"
    refs = ""
    if meta.get("references"):
        items = []
        for r in meta["references"]:
            if "|" in r:
                t, u = [x.strip() for x in r.split("|", 1)]
                items.append(f'<li><a href="{attr(u)}" target="_blank" rel="noopener">{esc(t)}</a></li>')
            else:
                items.append(f"<li>{esc(r)}</li>")
        refs = ('\n  <div class="refs">\n    <h4>References</h4>\n    <ul>'
                + "".join(items) + "</ul>\n  </div>\n")
    repl = {
        "TITLE": esc(meta.get("title", "")),
        "DESCRIPTION": attr(desc),
        "SUBTITLE": esc(meta.get("subtitle", "")),
        "SLUG": slug,
        "OG_IMAGE": attr(og_image),
        "PUBLISHED": meta.get("publishDate", ""),
        "KEYWORDS": json.dumps(tags),
        "TAGS": "".join(f'<span class="tag">{esc(t)}</span>' for t in tags),
        "READTIME": esc(meta.get("readTime", "")),
        "DATE_DISPLAY": fmt_date(meta.get("publishDate", "")),
        "CROSSPOST": crosspost,
        "COVER": cover_html,
        "BODY": body_html,
        "REFS": refs,
    }
    out = POST_TEMPLATE
    for k, v in repl.items():
        out = out.replace("{{" + k + "}}", v)
    return out

def render_card(meta, slug):
    cover = meta.get("cover")
    category = meta.get("category") or (meta.get("tags") or ["Article"])[0]
    thumb = ""
    if cover:
        thumb = (f'\n        <div class="card-thumb">\n          '
                 + cover_picture(cover, f'{meta.get("title","")} — cover', klass="",
                                 sizes="(max-width:560px) 92vw, 220px", webp_widths=(480, 800),
                                 img_class="", extra=' loading="lazy" decoding="async"')
                 + "\n        </div>")
    repl = {
        "SLUG": slug,
        "THUMB": thumb,
        "CATEGORY": esc(category),
        "DATE_DISPLAY": fmt_date(meta.get("publishDate", "")),
        "TITLE": esc(meta.get("title", "")),
        "SUBTITLE": esc(meta.get("subtitle", "")),
        "READTIME": esc(meta.get("readTime", "")),
    }
    out = CARD_TEMPLATE
    for k, v in repl.items():
        out = out.replace("{{" + k + "}}", v)
    return out


# ─────────────────────────── main ──────────────────────────────
def main():
    os.makedirs(POSTS, exist_ok=True)
    srcs = sorted(p for p in glob.glob(os.path.join(CONTENT, "*.md"))
                  if not os.path.basename(p).startswith("_"))
    posts = []
    for src in srcs:
        slug = os.path.splitext(os.path.basename(src))[0]
        meta, body = parse_frontmatter(open(src, encoding="utf-8").read())
        html_out = render_post(meta, render_markdown(body), slug)
        open(os.path.join(POSTS, f"{slug}.html"), "w", encoding="utf-8").write(html_out)
        posts.append((meta, slug))
        print(f"  post  {slug}.html")

    posts.sort(key=lambda p: p[0].get("publishDate", ""), reverse=True)

    cards = "\n".join(render_card(m, s) for m, s in posts)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        INDEX_TEMPLATE.replace("{{CARDS}}", cards))
    print("  index.html")

    urls = [f"  <url>\n    <loc>{SITE}/</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>"]
    items = []
    for m, s in posts:
        urls.append(f"  <url>\n    <loc>{SITE}/posts/{s}.html</loc>\n    <lastmod>{m.get('publishDate','')}</lastmod>\n    <priority>0.8</priority>\n  </url>")
        items.append(f"    <item>\n      <title>{esc(m.get('title',''))}</title>\n      <link>{SITE}/posts/{s}.html</link>\n      <guid>{SITE}/posts/{s}.html</guid>\n      <pubDate>{rfc822(m.get('publishDate',''))}</pubDate>\n      <description>{esc(m.get('subtitle',''))}</description>\n    </item>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8").write(FEED_TEMPLATE.replace("{{ITEMS}}", "\n".join(items)))
    print("  sitemap.xml + feed.xml")
    print(f"Done — {len(posts)} post(s) built.")


POST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>(function(){try{var s=localStorage.getItem('theme');document.documentElement.setAttribute('data-theme',(s==='light'||s==='dark')?s:(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));}catch(e){}})();</script>
<title>{{TITLE}} — Harsha Sridhar</title>
<meta name="description" content="{{DESCRIPTION}}">
<link rel="canonical" href="https://blog.msharsha.com/posts/{{SLUG}}.html">
<meta name="author" content="Harsha Sridhar">
<meta name="copyright" content="© 2026 Harsha Sridhar. All rights reserved.">
<meta property="og:type" content="article">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESCRIPTION}}">
<meta property="og:url" content="https://blog.msharsha.com/posts/{{SLUG}}.html">
<meta property="og:image" content="{{OG_IMAGE}}">
<meta property="article:published_time" content="{{PUBLISHED}}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="https://msharsha.com/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="https://msharsha.com/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Harsha Sridhar — Blog" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/style.css">
<script src="/components.js"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-H9NJDMDFE2"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-H9NJDMDFE2');</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BlogPosting","headline":"{{TITLE}}","description":"{{DESCRIPTION}}","datePublished":"{{PUBLISHED}}","dateModified":"{{PUBLISHED}}","author":{"@type":"Person","name":"Harsha Sridhar","alternateName":"MS Harsha","url":"https://msharsha.com"},"publisher":{"@type":"Person","name":"Harsha Sridhar","url":"https://msharsha.com"},"mainEntityOfPage":"https://blog.msharsha.com/posts/{{SLUG}}.html","image":"{{OG_IMAGE}}","keywords":{{KEYWORDS}}}
</script>
</head>
<body>

<site-header></site-header>

<main class="page">

  <div class="tags">{{TAGS}}</div>

  <h1>{{TITLE}}</h1>
  <p class="subtitle">{{SUBTITLE}}</p>

  <div class="byline">
    <div class="avatar">HS</div>
    <div>
      <div class="who">Harsha Sridhar</div>
      <div class="meta">{{READTIME}} read · {{DATE_DISPLAY}}</div>
    </div>
  </div>
{{CROSSPOST}}{{COVER}}
  <article>
{{BODY}}
  </article>
{{REFS}}
  <div class="endcta">
    <div class="h">Enjoyed this?</div>
    <p>I write about distributed systems, agentic AI, and the strange places engineering and the cosmos overlap.</p>
    <div class="btns">
      <a class="btn primary" href="/">Read more articles</a>
      <a class="btn" href="https://www.linkedin.com/in/harsha-sridhar/" target="_blank" rel="noopener">Connect on LinkedIn</a>
    </div>
  </div>

</main>

<site-footer></site-footer>

</body>
</html>
"""

CARD_TEMPLATE = """    <li>
      <a class="card" href="/posts/{{SLUG}}.html">{{THUMB}}
        <div class="card-body">
          <div class="card-top">
            <span class="chip">{{CATEGORY}}</span>
            <span class="card-date">{{DATE_DISPLAY}}</span>
          </div>
          <h2 class="card-title">{{TITLE}}</h2>
          <p class="card-dek">{{SUBTITLE}}</p>
          <div class="card-foot">
            <span>{{READTIME}} read</span>
            <span class="arrow">Read →</span>
          </div>
        </div>
      </a>
    </li>"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>(function(){try{var s=localStorage.getItem('theme');document.documentElement.setAttribute('data-theme',(s==='light'||s==='dark')?s:(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'));}catch(e){}})();</script>
<title>Blog — Harsha Sridhar</title>
<meta name="description" content="Essays on distributed systems, agentic AI, and engineering by Harsha Sridhar (MS Harsha), Senior Software Engineer at Roku.">
<link rel="canonical" href="https://blog.msharsha.com/">
<meta name="author" content="Harsha Sridhar">
<meta name="copyright" content="© 2026 Harsha Sridhar. All rights reserved.">
<meta property="og:type" content="website">
<meta property="og:title" content="Blog — Harsha Sridhar">
<meta property="og:description" content="Essays on distributed systems, agentic AI, and engineering.">
<meta property="og:url" content="https://blog.msharsha.com/">
<meta property="og:image" content="https://msharsha.com/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="https://msharsha.com/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="https://msharsha.com/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Harsha Sridhar — Blog" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&display=swap"></noscript>
<link rel="stylesheet" href="/style.css">
<script src="/components.js"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-H9NJDMDFE2"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-H9NJDMDFE2');</script>
</head>
<body>

<site-header></site-header>

<main>

  <div class="masthead">
    <p class="eyebrow">Field notes</p>
    <h1>The universe is a distributed system with no documentation.</h1>
    <p>Essays on software, agentic AI, and the physics of scale — from an engineer who keeps asking why.</p>
  </div>

  <ul class="feed">

{{CARDS}}

  </ul>

</main>

<site-footer></site-footer>

</body>
</html>
"""

FEED_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Harsha Sridhar — Blog</title>
    <link>https://blog.msharsha.com/</link>
    <description>Essays on distributed systems, agentic AI, and engineering.</description>
    <language>en-us</language>
    <atom:link href="https://blog.msharsha.com/feed.xml" rel="self" type="application/rss+xml"/>
{{ITEMS}}
  </channel>
</rss>
"""


if __name__ == "__main__":
    main()
