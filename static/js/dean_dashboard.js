// ---------- helpers ----------
const token = localStorage.getItem("access");

const api = async (url, opts = {}) => {
  const res = await fetch(url, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(opts.headers || {}),
    },
  });
  if (!res.ok) {
    let msg = "Request failed";
    try { const j = await res.json(); msg = j.detail || JSON.stringify(j); } catch {}
    throw new Error(msg);
  }
  return res.status === 204 ? null : res.json();
};

const el = (sel, scope = document) => scope.querySelector(sel);
const els = (sel, scope = document) => [...scope.querySelectorAll(sel)];
const show = (n) => n.classList.remove("hidden");
const hide = (n) => n.classList.add("hidden");
const setAlert = (msg, ok = true) => {
  const box = el("#alertBox");
  box.textContent = msg;
  box.classList.toggle("bg-green-100", ok);
  box.classList.toggle("text-green-700", ok);
  box.classList.toggle("bg-red-100", !ok);
  box.classList.toggle("text-red-700", !ok);
  show(box);
  setTimeout(() => hide(box), 1800);
};

// ---------- state ----------
let cache = {
  courses: [],
  subjects: [],
  terms: [],
  professors: [], // pulled from users with role=PROFESSOR (we'll stub via admin for now)
  sections: [],
};

// ---------- bootstrap fetches ----------
const loadAll = async () => {
  const [courses, subjects, terms, sections] = await Promise.all([
    api("/api/courses/"),
    api("/api/subjects/"),
    api("/api/terms/"),
    api("/api/sections/"),
  ]);
  cache.courses = courses;
  cache.subjects = subjects;
  cache.terms = terms;
  cache.sections = sections;
  renderTables();
};

const renderTables = () => {
  // Courses
  const tbodyC = el("#coursesTable tbody");
  tbodyC.innerHTML = "";
  cache.courses.forEach((c) => {
    const tr = document.createElement("tr");
    tr.className = "border-b";
    tr.innerHTML = `
      <td class="px-4 py-2">${c.code}</td>
      <td class="px-4 py-2">${c.title}</td>
      <td class="px-4 py-2">${c.description || ""}</td>
      <td class="px-4 py-2">
        <button class="text-indigo-600 hover:underline" data-edit="course" data-id="${c.id}">Edit</button>
        <button class="text-red-600 hover:underline ml-2" data-archive="courses" data-id="${c.id}">Archive</button>
      </td>`;
    tbodyC.appendChild(tr);
  });

  // Subjects
  const tbodyS = el("#subjectsTable tbody");
  tbodyS.innerHTML = "";
  cache.subjects.forEach((s) => {
    const courseTitle = (cache.courses.find(x => x.id === s.course) || {}).title || s.course;
    const tr = document.createElement("tr");
    tr.className = "border-b";
    tr.innerHTML = `
      <td class="px-4 py-2">${s.code}</td>
      <td class="px-4 py-2">${s.title}</td>
      <td class="px-4 py-2">${s.units}</td>
      <td class="px-4 py-2">${s.subject_type}</td>
      <td class="px-4 py-2">${courseTitle}</td>
      <td class="px-4 py-2">
        <button class="text-indigo-600 hover:underline" data-edit="subject" data-id="${s.id}">Edit</button>
        <button class="text-red-600 hover:underline ml-2" data-archive="subjects" data-id="${s.id}">Archive</button>
      </td>`;
    tbodyS.appendChild(tr);
  });

  // Sections
  const tbodySec = el("#sectionsTable tbody");
  tbodySec.innerHTML = "";
  cache.sections.forEach((sec) => {
    const courseTitle = (cache.courses.find(x => x.id === sec.course) || {}).title || sec.course;
    const termLabel = (cache.terms.find(x => x.id === sec.term) || {});
    const profName = sec.professor_name || (sec.professor || "");
    const capText = `${sec.capacity || 0}/${sec.slots_remaining ?? sec.capacity ?? 0}`;

    const tr = document.createElement("tr");
    tr.className = "border-b";
    tr.innerHTML = `
      <td class="px-4 py-2">${sec.code}</td>
      <td class="px-4 py-2">${courseTitle}</td>
      <td class="px-4 py-2">${termLabel.school_year ? `${termLabel.school_year} (${termLabel.semester})` : sec.term}</td>
      <td class="px-4 py-2">${profName || "-"}</td>
      <td class="px-4 py-2">${capText}</td>
      <td class="px-4 py-2">
        <button class="text-indigo-600 hover:underline" data-edit="section" data-id="${sec.id}">Edit</button>
        <button class="text-red-600 hover:underline ml-2" data-archive="sections" data-id="${sec.id}">Archive</button>
      </td>`;
    tbodySec.appendChild(tr);
  });
};

