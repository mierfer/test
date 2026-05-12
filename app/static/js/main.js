// AEN Blog — Main JavaScript

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initSearchOverlay();
  initUserDropdown();
  initFlashMessages();
  initMobileMenu();
  initEditorToolbar();
  initImageUploadPreview();
});

// Navbar scroll effect
function initNavbar() {
  const navbar = document.getElementById("navbar");
  if (!navbar) return;
  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.style.background = "rgba(10,10,15,.95)";
    } else {
      navbar.style.background = "rgba(10,10,15,.85)";
    }
  });
}

// Search overlay
function initSearchOverlay() {
  const toggle = document.getElementById("searchToggle");
  const overlay = document.getElementById("searchOverlay");
  const close = document.getElementById("searchClose");
  const input = overlay ? overlay.querySelector("input") : null;

  if (!toggle || !overlay) return;

  toggle.addEventListener("click", () => {
    overlay.classList.add("show");
    setTimeout(() => input && input.focus(), 100);
  });

  if (close) {
    close.addEventListener("click", () => overlay.classList.remove("show"));
  }

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.classList.remove("show");
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") overlay.classList.remove("show");
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      overlay.classList.toggle("show");
      if (overlay.classList.contains("show")) {
        setTimeout(() => input && input.focus(), 100);
      }
    }
  });
}

// User dropdown
function initUserDropdown() {
  const toggle = document.getElementById("userToggle");
  const dropdown = document.getElementById("userDropdown");
  if (!toggle || !dropdown) return;

  toggle.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.classList.toggle("show");
  });

  document.addEventListener("click", () => {
    dropdown.classList.remove("show");
  });
}

// Flash message auto dismiss
function initFlashMessages() {
  document.querySelectorAll(".flash[data-auto-dismiss]").forEach((flash) => {
    setTimeout(() => {
      flash.style.transition = "all .3s";
      flash.style.opacity = "0";
      flash.style.transform = "translateX(20px)";
      setTimeout(() => flash.remove(), 300);
    }, 4000);
  });

  document.querySelectorAll(".flash-close").forEach((btn) => {
    btn.addEventListener("click", () => {
      const flash = btn.parentElement;
      flash.style.transition = "all .3s";
      flash.style.opacity = "0";
      flash.style.transform = "translateX(20px)";
      setTimeout(() => flash.remove(), 300);
    });
  });
}

// Mobile menu
function initMobileMenu() {
  const toggle = document.getElementById("menuToggle");
  const links = document.getElementById("navLinks");
  if (!toggle || !links) return;

  toggle.addEventListener("click", () => {
    links.classList.toggle("show");
  });
}

// Simple editor toolbar for admin
function initEditorToolbar() {
  const textarea = document.getElementById("content");
  if (!textarea) return;

  document.querySelectorAll(".toolbar-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tag = btn.dataset.tag;
      const attr = btn.dataset.attr;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const selected = textarea.value.substring(start, end);
      const isBlock = ["h2", "h3", "p", "blockquote", "pre"].includes(tag);

      let replacement;
      if (attr && selected) {
        const val = prompt(`输入 ${attr}:`);
        if (!val) return;
        replacement = `<${tag} ${attr}="${val}">${selected}</${tag}>`;
      } else if (isBlock) {
        replacement = selected
          ? `<${tag}>\n  ${selected}\n</${tag}>`
          : `<${tag}>\n  \n</${tag}>`;
      } else {
        replacement = selected
          ? `<${tag}>${selected}</${tag}>`
          : `<${tag}></${tag}>`;
      }

      textarea.value =
        textarea.value.substring(0, start) +
        replacement +
        textarea.value.substring(end);

      textarea.focus();
      const cursorPos = isBlock
        ? start + replacement.indexOf("\n  ") + 3
        : start + replacement.length;
      textarea.setSelectionRange(cursorPos, cursorPos);
    });
  });
}

// Image upload preview
function initImageUploadPreview() {
  const input = document.getElementById("cover_image");
  if (!input) return;

  input.addEventListener("change", () => {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      let preview = input.parentElement.querySelector(".cover-preview");
      if (!preview) {
        preview = document.createElement("img");
        preview.className = "cover-preview";
        preview.style.cssText =
          "max-width:300px;border-radius:8px;margin-top:8px";
        input.parentElement.appendChild(preview);
      }
      preview.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

// Copy link utility
function copyToClipboard(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showToast("链接已复制");
    });
  } else {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
    showToast("链接已复制");
  }
}

// Simple inline toast
function showToast(msg) {
  const toast = document.createElement("div");
  toast.textContent = msg;
  toast.style.cssText = `
    position:fixed;bottom:24px;left:50%;transform:translateX(-50%);
    background:var(--accent);color:#fff;padding:10px 24px;
    border-radius:var(--radius-xl);font-size:14px;font-weight:500;
    z-index:9999;box-shadow:var(--shadow-lg);
    animation:fadeIn .2s ease;
  `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = "all .3s";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 2000);
}
