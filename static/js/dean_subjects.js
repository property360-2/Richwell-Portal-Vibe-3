document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("access");
  const table = document.querySelector("#subjectsTable tbody");
  const modal = document.getElementById("subjectModal");
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

  let courses = await api("/api/courses/");
  let subjects = [];

  const render = (data) => {
    table.innerHTML = "";
    data.forEach((s) => {
      const course = (courses.find((c) => c.id === s.course) || {}).title || s.course;
      const prereqs = s.prerequisites ? s.prerequisites.map(p => p.prerequisite_code).join(", ") : "";
      const tr = document.createElement("tr");
      tr.className = "border-b";
      tr.innerHTML = `
        <td class="px-4 py-2">${s.code}</td>
        <td class="px-4 py-2">${s.title}</td>
        <td class="px-4 py-2">${s.units}</td>
        <td class="px-4 py-2">${s.subject_type}</td>
        <td class="px-4 py-2">${course}</td>
        <td class="px-4 py-2">${prereqs}</td>
        <td class="px-4 py-2">
          <button data-del="${s.id}" class="text-red-600 hover:underline">Archive</button>
        </td>`;
      table.appendChild(tr);
    });
  };

  const load = async () => {
    subjects = await api("/api/subjects/");
    render(subjects);
    buildForm();
  };

  const buildForm = () => {
    fields.innerHTML = `
      <label class="block"><span>Code</span><input name="code" class="w-full border rounded p-2"/></label>
      <label class="block"><span>Title</span><input name="title" class="w-full border rounded p-2"/></label>
      <label class="block"><span>Units</span><input type="number" name="units" value="3" class="w-full border rounded p-2"/></label>
      <label class="block"><span>Type</span>
        <select name="subject_type" class="w-full border rounded p-2">
          <option value="MAJOR">MAJOR</option>
          <option value="MINOR">MINOR</option>
        </select>
      </label>
      <label class="block"><span>Course</span>
        <select name="course" class="w-full border rounded p-2">
          ${courses.map(c => `<option value="${c.id}">${c.title}</option>`).join("")}
        </select>
      </label>
      <label class="block"><span>Prerequisites (Ctrl+Click to select multiple)</span>
        <select name="prerequisites" multiple class="w-full border rounded p-2">
          ${subjects.map(s => `<option value="${s.id}">${s.code} - ${s.title}</option>`).join("")}
        </select>
      </label>
    `;
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {};
    form.querySelectorAll("input, select").forEach((f) => {
      if (f.multiple) {
        data[f.name] = Array.from(f.selectedOptions).map((o) => o.value);
      } else {
        data[f.name] = f.value;
      }
    });
    await api("/api/subjects/", { method: "POST", body: JSON.stringify(data) });
    modal.classList.add("hidden");
    load();
  });

  table.addEventListener("click", async (e) => {
    if (e.target.dataset.del) {
      await api(`/api/subjects/${e.target.dataset.del}/`, { method: "DELETE" });
      load();
    }
  });

  load();
});
