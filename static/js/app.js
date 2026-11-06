// app.js: Frontend logic for SAR Image Enhancement & Boundary Edge Studio (FastAPI + SPA)

let currentImageId = "oil_slick_01.jpg";
let customImageBase64 = null;
let histogramChart = null;
let sliceChart = null;
let debounceTimer = null;

// Khởi chạy khi tài liệu tải xong
document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  loadSampleGallery();
  executeProcessing();
});

// Chuyển đổi giữa các tab
function switchTab(tabId) {
  const tabs = ["studio", "experiments", "verification", "theory"];
  tabs.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (t === tabId) {
      el.classList.remove("hidden");
      btn.classList.add("active");
    } else {
      el.classList.add("hidden");
      btn.classList.remove("active");
    }
  });

  if (tabId === "experiments") {
    loadExperimentsData();
  }
}

// Cập nhật nhãn thanh trượt
function updateRangeLabel(sliderId, labelId, suffix = "", prefix = "") {
  const val = document.getElementById(sliderId).value;
  let text = prefix + val + suffix;
  if (suffix === "x") {
    text = `${val}x${val}`;
  }
  document.getElementById(labelId).innerText = text;
}

// Khi đổi bộ lọc đốm
function onFilterChange() {
  const type = document.getElementById("filter-type").value;
  document.getElementById("lee-params").classList.add("hidden");
  document.getElementById("bilateral-params").classList.add("hidden");
  document.getElementById("frost-params").classList.add("hidden");
  document.getElementById("homo-params").classList.add("hidden");
  document.getElementById("filter-size-group").classList.remove("hidden");

  if (type === "lee" || type === "kuan") {
    document.getElementById("lee-params").classList.remove("hidden");
  } else if (type === "bilateral") {
    document.getElementById("bilateral-params").classList.remove("hidden");
  } else if (type === "frost") {
    document.getElementById("frost-params").classList.remove("hidden");
  } else if (type === "homomorphic") {
    document.getElementById("homo-params").classList.remove("hidden");
    document.getElementById("filter-size-group").classList.add("hidden");
  } else if (type === "none") {
    document.getElementById("filter-size-group").classList.add("hidden");
  }
  triggerProcessing();
}

// Khi đổi phương pháp tăng tương phản
function onEnhChange() {
  const type = document.getElementById("enh-type").value;
  const claheGroup = document.getElementById("clahe-params");
  if (type === "clahe") {
    claheGroup.classList.remove("hidden");
  } else {
    claheGroup.classList.add("hidden");
  }
  triggerProcessing();
}

// Khi đổi phương pháp làm nét
function onSharpChange() {
  const type = document.getElementById("sharp-type").value;
  const kGroup = document.getElementById("sharp-k-group");
  if (type === "none") {
    kGroup.classList.add("hidden");
  } else {
    kGroup.classList.remove("hidden");
  }
  triggerProcessing();
}

// Khi đổi phương pháp bộc lộ biên
function onEdgeTypeChange() {
  const edgeType = document.getElementById("edge-type").value;
  const morphControls = document.getElementById("morphology-controls");
  const gradControls = document.getElementById("gradient-controls");

  if (edgeType === "morphology") {
    morphControls.classList.remove("hidden");
    gradControls.classList.add("hidden");
  } else if (edgeType === "none") {
    morphControls.classList.add("hidden");
    gradControls.classList.add("hidden");
  } else {
    morphControls.classList.add("hidden");
    gradControls.classList.remove("hidden");
  }
}

// Đặt lại mặc định
function resetDefaults() {
  document.getElementById("filter-type").value = "lee";
  document.getElementById("filter-size").value = 5;
  document.getElementById("num-looks").value = 4.0;
  document.getElementById("enh-type").value = "clahe";
  document.getElementById("clip-limit").value = 2.0;
  document.getElementById("tile-grid").value = "8";
  document.getElementById("sharp-type").value = "unsharp";
  document.getElementById("sharp-k").value = 0.8;
  document.getElementById("edge-type").value = "morphology";
  document.getElementById("min-area").value = 300;
  document.getElementById("min-contrast").value = 0.10;
  document.getElementById("edge-high").value = 90;
  document.getElementById("edge-low").value = 35;
  document.getElementById("edge-mode").value = "overlay";
  document.getElementById("overlay-color").value = "red";
  document.getElementById("slice-row").value = 200;

  updateRangeLabel("filter-size", "filter-size-val", "x");
  updateRangeLabel("num-looks", "num-looks-val");
  updateRangeLabel("clip-limit", "clip-val");
  updateRangeLabel("sharp-k", "sharp-k-val");
  updateRangeLabel("min-area", "min-area-val", " px");
  updateRangeLabel("min-contrast", "min-contrast-val");
  updateRangeLabel("edge-high", "edge-high-val");
  updateRangeLabel("edge-low", "edge-low-val");
  updateRangeLabel("slice-row", "slice-row-val", "", "y = ");

  onFilterChange();
  onEnhChange();
  onSharpChange();
  onEdgeTypeChange();
  executeProcessing();
}

