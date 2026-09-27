document.addEventListener("DOMContentLoaded", () => {
  const box = document.getElementById("eligibility-box");
  if (!box) return;
  const jobId = box.getAttribute("data-job-id");
  CampusHire.api(`/api/jobs/${jobId}/eligibility/`)
    .then((data) => {
      if (data.eligible) {
        box.innerHTML = `<div class="alert alert-success mb-0">You meet the eligibility criteria for this role.</div>`;
        const apply = document.getElementById("apply-actions");
        if (apply) apply.classList.remove("d-none");
      } else {
        const reasons = (data.reasons || []).map((r) => `<li>${r}</li>`).join("");
        box.innerHTML = `<div class="alert alert-warning mb-0"><strong>Not eligible yet</strong><ul class="mb-0 mt-2">${reasons}</ul></div>`;
      }
    })
    .catch((err) => {
      box.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    });

  const form = document.getElementById("apply-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const alertBox = document.getElementById("apply-alert");
      try {
        await CampusHire.api("/api/applications/", {
          method: "POST",
          body: JSON.stringify({
            job_id: Number(jobId),
            cover_letter: form.cover_letter.value,
          }),
        });
        window.location.href = "/student/applications/";
      } catch (err) {
        const reasons = err.payload && err.payload.reasons;
        CampusHire.showAlert(
          alertBox,
          reasons ? reasons.join(" · ") : err.message,
          "warning"
        );
      }
    });
  }
});
