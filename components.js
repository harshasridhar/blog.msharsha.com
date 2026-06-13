/* ───────────────────────────────────────────────────────────
   Shared chrome as Web Components. Edit once here; every page
   that includes this file and drops in <site-header></site-header>
   or <site-footer></site-footer> updates automatically.
   These render Harsha's own brand — not a clone of any platform.
   ─────────────────────────────────────────────────────────── */

const PORTFOLIO = 'https://msharsha.com';
const LINKEDIN  = 'https://www.linkedin.com/in/harsha-sridhar/';
const MEDIUM    = 'https://medium.com/@msharsha';

class SiteHeader extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class="site-header">
        <div class="inner">
          <a class="brand" href="/" aria-label="Harsha Sridhar — home">
            <span class="mono">H<em>S</em></span>
            <span class="full">Harsha Sridhar</span>
          </a>
          <nav class="nav">
            <a href="/">Articles</a>
            <a href="${PORTFOLIO}">Portfolio</a>
            <a href="${MEDIUM}" rel="me">Medium</a>
          </nav>
        </div>
      </header>`;
  }
}

class SiteFooter extends HTMLElement {
  connectedCallback() {
    const year = new Date().getFullYear();
    this.innerHTML = `
      <footer class="site-footer">
        <div class="inner">
          <span>© ${year} Harsha Sridhar · Built by hand.</span>
          <span class="flinks">
            <a href="${PORTFOLIO}">Portfolio</a>
            <a href="${LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
            <a href="${MEDIUM}" target="_blank" rel="noopener">Medium</a>
            <a href="/feed.xml">RSS</a>
          </span>
        </div>
      </footer>`;
  }
}

customElements.define('site-header', SiteHeader);
customElements.define('site-footer', SiteFooter);
