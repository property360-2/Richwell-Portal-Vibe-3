document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const btn = document.getElementById("loginBtn");
  const text = document.getElementById("loginText");
  const spinner = document.getElementById("spinner");
  const errorBox = document.getElementById("errorBox");

  const showError = (msg) => {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
    // trigger fade-in + shake
    errorBox.classList.add("opacity-100", "translate-y-0");
    errorBox.animate(
      [{ transform: "translateX(0)" }, { transform: "translateX(-8px)" },
       { transform: "translateX(8px)" }, { transform: "translateX(0)" }],
      { duration: 300, iterations: 1 }
    );
  };

  const resetError = () => {
    errorBox.classList.add("hidden");
    errorBox.classList.remove("opacity-100", "translate-y-0");
  };

  const setLoading = (state) => {
    if (state) {
      btn.disabled = true;
      text.textContent = "Logging in…";
      spinner.classList.remove("hidden");
    } else {
      btn.disabled = false;
      text.textContent = "Login";
      spinner.classList.add("hidden");
    }
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resetError();
    setLoading(true);

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const res = await fetch("/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Invalid username or password.");

      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      localStorage.setItem("role", data.user.role);

      const role = data.user.role.toLowerCase();
      // short delay for smoothness
      setTimeout(() => (window.location.href = `/dashboard/?role=${role}`), 400);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });
});
