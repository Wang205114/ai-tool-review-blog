// =============================================
// AI Tool Guide — Main Application Script
// =============================================

const root = document.documentElement;
const themeToggle = document.querySelector("[data-theme-toggle]");
const navToggle = document.querySelector("[data-nav-toggle]");
const siteNav = document.querySelector("[data-site-nav]");
const statusTargets = document.querySelectorAll("[data-status-target]");
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
// Ad Status (pre-AdSense placeholder)
// =============================================
if (statusTargets.length) {
  statusTargets.forEach((slot) => {
    const adName = slot.getAttribute("data-ad-slot");
    if (adName) {
      // Once AdSense is approved, replace this with actual AdSense code
      slot.textContent = `Ad · ` + adName;
    }
  });
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

console.log("AI Tool Guide — loaded");
