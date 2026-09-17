const header = document.querySelector("[data-header]");
const nav = document.querySelector("[data-nav]");
const navToggle = document.querySelector("[data-nav-toggle]");
const navLabel = navToggle?.querySelector(".sr-only");
const year = document.querySelector("[data-year]");

const setHeaderState = () => header?.classList.toggle("scrolled", window.scrollY > 14);
setHeaderState();
window.addEventListener("scroll", setHeaderState, { passive: true });
if (year) year.textContent = new Date().getFullYear();

const closeNav = () => {
  navToggle?.setAttribute("aria-expanded", "false");
  nav?.classList.remove("open");
  document.body.classList.remove("nav-open");
  if (navLabel) navLabel.textContent = "Open navigation";
};
navToggle?.addEventListener("click", () => {
  if (navToggle.getAttribute("aria-expanded") === "true") {
    closeNav();
  } else {
    navToggle.setAttribute("aria-expanded", "true");
    nav?.classList.add("open");
    document.body.classList.add("nav-open");
    if (navLabel) navLabel.textContent = "Close navigation";
  }
});
nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeNav));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && navToggle?.getAttribute("aria-expanded") === "true") {
    closeNav();
    navToggle.focus();
  }
});
window.addEventListener("resize", () => {
  if (window.innerWidth > 850) closeNav();
}, { passive: true });
document.documentElement.classList.add("nav-ready");
