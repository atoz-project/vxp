(() => {
  "use strict";

  const isHome = document.body.classList.contains("page-home");
  const isDoc = document.body.classList.contains("page-doc");

  function initSearch() {
    const tools = document.querySelector("[data-catalog-tools]");
    const input = tools?.querySelector("[data-catalog-search]");
    const status = tools?.querySelector("[data-search-status]");
    const catalog = document.querySelector(".catalog");

    if (!tools || !input || !status || !catalog) return;

    const rows = Array.from(catalog.querySelectorAll("table tbody tr"));
    const categories = Array.from(catalog.querySelectorAll("h2"));
    const total = rows.length;
    tools.hidden = false;

    rows.forEach((row) => {
      const id = row.cells[0]?.textContent.trim() ?? "";
      const link = row.querySelector("a");
      row.classList.toggle("is-child", /^VXP-\d{3}\.\d{3}/.test(id));
      row.classList.toggle("is-clickable", Boolean(link));

      if (!link) return;
      row.addEventListener("click", (event) => {
        if (event.target.closest("a") || window.getSelection()?.toString()) return;
        link.click();
      });
    });

    const updateStatus = (visible, query) => {
      if (!query) {
        status.textContent = `共 ${total} 个条目`;
        return;
      }

      status.textContent = visible === 0
        ? `没有匹配“${query}”的条目。可尝试编号、标题或字段名。`
        : `显示 ${visible} / ${total} 个条目`;
    };

    const filter = () => {
      const query = input.value.trim().toLocaleLowerCase("zh-CN");
      let visible = 0;

      rows.forEach((row) => {
        const matches = !query || row.textContent.toLocaleLowerCase("zh-CN").includes(query);
        row.hidden = !matches;
        if (matches) visible += 1;
      });

      categories.forEach((heading) => {
        const table = Array.from(heading.parentElement.children)
          .slice(Array.from(heading.parentElement.children).indexOf(heading) + 1)
          .find((element) => element.tagName === "TABLE");

        if (!table) return;

        const hasVisibleRow = Array.from(table.querySelectorAll("tbody tr"))
          .some((row) => !row.hidden);

        heading.hidden = !hasVisibleRow;
        table.hidden = !hasVisibleRow;
      });

      updateStatus(visible, query);
    };

    input.addEventListener("input", filter);
    input.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && input.value) {
        input.value = "";
        filter();
      }
    });

    document.addEventListener("keydown", (event) => {
      const target = event.target;
      const isTyping = target instanceof HTMLElement
        && (target.matches("input, textarea, select") || target.isContentEditable);

      if (event.key === "/" && !isTyping && !event.metaKey && !event.ctrlKey && !event.altKey) {
        event.preventDefault();
        input.focus();
      }
    });

    updateStatus(total, "");
  }

  function initEntryMetadata() {
    const meta = document.querySelector(".entry > h1 + ul");
    if (!meta) return;

    meta.classList.add("entry-meta");

    meta.querySelectorAll("li").forEach((item) => {
      const raw = item.textContent.trim();
      const separator = raw.indexOf("：");
      if (separator < 1) return;

      const label = document.createElement("span");
      const value = document.createElement("span");
      label.className = "meta-label";
      value.className = "meta-value";
      label.textContent = raw.slice(0, separator);
      value.textContent = raw.slice(separator + 1);
      item.replaceChildren(label, value);
    });
  }

  function initTableScrollers() {
    document.querySelectorAll(".entry table").forEach((table) => {
      if (table.parentElement?.classList.contains("table-scroll")) return;

      const scroller = document.createElement("div");
      scroller.className = "table-scroll";
      scroller.tabIndex = 0;
      scroller.setAttribute("role", "region");
      scroller.setAttribute("aria-label", "表格，可横向滚动");
      table.parentNode.insertBefore(scroller, table);
      scroller.append(table);
    });
  }

  function initOutline() {
    const outline = document.querySelector("[data-page-toc]");
    const article = document.querySelector(".entry");
    if (!outline || !article) return;

    const headings = Array.from(article.querySelectorAll("h2"));
    if (headings.length < 3) return;

    const title = document.createElement("p");
    title.className = "toc-title";
    title.textContent = "本页目录";

    const list = document.createElement("ol");
    const links = [];

    headings.forEach((heading, index) => {
      if (!heading.id) heading.id = `section-${index + 1}`;

      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.dataset.target = heading.id;
      link.textContent = heading.textContent.trim();
      item.append(link);
      list.append(item);
      links.push(link);
    });

    outline.replaceChildren(title, list);
    outline.hidden = false;

    headings.forEach((heading) => {
      const anchor = document.createElement("a");
      anchor.className = "heading-anchor";
      anchor.href = `#${heading.id}`;
      anchor.textContent = "#";
      anchor.setAttribute("aria-label", `链接到“${heading.textContent.trim()}”`);
      heading.append(anchor);
    });

    if (!("IntersectionObserver" in window)) return;

    const setActive = (id) => {
      links.forEach((link) => {
        link.classList.toggle("is-active", link.dataset.target === id);
      });
    };

    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

      if (visible.length > 0) setActive(visible[0].target.id);
    }, {
      rootMargin: "-96px 0px -68% 0px",
      threshold: 0
    });

    headings.forEach((heading) => observer.observe(heading));
  }

  if (isHome) initSearch();
  if (isDoc) {
    initEntryMetadata();
    initTableScrollers();
    initOutline();
  }
})();