document.addEventListener("DOMContentLoaded", () => {
  const list = document.getElementById("notification-list");
  if (!list) return;

  async function render() {
    const data = await CampusHire.api("/api/notifications/");
    const items = data.results || data;
    if (!items.length) {
      list.innerHTML = `<div class="empty">No notifications yet.</div>`;
      return;
    }
    list.innerHTML = items
      .map(
        (n) => `
      <article class="panel mb-2 ${n.is_read ? "" : "border-dark"}">
        <div class="d-flex justify-content-between gap-3">
          <div>
            <h3 class="h6 mb-1">${n.title}</h3>
            <p class="mb-1">${n.message}</p>
            <small class="muted">${new Date(n.created_at).toLocaleString()}</small>
          </div>
          ${n.is_read ? "" : `<button class="btn btn-sm btn-outline-primary" data-read="${n.id}">Mark read</button>`}
        </div>
      </article>`
      )
      .join("");
  }

  list.addEventListener("click", async (e) => {
    const id = e.target.getAttribute("data-read");
    if (!id) return;
    await CampusHire.api(`/api/notifications/${id}/read/`, { method: "PATCH", body: "{}" });
    render();
  });

  const all = document.getElementById("mark-all-read");
  if (all) {
    all.addEventListener("click", async () => {
      await CampusHire.api("/api/notifications/read-all/", { method: "POST", body: "{}" });
      render();
    });
  }

  render().catch((err) => {
    list.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  });
});
