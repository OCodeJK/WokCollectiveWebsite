import { animate, stagger, onScroll } from "./vendor/anime.esm.min.js";

document.getElementById("year").textContent = new Date().getFullYear();

// Header entrance
animate(".logo-img, .icon-link", {
  opacity: [0, 1],
  translateY: [-8, 0],
  delay: stagger(70),
  duration: 500,
  ease: "outQuad",
});

// Hero carousel
(function () {
  const hero = document.querySelector(".hero");
  if (!hero) return;

  const track = hero.querySelector(".hero-track");
  const slides = Array.from(hero.querySelectorAll(".hero-slide"));
  const dots = Array.from(hero.querySelectorAll(".hero-dot"));
  const prevBtn = hero.querySelector(".hero-arrow-prev");
  const nextBtn = hero.querySelector(".hero-arrow-next");
  const AUTOPLAY_MS = 6000;

  let index = 0;
  let timer = null;

  function goTo(i) {
    index = (i + slides.length) % slides.length;
    track.style.transform = `translateX(-${index * 100}%)`;
    dots.forEach((dot, d) => dot.setAttribute("aria-selected", d === index ? "true" : "false"));
  }

  function next() { goTo(index + 1); }
  function prev() { goTo(index - 1); }

  // Paused while hovered or focused; only ever one interval running
  let hovered = false;
  let focused = false;

  function stopAutoplay() { clearInterval(timer); timer = null; }
  function startAutoplay() {
    stopAutoplay();
    if (!hovered && !focused) timer = setInterval(next, AUTOPLAY_MS);
  }
  function restartAutoplay() { startAutoplay(); }

  function pressFeedback(btn) {
    animate(btn, { scale: [1, 0.82, 1], duration: 320, ease: "outQuad" });
  }

  nextBtn.addEventListener("click", () => { next(); restartAutoplay(); pressFeedback(nextBtn); });
  prevBtn.addEventListener("click", () => { prev(); restartAutoplay(); pressFeedback(prevBtn); });

  dots.forEach((dot, i) => {
    dot.addEventListener("click", () => { goTo(i); restartAutoplay(); });
  });

  hero.addEventListener("mouseenter", () => { hovered = true; stopAutoplay(); });
  hero.addEventListener("mouseleave", () => { hovered = false; startAutoplay(); });
  // Only keyboard focus pauses; a mouse click on an arrow shouldn't leave it stuck
  hero.addEventListener("focusin", (e) => {
    if (!e.target.matches(":focus-visible")) return;
    focused = true;
    stopAutoplay();
  });
  hero.addEventListener("focusout", (e) => {
    if (hero.contains(e.relatedTarget)) return; // focus moved between arrows/dots
    focused = false;
    startAutoplay();
  });

  hero.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { next(); restartAutoplay(); }
    if (e.key === "ArrowLeft") { prev(); restartAutoplay(); }
  });

  // Touch swipe
  let touchStartX = null;
  track.addEventListener("touchstart", (e) => { touchStartX = e.touches[0].clientX; }, { passive: true });
  track.addEventListener("touchend", (e) => {
    if (touchStartX === null) return;
    const delta = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(delta) > 40) {
      delta < 0 ? next() : prev();
      restartAutoplay();
    }
    touchStartX = null;
  });

  goTo(0);
  startAutoplay();
})();

// Scroll reveal for section headings and card grids
(function () {
  function hide(el, y) {
    el.style.opacity = "0";
    el.style.transform = `translateY(${y}px)`;
  }

  document.querySelectorAll(".page-section .section-head").forEach((heading) => {
    hide(heading, 16);
    animate(heading, {
      opacity: [0, 1],
      translateY: [16, 0],
      duration: 700,
      ease: "outQuad",
      autoplay: onScroll({ target: heading, enter: "bottom-=10% top", repeat: false }),
    });
  });

  document.querySelectorAll(".reveal-grid").forEach((grid) => {
    const cards = Array.from(grid.children);
    cards.forEach((el) => hide(el, 28));
    animate(cards, {
      opacity: [0, 1],
      translateY: [28, 0],
      duration: 700,
      delay: stagger(150),
      ease: "outExpo",
      autoplay: onScroll({ target: grid, enter: "bottom-=10% top", repeat: false }),
    });
  });
})();

// Highlight the nav chip for the section in view (homepage sections, menu categories)
(function () {
  const chips = Array.from(document.querySelectorAll(".menu-chip"));
  // Skip chips that link to another page (Shop -> menu.html)
  const sections = chips
    .filter((chip) => chip.getAttribute("href").startsWith("#"))
    .map((chip) => document.querySelector(chip.getAttribute("href")))
    .filter(Boolean);
  if (!chips.length || !sections.length) return;

  function setActive(id) {
    chips.forEach((chip) => {
      const active = chip.getAttribute("href") === `#${id}`;
      chip.classList.toggle("is-active", active);
      // Scroll only the chip row sideways; scrollIntoView would also scroll the page
      if (active) {
        const row = chip.parentElement;
        const left = chip.offsetLeft - row.offsetLeft;
        if (left < row.scrollLeft || left + chip.offsetWidth > row.scrollLeft + row.clientWidth) {
          row.scrollTo({ left: left - 24, behavior: "smooth" });
        }
      }
    });
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) setActive(entry.target.id);
      });
    },
    { rootMargin: "-160px 0px -60% 0px" }
  );

  sections.forEach((section) => observer.observe(section));
  setActive(sections[0].id);
})();

// Menu page: fade cards in as each category scrolls into view
(function () {
  const grids = document.querySelectorAll(".menu-grid");
  grids.forEach((grid) => {
    const cards = grid.querySelectorAll(".menu-card");
    cards.forEach((el) => {
      el.style.opacity = "0";
      el.style.transform = "translateY(20px)";
    });
    animate(cards, {
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 600,
      delay: stagger(60),
      ease: "outQuad",
      autoplay: onScroll({ target: grid, enter: "bottom-=5% top", repeat: false }),
    });
  });
})();