// Khởi tạo các đồ thị Chart.js
function initCharts() {
  // Chart 1: Histogram
  const ctxHist = document.getElementById("chart-histogram").getContext("2d");
  const dummyLabels = Array.from({ length: 256 }, (_, i) => i);
  histogramChart = new Chart(ctxHist, {
    type: "bar",
    data: {
      labels: dummyLabels,
      datasets: [
        {
          label: "Ảnh Gốc",
          data: [],
          backgroundColor: "rgba(100, 116, 139, 0.4)",
          borderWidth: 0,
          barPercentage: 1.0,
          categoryPercentage: 1.0,
        },
        {
          label: "Sau Tăng Cường",
          data: [],
          backgroundColor: "rgba(37, 99, 235, 0.6)",
          borderWidth: 0,
          barPercentage: 1.0,
          categoryPercentage: 1.0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 200 },
      plugins: {
        legend: { position: "top", labels: { boxWidth: 10, font: { size: 10 } } },
      },
      scales: {
        x: {
          display: true,
          ticks: { maxTicksLimit: 8, font: { size: 9 } },
          grid: { display: false },
        },
        y: {
          display: true,
          ticks: { maxTicksLimit: 5, font: { size: 9 } },
        },
      },
    },
  });

  // Chart 2: Profile Slice
  const ctxSlice = document.getElementById("chart-slice").getContext("2d");
  const dummySliceLabels = Array.from({ length: 400 }, (_, i) => i);
  sliceChart = new Chart(ctxSlice, {
    type: "line",
    data: {
      labels: dummySliceLabels,
      datasets: [
        {
          label: "Gốc (Nhiễu đốm)",
          data: [],
          borderColor: "rgba(148, 163, 184, 0.8)",
          borderWidth: 1.2,
          pointRadius: 0,
          fill: false,
        },
        {
          label: "Sau xử lý (Vết dầu sâu, biên nét)",
          data: [],
          borderColor: "#dc2626",
          borderWidth: 2.0,
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 200 },
      plugins: {
        legend: { position: "top", labels: { boxWidth: 10, font: { size: 10 } } },
      },
      scales: {
        x: {
          display: true,
          title: { display: true, text: "Tọa độ pixel x", font: { size: 10 } },
          ticks: { maxTicksLimit: 8, font: { size: 9 } },
          grid: { display: false },
        },
        y: {
          display: true,
          title: { display: true, text: "Mức xám (0 - 255)", font: { size: 10 } },
          min: 0,
          max: 255,
          ticks: { font: { size: 9 } },
        },
      },
    },
  });
}

// Nạp danh sách ảnh mẫu
async function loadSampleGallery() {
  const container = document.getElementById("sample-gallery");
  try {
    const res = await fetch("/api/samples");
    const data = await res.json();
    if (!data.samples || data.samples.length === 0) {
      container.innerHTML = '<div class="text-xs text-red-500">Không tìm thấy ảnh mẫu!</div>';
      return;
    }

    container.innerHTML = "";
    data.samples.forEach(sample => {
      const card = document.createElement("div");
      const isOil = sample.category === "oil";
      const badgeBg = isOil ? "bg-amber-100 text-amber-800" : "bg-cyan-100 text-cyan-800";
      const badgeText = isOil ? "Vết dầu" : "Mặt biển";

      card.className = `thumbnail-card border-2 rounded-xl p-2 bg-white text-center flex-shrink-0 w-28 transition shadow-xs ${
        sample.id === currentImageId ? "active" : "border-slate-200/80 hover:border-slate-300"
      }`;
      card.id = `thumb-${sample.id}`;
      card.onclick = () => selectSample(sample.id);

      card.innerHTML = `
        <div class="w-full h-16 bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center mb-1.5">
          <img src="data:image/jpeg;base64,${sample.thumb_base64}" alt="${sample.id}" class="w-full h-full object-cover">
        </div>
        <div class="text-[11px] font-mono font-bold text-slate-800 truncate">${sample.id}</div>
        <span class="inline-block text-[10px] px-1.5 py-0.5 rounded-md font-semibold ${badgeBg} mt-0.5">${badgeText}</span>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Lỗi nạp ảnh mẫu:", err);
    container.innerHTML = '<div class="text-xs text-red-500">Lỗi kết nối máy chủ!</div>';
  }
}

// Chọn ảnh mẫu từ danh sách
function selectSample(id) {
  currentImageId = id;
  customImageBase64 = null;
  document.getElementById("current-image-tag").innerText = id;

  document.querySelectorAll(".thumbnail-card").forEach(c => c.classList.remove("active"));
  const activeCard = document.getElementById(`thumb-${id}`);
  if (activeCard) activeCard.classList.add("active");

  executeProcessing();
}

// Xử lý tải ảnh lên từ máy tính
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = e => {
    customImageBase64 = e.target.result;
    currentImageId = file.name;
    document.getElementById("current-image-tag").innerText = `[Tải lên] ${file.name}`;

    document.querySelectorAll(".thumbnail-card").forEach(c => c.classList.remove("active"));

    executeProcessing();
  };
  reader.readAsDataURL(file);
}

// Debounce khi kéo thanh trượt
function triggerProcessing() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    executeProcessing();
  }, 120);
}

// Gửi yêu cầu xử lý lên Backend FastAPI
async function executeProcessing() {
  const filterType = document.getElementById("filter-type").value;
  const filterSize = parseInt(document.getElementById("filter-size").value);
  const numLooks = parseFloat(document.getElementById("num-looks").value);
  const sigmaS = parseFloat(document.getElementById("sigma-s").value);
  const sigmaR = parseFloat(document.getElementById("sigma-r").value);
  const damping = parseFloat(document.getElementById("damping").value);
  const d0Val = parseFloat(document.getElementById("d0").value);

  const enhType = document.getElementById("enh-type").value;
  const clipLimit = parseFloat(document.getElementById("clip-limit").value);
  const tileGrid = parseInt(document.getElementById("tile-grid").value);

  const sharpType = document.getElementById("sharp-type").value;
  const sharpK = parseFloat(document.getElementById("sharp-k").value);
  const sliceRow = parseInt(document.getElementById("slice-row").value);

  // Tham số xử lý biên & hình thái học
  const edgeType = document.getElementById("edge-type").value;
  const edgeHigh = parseFloat(document.getElementById("edge-high").value);
  const edgeLow = parseFloat(document.getElementById("edge-low").value);
  const edgeMode = document.getElementById("edge-mode").value;
  const overlayColor = document.getElementById("overlay-color").value;
  const minArea = parseInt(document.getElementById("min-area")?.value || "300");
  const minContrast = parseFloat(document.getElementById("min-contrast")?.value || "0.10");

  // Cập nhật vị trí đường đỏ lát cắt
  const percentY = (sliceRow / 400.0) * 100.0;
  document.getElementById("slice-line-raw").style.top = `${percentY}%`;
  document.getElementById("slice-line-proc").style.top = `${percentY}%`;
  document.getElementById("chart-slice-label").innerText = `Hàng y = ${sliceRow}`;

  const payload = {
    image_id: currentImageId,
    custom_image_base64: customImageBase64,
    filter_type: filterType,
    filter_size: filterSize,
    num_looks: numLooks,
    sigma_s: sigmaS,
    sigma_r: sigmaR,
    damping: damping,
    d0: d0Val,
    enhancement_type: enhType,
    clip_limit: clipLimit,
    tile_grid: tileGrid,
    sharpening_type: sharpType,
    sharp_k: sharpK,
    slice_row: sliceRow,
    edge_type: edgeType,
    edge_high: edgeHigh,
    edge_low: edgeLow,
    edge_mode: edgeMode,
    overlay_color: overlayColor,
    min_area: minArea,
    min_contrast: minContrast,
  };

  try {
    const res = await fetch("/api/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    // 1. Cập nhật 4 ảnh hiển thị
    document.getElementById("img-raw").src = `data:image/png;base64,${data.raw_image_base64}`;
    document.getElementById("img-processed").src = `data:image/png;base64,${data.proc_image_base64}`;
    document.getElementById("img-edge").src = `data:image/png;base64,${data.edge_image_base64}`;
    document.getElementById("img-diff").src = `data:image/png;base64,${data.diff_image_base64}`;

    // 2. Cập nhật 6 thẻ đo lường
    document.getElementById("m-enl").innerText = data.metrics.ENL.toFixed(2);
    document.getElementById("m-ssi").innerText = data.metrics.SSI.toFixed(3);
    document.getElementById("m-rms").innerText = data.metrics.RMS_Contrast.toFixed(2);
    document.getElementById("m-entropy").innerText = data.metrics.Entropy.toFixed(3);
    document.getElementById("m-ambe").innerText = data.metrics.AMBE.toFixed(2);
    document.getElementById("m-epi").innerText = data.metrics.EPI.toFixed(3);

    // 2b. Cập nhật Thẻ Thống Kê Đặc Trưng Vết Dầu Tràn (NASA & Chương 6, 7)
    if (data.oil_slick_stats) {
      document.getElementById("stat-slicks-count").innerText = data.oil_slick_stats.slicks_count;
      document.getElementById("stat-total-area").innerText = `${data.oil_slick_stats.total_area_px.toLocaleString()} px`;
      document.getElementById("stat-area-pct").innerText = `${data.oil_slick_stats.area_pct}% diện tích ảnh`;
      document.getElementById("stat-contrast-ratio").innerText = data.oil_slick_stats.mean_contrast_ratio.toFixed(3);
      document.getElementById("stat-separability").innerText = data.oil_slick_stats.separability_eta.toFixed(3);
      document.getElementById("stat-otsu-t").innerText = `Ngưỡng Otsu T = ${data.oil_slick_stats.otsu_threshold}`;
      document.getElementById("stat-method-tag").innerText = "Hình Thái Học beta(A)";
      document.getElementById("stat-method-tag").className = "text-xs bg-slate-100 text-slate-800 border border-slate-200 px-3 py-1 rounded-md font-mono font-semibold";
    } else {
      document.getElementById("stat-slicks-count").innerText = "--";
      document.getElementById("stat-total-area").innerText = "Không kích hoạt";
      document.getElementById("stat-area-pct").innerText = "Chế độ Gradient";
      document.getElementById("stat-contrast-ratio").innerText = "--";
      document.getElementById("stat-separability").innerText = "--";
      document.getElementById("stat-otsu-t").innerText = "Đạo hàm bậc 1/2";
      document.getElementById("stat-method-tag").innerText = `Cạnh ${edgeType.toUpperCase()}`;
      document.getElementById("stat-method-tag").className = "text-xs bg-slate-100 text-slate-600 border border-slate-200 px-3 py-1 rounded-md font-mono font-medium";
    }

    // 3. Cập nhật biểu đồ Histogram
    histogramChart.data.datasets[0].data = data.raw_hist;
    histogramChart.data.datasets[1].data = data.proc_hist;
    histogramChart.update("none");

    // 4. Cập nhật biểu đồ Profile Slice
    sliceChart.data.datasets[0].data = data.raw_slice;
    sliceChart.data.datasets[1].data = data.proc_slice;
    sliceChart.update("none");
  } catch (err) {
    console.error("Lỗi thực thi chuỗi xử lý:", err);
  }
}

// Nạp dữ liệu các bảng thử nghiệm Chương 4, 5, 6, 7 & NASA
async function loadExperimentsData() {
  try {
    const res = await fetch("/api/experiments");
    const data = await res.json();

    renderTable("exp1-table-container", data.exp1);
    renderTable("exp2-table-container", data.exp2);
    renderTable("exp3-table-container", data.exp3);
    renderTable("exp4-table-container", data.exp4);
    renderTable("exp5-table-container", data.exp5);
  } catch (err) {
    console.error("Lỗi nạp báo cáo thực nghiệm:", err);
  }
}

// Hàm hỗ trợ vẽ bảng HTML từ dữ liệu JSON
function renderTable(containerId, rows) {
  const container = document.getElementById(containerId);
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div class="text-xs text-slate-400">Không có dữ liệu!</div>';
    return;
  }

  const keys = Object.keys(rows[0]);
  let html = '<table class="w-full text-xs text-left border-collapse border border-slate-200"><thead class="bg-slate-100 font-bold text-slate-700"><tr>';
  keys.forEach(k => {
    html += `<th class="p-2 border border-slate-200">${k}</th>`;
  });
  html += '</tr></thead><tbody class="divide-y divide-slate-200 font-mono">';
  rows.forEach(r => {
    html += '<tr class="hover:bg-slate-50">';
    keys.forEach(k => {
      const val = r[k];
      const isNum = typeof val === "number";
      const highlight = (k.includes("ENL") || k.includes("EPI") || k.includes("RMS") || k.includes("Canny")) ? "text-blue-700 font-bold" : "";
      html += `<td class="p-2 border border-slate-200 ${highlight}">${isNum ? val.toFixed(2) : val}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

// Phóng to ảnh (Lightbox Zoom Modal)
function openZoomModal(src, title) {
  if (!src) return;
  const modal = document.getElementById("image-zoom-modal");
  const modalImg = document.getElementById("zoom-modal-img");
  const modalTitle = document.getElementById("zoom-modal-title");

  modalImg.src = src;
  modalTitle.innerText = title || "Xem Chi Tiết Ảnh";
  modal.classList.remove("hidden");
}

function closeZoomModal() {
  const modal = document.getElementById("image-zoom-modal");
  modal.classList.add("hidden");
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeZoomModal();
  }
});
