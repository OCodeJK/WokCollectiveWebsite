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
  const hero = document.getElementById("hero-slider");
  if (!hero) return;

  const track = hero.querySelector(".hero-track");
  const slides = Array.from(hero.querySelectorAll(".hero-slide"));
  const dots = Array.from(hero.querySelectorAll(".hero-dot"));
  const prevBtn = hero.querySelector(".hero-arrow-prev");
  const nextBtn = hero.querySelector(".hero-arrow-next");
  const AUTOPLAY_MS = 6000;

  let index = 0;
  let timer = null;

  function revealSlideContent(slideEl) {
    const items = slideEl.querySelectorAll(".hero-eyebrow, h1, .hero-sub, .btn");
    animate(items, {
      opacity: [0, 1],
      translateY: [18, 0],
      delay: stagger(90),
      duration: 550,
      ease: "outQuad",
    });
  }

  function goTo(i) {
    index = (i + slides.length) % slides.length;
    track.style.transform = `translateX(-${index * 100}%)`;
    dots.forEach((dot, d) => dot.setAttribute("aria-selected", d === index ? "true" : "false"));
    revealSlideContent(slides[index]);
  }

  function next() { goTo(index + 1); }
  function prev() { goTo(index - 1); }

  function startAutoplay() { timer = setInterval(next, AUTOPLAY_MS); }
  function stopAutoplay() { clearInterval(timer); }
  function restartAutoplay() { stopAutoplay(); startAutoplay(); }

  function pressFeedback(btn) {
    animate(btn, { scale: [1, 0.82, 1], duration: 320, ease: "outQuad" });
  }

  nextBtn.addEventListener("click", () => { next(); restartAutoplay(); pressFeedback(nextBtn); });
  prevBtn.addEventListener("click", () => { prev(); restartAutoplay(); pressFeedback(prevBtn); });

  dots.forEach((dot, i) => {
    dot.addEventListener("click", () => { goTo(i); restartAutoplay(); });
  });

  hero.addEventListener("mouseenter", stopAutoplay);
  hero.addEventListener("mouseleave", startAutoplay);
  hero.addEventListener("focusin", stopAutoplay);
  hero.addEventListener("focusout", startAutoplay);

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

// Scroll reveal for the Visit section
(function () {
  const heading = document.querySelector("#visit .section-head");
  const cards = document.querySelectorAll("#visit .outlet-card, #visit .qr-card");
  const grid = document.querySelector("#visit .visit-grid");

  function hide(el, y) {
    el.style.opacity = "0";
    el.style.transform = `translateY(${y}px)`;
  }

  if (heading) {
    hide(heading, 16);
    animate(heading, {
      opacity: [0, 1],
      translateY: [16, 0],
      duration: 700,
      ease: "outQuad",
      autoplay: onScroll({ target: heading, enter: "bottom-=10% top", repeat: false }),
    });
  }

  if (cards.length && grid) {
    cards.forEach((el) => hide(el, 28));
    animate(cards, {
      opacity: [0, 1],
      translateY: [28, 0],
      duration: 700,
      delay: stagger(150),
      ease: "outExpo",
      autoplay: onScroll({ target: grid, enter: "bottom-=10% top", repeat: false }),
    });
  }
})();

// QR "scan line" sweep
(function () {
  const scanline = document.querySelector(".qr-scanline");
  if (!scanline) return;

  animate(scanline, {
    translateY: [0, 172],
    loop: true,
    alternate: true,
    duration: 1800,
    ease: "inOutSine",
  });
})();
