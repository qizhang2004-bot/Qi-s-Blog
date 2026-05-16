(function () {
  function escapeHtml(value) {
    return value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderInline(value) {
    return escapeHtml(value)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
  }

  function renderMarkdown(markdown) {
    const lines = markdown.split(/\r?\n/);
    const html = [];
    let inCode = false;
    let paragraph = [];

    function flushParagraph() {
      if (!paragraph.length) return;
      html.push(`<p>${renderInline(paragraph.join(" "))}</p>`);
      paragraph = [];
    }

    for (const line of lines) {
      if (line.startsWith("```")) {
        if (inCode) {
          html.push("</code></pre>");
          inCode = false;
        } else {
          flushParagraph();
          html.push("<pre><code>");
          inCode = true;
        }
        continue;
      }
      if (inCode) {
        html.push(`${escapeHtml(line)}\n`);
        continue;
      }
      if (!line.trim()) {
        flushParagraph();
        continue;
      }
      const heading = line.match(/^(#{1,4})\s+(.*)$/);
      if (heading) {
        flushParagraph();
        const level = heading[1].length;
        html.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
        continue;
      }
      if (line.startsWith("> ")) {
        flushParagraph();
        html.push(`<blockquote>${renderInline(line.slice(2))}</blockquote>`);
        continue;
      }
      paragraph.push(line.trim());
    }
    flushParagraph();
    if (inCode) html.push("</code></pre>");
    return html.join("\n");
  }

  function setupEditor() {
    const textarea = document.querySelector("#id_content, #id_bio");
    if (!textarea || textarea.dataset.mdEditorReady) return;
    textarea.dataset.mdEditorReady = "1";

    const shell = document.createElement("div");
    shell.className = "markdown-editor-shell";
    const preview = document.createElement("div");
    preview.className = "markdown-preview";

    textarea.parentNode.insertBefore(shell, textarea);
    shell.appendChild(textarea);
    shell.appendChild(preview);

    function updatePreview() {
      preview.innerHTML = renderMarkdown(textarea.value || "");
    }

    textarea.addEventListener("input", updatePreview);
    updatePreview();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupEditor);
  } else {
    setupEditor();
  }
})();
