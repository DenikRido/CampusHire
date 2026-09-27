document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("job-grid");
  if (!grid) return;
  const search = document.getElementById("job-search");
  const location = document.getElementById("job-location");
  const department = document.getElementById("job-department");
  const employment = document.getElementById("job-employment");
  const pager = document.getElementById("job-pager");
  const empty = document.getElementById("job-empty");
  const loading = document.getElementById("job-loading");
  let page = 1;

  async function load() {
    loading.classList.remove("d-none");
    empty.classList.add("d-none");
    const params = new URLSearchParams();
    if (search.value) params.set("search", search.value);
    if (location.value) params.set("location", location.value);
    if (department.value) params.set("department", department.value);
    if (employment.value) params.set("employment_type", employment.value);
    params.set("page", String(page));
    try {
      const data = await CampusHire.api(`/api/jobs/?${params.toString()}`);
      const results = data.results || data;
      grid.innerHTML = results
        .map(
          (job) => `
        <div class="col-md-6 col-xl-4">
          <article class="job-card">
            <div class="d-flex justify-content-between gap-2">
              <p class="muted mb-0">${job.company_name}</p>
              ${CampusHire.badge(job.employment_type)}
            </div>
            <h3><a href="/student/jobs/${job.id}/">${job.title}</a></h3>
            <p class="muted mb-1">${job.location} · ${job.salary_range}</p>
            <p class="mb-2">${(job.description || "").slice(0, 140)}…</p>
            <div class="mt-auto d-flex justify-content-between align-items-center">
              <small class="muted">Deadline ${new Date(job.application_deadline).toLocaleDateString()}</small>
              <a class="btn btn-sm btn-primary" href="/student/jobs/${job.id}/">View</a>
            </div>
          </article>
        </div>`
        )
        .join("");
      if (!results.length) empty.classList.remove("d-none");
      const next = data.next ? `<button class="btn btn-outline-primary btn-sm" data-dir="next">Next</button>` : "";
      const prev = data.previous ? `<button class="btn btn-outline-primary btn-sm" data-dir="prev">Previous</button>` : "";
      pager.innerHTML = `${prev} ${next}`;
    } catch (err) {
      grid.innerHTML = `<p class="muted">Could not load jobs. ${err.message}</p>`;
    } finally {
      loading.classList.add("d-none");
    }
  }

  ["input", "change"].forEach((evt) => {
    [search, location, department, employment].forEach((el) => {
      el && el.addEventListener(evt, () => { page = 1; load(); });
    });
  });
  pager.addEventListener("click", (e) => {
    const dir = e.target.getAttribute("data-dir");
    if (dir === "next") page += 1;
    if (dir === "prev") page = Math.max(1, page - 1);
    if (dir) load();
  });
  load();
});
