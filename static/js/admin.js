document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-verify]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-verify");
      const status = btn.getAttribute("data-status");
      await CampusHire.api(`/api/companies/${id}/verify/`, {
        method: "POST",
        body: JSON.stringify({ verification_status: status }),
      });
      window.location.reload();
    });
  });

  document.querySelectorAll("[data-job-action]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-id");
      const action = btn.getAttribute("data-job-action");
      await CampusHire.api(`/api/jobs/${id}/${action}/`, {
        method: "POST",
        body: JSON.stringify({ reason: "Reviewed by placement cell" }),
      });
      window.location.reload();
    });
  });
});
