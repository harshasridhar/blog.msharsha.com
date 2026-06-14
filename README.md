# blog.msharsha.com

A static blog with Harsha Sridhar's own branding — **not** a clone of any
platform. Long-form reading layout: serif body, narrow column, light/dark themes.

**You write posts in Markdown.** A tiny zero-dependency generator
(`scripts/build-site.py`) turns each `content/*.md` file into the post HTML, and
regenerates the index, sitemap, and RSS feed. Images are optimized by
`scripts/build-images.py`. Both run automatically on deploy via GitHub Actions,
so the repo holds only sources (Markdown + covers + CSS/JS) — never generated HTML.

## This is a SEPARATE site from the portfolio

These files belong in their **own GitHub repository** that publishes to the
subdomain `blog.msharsha.com`. Do **not** leave this `blog/` folder inside the
portfolio repo when you deploy the portfolio — it would publish to
`msharsha.com/blog/`, which is not what we want. (A `.gitignore` entry already
guards against that.)

## Files

### Sources (committed)

| File | What it is |
|------|------------|
| `content/*.md` | **Your posts.** One Markdown file per article (frontmatter + body). |
| `content/_template.md` | Starter to copy for a new post (the `_` prefix means the build skips it). |
| `images/cover-<slug>.jpg` | One source cover per post (any size). |
| `style.css` | Shared reading theme. |
| `components.js` | `<site-header>` / `<site-footer>` web components + theme toggle — edit chrome here once. |
| `scripts/build-site.py` | Renders Markdown → HTML, index, sitemap, feed. No dependencies. |
| `scripts/build-images.py` | Turns each source cover into responsive WebP + JPG. |
| `robots.txt`, `CNAME`, `LICENSE.txt`, `THUMBNAIL-PROMPT.md` | Static. |
| `.github/workflows/deploy.yml` | Runs both build scripts, then deploys to Pages on every push. |

### Generated (git-ignored, rebuilt on deploy)

`index.html`, `posts/*.html`, `sitemap.xml`, `feed.xml`, and the image
derivatives (`images/*-480/800/1200.webp`, `-1200.jpg`).

## Publishing a new post

1. `cp content/_template.md content/your-slug.md`
2. Fill in the frontmatter (title, subtitle, tags, category, readTime, publishDate,
   `medium` link, `cover`) and write the body in Markdown.
3. Save a cover at `images/cover-your-slug.jpg` and set `cover: cover-your-slug`
   in the frontmatter.
4. Commit + push. The Action builds the HTML + images, regenerates the index /
   sitemap / feed, and deploys. **That's the whole workflow — one Markdown file.**

### Markdown → components

`##`/`###` → section headings · blank-line text → paragraphs · `>` → pull-quote ·
` ``` ` fenced → code panel · `* * *` or `---` → divider · `- ` / `1. ` → lists ·
`![alt](src)` → figure with caption · raw HTML blocks pass through untouched.

## Deploy (one-time setup)

1. Create a new GitHub repo, e.g. `harshasridhar/blog`.
2. Push these files to `main`.
3. Repo → **Settings → Pages** → Source: **GitHub Actions** (the included
   `deploy.yml` builds the images, then publishes — *not* "Deploy from a branch").
4. Set custom domain to `blog.msharsha.com` (the `CNAME` file already declares it).
5. **DNS** at your registrar: add a `CNAME` record
   `blog` → `harshasridhar.github.io` (your Pages host). Wait for it to resolve,
   then enable *Enforce HTTPS* in Pages settings.

## Local preview

Run both build scripts once (outputs are git-ignored), then serve — `file://`
won't resolve the root-absolute paths (`/style.css`):

```
cd blog
python3 scripts/build-images.py    # needs: pip install Pillow
python3 scripts/build-site.py      # no dependencies
python3 -m http.server 8000        # open http://localhost:8000
```

## SEO notes

- Each post's `<title>`, meta description, canonical, and body are static in the
  file (header/footer are injected, but those aren't indexed content).
- The full article lives here and is the **canonical** source; Medium gets a
  shorter teaser that links back. Publish here first so Google attributes it to you.
- Add `blog.msharsha.com` as its own property in Google Search Console and submit
  `sitemap.xml`. Cross-link with the portfolio (already linked in the header/footer).
