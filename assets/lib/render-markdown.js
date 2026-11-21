// 归档气泡 Markdown 渲染：只处理纯文本气泡，保留已内联的图片/附件节点。
(function () {
  if (typeof marked === "undefined" || typeof DOMPurify === "undefined") return;
  try { marked.setOptions({ breaks: true, gfm: true }); } catch (e) {}

  document.querySelectorAll(".bubble").forEach(function (el) {
    if (el.dataset.rendered === "1") return;
    // 已含图片/链接等附件节点的气泡不再整泡重渲染，避免把附件冲掉。
    if (el.querySelector("img, a, video")) return;
    var raw = el.textContent.replace(/\s+$/, "");
    if (!raw) return;
    var html = marked.parse(raw);
    el.innerHTML = DOMPurify.sanitize(html);
    el.dataset.rendered = "1";
  });
})();
