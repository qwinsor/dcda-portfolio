document.addEventListener("DOMContentLoaded", () => {
    setupThemeToggle();
    setupBackToTop();
    setupLabFilters();
});

function setupThemeToggle() {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    const root = document.documentElement;
    const saved = localStorage.getItem("theme"); // "dark" | "light" | null

    if (saved === "dark") root.classList.add("dark");
    btn.textContent = root.classList.contains("dark") ? "Light" : "Dark";

    btn.addEventListener("click", () => {
        root.classList.toggle("dark");
        const isDark = root.classList.contains("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        btn.textContent = isDark ? "Light" : "Dark";
    });
}

function setupBackToTop() {
    const btn = document.getElementById("backToTop");
    if (!btn) return;

    const showAfter = 300;

    window.addEventListener("scroll", () => {
        if (window.scrollY > showAfter) btn.classList.add("is-visible");
        else btn.classList.remove("is-visible");
    });

    btn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

function setupLabFilters() {
    const search = document.getElementById("labSearch");
    const tagWrap = document.getElementById("tagFilters");
    const countEl = document.getElementById("resultsCount");
    const cards = Array.from(document.querySelectorAll(".portfolio-card"));

    // Only runs on pages that actually have the lab grid + controls (your index)
    if (!search || !tagWrap || cards.length === 0) return;

    let activeTag = "all";

    function normalize(s) {
        return (s || "").toLowerCase().trim();
    }

    function cardMatches(card, query, tag) {
        const text = normalize(card.innerText);
        const tags = normalize(card.getAttribute("data-tags"));
        const queryOK = !query || text.includes(query);
        const tagOK = tag === "all" || (tags && tags.split(/\s+/).includes(tag));
        return queryOK && tagOK;
    }

    function update() {
        const q = normalize(search.value);
        let visibleCount = 0;

        cards.forEach((card) => {
            const ok = cardMatches(card, q, activeTag);
            card.style.display = ok ? "" : "none";
            if (ok) visibleCount += 1;
        });

        if (countEl) {
            countEl.textContent = `${visibleCount} lab${visibleCount === 1 ? "" : "s"} shown`;
        }
    }

    tagWrap.addEventListener("click", (e) => {
        const btn = e.target.closest("button[data-tag]");
        if (!btn) return;

        activeTag = btn.dataset.tag;

        tagWrap.querySelectorAll(".tag-btn").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");

        update();
    });

    search.addEventListener("input", update);
    update();
}

