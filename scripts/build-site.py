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

# Outbound link attribution. Every external URL in a post body or References
# block gets these UTM params appended so referral traffic is identifiable on
# the destination side. Hosts in UTM_SKIP_HOSTS are left untouched (own sites,
# infra endpoints that don't accept query params). The per-post campaign is
# the slug; source/medium are constant.
UTM_PARAMS = {"utm_source": "blog.msharsha.com", "utm_medium": "referral"}
UTM_SKIP_HOSTS = {"msharsha.com", "blog.msharsha.com", "fonts.googleapis.com",
                  "fonts.gstatic.com", "www.googletagmanager.com"}


# ─────────────────────────── helpers ───────────────────────────
def esc(s):
    return html.escape(str(s), quote=False)

def attr(s):
    return html.escape(str(s), quote=True)

def utm(url, campaign):
    """Append UTM params to an external http(s) URL. No-op for in-site, mailto,
    fragment-only, or already-tagged URLs."""
    if not url.startswith(("http://", "https://")):
        return url
    # Split off the fragment so params land before #, not after.
    base, _, frag = url.partition("#")
    if "utm_source=" in base:
        return url
    # Crude host parse — avoids importing urllib for one operation.
    host = base.split("/", 3)[2].lower()
    if host in UTM_SKIP_HOSTS:
        return url
    sep = "&" if "?" in base else "?"
    params = "&".join(f"{k}={v}" for k, v in UTM_PARAMS.items())
    if campaign:
        params += f"&utm_campaign={campaign}"
    tagged = f"{base}{sep}{params}"
    return f"{tagged}#{frag}" if frag else tagged

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
# Per-post slug used to stamp utm_campaign on outbound links from inside the
# markdown renderer. render_post sets this before rendering each post.
_CURRENT_SLUG = ""

def _inline(text):
    codes = []
    text = re.sub(r"`([^`]+)`", lambda m: codes.append(esc(m.group(1))) or f"\x00{len(codes)-1}\x00", text)
    text = esc(text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">', text)
    def link(m):
        label, url = m.group(1), m.group(2)
        ext = " target=\"_blank\" rel=\"noopener\"" if url.startswith("http") else ""
        url = utm(url, _CURRENT_SLUG)
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
            or line.lstrip().startswith("|")
            or re.match(r"^!\[[^\]]*\]\([^)]+\)\s*$", line))

def _is_sep_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and any(cells) and all(re.match(r"^:?-{1,}:?$", c) for c in cells if c)

