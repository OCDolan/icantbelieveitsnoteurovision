const root = document.documentElement;
const btn = document.getElementById("theme-toggle");

// Load saved theme
if (localStorage.theme) {
  root.setAttribute("data-theme", localStorage.theme);
}

btn.addEventListener("click", () => {
  const currentold = root.getAttribute("data-theme");
  const current = resolvedTheme();
  console.log(current);
  const next = current === "light" ? "dark" : "light";
  console.log(next);
  root.setAttribute("data-theme", next);
  localStorage.theme = next;
});

function resolvedTheme() {
  const theme = document.documentElement.getAttribute("data-theme");

  if (theme !== "auto") return theme;

  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}
