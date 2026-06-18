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
            <img class="brand-logo" src="${PORTFOLIO}/icon-192.png" alt="" width="28" height="28" loading="eager" decoding="async">
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

    // Auto-hide header on scroll-down, reveal on scroll-up. Medium-style:
    // gives the reader the full vertical real estate while reading, but keeps
    // the theme toggle and nav one upward flick away. Stays visible near the
    // top, and ignores tiny jitter so quick taps don't flicker it.
    const header = this.querySelector('.site-header');

    // Publish the real header height into --header-h so the grid placeholder
    // <site-header>'s reserved height matches what the fixed header occupies.
    const syncHeaderHeight = () => {
      document.documentElement.style.setProperty('--header-h', `${header.offsetHeight}px`);
    };
    syncHeaderHeight();
    new ResizeObserver(syncHeaderHeight).observe(header);

    const REVEAL_AT_TOP = 80;   // px from top — header always visible above this
    const JITTER = 6;           // px — ignore micro-scrolls
    let lastY = window.scrollY;
    let ticking = false;
    const onScroll = () => {
      const y = window.scrollY;
      const delta = y - lastY;
      if (Math.abs(delta) < JITTER) { ticking = false; return; }
      if (y < REVEAL_AT_TOP) {
        header.removeAttribute('data-hidden');
      } else if (delta > 0) {
        header.setAttribute('data-hidden', 'true');   // scrolling down → hide
      } else {
        header.removeAttribute('data-hidden');        // scrolling up → reveal
      }
      lastY = y;
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) { requestAnimationFrame(onScroll); ticking = true; }
    }, { passive: true });
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
