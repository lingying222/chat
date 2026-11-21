// 长按聊天记录可删除：对 .msg 加 pointerdown/pointerup 长按 600ms 识别，
// 长按后弹确认框，确认后移除该条并把已删 id 存进 localStorage（按文件区分）。
(function () {
  var STORAGE_KEY = "tdwx-deleted-msgs";
  var LONG_PRESS_MS = 600;

  function todayKey() {
    // 按文件路径区分存储，避免不同日期互相影响
    return location.pathname + location.search;
  }

  function loadDeleted() {
    try {
      var data = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      return data[todayKey()] || [];
    } catch (e) { return []; }
  }

  function saveDeleted(ids) {
    try {
      var data = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      data[todayKey()] = ids;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) { /* ignore */ }
  }

  // 给每条 .msg 加一个稳定 id（基于内容 hash 的简化版：用索引+时间戳）
  function assignIds(root) {
    var msgs = root.querySelectorAll(".msg");
    msgs.forEach(function (el, i) {
      if (el.dataset.msgId) return;
      var t = el.querySelector(".time");
      var text = el.textContent.slice(0, 60);
      var h = 0;
      for (var j = 0; j < text.length; j++) { h = ((h << 5) - h + text.charCodeAt(j)) | 0; }
      el.dataset.msgId = i + "-" + (t ? t.textContent.trim() : "") + "-" + h;
    });
  }

  function applyDeletions(root) {
    var deleted = loadDeleted();
    if (!deleted.length) return;
    var set = {};
    deleted.forEach(function (id) { set[id] = true; });
    root.querySelectorAll(".msg").forEach(function (el) {
      if (set[el.dataset.msgId]) {
        el.remove();
      }
    });
  }

  var container = document.querySelector(".container") || document.body;

  assignIds(container);
  applyDeletions(container);

  var longPressTimer = null;
  var longPressTarget = null;
  var longPressFired = false;
  var moved = false;

  container.addEventListener("pointerdown", function (e) {
    var msg = e.target.closest(".msg");
    if (!msg) return;
    longPressFired = false;
    moved = false;
    longPressTarget = msg;
    var startX = e.clientX, startY = e.clientY;

    var onMove = function (ev) {
      if (Math.abs(ev.clientX - startX) > 10 || Math.abs(ev.clientY - startY) > 10) {
        moved = true;
        if (longPressTimer) { clearTimeout(longPressTimer); longPressTimer = null; }
      }
    };
    var onUp = function () {
      document.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerup", onUp);
      document.removeEventListener("pointercancel", onUp);
    };
    document.addEventListener("pointermove", onMove);
    document.addEventListener("pointerup", onUp);
    document.addEventListener("pointercancel", onUp);

    longPressTimer = setTimeout(function () {
      if (moved) return;
      longPressFired = true;
      longPressTimer = null;
      doDelete(msg);
    }, LONG_PRESS_MS);
  });

  function doDelete(msg) {
    if (!confirm("长按删除这条聊天记录？\n\n" + msg.textContent.slice(0, 80) + "…")) return;
    var id = msg.dataset.msgId;
    var deleted = loadDeleted();
    if (deleted.indexOf(id) === -1) deleted.push(id);
    saveDeleted(deleted);
    msg.style.transition = "opacity .25s, transform .25s";
    msg.style.opacity = "0";
    msg.style.transform = "translateX(24px)";
    setTimeout(function () { msg.remove(); }, 250);
  }

  // 在页面顶部加个提示
  var tip = document.createElement("div");
  tip.style.cssText = "text-align:center;color:#888;font-size:12px;margin-bottom:12px;";
  tip.textContent = "💡 长按某条聊天记录（按住 0.6 秒）可删除该条";
  var header = document.querySelector(".header");
  if (header && header.parentNode) header.parentNode.insertBefore(tip, header);
})();
