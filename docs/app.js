(function() {
  // Theme Management
  const html = document.documentElement;
  const themeBtn = document.getElementById("themeToggle");

  function getPreferredTheme() {
    const saved = localStorage.getItem("gtg_theme");
    if (saved) return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    localStorage.setItem("gtg_theme", theme);
  }

  applyTheme(getPreferredTheme());

  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const current = html.getAttribute("data-theme");
      applyTheme(current === "dark" ? "light" : "dark");
    });
  }

  // Specimen Console Tab Switching
  const tabs = document.querySelectorAll(".tab-btn");
  const views = {
    verify: document.getElementById("view-verify"),
    certify: document.getElementById("view-certify"),
    replay: document.getElementById("view-replay")
  };

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.view;
      tabs.forEach(t => {
        t.classList.remove("is-active");
        t.setAttribute("aria-selected", "false");
      });
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");

      Object.keys(views).forEach(k => {
        if (views[k]) {
          views[k].classList.toggle("is-visible", k === target);
        }
      });
    });
  });

  // Clipboard Actions
  function setupCopy(btnId) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    btn.addEventListener("click", async () => {
      const text = "git clone https://github.com/habinsong/GeminiToGenius";
      try {
        await navigator.clipboard.writeText(text);
        const orig = btn.textContent;
        btn.textContent = "복사됨";
        btn.style.color = "var(--accent-pass)";
        setTimeout(() => {
          btn.textContent = orig;
          btn.style.color = "";
        }, 1800);
      } catch (err) {
        btn.textContent = "실패";
      }
    });
  }

  setupCopy("copyBtn");
  setupCopy("copyBtnFooter");
})();
