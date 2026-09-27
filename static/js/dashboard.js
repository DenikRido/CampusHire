document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-dashboard]");
  if (!root) return;
  const kind = root.getAttribute("data-dashboard");
  CampusHire.api(`/api/dashboard/${kind}/`)
    .then((data) => {
      Object.entries(data).forEach(([key, value]) => {
        const el = root.querySelector(`[data-stat="${key}"]`);
        if (!el) return;
        if (typeof value === "object") {
          el.textContent = JSON.stringify(value);
        } else {
          el.textContent = value;
        }
      });
      const chart = document.getElementById("status-breakdown");
      if (chart && Array.isArray(data.applications_by_status)) {
        chart.innerHTML = data.applications_by_status
          .map(
            (row) =>
              `<div class="d-flex justify-content-between border-bottom py-2"><span>${row.status.replaceAll("_", " ")}</span><strong class="mono">${row.count}</strong></div>`
          )
          .join("");
      }
      const depts = document.getElementById("dept-breakdown");
      if (depts && Array.isArray(data.jobs_by_department)) {
        depts.innerHTML = data.jobs_by_department
          .map(
            (row) =>
              `<div class="d-flex justify-content-between border-bottom py-2"><span>${row.department}</span><strong class="mono">${row.count}</strong></div>`
          )
          .join("");
      }
      const companies = document.getElementById("company-breakdown");
      if (companies && Array.isArray(data.applications_by_company)) {
        companies.innerHTML = data.applications_by_company
          .map(
            (row) =>
              `<div class="d-flex justify-content-between border-bottom py-2"><span>${row.job__company__company_name}</span><strong class="mono">${row.count}</strong></div>`
          )
          .join("");
      }
    })
    .catch((err) => {
      root.insertAdjacentHTML("afterbegin", `<div class="alert alert-danger">${err.message}</div>`);
    });
});