def _table_align(cell):
    c = cell.strip()
    if c.startswith(":") and c.endswith(":"):
        return "center"
    if c.endswith(":"):
        return "right"
    if c.startswith(":"):
        return "left"
    return ""

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
        elif "|" in line and i + 1 < n and _is_sep_row(lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            aligns = [_table_align(c) for c in lines[i + 1].strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            al = lambda j: f' style="text-align:{aligns[j]}"' if j < len(aligns) and aligns[j] else ""
            thead = "<thead><tr>" + "".join(f"<th{al(j)}>{_inline(h)}</th>" for j, h in enumerate(header)) + "</tr></thead>"
            tbody = "".join("<tr>" + "".join(f"<td{al(j)}>{_inline(c)}</td>" for j, c in enumerate(r)) + "</tr>" for r in rows)
            out.append(f'<div class="table-wrap"><table>{thead}<tbody>{tbody}</tbody></table></div>')
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

def render_post(meta, body_html, slug, firebase_config_json="null", recaptcha_script=""):
    tags = meta.get("tags", [])
    section = meta.get("category") or (tags[0] if tags else "")
    desc = meta.get("description") or meta.get("subtitle", "")
    cover = meta.get("cover")
    og_image = f"{SITE}/images/{cover}-1200.jpg" if cover else "https://msharsha.com/og-image.jpg"
    # OpenGraph article extensions — LinkedIn / Facebook / Discord scrapers read
    # these to build richer preview cards. Bing/DuckDuckGo also use them.
    og_article_meta = []
    if section:
        og_article_meta.append(f'<meta property="article:section" content="{attr(section)}">')
    for t in tags:
        og_article_meta.append(f'<meta property="article:tag" content="{attr(t)}">')
    og_article_html = "\n".join(og_article_meta)
    keywords_meta = f'<meta name="keywords" content="{attr(", ".join(tags))}">' if tags else ""
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
                items.append(f'<li><a href="{attr(utm(u, slug))}" target="_blank" rel="noopener">{esc(t)}</a></li>')
            else:
                items.append(f"<li>{esc(r)}</li>")
        refs = ('\n  <div class="refs">\n    <h4>References</h4>\n    <ul>'
                + "".join(items) + "</ul>\n  </div>\n")
    # Conditionally include comments section (can be disabled per-post via frontmatter)
    comments_html = ""
    if meta.get("comments", True):  # Default to True; set to False to disable
        comments_html = f'<post-comments post="{slug}"></post-comments>'

    repl = {
        "TITLE": esc(meta.get("title", "")),
        "DESCRIPTION": attr(desc),
        "SUBTITLE": esc(meta.get("subtitle", "")),
        "SLUG": slug,
        "OG_IMAGE": attr(og_image),
        "PUBLISHED": meta.get("publishDate", ""),
        "KEYWORDS": json.dumps(tags),
        "SECTION": attr(section),
        "OG_ARTICLE_META": og_article_html,
        "KEYWORDS_META": keywords_meta,
        "TAGS": "".join(f'<span class="tag">{esc(t)}</span>' for t in tags),
        "READTIME": esc(meta.get("readTime", "")),
        "DATE_DISPLAY": fmt_date(meta.get("publishDate", "")),
        "CROSSPOST": crosspost,
        "COVER": cover_html,
        "BODY": body_html,
        "REFS": refs,
        "COMMENTS": comments_html,
        "FIREBASE_CONFIG": firebase_config_json,
        "RECAPTCHA_SCRIPT": recaptcha_script,
    }
    out = POST_TEMPLATE
    for k, v in repl.items():
        out = out.replace("{{" + k + "}}", v)
    return out

def render_card(meta, slug):
    cover = meta.get("cover")
    category = meta.get("category") or (meta.get("tags") or ["Article"])[0]
    # Show up to 3 secondary tags per card — feeds both readers scanning the
    # index and crawlers building topic clusters. Skip the category, which is
    # already shown as the chip above.
    tags = [t for t in (meta.get("tags") or []) if t and t != category][:3]
    tags_html = ""
    if tags:
        tags_html = ('\n          <div class="card-tags">'
                     + "".join(f'<span class="card-tag">{esc(t)}</span>' for t in tags)
                     + "</div>")
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
        "CARDTAGS": tags_html,
    }
    out = CARD_TEMPLATE
    for k, v in repl.items():
        out = out.replace("{{" + k + "}}", v)
    return out


# ─────────────────────────── main ──────────────────────────────
def load_recaptcha_key():
    """Read the reCAPTCHA v3 site key from RECAPTCHA_SITE_KEY env var (set by
    GitHub Actions from a repository secret), falling back to the file
    .recaptcha-site-key for local development.

    Returns the rendered <script> tag to inline, or an empty string if the key
    is unavailable (reCAPTCHA silently disabled, everything else still works).
    """
    key = os.environ.get("RECAPTCHA_SITE_KEY", "").strip()
    if not key:
        key_file = os.path.join(ROOT, ".recaptcha-site-key")
        if os.path.exists(key_file):
            key = open(key_file).read().strip()
    if not key:
        print("  WARNING: RECAPTCHA_SITE_KEY not set — reCAPTCHA will be "
              "disabled in the built site. Set the secret in GitHub repository "
              "settings or create .recaptcha-site-key locally.")
        return ""
    return (f'<script src="https://www.google.com/recaptcha/api.js'
            f'?render={key}" async defer></script>')


def load_firebase_config():
    """Read firebase-config.json from the repo root.

    At build time the file is either:
    - Written by the GitHub Actions step that injects secrets, OR
    - Present locally (gitignored) for local development.

    Returns the raw JSON string so it can be inlined directly into the HTML
    instead of being fetched at runtime (one fewer network round-trip).
    If the file is missing the build succeeds but Firebase will not initialise;
    a clear warning is printed so the developer notices immediately.
    """
    config_path = os.path.join(ROOT, "firebase-config.json")
    if not os.path.exists(config_path):
        print("  WARNING: firebase-config.json not found — Firebase features "
              "will be disabled in the built site. "
              "Add FIREBASE_CONFIG_JSON to your GitHub repository secrets.")
        return "null"
    with open(config_path, encoding="utf-8") as f:
        raw = f.read().strip()
    # Validate it's parseable JSON before inlining it into a <script> tag.
    json.loads(raw)
    return raw


def main():
    os.makedirs(POSTS, exist_ok=True)
    firebase_config_json = load_firebase_config()
    recaptcha_script = load_recaptcha_key()
    srcs = sorted(p for p in glob.glob(os.path.join(CONTENT, "*.md"))
                  if not os.path.basename(p).startswith("_"))
    posts = []
    global _CURRENT_SLUG
    for src in srcs:
        slug = os.path.splitext(os.path.basename(src))[0]
        meta, body = parse_frontmatter(open(src, encoding="utf-8").read())
        _CURRENT_SLUG = slug
        html_out = render_post(meta, render_markdown(body), slug, firebase_config_json, recaptcha_script)
        open(os.path.join(POSTS, f"{slug}.html"), "w", encoding="utf-8").write(html_out)
        posts.append((meta, slug))
        print(f"  post  {slug}.html")

    posts.sort(key=lambda p: p[0].get("publishDate", ""), reverse=True)

    cards = "\n".join(render_card(m, s) for m, s in posts)
    # Index-page JSON-LD: a Blog with an embedded ItemList so Google can index
    # the feed structure and understand this URL as the root of a series of
    # articles.
    all_tags = []
    seen = set()
    for m, _s in posts:
        for t in (m.get("tags") or []):
            if t and t not in seen:
                seen.add(t); all_tags.append(t)
    index_ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "@id": f"{SITE}/",
        "url": f"{SITE}/",
        "name": "Harsha Sridhar — Blog",
        "description": "Essays on distributed systems, agentic AI, and engineering by Harsha Sridhar (MS Harsha), Senior Software Engineer at Roku.",
        "author": {"@type": "Person", "name": "Harsha Sridhar",
                   "alternateName": "MS Harsha", "url": "https://msharsha.com"},
        "publisher": {"@type": "Person", "name": "Harsha Sridhar",
                      "url": "https://msharsha.com"},
        "keywords": all_tags,
        "blogPost": [
            {"@type": "BlogPosting",
             "headline": m.get("title", ""),
             "url": f"{SITE}/posts/{s}.html",
             "datePublished": m.get("publishDate", ""),
             "description": m.get("subtitle", ""),
             "keywords": m.get("tags") or []}
            for m, s in posts
        ],
    }
    itemlist_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "url": f"{SITE}/posts/{s}.html", "name": m.get("title", "")}
            for i, (m, s) in enumerate(posts)
        ],
    }
    index_ld_html = (
        f'<script type="application/ld+json">\n{json.dumps(index_ld, ensure_ascii=False)}\n</script>\n'
        f'<script type="application/ld+json">\n{json.dumps(itemlist_ld, ensure_ascii=False)}\n</script>'
    )
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        INDEX_TEMPLATE.replace("{{CARDS}}", cards).replace("{{INDEX_LD}}", index_ld_html))
    print("  index.html")

    urls = [f"  <url>\n    <loc>{SITE}/</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>"]
    items = []
    for m, s in posts:
        urls.append(f"  <url>\n    <loc>{SITE}/posts/{s}.html</loc>\n    <lastmod>{m.get('publishDate','')}</lastmod>\n    <priority>0.8</priority>\n  </url>")
        # Categorize each RSS item by its tags so readers/aggregators can filter.
        # Category is added first so the primary bucket sorts to the top.
        cats = []
        primary = m.get("category")
        if primary:
            cats.append(primary)
        for t in (m.get("tags") or []):
            if t and t != primary:
                cats.append(t)
        cats_xml = "".join(f"\n      <category>{esc(c)}</category>" for c in cats)
        # Per-item image: emit both legacy <enclosure> (classic RSS readers,
        # podcast tooling) and MediaRSS <media:content> + <media:thumbnail>
        # (Feedly, Inoreader, Flipboard). Google's Discover feed also reads
        # media:thumbnail. Byte size is included when the file is on disk;
        # some validators warn if length="0" so we omit that attr when unknown.
        media_xml = ""
        cover = m.get("cover")
        if cover:
            img_path = os.path.join(ROOT, "images", f"{cover}-1200.jpg")
            img_url = f"{SITE}/images/{cover}-1200.jpg"
            try:
                length_attr = f' length="{os.path.getsize(img_path)}"'
            except OSError:
                length_attr = ""
            media_xml = (
                f'\n      <enclosure url="{img_url}"{length_attr} type="image/jpeg"/>'
                f'\n      <media:content url="{img_url}" medium="image" type="image/jpeg" width="1200" height="630"/>'
                f'\n      <media:thumbnail url="{img_url}" width="1200" height="630"/>'
            )
        items.append(
            f'    <item>\n'
            f'      <title>{esc(m.get("title",""))}</title>\n'
            f'      <link>{SITE}/posts/{s}.html</link>\n'
            f'      <guid isPermaLink="true">{SITE}/posts/{s}.html</guid>\n'
            f'      <pubDate>{rfc822(m.get("publishDate",""))}</pubDate>\n'
            f'      <dc:creator>Harsha Sridhar</dc:creator>\n'
            f'      <description>{esc(m.get("subtitle",""))}</description>'
            f'{media_xml}{cats_xml}\n'
            f'    </item>'
        )
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
{{KEYWORDS_META}}
<link rel="canonical" href="https://blog.msharsha.com/posts/{{SLUG}}.html">
<meta name="author" content="Harsha Sridhar">
<meta name="copyright" content="© 2026 Harsha Sridhar. All rights reserved.">
<meta property="og:type" content="article">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESCRIPTION}}">
<meta property="og:url" content="https://blog.msharsha.com/posts/{{SLUG}}.html">
<meta property="og:image" content="{{OG_IMAGE}}">
<meta property="og:site_name" content="Harsha Sridhar — Blog">
<meta property="article:published_time" content="{{PUBLISHED}}">
<meta property="article:author" content="Harsha Sridhar">
{{OG_ARTICLE_META}}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{TITLE}}">
<meta name="twitter:description" content="{{DESCRIPTION}}">
<meta name="twitter:image" content="{{OG_IMAGE}}">
<link rel="icon" href="https://msharsha.com/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="https://msharsha.com/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Harsha Sridhar — Blog" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/style.css">
<script src="/components.js"></script>
<script src="/post-comments.js"></script>
<!-- Firebase compat builds (UMD) — expose firebase.* globals, no import/export needed -->
<script src="https://www.gstatic.com/firebasejs/10.7.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.2/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.2/firebase-firestore-compat.js"></script>
<script>
(function(){
  var config={{FIREBASE_CONFIG}};
  if(!config){ console.warn('Firebase config missing — dynamic features disabled.'); return; }
  window.firebaseConfig=config;
  if(!firebase.apps.length){ firebase.initializeApp(config); }
  window.firebaseAuth=firebase.auth();
  window.firebaseDb=firebase.firestore();

  // Enable anonymous auth for likes (silent, no UI on first visit).
  // Strategy: auto-sign-in anon only if the user has never had any auth session.
  // Track "ever had auth" flag; once set, only sign out clears it (on next page load).
  var sessionHasHadAuthUser = false;  // Track within this page session
  window.firebaseAuth.onAuthStateChanged(function(user){
    if(user){
      // User is authenticated (GitHub, Google, or anon)
      sessionHasHadAuthUser = true;
    } else if(!user && !sessionHasHadAuthUser){
      // No user AND this session never had one → sign in anon for first time
      window.firebaseAuth.signInAnonymously().catch(function(err){
        console.warn('Anonymous sign-in failed:',err);
      });
      sessionHasHadAuthUser = true;  // Mark that we tried
    }
    // If !user && sessionHasHadAuthUser, user clicked sign out → stay signed out
  });
})();
</script>
{{RECAPTCHA_SCRIPT}}
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
if(!/^(localhost|127\\.0\\.0\\.1|::1|\\[::1\\])$/.test(location.hostname)&&location.protocol!=='file:'){var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id=G-H9NJDMDFE2';document.head.appendChild(s);gtag('js',new Date());gtag('config','G-H9NJDMDFE2');}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BlogPosting","headline":"{{TITLE}}","description":"{{DESCRIPTION}}","datePublished":"{{PUBLISHED}}","dateModified":"{{PUBLISHED}}","author":{"@type":"Person","name":"Harsha Sridhar","alternateName":"MS Harsha","url":"https://msharsha.com"},"publisher":{"@type":"Person","name":"Harsha Sridhar","url":"https://msharsha.com"},"mainEntityOfPage":"https://blog.msharsha.com/posts/{{SLUG}}.html","image":"{{OG_IMAGE}}","keywords":{{KEYWORDS}},"articleSection":"{{SECTION}}"}
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
    <subscribe-form></subscribe-form>
  </div>

{{COMMENTS}}

</main>

<subscribe-popup></subscribe-popup>

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
          <p class="card-dek">{{SUBTITLE}}</p>{{CARDTAGS}}
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
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
if(!/^(localhost|127\\.0\\.0\\.1|::1|\\[::1\\])$/.test(location.hostname)&&location.protocol!=='file:'){var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id=G-H9NJDMDFE2';document.head.appendChild(s);gtag('js',new Date());gtag('config','G-H9NJDMDFE2');}
</script>
{{INDEX_LD}}
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
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:media="http://search.yahoo.com/mrss/"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Harsha Sridhar — Blog</title>
    <link>https://blog.msharsha.com/</link>
    <description>Essays on distributed systems, agentic AI, and engineering.</description>
    <language>en-us</language>
    <atom:link href="https://blog.msharsha.com/feed.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>https://msharsha.com/apple-touch-icon.png</url>
      <title>Harsha Sridhar — Blog</title>
      <link>https://blog.msharsha.com/</link>
    </image>
{{ITEMS}}
  </channel>
</rss>
"""


if __name__ == "__main__":
    main()
