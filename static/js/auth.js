document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const alertBox = document.getElementById("auth-alert");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(loginForm);
      try {
        const data = await CampusHire.api("/api/auth/login/", {
          method: "POST",
          body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }),
        });
        localStorage.setItem("ch_access", data.access);
        localStorage.setItem("ch_refresh", data.refresh);
        window.location.href = "/app/";
      } catch (err) {
        CampusHire.showAlert(alertBox, (err.payload && err.payload.message) || "Invalid email or password.");
      }
    });
  }

  if (registerForm) {
    const role = registerForm.querySelector("[name=role]");
    const studentFields = document.getElementById("student-fields");
    const recruiterFields = document.getElementById("recruiter-fields");
    const toggle = () => {
      const isStudent = role.value === "STUDENT";
      studentFields.classList.toggle("d-none", !isStudent);
      recruiterFields.classList.toggle("d-none", isStudent);
    };
    role.addEventListener("change", toggle);
    toggle();

    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(registerForm);
      const payload = Object.fromEntries(fd.entries());
      if (payload.graduation_year) payload.graduation_year = Number(payload.graduation_year);
      try {
        const data = await CampusHire.api("/api/auth/register/", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        localStorage.setItem("ch_access", data.access);
        localStorage.setItem("ch_refresh", data.refresh);
        window.location.href = "/app/";
      } catch (err) {
        const errors = err.payload && err.payload.errors;
        let msg = err.message;
        if (errors && typeof errors === "object") {
          msg = Object.entries(errors)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(" ") : v}`)
            .join(" · ");
        }
        CampusHire.showAlert(alertBox, msg);
      }
    });
  }
});
