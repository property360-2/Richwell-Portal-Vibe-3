document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access");
    const table = document.querySelector("#coursesTable tbody");
    const modal = document.getElementById("courseModal");
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

    const render = (courses) => {
        table.innerHTML = "";
        courses.forEach((c) => {
            const tr = document.createElement("tr");
            tr.className = "border-b";
            tr.innerHTML = `
        <td class="px-4 py-2">${c.code}</td>
        <td class="px-4 py-2">${c.title}</td>
        <td class="px-4 py-2">${c.description || ""}</td>
        <td class="px-4 py-2">${c.sector}</td>
        <td class="px-4 py-2">
          <button data-edit="${c.id}" class="text-indigo-600 hover:underline">Edit</button>
          <button data-del="${c.id}" class="text-red-600 hover:underline ml-2">Archive</button>
        </td>`;
            table.appendChild(tr);
        });
    };

    const load = async () => render(await api("/api/courses/"));

    fields.innerHTML = `
    <label class="block"><span>Code</span><input name="code" class="w-full border rounded p-2"/></label>
    <label class="block"><span>Title</span><input name="title" class="w-full border rounded p-2"/></label>
    <label class="block"><span>Description</span><textarea name="description" class="w-full border rounded p-2"></textarea></label>
    <label class="block"><span>Sector</span>
      <select name="sector" class="w-full border rounded p-2">
        <option value="COLLEGE">Higher Education / College</option>
        <option value="SHS">Senior High School</option>
        <option value="TVET">Technical-Vocational</option>
      </select>
    </label>
  `;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const data = {};
        form.querySelectorAll("input, select, textarea").forEach((f) => (data[f.name] = f.value));
        await api("/api/courses/", { method: "POST", body: JSON.stringify(data) });
        modal.classList.add("hidden");
        load();
    });

    table.addEventListener("click", async (e) => {
        if (e.target.dataset.del) {
            await api(`/api/courses/${e.target.dataset.del}/`, { method: "DELETE" });
            load();
        }
    });

    load();
});
