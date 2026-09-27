document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("application-table");
  if (table) {
    const status = document.getElementById("app-status");
    async function load() {
      const params = new URLSearchParams();
      if (status && status.value) params.set("status", status.value);
      const jobId = table.getAttribute("data-job");
      if (jobId) params.set("job", jobId);
      const data = await CampusHire.api(`/api/applications/?${params.toString()}`);
      const rows = data.results || [];
      const body = table.querySelector("tbody");
      if (!rows.length) {
        body.innerHTML = `<tr><td colspan="5" class="empty">No applications found.</td></tr>`;
        return;
      }
      const isRecruiter = table.getAttribute("data-role") === "recruiter";
      body.innerHTML = rows
        .map((a) => {
          const href = isRecruiter ? `/recruiter/applications/${a.id}/` : `/student/applications/${a.id}/`;
          return `<tr>
            <td>${isRecruiter ? a.student_name : a.job.title}</td>
            <td>${isRecruiter ? a.registration_number : a.job.company_name}</td>
            <td>${CampusHire.badge(a.status)}</td>
            <td class="muted">${new Date(a.applied_at).toLocaleDateString()}</td>
            <td><a href="${href}">Open</a></td>
          </tr>`;
        })
        .join("");
    }
    if (status) status.addEventListener("change", load);
    load().catch((err) => {
      table.querySelector("tbody").innerHTML = `<tr><td colspan="5">${err.message}</td></tr>`;
    });
  }

  const statusForm = document.getElementById("status-form");
  if (statusForm) {
    statusForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const id = statusForm.getAttribute("data-id");
      const alertBox = document.getElementById("status-alert");
      try {
        await CampusHire.api(`/api/applications/${id}/status/`, {
          method: "PATCH",
          body: JSON.stringify({
            status: statusForm.status.value,
            remarks: statusForm.remarks.value,
          }),
        });
        window.location.reload();
      } catch (err) {
        CampusHire.showAlert(alertBox, err.message);
      }
    });
  }

  const withdraw = document.getElementById("withdraw-btn");
  if (withdraw) {
    withdraw.addEventListener("click", async () => {
      if (!confirm("Withdraw this application?")) return;
      const id = withdraw.getAttribute("data-id");
      await CampusHire.api(`/api/applications/${id}/withdraw/`, { method: "POST", body: "{}" });
      window.location.href = "/student/applications/";
    });
  }
});
