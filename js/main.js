// =============================================
// AI Tool Guide — Main Application Script
// =============================================

const root = document.documentElement;
const themeToggle = document.querySelector("[data-theme-toggle]");
const navToggle = document.querySelector("[data-nav-toggle]");
const siteNav = document.querySelector("[data-site-nav]");
const yearTarget = document.querySelector("[data-current-year]");

// =============================================
// Theme management
// =============================================
const storedTheme = localStorage.getItem("aitg-theme");
if (storedTheme === "dark") {
  root.setAttribute("data-theme", "dark");
}

if (themeToggle) {
  const syncLabel = () => {
    const dark = root.getAttribute("data-theme") === "dark";
    themeToggle.setAttribute("aria-pressed", String(dark));
    themeToggle.textContent = dark ? "☀" : "☾";
  };
  syncLabel();

  themeToggle.addEventListener("click", () => {
    const nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    if (nextTheme === "light") {
      root.removeAttribute("data-theme");
      localStorage.setItem("aitg-theme", "light");
    } else {
      root.setAttribute("data-theme", "dark");
      localStorage.setItem("aitg-theme", "dark");
    }
    syncLabel();
  });
}

// =============================================
// Mobile navigation
// =============================================
if (navToggle && siteNav) {
  navToggle.addEventListener("click", () => {
    const open = siteNav.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(open));
  });

  // Close nav on link click
  siteNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      siteNav.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });
}

// =============================================
// Cookie Consent Banner
// =============================================
(function cookieConsent() {
  const banner = document.querySelector("[data-cookie-banner]");
  const acceptBtn = document.querySelector("[data-cookie-accept]");
  const declineBtn = document.querySelector("[data-cookie-decline]");

  if (!banner) return;

  const consent = localStorage.getItem("aitg-cookie-consent");
  if (consent === "accepted" || consent === "declined") {
    return; // already decided
  }

  // Show banner after a short delay
  setTimeout(() => {
    banner.classList.add("is-visible");
  }, 800);

  if (acceptBtn) {
    acceptBtn.addEventListener("click", () => {
      localStorage.setItem("aitg-cookie-consent", "accepted");
      banner.classList.remove("is-visible");
      // Enable AdSense personalization if needed
      if (typeof window.trackAdConsent === "function") {
        window.trackAdConsent(true);
      }
    });
  }

  if (declineBtn) {
    declineBtn.addEventListener("click", () => {
      localStorage.setItem("aitg-cookie-consent", "declined");
      banner.classList.remove("is-visible");
      // Disable AdSense personalization
      if (typeof window.trackAdConsent === "function") {
        window.trackAdConsent(false);
      }
    });
  }
})();

// =============================================
// Scroll to Top Button
// =============================================
(function scrollToTop() {
  const btn = document.querySelector("[data-scroll-top]");
  if (!btn) return;

  const toggleVisibility = () => {
    btn.classList.toggle("is-visible", window.scrollY > 400);
  };

  window.addEventListener("scroll", toggleVisibility, { passive: true });

  btn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
})();

// =============================================
// Auto-update year in footer
// =============================================
if (yearTarget) {
  yearTarget.textContent = new Date().getFullYear();
}

// =============================================
// Smooth scroll for anchor links
// =============================================
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", (e) => {
    const href = anchor.getAttribute("href");
    if (href === "#") return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});

// =============================================
// Auto-star-rating: data-stars attribute
// =============================================
document.querySelectorAll("[data-stars]").forEach((el) => {
  const val = parseFloat(el.getAttribute("data-stars"));
  if (isNaN(val)) return;

  const full = Math.floor(val);
  const half = val - full >= 0.25 && val - full < 0.75;
  const empty = 5 - full - (half ? 1 : 0);

  let html = '<span class="star-rating">';
  for (let i = 0; i < full; i++) html += '<span class="star filled">★</span>';
  if (half) html += '<span class="star half">★</span>';
  for (let i = 0; i < empty; i++) html += '<span class="star">★</span>';
  html += ` <span class="rating-text">${val.toFixed(1)}/5.0</span></span>`;
  el.innerHTML = html;
});

// =============================================
// Lazy load images (performance)
// =============================================
document.querySelectorAll("img[data-src]").forEach((img) => {
  img.addEventListener("load", () => img.removeAttribute("data-src"));
});

// =============================================
// Search overlay
// =============================================
(function searchOverlay() {
  const toggle = document.querySelector("[data-search-toggle]");
  if (!toggle) return;

  // Create overlay HTML
  const overlay = document.createElement("div");
  overlay.className = "search-overlay";
  overlay.setAttribute("data-search-overlay", "");
  overlay.innerHTML =
    '<div class="search-modal">' +
      '<div class="search-input-wrap">' +
        '<span class="search-icon">🔍</span>' +
        '<input type="text" data-search-input placeholder="Search articles…" autocomplete="off">' +
        '<button class="search-close" data-search-close type="button">&times;</button>' +
      "</div>" +
      '<div class="search-results" data-search-results></div>' +
    "</div>";
  document.body.appendChild(overlay);

  const input = overlay.querySelector("[data-search-input]");
  const resultsEl = overlay.querySelector("[data-search-results]");
  const closeBtn = overlay.querySelector("[data-search-close]");
  let index = null;

  const open = () => {
    overlay.classList.add("is-open");
    document.body.style.overflow = "hidden";
    setTimeout(() => input.focus(), 100);
  };

  const close = () => {
    overlay.classList.remove("is-open");
    document.body.style.overflow = "";
    input.value = "";
    resultsEl.innerHTML = "";
  };

  const loadIndex = async () => {
    if (index) return index;
    try {
      const res = await fetch("js/search.json");
      index = await res.json();
      return index;
    } catch {
      resultsEl.innerHTML = '<div class="search-empty">Search temporarily unavailable.</div>';
      return [];
    }
  };

  const search = async (query) => {
    const q = query.toLowerCase().trim();
    if (!q) { resultsEl.innerHTML = '<div class="search-empty">Start typing to search articles…</div>'; return; }
    const data = await loadIndex();
    const matches = data.filter(
      (item) =>
        item.title.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q)
    ).slice(0, 8);
    if (matches.length === 0) {
      resultsEl.innerHTML = '<div class="search-empty">No articles found for &quot;' + query + '&quot;.</div>';
      return;
    }
    resultsEl.innerHTML = matches
      .map(
        (m) =>
          '<a class="search-result-item" href="' + m.url + '">' +
            '<div class="result-title">' + m.title + '</div>' +
            '<span class="result-category">' + m.category + '</span>' +
            '<div class="result-desc">' + m.description + '</div>' +
          "</a>"
      )
      .join("");
  };

  // Events
  toggle.addEventListener("click", open);
  closeBtn.addEventListener("click", close);
  overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("is-open")) close();
    if ((e.ctrlKey || e.metaKey) && e.key === "k" && !overlay.classList.contains("is-open")) { e.preventDefault(); open(); }
  });
  input.addEventListener("input", () => search(input.value));
})();

console.log("KnowAITool — loaded");
