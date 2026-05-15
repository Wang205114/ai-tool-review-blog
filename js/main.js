const root = document.documentElement;
const themeToggle = document.querySelector("[data-theme-toggle]");
const navToggle = document.querySelector("[data-nav-toggle]");
const siteNav = document.querySelector("[data-site-nav]");
const statusTargets = document.querySelectorAll("[data-status-target]");
const yearTarget = document.querySelector("[data-current-year]");

const storedTheme = localStorage.getItem("ai-review-theme");
if (storedTheme) {
  root.setAttribute("data-theme", storedTheme);
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
      localStorage.setItem("ai-review-theme", "light");
    } else {
      root.setAttribute("data-theme", "dark");
      localStorage.setItem("ai-review-theme", "dark");
    }
    syncLabel();
  });
}

if (navToggle && siteNav) {
  navToggle.addEventListener("click", () => {
    const open = siteNav.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(open));
  });
}

document.querySelectorAll("form[data-static-form]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const target = form.querySelector("[data-form-status]");
    if (target) {
      target.textContent = "Thanks. This static demo form is wired for layout only. Connect your email or form service before launch.";
    }
    form.reset();
  });
});

if (yearTarget) {
  yearTarget.textContent = new Date().getFullYear();
}

if (statusTargets.length) {
  statusTargets.forEach((slot) => {
    const adName = slot.getAttribute("data-ad-slot");
    if (adName) {
      slot.textContent = `AdSense placeholder: ${adName}`;
    }
  });
}
