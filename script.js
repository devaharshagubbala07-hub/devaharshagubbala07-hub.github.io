(() => {
  "use strict";
  const root = document.documentElement;
  const header = document.querySelector("[data-header]");
  const nav = document.querySelector("[data-nav]");
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navLabel = document.querySelector("[data-nav-label]");
  const progress = document.querySelector("[data-reading-progress]");
  const motionToggle = document.querySelector("[data-motion-toggle]");
  const motionLabel = document.querySelector("[data-motion-label]");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const year = document.querySelector("[data-year]");
  if (year) year.textContent = new Date().getFullYear();

  let motionPreference = "on";
  try { motionPreference = localStorage.getItem("dg-portfolio-motion") || "on"; } catch (_) { /* Preferences are optional. */ }
  const motionAllowed = () => motionPreference !== "off" && !reducedMotion.matches;
  const applyMotion = () => {
    const enabled = motionAllowed();
    root.dataset.motion = enabled ? "on" : "off";
    motionToggle.hidden = false;
    motionToggle.disabled = reducedMotion.matches;
    motionToggle.setAttribute("aria-pressed", String(enabled));
    motionToggle.setAttribute("aria-label", reducedMotion.matches ? "Motion reduced by your device preference" : "Portfolio animations");
    motionToggle.title = reducedMotion.matches ? "Following your device’s reduced-motion setting" : "Turn portfolio animations on or off";
    motionLabel.textContent = reducedMotion.matches ? "Reduced motion" : enabled ? "Motion on" : "Motion off";
    motionToggle.querySelector(".motion-icon").textContent = enabled ? "Ⅱ" : "▷";
    if (!enabled) document.querySelectorAll(".will-reveal").forEach(el => el.classList.add("is-visible"));
  };
  applyMotion();
  motionToggle.addEventListener("click", () => {
    motionPreference = motionAllowed() ? "off" : "on";
    try { localStorage.setItem("dg-portfolio-motion", motionPreference); } catch (_) { /* No persistent storage is required. */ }
    applyMotion();
  });
  reducedMotion.addEventListener("change", applyMotion);

  const closeNav = () => {
    navToggle.setAttribute("aria-expanded", "false");
    nav.classList.remove("open");
    document.body.classList.remove("nav-open");
    navLabel.textContent = "Menu";
  };
  navToggle.hidden = false;
  navToggle.addEventListener("click", () => {
    const open = navToggle.getAttribute("aria-expanded") !== "true";
    navToggle.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("open", open);
    document.body.classList.toggle("nav-open", open);
    navLabel.textContent = open ? "Close" : "Menu";
  });
  document.querySelector(".brand").addEventListener("click", closeNav);
  nav.querySelectorAll("a").forEach(link => link.addEventListener("click", closeNav));
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && navToggle.getAttribute("aria-expanded") === "true") {
      closeNav();
      navToggle.focus();
    }
  });
  window.addEventListener("resize", () => { if (window.innerWidth > 900) closeNav(); }, { passive: true });
  root.classList.add("nav-ready");

  const navSections = [...nav.querySelectorAll('a[href^="#"]')].map(link => ({link, section: document.querySelector(link.getAttribute("href"))})).filter(item => item.section);
  let scrollQueued = false;
  const updateScroll = () => {
    header.classList.toggle("scrolled", window.scrollY > 14);
    const range = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${range > 0 ? Math.min(1, Math.max(0, window.scrollY / range)) : 0})`;
    let active = null;
    for (const item of navSections) if (item.section.getBoundingClientRect().top <= 170) active = item.link;
    for (const item of navSections) {
      if (item.link === active) item.link.setAttribute("aria-current", "location");
      else item.link.removeAttribute("aria-current");
    }
    scrollQueued = false;
  };
  window.addEventListener("scroll", () => {
    if (!scrollQueued) { scrollQueued = true; requestAnimationFrame(updateScroll); }
  }, { passive: true });
  window.addEventListener("resize", updateScroll, { passive: true });
  updateScroll();

  // Same pipeline results as the full demonstration. Figures update immediately;
  // visual transitions never generate intermediate numerical values.
  try {
    const data = JSON.parse(document.querySelector("#preview-data").textContent);
    const previewButtons = [...document.querySelectorAll("[data-preview-year]")];
    const money = new Intl.NumberFormat("en-US", {style:"currency", currency:"USD", minimumFractionDigits:2});
    const integer = new Intl.NumberFormat("en-US");
    let currentYear = "2025";
    const updatePreview = selectedYear => {
      const row = data.annual.find(item => String(item.year) === selectedYear);
      if (!row) return;
      document.querySelector("[data-preview-pmpm]").textContent = money.format(row.pmpm);
      document.querySelector("[data-preview-members]").textContent = integer.format(row.members);
      document.querySelector("[data-preview-months]").textContent = integer.format(row.member_months);
      document.querySelector("[data-preview-scope]").textContent = selectedYear;
      previewButtons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.previewYear === selectedYear)));
      document.querySelectorAll("[data-year-bar]").forEach(bar => bar.classList.toggle("is-selected", bar.dataset.yearBar === selectedYear));
      if (currentYear !== selectedYear && motionAllowed()) document.querySelector(".desk-readout").animate([{opacity:.5,transform:"translateY(4px)"},{opacity:1,transform:"translateY(0)"}], {duration:250,easing:"ease-out"});
      currentYear = selectedYear;
    };
    previewButtons.forEach(button => button.addEventListener("click", () => updatePreview(button.dataset.previewYear)));
    updatePreview(currentYear);
    document.querySelector(".year-switch").hidden = false;
  } catch (error) {
    // Static chart, labels, and the link remain useful if data cannot be parsed.
    console.warn("Interactive preview unavailable; showing the static chart.", error);
  }

  const methodButtons = [...document.querySelectorAll("[data-method]")];
  const methodPanels = [...document.querySelectorAll(".method-panel")];
  const showMethod = button => {
    methodButtons.forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    methodPanels.forEach(panel => {
      panel.hidden = panel.id !== button.getAttribute("aria-controls");
      panel.classList.toggle("method-ready-panel", !panel.hidden);
    });
  };
  methodButtons.forEach(button => button.addEventListener("click", () => showMethod(button)));
  if (methodButtons.length) { showMethod(methodButtons[0]); root.classList.add("method-ready"); }

  if ("IntersectionObserver" in window && motionAllowed()) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.07, rootMargin: "0px 0px -20px 0px" });
    document.querySelectorAll("[data-reveal]").forEach(element => {
      // Only animate off-screen content; no content is hidden while awaiting observation.
      if (element.getBoundingClientRect().top > window.innerHeight && !element.contains(document.querySelector(":target"))) {
        element.classList.add("will-reveal");
        observer.observe(element);
      }
    });
  }
})();