// ---------- modal controls ----------
const openModal = (id) => show(el(`#${id}`));
const closeModal = (n) => hide(n);

els(".open-modal").forEach((b) => b.addEventListener("click", () => openModal(b.dataset.modal)));
els(".close-modal").forEach((b) => b.addEventListener("click", () => closeModal(b.closest(".modal"))));

// populate form fields per modal
const buildFields = (container, kind, defaults = {}) => {
  const html = {
    course: `
      <label class="block">
        <span class="text-sm">Code</span>
        <input name="code" value="${defaults.code||""}" class="w-full border rounded p-2"/>
      </label>
      <label class="block">
        <span class="text-sm">Title</span>
        <input name="title" value="${defaults.title||""}" class="w-full border rounded p-2"/>
      </label>
      <label class="block">
        <span class="text-sm">Description</span>
        <textarea name="description" class="w-full border rounded p-2">${defaults.description||""}</textarea>
      </label>
    `,
    subject: `
      <label class="block">
        <span class="text-sm">Code</span>
        <input name="code" value="${defaults.code||""}" class="w-full border rounded p-2"/>
      </label>
      <label class="block">
        <span class="text-sm">Title</span>
        <input name="title" value="${defaults.title||""}" class="w-full border rounded p-2"/>
      </label>
      <label class="block">
        <span class="text-sm">Units</span>
        <input type="number" min="0" name="units" value="${defaults.units||3}" class="w-full border rounded p-2"/>
      </label>
      <label class="block">
        <span class="text-sm">Type</span>
        <select name="subject_type" class="w-full border rounded p-2">
          <option value="MAJOR" ${defaults.subject_type==="MAJOR"?"selected":""}>MAJOR</option>
          <option value="MINOR" ${defaults.subject_type==="MINOR"?"selected":""}>MINOR</option>
        </select>
      </label>
      <label class="block">
        <span class="text-sm">Course</span>
        <select name="course" class="w-full border rounded p-2">
          ${cache.courses.map(c=>`<option value="${c.id}" ${defaults.course===c.id?"selected":""}>${c.title}</option>`).join("")}
        </select>
      </label>
    `,
    section: `
      <label class="block">
        <span class="text-sm">Code</span>
        <input name="code" value="${defaults.code||""}" class="w-full border rounded p-2"/>
      </label>
      <label class="block">
        <span class="text-sm">Course</span>
        <select name="course" class="w-full border rounded p-2">
          ${cache.courses.map(c=>`<option value="${c.id}" ${defaults.course===c.id?"selected":""}>${c.title}</option>`).join("")}
        </select>
      </label>
      <label class="block">
        <span class="text-sm">Term</span>
        <select name="term" class="w-full border rounded p-2">
          ${cache.terms.map(t=>`<option value="${t.id}" ${defaults.term===t.id?"selected":""}>${t.school_year} (${t.semester})</option>`).join("")}
        </select>
      </label>
      <label class="block">
        <span class="text-sm">Professor (user id)</span>
        <input name="professor" value="${defaults.professor||""}" class="w-full border rounded p-2" placeholder="Optional for now"/>
      </label>
      <label class="block">
        <span class="text-sm">Capacity</span>
        <input type="number" min="1" name="capacity" value="${defaults.capacity||30}" class="w-full border rounded p-2"/>
      </label>
    `,
  }[kind];

  container.innerHTML = html;
};

// wire up each modal
const wireModal = (modalId, kind, endpoint) => {
  const modal = el(`#${modalId}`);
  const form = el(".modal-form", modal);
  const fields = el(".form-fields", modal);
  buildFields(fields, kind);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {};
    els("input, select, textarea", form).forEach(i => data[i.name] = i.value);
    try {
      await api(`/api/${endpoint}/`, { method: "POST", body: JSON.stringify(data) });
      setAlert(`${kind[0].toUpperCase()+kind.slice(1)} created`);
      closeModal(modal);
      await loadAll();
    } catch (err) {
      const errBox = el(`#${modalId}__error`);
      errBox.textContent = err.message;
      show(errBox);
      setTimeout(()=>hide(errBox), 2000);
    }
  });
};

document.addEventListener("DOMContentLoaded", async () => {
  // Protect page if no token
  if (!token) {
    window.location.href = "/";
    return;
  }

  // open/close buttons (declared in template)
  els(".open-modal").forEach((b) => b.addEventListener("click", () => openModal(b.dataset.modal)));
  els(".close-modal").forEach((b) => b.addEventListener("click", () => closeModal(b.closest(".modal"))));

  // wire modals
  wireModal("courseModal", "course", "courses");
  wireModal("subjectModal", "subject", "subjects");
  wireModal("sectionModal", "section", "sections");

  // initial data
  try {
    await loadAll();
  } catch (e) {
    setAlert(e.message, false);
  }
});
