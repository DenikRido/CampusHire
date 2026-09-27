(function (window) {
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
    return "";
  }

  async function api(path, options = {}) {
    const headers = Object.assign(
      {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      options.body instanceof FormData ? {} : { "Content-Type": "application/json" },
      options.headers || {}
    );
    const token = localStorage.getItem("ch_access");
    if (token) headers.Authorization = `Bearer ${token}`;

    const resp = await fetch(path, Object.assign({}, options, { headers, credentials: "same-origin" }));
    const text = await resp.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch (err) {
      data = { message: text };
    }
    if (!resp.ok) {
      const error = new Error((data && (data.message || data.detail)) || "Request failed");
      error.status = resp.status;
      error.payload = data;
      throw error;
    }
    return data;
  }

  function showAlert(container, message, kind) {
    if (!container) return;
    container.innerHTML = `<div class="alert alert-${kind || "danger"} py-2 px-3">${message}</div>`;
  }

  function statusClass(status) {
    return String(status || "").toLowerCase();
  }

  function badge(status) {
    const label = String(status || "").replaceAll("_", " ");
    return `<span class="badge-status ${statusClass(status)}">${label}</span>`;
  }

  function formatMoney(n) {
    if (n === null || n === undefined) return "—";
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
  }

  window.CampusHire = {
    api,
    getCookie,
    showAlert,
    badge,
    formatMoney,
  };
})(window);
