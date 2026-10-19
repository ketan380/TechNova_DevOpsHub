/**
 * DevOpsHub - Frontend Interactive Logic
 * TechNova Cloud Computing Internship Task 4: Docker Containerization
 * Handles Text Processing, JSON Formatting & Validation, System Health Polling, and API Testing.
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initTextUtility();
  initJsonUtility();
  initHealthMonitor();
  initApiTester();
});

// =====================================================================
// Toast Notification Utility (Accessible Live Region)
// =====================================================================

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast-msg toast-${type}`;
  toast.setAttribute("role", "status");
  
  let icon = "bi-info-circle";
  if (type === "success") icon = "bi-check-circle-fill";
  if (type === "error") icon = "bi-exclamation-triangle-fill";

  toast.innerHTML = `<i class="bi ${icon}"></i> <span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.25s ease";
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// =====================================================================
// Navbar & Section Active Tracking
// =====================================================================

function initNavbar() {
  const navLinks = document.querySelectorAll(".nav-link-custom");
  const sections = document.querySelectorAll(".section-block");

  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach((section) => {
      const sectionTop = section.offsetTop - 120;
      if (window.scrollY >= sectionTop) {
        current = section.getAttribute("id");
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove("active");
      if (link.getAttribute("href") === `#${current}`) {
        link.classList.add("active");
      }
    });
  });
}

// =====================================================================
// Feature B: Text Utility Tool
// =====================================================================

function initTextUtility() {
  const textarea = document.getElementById("text-input");
  const btnUppercase = document.getElementById("btn-uppercase");
  const btnLowercase = document.getElementById("btn-lowercase");
  const btnWhitespace = document.getElementById("btn-whitespace");
  const btnCopy = document.getElementById("btn-copy-text");
  const btnClear = document.getElementById("btn-clear-text");
  const btnAnalyzeApi = document.getElementById("btn-analyze-api");

  const statWords = document.getElementById("stat-words");
  const statChars = document.getElementById("stat-chars");
  const statCharsNoSpace = document.getElementById("stat-chars-nospace");
  const statLines = document.getElementById("stat-lines");
  const statBytes = document.getElementById("stat-bytes");

  function calculateLocalMetrics(text) {
    const chars = text.length;
    const charsNoSpace = text.replace(/\s+/g, "").length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const lines = text ? text.split(/\r\n|\r|\n/).length : 0;
    const bytes = new Blob([text]).size;

    statWords.textContent = words.toLocaleString();
    statChars.textContent = chars.toLocaleString();
    statCharsNoSpace.textContent = charsNoSpace.toLocaleString();
    statLines.textContent = lines.toLocaleString();
    statBytes.textContent = `${bytes} B`;
  }

  // Real-time calculation on input
  textarea.addEventListener("input", () => {
    calculateLocalMetrics(textarea.value);
  });

  // Action: Uppercase
  btnUppercase.addEventListener("click", () => {
    if (!textarea.value) {
      showToast("Text area is empty. Please enter some text.", "error");
      return;
    }
    textarea.value = textarea.value.toUpperCase();
    calculateLocalMetrics(textarea.value);
    showToast("Converted text to UPPERCASE.", "success");
  });

  // Action: Lowercase
  btnLowercase.addEventListener("click", () => {
    if (!textarea.value) {
      showToast("Text area is empty. Please enter some text.", "error");
      return;
    }
    textarea.value = textarea.value.toLowerCase();
    calculateLocalMetrics(textarea.value);
    showToast("Converted text to lowercase.", "success");
  });

  // Action: Remove Extra Whitespace
  btnWhitespace.addEventListener("click", () => {
    if (!textarea.value) {
      showToast("Text area is empty. Please enter some text.", "error");
      return;
    }
    // Replace multiple spaces with a single space, trim each line
    const cleaned = textarea.value
      .split(/\r?\n/)
      .map((line) => line.replace(/[ \t]+/g, " ").trim())
      .filter((line, idx, arr) => line !== "" || (idx > 0 && arr[idx - 1] !== ""))
      .join("\n")
      .trim();

    textarea.value = cleaned;
    calculateLocalMetrics(textarea.value);
    showToast("Removed redundant whitespace and trailing spaces.", "success");
  });

  // Action: Copy Processed Text
  btnCopy.addEventListener("click", async () => {
    if (!textarea.value) {
      showToast("Nothing to copy. Enter text first.", "error");
      return;
    }
    try {
      await navigator.clipboard.writeText(textarea.value);
      showToast("Copied text to clipboard!", "success");
    } catch (err) {
      // Fallback for older browsers
      textarea.select();
      document.execCommand("copy");
      showToast("Copied text to clipboard (fallback)!", "success");
    }
  });

  // Action: Clear
  btnClear.addEventListener("click", () => {
    textarea.value = "";
    calculateLocalMetrics("");
    showToast("Text area cleared.", "info");
    textarea.focus();
  });

  // Action: Analyze via Flask REST API (/api/text/analyze)
  btnAnalyzeApi.addEventListener("click", async () => {
    const content = textarea.value;
    btnAnalyzeApi.disabled = true;
    btnAnalyzeApi.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calling API...`;

    try {
      const response = await fetch("/api/text/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: content })
      });

      const data = await response.json();
      if (response.ok && data.success) {
        const m = data.metrics;
        statWords.textContent = m.word_count.toLocaleString();
        statChars.textContent = m.character_count.toLocaleString();
        statCharsNoSpace.textContent = m.character_count_no_spaces.toLocaleString();
        statLines.textContent = m.line_count.toLocaleString();
        statBytes.textContent = `${m.byte_size} B`;
        showToast("Analysis verified via Flask Backend (/api/text/analyze)!", "success");
      } else {
        showToast(data.error || "Analysis failed.", "error");
      }
    } catch (err) {
      showToast("Failed to connect to Flask API backend.", "error");
    } finally {
      btnAnalyzeApi.disabled = false;
      btnAnalyzeApi.innerHTML = `<i class="bi bi-cpu"></i> Analyze via Flask API`;
    }
  });
}

// =====================================================================
// Feature C: JSON Formatter & Validator
// =====================================================================

function initJsonUtility() {
  const jsonInput = document.getElementById("json-input");
  const indentSelect = document.getElementById("json-indent");
  const btnFormat = document.getElementById("btn-format-json");
  const btnMinify = document.getElementById("btn-minify-json");
  const btnSampleValid = document.getElementById("btn-sample-valid");
  const btnSampleInvalid = document.getElementById("btn-sample-invalid");
  const btnCopyJson = document.getElementById("btn-copy-json");
  const btnClearJson = document.getElementById("btn-clear-json");

  const alertContainer = document.getElementById("json-alert-container");
  const outputContainer = document.getElementById("json-output-wrapper");
  const outputCode = document.getElementById("json-output-code");
  const outputMeta = document.getElementById("json-output-meta");

  function clearAlerts() {
    alertContainer.innerHTML = "";
    outputContainer.style.display = "none";
  }

  // Load Valid Sample
  btnSampleValid.addEventListener("click", () => {
    jsonInput.value = JSON.stringify(
      {
        project: "DevOpsHub",
        task: "TechNova Cloud Computing Internship Task 4",
        container: {
          image: "devopshub:1.0",
          base: "python:3.12-slim",
          port: 5000,
          nonRootUser: true
        },
        services: ["Flask", "Gunicorn", "Pytest", "Docker Compose"],
        active: true
      },
      null,
      2
    );
    clearAlerts();
    showToast("Loaded valid JSON demonstration sample.", "info");
  });

  // Load Invalid Sample
  btnSampleInvalid.addEventListener("click", () => {
    jsonInput.value = `{\n  "project": "DevOpsHub",\n  "syntaxError": true\n  "missingComma": "Notice missing comma on line 3"\n}`;
    clearAlerts();
    showToast("Loaded invalid JSON sample with missing comma.", "warning");
  });

  // Format and Validate via Backend API
  btnFormat.addEventListener("click", async () => {
    const rawText = jsonInput.value.trim();
    if (!rawText) {
      clearAlerts();
      alertContainer.innerHTML = `
        <div class="alert-box error" role="alert">
          <i class="bi bi-exclamation-triangle-fill"></i>
          <div><strong>Empty Input:</strong> Please enter or paste JSON to validate.</div>
        </div>`;
      showToast("JSON input is empty.", "error");
      return;
    }

    const indent = parseInt(indentSelect.value, 10) || 2;
    btnFormat.disabled = true;
    btnFormat.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span> Validating...`;

    try {
      const response = await fetch("/api/json/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ json_string: rawText, indent: indent })
      });

      const data = await response.json();
      clearAlerts();

      if (response.ok && data.valid) {
        alertContainer.innerHTML = `
          <div class="alert-box success" role="status">
            <i class="bi bi-check-circle-fill"></i>
            <div>
              <strong>Valid JSON Syntax!</strong> Verified successfully by Flask backend.<br>
              <span class="text-muted">Type: <code>${data.type}</code> | Items: <code>${data.item_count}</code> | Size: <code>${data.size_bytes} bytes</code></span>
            </div>
          </div>`;

        outputCode.textContent = data.formatted;
        outputMeta.textContent = `Formatted (${indent} spaces) • ${data.size_bytes} bytes`;
        outputContainer.style.display = "block";
        showToast("JSON formatted and validated successfully!", "success");
      } else {
        alertContainer.innerHTML = `
          <div class="alert-box error" role="alert">
            <i class="bi bi-x-octagon-fill"></i>
            <div>
              <strong>JSON Syntax Error:</strong> ${escapeHtml(data.error || "Invalid JSON syntax")}<br>
              ${data.line ? `<span class="text-dim">Location: Line <strong>${data.line}</strong>, Column <strong>${data.column}</strong></span>` : ""}
            </div>
          </div>`;
        showToast("JSON validation failed: Syntax error.", "error");
      }
    } catch (err) {
      showToast("Network error connecting to Flask JSON validator.", "error");
    } finally {
      btnFormat.disabled = false;
      btnFormat.innerHTML = `<i class="bi bi-check2-circle"></i> Format & Validate`;
    }
  });

  // Minify JSON
  btnMinify.addEventListener("click", () => {
    const rawText = jsonInput.value.trim();
    if (!rawText) {
      showToast("Enter JSON before minifying.", "error");
      return;
    }
    try {
      const parsed = JSON.parse(rawText);
      const minified = JSON.stringify(parsed);
      jsonInput.value = minified;
      outputCode.textContent = minified;
      outputMeta.textContent = `Minified • ${new Blob([minified]).size} bytes`;
      outputContainer.style.display = "block";
      alertContainer.innerHTML = `
        <div class="alert-box success" role="status">
          <i class="bi bi-check-circle-fill"></i>
          <div><strong>Successfully Minified JSON:</strong> Removed all superfluous whitespace.</div>
        </div>`;
      showToast("JSON minified successfully.", "success");
    } catch (err) {
      alertContainer.innerHTML = `
        <div class="alert-box error" role="alert">
          <i class="bi bi-x-octagon-fill"></i>
          <div><strong>Cannot Minify:</strong> ${escapeHtml(err.message)}</div>
        </div>`;
      showToast("Cannot minify invalid JSON.", "error");
    }
  });

  // Copy Output
  btnCopyJson.addEventListener("click", async () => {
    const content = outputCode.textContent;
    if (!content) {
      showToast("No formatted output to copy.", "error");
      return;
    }
    await navigator.clipboard.writeText(content);
    showToast("Formatted JSON copied to clipboard!", "success");
  });

  // Clear
  btnClearJson.addEventListener("click", () => {
    jsonInput.value = "";
    clearAlerts();
    showToast("JSON workspace cleared.", "info");
    jsonInput.focus();
  });
}

// =====================================================================
// Feature D: System & Application Health Polling
// =====================================================================

function initHealthMonitor() {
  const btnRefresh = document.getElementById("btn-refresh-health");
  const healthBadge = document.getElementById("health-status-badge");
  const uptimeVal = document.getElementById("uptime-metric");
  const serverTimeVal = document.getElementById("server-time-metric");

  async function fetchLiveHealth() {
    if (!btnRefresh) return;
    btnRefresh.disabled = true;
    btnRefresh.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span> Updating...`;

    try {
      const response = await fetch("/api/health");
      const data = await response.json();
      if (response.ok && data.status === "healthy") {
        if (healthBadge) {
          healthBadge.innerHTML = `<span class="pulse-dot"></span> Active & Healthy`;
          healthBadge.className = "status-pill healthy";
        }
        if (uptimeVal) {
          const up = data.uptime_seconds;
          const mins = Math.floor(up / 60);
          const secs = up % 60;
          uptimeVal.textContent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
        }
        if (serverTimeVal) {
          serverTimeVal.textContent = data.timestamp;
        }
        showToast("System health metrics refreshed.", "info");
      }
    } catch (err) {
      if (healthBadge) {
        healthBadge.innerHTML = `<span class="pulse-dot"></span> Disconnected`;
        healthBadge.className = "status-pill";
        healthBadge.style.backgroundColor = "rgba(239, 68, 68, 0.15)";
        healthBadge.style.color = "#f87171";
      }
      showToast("Failed to fetch health check from server.", "error");
    } finally {
      btnRefresh.disabled = false;
      btnRefresh.innerHTML = `<i class="bi bi-arrow-clockwise"></i> Refresh Live Health`;
    }
  }

  if (btnRefresh) {
    btnRefresh.addEventListener("click", fetchLiveHealth);
  }
}

// =====================================================================
// Feature E: Interactive REST API Tester
// =====================================================================

function initApiTester() {
  const apiButtons = document.querySelectorAll(".btn-test-api");
  const apiModalCode = document.getElementById("api-test-output");
  const apiModalStatus = document.getElementById("api-test-status");
  const apiModalTitle = document.getElementById("api-test-endpoint-title");

  apiButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const endpoint = btn.getAttribute("data-endpoint");
      const method = btn.getAttribute("data-method");
      let body = null;

      if (endpoint === "/api/text/analyze") {
        body = JSON.stringify({ text: "TechNova Cloud Computing Task 4: Docker Containerization testing." });
      } else if (endpoint === "/api/json/validate") {
        body = JSON.stringify({ json_string: '{"service":"DevOpsHub","status":"operational"}', indent: 2 });
      }

      apiModalTitle.textContent = `${method} ${endpoint}`;
      apiModalStatus.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Sending request...`;
      apiModalCode.textContent = "Waiting for response...";

      const modalElement = document.getElementById("apiTestModal");
      const modal = new bootstrap.Modal(modalElement);
      modal.show();

      const startTime = performance.now();
      try {
        const options = {
          method: method,
          headers: body ? { "Content-Type": "application/json" } : {}
        };
        if (body) options.body = body;

        const res = await fetch(endpoint, options);
        const duration = Math.round(performance.now() - startTime);
        const jsonRes = await res.json();

        apiModalStatus.innerHTML = `<span class="badge ${res.ok ? "bg-success" : "bg-danger"}">${res.status} ${res.statusText}</span> <span class="text-muted ms-2">${duration} ms</span>`;
        apiModalCode.textContent = JSON.stringify(jsonRes, null, 2);
      } catch (err) {
        apiModalStatus.innerHTML = `<span class="badge bg-danger">Network Error</span>`;
        apiModalCode.textContent = `Error: ${err.message}`;
      }
    });
  });
}
