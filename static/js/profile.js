document.addEventListener("DOMContentLoaded", () => {
  const profileForm = document.getElementById("profile-form");
  if (profileForm) {
    profileForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(profileForm);
      const payload = Object.fromEntries(fd.entries());
      if (payload.cgpa) payload.cgpa = payload.cgpa;
      if (payload.backlogs) payload.backlogs = Number(payload.backlogs);
      if (payload.graduation_year) payload.graduation_year = Number(payload.graduation_year);
      const alertBox = document.getElementById("profile-alert");
      try {
        await CampusHire.api("/api/students/me/", { method: "PUT", body: JSON.stringify(payload) });
        CampusHire.showAlert(alertBox, "Profile saved.", "success");
      } catch (err) {
        CampusHire.showAlert(alertBox, err.message);
      }
    });
  }

  const resumeForm = document.getElementById("resume-form");
  if (resumeForm) {
    resumeForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const alertBox = document.getElementById("resume-alert");
      const data = new FormData(resumeForm);
      try {
        await CampusHire.api("/api/students/me/resume/", { method: "POST", body: data });
        CampusHire.showAlert(alertBox, "Resume uploaded.", "success");
      } catch (err) {
        CampusHire.showAlert(alertBox, err.message);
      }
    });
  }

  const skillForm = document.getElementById("skill-form");
  if (skillForm) {
    skillForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      await CampusHire.api("/api/students/me/skills/", {
        method: "POST",
        body: JSON.stringify({
          skill_name: skillForm.skill_name.value,
          proficiency: skillForm.proficiency.value,
        }),
      });
      window.location.reload();
    });
  }

  document.querySelectorAll("[data-skill-delete]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await CampusHire.api(`/api/students/me/skills/${btn.getAttribute("data-skill-delete")}/`, { method: "DELETE" });
      window.location.reload();
    });
  });

  const companyForm = document.getElementById("company-form");
  if (companyForm) {
    companyForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(companyForm);
      const payload = Object.fromEntries(fd.entries());
      const alertBox = document.getElementById("company-alert");
      const id = companyForm.getAttribute("data-id");
      try {
        if (id) {
          await CampusHire.api(`/api/companies/${id}/`, { method: "PUT", body: JSON.stringify(payload) });
        } else {
          await CampusHire.api("/api/companies/", { method: "POST", body: JSON.stringify(payload) });
        }
        CampusHire.showAlert(alertBox, "Company profile saved.", "success");
        setTimeout(() => window.location.reload(), 600);
      } catch (err) {
        CampusHire.showAlert(alertBox, err.message);
      }
    });
  }

  const jobForm = document.getElementById("job-form");
  if (jobForm) {
    jobForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(jobForm);
      const payload = {
        title: fd.get("title"),
        description: fd.get("description"),
        employment_type: fd.get("employment_type"),
        location: fd.get("location"),
        minimum_cgpa: fd.get("minimum_cgpa"),
        maximum_backlogs: Number(fd.get("maximum_backlogs") || 0),
        eligible_departments: fd.getAll("eligible_departments"),
        eligible_degrees: fd.getAll("eligible_degrees"),
        graduation_year: fd.get("graduation_year") ? Number(fd.get("graduation_year")) : null,
        salary_min: fd.get("salary_min") ? Number(fd.get("salary_min")) : null,
        salary_max: fd.get("salary_max") ? Number(fd.get("salary_max")) : null,
        required_skill_ids: fd.getAll("required_skill_ids").map(Number),
        application_deadline: fd.get("application_deadline"),
      };
      const id = jobForm.getAttribute("data-id");
      const alertBox = document.getElementById("job-alert");
      try {
        if (id) {
          await CampusHire.api(`/api/jobs/${id}/`, { method: "PUT", body: JSON.stringify(payload) });
        } else {
          const created = await CampusHire.api("/api/jobs/", { method: "POST", body: JSON.stringify(payload) });
          await CampusHire.api(`/api/jobs/${created.id}/submit/`, { method: "POST", body: "{}" });
        }
        window.location.href = "/recruiter/jobs/";
      } catch (err) {
        CampusHire.showAlert(alertBox, err.message);
      }
    });
  }
});
