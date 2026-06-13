/* ───────────────────────────────────────────────────────────
   Shared chrome as Web Components. Edit once here; every page
   that includes this file and drops in <site-header></site-header>
   or <site-footer></site-footer> updates automatically.
   These render Harsha's own brand — not a clone of any platform.
   ─────────────────────────────────────────────────────────── */

const PORTFOLIO = 'https://msharsha.com';
const LINKEDIN  = 'https://www.linkedin.com/in/harsha-sridhar/';
const MEDIUM    = 'https://medium.com/@msharsha';

const SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2.5v2M12 19.5v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2.5 12h2M19.5 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/></svg>';
const MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
const resolvedTheme = () => document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';

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
            <button class="theme-toggle" type="button" role="switch"><span class="knob"></span></button>
          </nav>
        </div>
      </header>`;

    const btn = this.querySelector('.theme-toggle');
    const knob = btn.querySelector('.knob');
    const render = () => {
      const dark = resolvedTheme() === 'dark';
      knob.innerHTML = dark ? MOON : SUN;
      btn.setAttribute('aria-checked', dark);
      const label = dark ? 'Switch to light mode' : 'Switch to dark mode';
      btn.title = label;
      btn.setAttribute('aria-label', label);
    };
    btn.addEventListener('click', () => {
      const next = resolvedTheme() === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', next);
      document.documentElement.setAttribute('data-theme', next);
      render();
    });
    // until the visitor picks a theme, keep following the OS setting live
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) { document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light'); render(); }
    });
    render();
  }
}

class SiteFooter extends HTMLElement {
  connectedCallback() {
    const year = new Date().getFullYear();
    this.innerHTML = `
      <footer class="site-footer">
        <div class="inner">
          <span>© ${year} Harsha Sridhar · All rights reserved.</span>
          <span class="flinks">
            <a href="${PORTFOLIO}">Portfolio</a>
            <a href="${LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
            <a href="${MEDIUM}" target="_blank" rel="noopener">Medium</a>
            <a href="/feed.xml">RSS</a>
            <a href="/LICENSE.txt">License</a>
          </span>
        </div>
      </footer>`;
  }
}

customElements.define('site-header', SiteHeader);
customElements.define('site-footer', SiteFooter);
