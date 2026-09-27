document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("interview-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const alertBox = document.getElementById("interview-alert");
    try {
      await CampusHire.api("/api/interviews/", {
        method: "POST",
        body: JSON.stringify({
          application_id: Number(fd.get("application_id")),
          scheduled_at: fd.get("scheduled_at"),
          mode: fd.get("mode"),
          meeting_link: fd.get("meeting_link"),
          interviewer_name: fd.get("interviewer_name"),
          notes: fd.get("notes"),
        }),
      });
      window.location.href = "/recruiter/interviews/";
    } catch (err) {
      CampusHire.showAlert(alertBox, err.message);
    }
  });
});
