# blog.msharsha.com

A hand-built static blog. No build step, no generator. Long-form reading layout
(serif body, narrow column) with Harsha Sridhar's own branding — **not** a clone
of any platform.

## This is a SEPARATE site from the portfolio

These files belong in their **own GitHub repository** that publishes to the
subdomain `blog.msharsha.com`. Do **not** leave this `blog/` folder inside the
portfolio repo when you deploy the portfolio — it would publish to
`msharsha.com/blog/`, which is not what we want. (A `.gitignore` entry already
guards against that.)

## Files

| File | What it is |
|------|------------|
| `index.html` | Article list. Add a `<li class="post-card">` block per new post. |
| `posts/*.html` | One file per article. |
| `post-template.html` | Copy this to start a new post; fill in the `EDIT` markers. |
| `style.css` | Shared reading theme. |
| `components.js` | `<site-header>` / `<site-footer>` web components — edit chrome here once. |
| `sitemap.xml`, `feed.xml`, `robots.txt` | SEO + RSS. Add an entry when you publish. |
| `CNAME` | Tells GitHub Pages the custom domain. |

## Publishing a new post

1. `cp post-template.html posts/your-slug.html`
2. Replace every `EDIT` marker (title, description, canonical URL, date, slug, JSON-LD).
3. Write the article inside `<article>` using the building blocks: `<h2>`, `<p>`,
   `.pull-quote`, `<figure>`, `<pre><code>`, `.divider`, `.refs`.
4. Add a `<li class="post-card">` to `index.html` (newest on top).
5. Add `<url>` to `sitemap.xml` and an `<item>` to `feed.xml`.
6. Commit + push. Done.

## Deploy (one-time setup)

1. Create a new GitHub repo, e.g. `harshasridhar/blog`.
2. Push these files to `main`.
3. Repo → **Settings → Pages** → Source: *Deploy from a branch* → `main` / root.
   (Pure static — no GitHub Action needed.)
4. Set custom domain to `blog.msharsha.com` (the `CNAME` file already declares it).
5. **DNS** at your registrar: add a `CNAME` record
   `blog` → `harshasridhar.github.io` (your Pages host). Wait for it to resolve,
   then enable *Enforce HTTPS* in Pages settings.

## Local preview

`file://` won't resolve the root-absolute paths (`/style.css`), so run a tiny server:

```
cd blog && python3 -m http.server 8000
# open http://localhost:8000
```

## SEO notes

- Each post's `<title>`, meta description, canonical, and body are static in the
  file (header/footer are injected, but those aren't indexed content).
- The full article lives here and is the **canonical** source; Medium gets a
  shorter teaser that links back. Publish here first so Google attributes it to you.
- Add `blog.msharsha.com` as its own property in Google Search Console and submit
  `sitemap.xml`. Cross-link with the portfolio (already linked in the header/footer).
