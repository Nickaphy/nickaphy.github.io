/**
 * main.js — small site interactions (vanilla only).
 * - Typed tagline on the homepage
 * - Fade-in-on-scroll for cards / list items
 * - Writeups tag filter
 */

(function () {
  "use strict";

  /**
   * Types `text` into `el` one character at a time, then keeps a blinking cursor.
   * Skips animation when the user prefers reduced motion.
   */
  function typeText(el, text, msPerChar) {
    if (!el) return;

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) {
      el.textContent = text;
      return;
    }

    var i = 0;
    el.textContent = "";

    // Cursor span sits after the typed characters
    var cursor = document.createElement("span");
    cursor.className = "cursor";
    cursor.setAttribute("aria-hidden", "true");
    el.appendChild(cursor);

    function tick() {
      if (i < text.length) {
        // Insert the next character before the cursor
        el.insertBefore(document.createTextNode(text.charAt(i)), cursor);
        i += 1;
        window.setTimeout(tick, msPerChar);
      }
    }

    tick();
  }

  /**
   * Show/hide writeup list items by tag (buttons with .tag-filter + data-tag).
   * data-tag="" means "All".
   */
  function initWriteupFilters() {
    var list = document.querySelector(".post-list");
    var buttons = document.querySelectorAll(".tag-filter");
    if (!list || !buttons.length) return;

    var items = list.querySelectorAll(".post-list__item");
    var empty = document.querySelector(".filter-empty");

    function applyFilter(tag) {
      var visible = 0;
      items.forEach(function (item) {
        var tags = (item.getAttribute("data-tags") || "").split(/\s+/);
        var show = !tag || tags.indexOf(tag) !== -1;
        item.hidden = !show;
        if (show) visible += 1;
      });
      if (empty) empty.hidden = visible > 0;
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) {
          b.classList.remove("is-active");
        });
        btn.classList.add("is-active");
        applyFilter(btn.getAttribute("data-tag") || "");
      });
    });
  }

  /**
   * Adds .is-visible when elements with .fade-in enter the viewport.
   * One reusable observer for every matching element on the page.
   */
  function observeFadeIns() {
    var targets = document.querySelectorAll(".fade-in");
    if (!targets.length) return;

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion || !("IntersectionObserver" in window)) {
      targets.forEach(function (el) {
        el.classList.add("is-visible");
      });
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -40px 0px", threshold: 0.05 }
    );

    targets.forEach(function (el) {
      // Reveal anything already on screen without waiting for a scroll event
      var rect = el.getBoundingClientRect();
      var onScreen = rect.top < window.innerHeight && rect.bottom > 0;
      if (onScreen) {
        el.classList.add("is-visible");
      } else {
        observer.observe(el);
      }
    });
  }

  /**
   * Boots homepage typing, writeup filters, and fade-ins after DOM is ready.
   */
  function init() {
    var tagline = document.getElementById("typed-tagline");
    if (tagline) {
      var text = tagline.getAttribute("data-text") || "";
      typeText(tagline, text, 40);
    }

    initWriteupFilters();
    observeFadeIns();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
