document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("access");
  const table = document.querySelector("#sectionsTable tbody");
  const modal = document.getElementById("sectionModal");
  const form = modal.querySelector(".modal-form");
  const fields = modal.querySelector(".form-fields");

  const api = async (url, opts = {}) => {
    const res = await fetch(url, {
      ...opts,
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Request failed");
    return res.json();
  };

  const [courses, terms, professors] = await Promise.all([
    api("/api/courses/"),
    api("/api/terms/"),
    api("/api/users/me/"), // current user for testing
  ]);

  const render = async () => {
    const sections = await api("/api/sections/");
    table.innerHTML = "";
    sections.forEach((sec) => {
      const course = (courses.find((c) => c.id === sec.course) || {}).title || sec.course;
      const term = (terms.find((t) => t.id === sec.term) || {});
      const profs = (sec.professors || []).join(", ") || "TBA";
      const tr = document.createElement("tr");
      tr.className = "border-b";
      tr.innerHTML = `
        <td class="px-4 py-2">${sec.code}</td>
        <td class="px-4 py-2">${course}</td>
        <td class="px-4 py-2">${term.school_year ? term.school_year + " (" + term.semester + ")" : "-"}</td>
        <td class="px-4 py-2">${profs}</td>
        <td class="px-4 py-2">${sec.capacity}</td>
        <td class="px-4 py-2">${sec.slots_remaining}</td>
        <td class="px-4 py-2">
          <button data-del="${sec.id}" class="text-red-600 hover:underline">Archive</button>
        </td>`;
      table.appendChild(tr);
    });
  };

  const buildForm = async () => {
    const profs = await api("/api/users/?role=PROFESSOR"); // you’ll need to expose this endpoint
    fields.innerHTML = `
      <label class="block"><span>Code</span><input name="code" class="w-full border rounded p-2"/></label>
      <label class="block"><span>Course</span><select name="course" class="w-full border rounded p-2">
        ${courses.map(c => `<option value="${c.id}">${c.title}</option>`).join("")}
      </select></label>
      <label class="block"><span>Term</span><select name="term" class="w-full border rounded p-2">
        ${terms.map(t => `<option value="${t.id}">${t.school_year} (${t.semester})</option>`).join("")}
      </select></label>
      <label class="block"><span>Professors (multi-select)</span>
        <select name="professors" multiple class="w-full border rounded p-2">
          ${profs.map(p => `<option value="${p.id}">${p.first_name} ${p.last_name}</option>`).join("")}
        </select>
      </label>
      <label class="block"><span>Capacity</span><input type="number" name="capacity" value="30" class="w-full border rounded p-2"/></label>
    `;
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {};
    form.querySelectorAll("input, select").forEach((f) => {
      if (f.multiple) data[f.name] = Array.from(f.selectedOptions).map(o => o.value);
      else data[f.name] = f.value;
    });
    await api("/api/sections/", { method: "POST", body: JSON.stringify(data) });
    modal.classList.add("hidden");
    render();
  });

  table.addEventListener("click", async (e) => {
    if (e.target.dataset.del) {
      await api(`/api/sections/${e.target.dataset.del}/`, { method: "DELETE" });
      render();
    }
  });

  await buildForm();
  render();
});
