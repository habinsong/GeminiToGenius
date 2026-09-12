/**
 * GeminiToGenius - High-End Interaction & Motion Orchestration
 * Driven strictly via IntersectionObserver. Zero scroll event overhead.
 */
(function () {
  "use strict";

  // 01. Theme Management (System Sync & Persistence)
  const themeToggle = document.getElementById("themeToggle");
  const htmlRoot = document.documentElement;

  function initTheme() {
    const savedTheme = localStorage.getItem("gtg-theme");
    if (savedTheme) {
      htmlRoot.setAttribute("data-theme", savedTheme);
    } else {
      const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
      htmlRoot.setAttribute("data-theme", prefersLight ? "light" : "dark");
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const currentTheme = htmlRoot.getAttribute("data-theme") || "dark";
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      htmlRoot.setAttribute("data-theme", nextTheme);
      localStorage.setItem("gtg-theme", nextTheme);
    });
  }

  // 02. Haptic One-Click Copy Feedback
  const copyBtn = document.getElementById("copyInstallBtn");
  const installCode = document.getElementById("installCommand");

  if (copyBtn && installCode) {
    copyBtn.addEventListener("click", async () => {
      const textToCopy = installCode.innerText.trim();
      try {
        await navigator.clipboard.writeText(textToCopy);
        const label = copyBtn.querySelector(".capsule-btn-label");
        const originalText = label.textContent;

        label.textContent = "복사 완료!";
        copyBtn.style.background = "var(--color-ok)";
        copyBtn.style.color = "#ffffff";
        copyBtn.style.borderColor = "transparent";

        setTimeout(() => {
          label.textContent = originalText;
          copyBtn.style.background = "";
          copyBtn.style.color = "";
          copyBtn.style.borderColor = "";
        }, 2200);
      } catch (err) {
        console.error("복사 실패:", err);
      }
    });
  }

  // 03. Scroll Interpolation (IntersectionObserver)
  const revealElements = document.querySelectorAll(".reveal-on-scroll");

  if ("IntersectionObserver" in window && revealElements.length > 0) {
    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-revealed");
            obs.unobserve(entry.target);
          }
        });
      },
      {
        root: null,
        threshold: 0.12,
        rootMargin: "0px 0px -40px 0px",
      }
    );

    revealElements.forEach((el) => observer.observe(el));
  } else {
    revealElements.forEach((el) => el.classList.add("is-revealed"));
  }

  // Initialize
  initTheme();
})();
