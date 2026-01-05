function $(id) {
  return document.getElementById(id);
}

function setStatus(msg, type = "info") {
  const el = $("status");
  el.className = "status";
  if (type === "error") el.classList.add("error");
  if (type === "ok") el.classList.add("ok");
  el.textContent = msg || "";
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderResult(data) {
  const root = $("result");

  if (!data || !data.best_option) {
    root.innerHTML = `<p class="hint">沒有收到有效回應。</p>`;
    return;
  }

  const best = data.best_option;
  const segs = best.segments || [];

  root.innerHTML = `
    <div>
      <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
        <span class="badge">seat_type: ${escapeHtml(best.seat_type)}</span>
        <span class="badge">總時間: ${escapeHtml(best.total_minutes)} 分</span>
        <span class="badge">出發: ${escapeHtml(best.departure_time)} → 抵達: ${escapeHtml(best.arrival_time)}</span>
</div>

      <div class="kv">
        <div class="k">方案</div><div>best_option</div>
        <div class="k">段數</div><div>${escapeHtml(segs.length)}</div>
      </div>

      <table class="table">
        <thead>
          <tr>
            <th>車次</th>
            <th>起訖</th>
            <th>時間</th>
</tr>
        </thead>
        <tbody>
          ${segs.map(s => `
            <tr>
              <td>${escapeHtml(s.train_no)}</td>
              <td>${escapeHtml(s.origin)} → ${escapeHtml(s.destination)}</td>
              <td>${escapeHtml(s.departure_time)} → ${escapeHtml(s.arrival_time)}</td>
</tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function buildPayload() {
  const date = $("date").value;         // YYYY-MM-DD
  const time = $("time").value;         // HH:MM
  const origin = $("origin").value.trim();
  const destination = $("destination").value.trim();
  const seat_type = $("seatType").value;

  if (!date || !time || !origin || !destination || !seat_type) {
    throw new Error("請確認所有欄位都已填寫。");
  }

  // FastAPI/Pydantic 期望 time 是 HH:MM:SS 也可；但你後端目前用 hour/minute，HH:MM 即可。
  // 為保險，補上秒數。
  const timeWithSeconds = time.length === 5 ? `${time}:00` : time;

  return { date, time: timeWithSeconds, origin, destination, seat_type };
}

function getApiUrl() {
  const base = $("apiBase").value.trim();
  // 留空：使用同網域（例如你前端也被同一個 FastAPI 或反向代理提供）
  if (!base) return "/api/plan-trip";
  return base.replace(/\/+$/, "") + "/api/plan-trip";
}

async function planTrip() {
  setStatus("查詢中…");
  $("submitBtn").disabled = true;

  try {
    const url = getApiUrl();
    const payload = buildPayload();

    const res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });

    // 你的後端：找不到路徑會回 404 + detail
    if (!res.ok) {
      let detail = "";
      try {
        const err = await res.json();
        detail = err?.detail ? String(err.detail) : "";
      } catch { /* ignore */ }

      if (res.status === 404) {
        throw new Error(detail || "找不到可到達路徑（404）。");
      }
      throw new Error(detail || `API 錯誤：HTTP ${res.status}`);
    }

    const data = await res.json();
    renderResult(data);
    setStatus("完成。", "ok");
  } catch (err) {
    $("result").innerHTML = `<p class="error">${escapeHtml(err.message || String(err))}</p>`;
    setStatus(err.message || String(err), "error");
  } finally {
    $("submitBtn").disabled = false;
  }
}

function fillDemo() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  $("date").value = `${yyyy}-${mm}-${dd}`;
  $("time").value = "09:00";
  $("origin").value = "臺北";
  $("destination").value = "臺中";
  $("seatType").value = "non_reserved";
  $("apiBase").value = "https://tra-fastapi-planner.zeabur.app";
  setStatus("已填入範例。");
}

document.addEventListener("DOMContentLoaded", () => {
  $("tripForm").addEventListener("submit", (e) => {
    e.preventDefault();
    planTrip();
  });
  $("fillDemoBtn").addEventListener("click", fillDemo);
});
