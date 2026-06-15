document.addEventListener("DOMContentLoaded", () => {
  // Initialize Bootstrap tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    new bootstrap.Tooltip(el);
  });

  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll(".alert").forEach((alert) => {
    setTimeout(() => {
      bootstrap.Alert.getOrCreateInstance(alert).close();
    }, 5000);
  });

  // Confirm action for forms with data-confirm attribute
  document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) {
        event.preventDefault();
      }
    });
  });

  // Enhanced form validation feedback
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const invalidInputs = form.querySelectorAll(":invalid");
      if (invalidInputs.length > 0) {
        event.preventDefault();
        invalidInputs[0].focus();
      }
    });
  });

  // Sidebar toggle for mobile
  const sidebarToggle = document.querySelector(".sidebar-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  // Dynamic table row highlighting
  document.querySelectorAll(".table tbody tr").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (event.target.tagName !== "A" && event.target.tagName !== "BUTTON" && event.target.tagName !== "INPUT") {
        const link = row.querySelector("a");
        if (link) {
          window.location.href = link.href;
        }
      }
    });
  });

  // Image preview for file uploads
  document.querySelectorAll('input[type="file"]').forEach((input) => {
    input.addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const preview = document.createElement("img");
          preview.src = e.target.result;
          preview.className = "img-thumbnail mt-2";
          preview.style.maxWidth = "200px";
          preview.style.maxHeight = "200px";
          
          const existingPreview = input.parentElement.querySelector(".img-thumbnail");
          if (existingPreview) {
            existingPreview.remove();
          }
          input.parentElement.appendChild(preview);
        };
        reader.readAsDataURL(file);
      }
    });
  });

  // Auto-resize textareas
  document.querySelectorAll("textarea").forEach((textarea) => {
    textarea.addEventListener("input", () => {
      textarea.style.height = "auto";
      textarea.style.height = textarea.scrollHeight + "px";
    });
  });

  // Copy to clipboard functionality
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.dataset.copy;
      try {
        await navigator.clipboard.writeText(text);
        const originalText = button.textContent;
        button.textContent = "Copied!";
        button.classList.add("btn-success");
        setTimeout(() => {
          button.textContent = originalText;
          button.classList.remove("btn-success");
        }, 2000);
      } catch (err) {
        console.error("Failed to copy:", err);
      }
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (event) => {
      const targetId = anchor.getAttribute("href");
      if (targetId !== "#") {
        event.preventDefault();
        const target = document.querySelector(targetId);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  });

  // Loading state for buttons
  document.querySelectorAll("[data-loading]").forEach((button) => {
    button.addEventListener("click", () => {
      const originalText = button.textContent;
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
      
      setTimeout(() => {
        button.disabled = false;
        button.textContent = originalText;
      }, 2000);
    });
  });

  // Character counter for text inputs
  document.querySelectorAll("[data-maxlength]").forEach((input) => {
    const maxLength = parseInt(input.dataset.maxlength);
    const counter = document.createElement("small");
    counter.className = "text-muted";
    input.parentElement.appendChild(counter);
    
    const updateCounter = () => {
      const remaining = maxLength - input.value.length;
      counter.textContent = `${remaining} characters remaining`;
      if (remaining < 10) {
        counter.classList.add("text-danger");
      } else {
        counter.classList.remove("text-danger");
      }
    };
    
    input.addEventListener("input", updateCounter);
    updateCounter();
  });

  // Password strength indicator
  document.querySelectorAll('input[type="password"][data-strength]').forEach((input) => {
    const strengthBar = document.createElement("div");
    strengthBar.className = "progress mt-2";
    strengthBar.style.height = "5px";
    strengthBar.innerHTML = '<div class="progress-bar" role="progressbar" style="width: 0%"></div>';
    input.parentElement.appendChild(strengthBar);
    
    const strengthText = document.createElement("small");
    strengthText.className = "text-muted";
    input.parentElement.appendChild(strengthText);
    
    input.addEventListener("input", () => {
      const password = input.value;
      let strength = 0;
      
      if (password.length >= 8) strength += 25;
      if (password.length >= 12) strength += 15;
      if (/[a-z]/.test(password)) strength += 15;
      if (/[A-Z]/.test(password)) strength += 15;
      if (/[0-9]/.test(password)) strength += 15;
      if (/[^a-zA-Z0-9]/.test(password)) strength += 15;
      
      const progressBar = strengthBar.querySelector(".progress-bar");
      progressBar.style.width = `${strength}%`;
      
      if (strength < 30) {
        progressBar.className = "progress-bar bg-danger";
        strengthText.textContent = "Weak";
      } else if (strength < 60) {
        progressBar.className = "progress-bar bg-warning";
        strengthText.textContent = "Medium";
      } else if (strength < 80) {
        progressBar.className = "progress-bar bg-info";
        strengthText.textContent = "Good";
      } else {
        progressBar.className = "progress-bar bg-success";
        strengthText.textContent = "Strong";
      }
    });
  });

  // Date picker enhancement
  document.querySelectorAll('input[type="date"]').forEach((input) => {
    input.min = new Date().toISOString().split("T")[0];
  });

  // Search filter enhancement
  const searchInputs = document.querySelectorAll("[data-search]");
  searchInputs.forEach((input) => {
    const debounceTimer = null;
    input.addEventListener("input", (event) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const searchTerm = event.target.value.toLowerCase();
        const targetSelector = input.dataset.search;
        const targets = document.querySelectorAll(targetSelector);
        
        targets.forEach((target) => {
          const text = target.textContent.toLowerCase();
          target.style.display = text.includes(searchTerm) ? "" : "none";
        });
      }, 300);
    });
  });

  // Notification badge update
  const updateNotificationBadge = () => {
    const badge = document.querySelector(".notification-badge");
    if (badge) {
      const count = parseInt(badge.textContent);
      if (count === 0) {
        badge.style.display = "none";
      } else {
        badge.style.display = "inline-block";
      }
    }
  };
  updateNotificationBadge();

  // Print functionality
  document.querySelectorAll("[data-print]").forEach((button) => {
    button.addEventListener("click", () => {
      window.print();
    });
  });

  // Export functionality
  document.querySelectorAll("[data-export]").forEach((button) => {
    button.addEventListener("click", () => {
      const format = button.dataset.export;
      const table = document.querySelector(button.dataset.target);
      if (table && format === "csv") {
        const rows = Array.from(table.querySelectorAll("tr"));
        const csv = rows
          .map((row) => {
            const cells = Array.from(row.querySelectorAll("td, th"));
            return cells.map((cell) => cell.textContent).join(",");
          })
          .join("\n");
        
        const blob = new Blob([csv], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "export.csv";
        a.click();
        window.URL.revokeObjectURL(url);
      }
    });
  });
});
