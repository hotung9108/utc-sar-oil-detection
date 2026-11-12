"""TV1/TV5: build the report from editable content and measured evidence.

Outputs a PDF, editable Word/LaTeX sources and frozen supporting measurements.
Requires Windows Times New Roman (read for rendering, not copied into the repo).
"""

import ctypes
import hashlib
import json
import shutil
import sys
import zipfile
from html import escape
from importlib.metadata import version
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import MathTextParser
from PIL import Image as PILImage
from pypdf import PdfReader
from report_content import REFERENCES, sections
from report_content import paragraph as P
from report_content import table as T
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.tv5.experiments import code_digest

OUT = ROOT / "docs/report"
DATA = ROOT / "results/reproducible"
VER = ROOT / "results/verification"
ASSETS = OUT / "assets"
TEAM = json.loads((ROOT / "docs/management/thanh_vien.json").read_text(encoding="utf-8"))
CHAPTERS = {
    1: "Tổng quan bài toán",
    2: "Cơ sở lý thuyết",
    3: "Thiết kế và cài đặt",
    4: "Thực nghiệm và đánh giá",
    5: "Kết luận và hướng phát triển",
}


def load_data():
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    if manifest["source_sha256"] != code_digest():
        raise RuntimeError("Source changed since measurements; run reproduce.py again")
    if manifest.get("completed_scope") != "full":
        raise RuntimeError(
            "A samples-only run cannot supply the full-dataset report; run reproduce.py"
        )
    df = pd.read_csv(VER / "per_case.csv")
    if (df.verdict == "FAIL").any():
        raise RuntimeError("Cannot publish failed library checks as passed")
    conf = json.loads((DATA / "confusion.json").read_text())
    assert conf["n"] == 5538
    hand = json.loads((VER / "hand_examples.json").read_text())
    filt = pd.read_csv(DATA / "filters_summary.csv")
    clahe = pd.read_csv(DATA / "clahe_summary.csv")
    fail = pd.read_csv(DATA / "failure_cases_per_image.csv")
    case = fail[(fail.image.str.contains("00013")) & (fail.enhancement == "clahe")].iloc[0]
    sea = fail[(fail.image.str.contains("sea_surface")) & (fail.enhancement == "clahe")]
    groups = df.groupby(["algorithm", "kind"], sort=False).agg(
        error=("max_abs_error", "max"), mse=("mse", "mean")
    )

    def comparison(names):
        rows = [["Phép toán", "Nhóm đối chứng", "Max |Δ|", "MSE TB"]]
        for (name, kind), row in groups.iterrows():
            if name in names:
                rows.append(
                    [
                        name,
                        {"direct": "Trực tiếp", "composition": "Ghép hàm", "variant": "Biến thể"}[
                            kind
                        ],
                        f"{row.error:.3g}",
                        f"{row.mse:.3g}",
                    ]
                )
        return rows

    names = [
        "box",
        "gaussian",
        "median",
        "bilateral",
        "lee",
        "frost",
        "kuan",
        "log",
        "HE",
        "CLAHE",
        "homomorphic",
    ]
    data = {
        "manifest": manifest,
        "hand_table": [["Ví dụ", "Kết quả kỳ vọng", "Sai số lớn nhất"]]
        + [[r["example"], str(r["expected"]), f"{r['max_abs_error']:.1g}"] for r in hand],
        "environment_table": [
            ["Thuộc tính", "Giá trị"],
            ["Python", manifest["python"]],
            ["Hệ điều hành", manifest["platform"]],
            ["CPU / logical CPUs", manifest["cpu"] + " / " + str(manifest["logical_cpus"])],
            ["NumPy / OpenCV", manifest["numpy"] + " / " + manifest["opencv"]],
            ["Seed / process dataset", str(manifest["seed"]) + " / 4"],
            ["Ngày chạy", manifest["executed_at"]],
            ["Hash mã nguồn (rút gọn)", manifest["source_sha256"][:24]],
        ],
        "comparison_a": comparison(names),
        "comparison_b": comparison(
            [
                n
                for n in df.algorithm.unique()
                if n not in names and n not in ["ENL", "SSI", "RMS", "entropy", "AMBE", "EPI"]
            ]
        ),
        "comparison_metrics": comparison(["ENL", "SSI", "RMS", "entropy", "AMBE", "EPI"]),
        "filters_table": [["Bộ lọc", "SSI (TB ± SD)", "EPI (TB ± SD)"]]
        + [
            [r.method, f"{r.SSI_mean:.4f} ± {r.SSI_std:.4f}", f"{r.EPI_mean:.4f} ± {r.EPI_std:.4f}"]
            for r in filt.itertuples()
        ],
        "filters_best": [
            (int(filt.loc[filt.method != "none", "SSI_mean"].idxmin()) + 1, 1),
            (int((filt.loc[filt.method != "none", "EPI_mean"] - 1).abs().idxmin()) + 1, 2),
        ],
        "clahe_table": [["Grid", "AMBE (TB ± SD)", "Entropy (TB ± SD)"]]
        + [
            [
                str(r.grid),
                f"{r.AMBE_mean:.3f} ± {r.AMBE_std:.3f}",
                f"{r.Entropy_mean:.3f} ± {r.Entropy_std:.3f}",
            ]
            for r in clahe[clahe["clip"] == 2].itertuples()
        ],
        "case_analysis": f"Với cấu hình mặc định hiện tại, ảnh 00013 giữ {int(case.candidates)} vùng ứng viên, chiếm {case.area_pct:.2f}% ảnh, CR trung bình {case.contrast:.3f}. Hình 4.3–4.4 cho thấy vệt chính nổi bật hơn, nhưng chưa có mask chuẩn để lượng hóa độ khớp. Trong năm ảnh biển mẫu, {int((sea.candidates > 0).sum())}/5 ảnh vẫn có ứng viên; do đó không thể kết luận lọc đã loại hết báo động giả.",
        "sea_table": [["Ảnh biển", "Số vùng", "Diện tích (%)"]]
        + [[Path(r.image).stem, str(r.candidates), f"{r.area_pct:.2f}"] for r in sea.itertuples()],
        "confusion_table": [
            ["Nhãn thật theo thư mục", "Không có ứng viên", "Có ứng viên"],
            ["Class_0", str(conf["TN"]), str(conf["FP"])],
            ["Class_1", str(conf["FN"]), str(conf["TP"])],
        ],
        "class_metrics": [
            ["Chỉ số", "Giá trị"],
            ["Precision", f"{conf['precision'] * 100:.2f}%"],
            ["Recall", f"{conf['recall'] * 100:.2f}%"],
            ["F1", f"{conf['f1'] * 100:.2f}%"],
            ["Specificity", f"{conf['specificity'] * 100:.2f}%"],
            ["Accuracy cấp ảnh", f"{conf['accuracy'] * 100:.2f}%"],
        ],
    }
    data["environment_table"].extend(
        [
            [name, version(name)]
            for name in ["scipy", "scikit-image", "matplotlib", "pandas", "streamlit"]
        ]
    )

    # RAM is an actual measurement, not a guessed laptop specification.
    class Mem(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
            (n, ctypes.c_ulonglong)
            for n in [
                "total",
                "available",
                "page_total",
                "page_available",
                "virtual_total",
                "virtual_available",
                "extended",
            ]
        ]

    if sys.platform == "win32":
        memory = Mem()
        memory.length = ctypes.sizeof(memory)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
            data["environment_table"].insert(4, ["RAM vật lý", f"{memory.total / 2**30:.1f} GiB"])
    return data


def make_figures():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name in ["class_1_00013_clahe.png", "roi_00013.png", "sea_surface_01_clahe.png"]:
        shutil.copy2(DATA / name, ASSETS / name)
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.axis("off")
    for x, title in [(0.1, "Input"), (0.35, "NumPy filter"), (0.6, "CLAHE"), (0.86, "Display")]:
        ax.text(
            x,
            0.75,
            title,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=.6", fc="#e6f1f5", ec="#167d9a"),
            fontsize=12,
        )
    for a, b in [(0.15, 0.28), (0.43, 0.53), (0.67, 0.8)]:
        ax.annotate("", xy=(b, 0.75), xytext=(a, 0.75), arrowprops=dict(arrowstyle="->"))
    ax.text(
        0.6,
        0.25,
        "Otsu + morphology + contrast\nCandidate mask and boundary",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=.6", fc="#fff2df", ec="#b86b31"),
        fontsize=12,
    )
    ax.annotate(
        "reference",
        xy=(0.43, 0.25),
        xytext=(0.35, 0.59),
        arrowprops=dict(arrowstyle="->"),
        fontsize=10,
    )
    ax.annotate("", xy=(0.6, 0.42), xytext=(0.6, 0.62), arrowprops=dict(arrowstyle="->"))
    fig.tight_layout()
    fig.savefig(ASSETS / "pipeline.png", dpi=180)
    plt.close(fig)
    df = pd.read_csv(DATA / "clahe_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for grid, g in df.groupby("grid"):
        for ax, col in zip(axes, ["AMBE", "Entropy"]):
            ax.errorbar(
                g["clip"],
                g[col + "_mean"],
                yerr=g[col + "_std"],
                marker="o",
                label=f"grid {grid}",
                capsize=3,
            )
            ax.set(xlabel="Clip limit", ylabel=col + " (mean ± SD)")
    for ax in axes:
        ax.legend(fontsize=9)
        ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(ASSETS / "clahe_survey.png", dpi=180)
    plt.close(fig)
    df = pd.read_csv(DATA / "edge_noise_summary.csv")
    fig, ax = plt.subplots(figsize=(9, 3.6))
    for name, g in df.groupby("method"):
        ax.plot(g.noise_sigma, g.edge_density_pct_mean, marker="o", label=name)
    ax.set(xlabel="Gaussian noise sigma (gray levels)", ylabel="Edge density (%)")
    ax.grid(alpha=0.2)
    ax.legend(ncol=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(ASSETS / "edge_noise.png", dpi=180)
    plt.close(fig)


def freeze_evidence():
    dest = OUT / "evidence"
    dest.mkdir(exist_ok=True)
    hashes = {}
    for folder in [VER, DATA]:
        for p in sorted(folder.glob("*")):
            if p.suffix in [".csv", ".json"]:
                target = dest / (folder.name + "_" + p.name)
                shutil.copy2(p, target)
                hashes[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    (dest / "checksums.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")


def front_pages(body, page_map=None):
    page_map = page_map or {}
    front = [
        {
            "title": "BÁO CÁO BÀI TẬP LỚN XỬ LÝ ẢNH",
            "chapter": 0,
            "items": [
                P("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI — KHOA CÔNG NGHỆ THÔNG TIN"),
                P("TĂNG CƯỜNG TƯƠNG PHẢN, KHỬ NHIỄU VÀ XỬ LÝ BIÊN VÙNG TỐI ỨNG VIÊN TRÊN ẢNH SAR"),
                P(
                    "Đề kết hợp đã đăng ký — Xử lý ảnh truyền thống NumPy — Demo Streamlit — Python 3.13"
                ),
                P(
                    "; ".join(m["id"] + " — " + m["name"] for m in TEAM)
                    + ". TV1 là trưởng nhóm. MSSV, lớp và chữ ký: nhóm bổ sung."
                ),
                P(
                    "Giảng viên: theo phân công của lớp. Tài liệu học phần trong dự án ghi TS. Phan Thanh Toàn và TS. Cao Thị Luyên; nhóm xác nhận người hướng dẫn trực tiếp trước khi nộp."
                ),
                P(
                    "Hà Nội, tháng 11 năm 2026. Bản cập nhật từ mã nguồn và kết quả đo thực tế. Không thực hiện video demo trong đợt công việc này theo yêu cầu người dùng."
                ),
            ],
        },
        {
            "title": "Lời xác nhận phạm vi và phân công nhóm",
            "chapter": 0,
            "items": [
                P(
                    "Tài liệu trình bày phương pháp và kết quả của phiên bản dự án đang được kiểm tra. Các số liệu lấy từ lần chạy có manifest và hash mã nguồn. Đây không phải lời cam đoan đã được sinh viên ký: từng thành viên cần đọc, xác nhận công việc và chịu trách nhiệm về nội dung trước khi nộp."
                ),
                T(
                    "Phân công hiện tại — tên do nhóm cung cấp, đóng góp/chữ ký chờ xác nhận",
                    [
                        ["Vai trò", "Phần mã / báo cáo", "Đóng góp / ký"],
                        *[
                            [m["id"] + " — " + m["name"], responsibility, "Để trống"]
                            for m, responsibility in zip(
                                TEAM,
                                [
                                    "Tích hợp, demo; chương 1 và 5",
                                    "Kiểm chứng; chương 2, mục 3.7",
                                    "Lọc, tăng cường; mục 3.2–3.3",
                                    "Biên, hình thái; mục 3.4–3.6",
                                    "Dữ liệu, thực nghiệm; chương 4",
                                ],
                            )
                        ],
                    ],
                ),
                P(
                    "Mỗi người cần có đóng góp thực tế và trả lời được câu hỏi liên quan phần của người khác. Không suy ra đóng góp từ phân công đề xuất hoặc tự chia đều 20%. Bảng đánh giá chéo có 20 lượt trong Excel, được để trống để nhóm tự nhận xét và xác nhận."
                ),
                P(
                    "Hồ sơ sử dụng công cụ AI được nêu ở phụ lục. Không sửa ngày/tác giả commit để tạo lịch sử 8 tuần. Các công việc hồi cứu phải có minh chứng, ngày bổ sung và người xác nhận thật."
                ),
            ],
        },
        {
            "title": "Mục lục",
            "chapter": 0,
            "items": [
                T(
                    "Nội dung và trang PDF",
                    [["Mục", "Trang"]]
                    + [
                        [
                            f"Chương {ch}. {CHAPTERS[ch]}",
                            str(
                                page_map.get(
                                    next(p["title"] for p in body if p["chapter"] == ch), "—"
                                )
                            ),
                        ]
                        for ch in range(1, 6)
                    ]
                    + [
                        [p["title"], str(page_map.get(p["title"], "—"))]
                        for p in back_pages()
                        if "(tiếp)" not in p["title"]
                    ],
                )
            ],
        },
        {
            "title": "Danh mục ký hiệu",
            "chapter": 0,
            "items": [
                T(
                    "Ký hiệu dùng thống nhất trong báo cáo",
                    [
                        ["Ký hiệu", "Ý nghĩa"],
                        ["I, R̂", "Ảnh quan sát và ước lượng ảnh sau lọc"],
                        ["N=H×W; k", "Số pixel và kích thước cửa sổ lẻ"],
                        ["μ, σ², L", "Trung bình, phương sai cục bộ, số look mô hình"],
                        ["CDF, LUT", "Phân bố tích lũy và bảng ánh xạ"],
                        ["Gx, Gy, G, θ", "Gradient theo trục, độ lớn và góc"],
                        ["A, B, β(A)", "Mask vùng, phần tử cấu trúc và biên hình thái"],
                        ["C_R", "Tương phản vùng/nền; không phải độ tròn"],
                        ["η", "Khả năng tách histogram Otsu"],
                        ["ENL, SSI, EPI", "Chỉ số độ phẳng ROI, biến thiên và đáp ứng Laplacian"],
                        ["AMBE, RMS", "Độ lệch sáng và độ tương phản chuẩn"],
                        ["TP, FP, TN, FN", "Kết quả dự đoán ở cấp ảnh theo nhãn thư mục"],
                        ["TB, SD", "Trung bình và độ lệch chuẩn mẫu"],
                        [
                            "σ_s, σ_r; a",
                            "Độ rộng không gian/mức xám Bilateral; hệ số damping Frost",
                        ],
                        [
                            "γ_L, γ_H, D₀, c",
                            "Mức gain thấp/cao, tần số cắt, độ dốc bộ lọc đồng hình",
                        ],
                        ["Ω, p_ij; ω₀, ω₁", "Cửa sổ, mẫu hàng i cột j; xác suất hai lớp Otsu"],
                        [
                            "h, CDF, μ_nền, μ_vùng",
                            "Histogram đếm, tổng tích lũy, hai trung bình dùng tính tương phản",
                        ],
                    ],
                ),
                P(
                    "Khi gặp thuật ngữ tiếng Anh: CLAHE là cân bằng histogram thích nghi có giới hạn tương phản; NMS là triệt tiêu không cực đại; hysteresis là nối biên bằng ngưỡng kép; ROI là vùng quan tâm; dark spot là vùng tối ứng viên. Không đồng nhất dark spot với dầu đã xác nhận."
                ),
            ],
        },
        {
            "title": "Danh mục hình và bảng",
            "chapter": 0,
            "items": [
                dict(
                    type="catalog_entry",
                    text=item["caption"] + " — mục " + ".".join(p["title"].split(".")[:2]),
                )
                for p in body
                for item in p["items"]
                if item["type"] in ["figure", "table"]
            ],
        },
    ]
    return front


def back_pages():
    return [
        {"title": "Tài liệu tham khảo", "chapter": 6, "items": [P(r) for r in REFERENCES[:6]]},
        {
            "title": "Tài liệu tham khảo (tiếp)",
            "chapter": 6,
            "items": [P(r) for r in REFERENCES[6:]]
            + [
                P(
                    "Danh mục dùng định dạng đánh số IEEE theo thứ tự xuất hiện. Metadata bài báo kế thừa hồ sơ tham khảo của dự án; nhóm cần mở bản gốc và kiểm tra lại trích dẫn trước nộp. Trong đợt này không truy cập nguồn ngoài dự án để xác minh giấy phép hay nội dung từng bài."
                )
            ],
        },
        {
            "title": "Phụ lục A. Tái lập và truy nguyên kết quả",
            "chapter": 7,
            "items": [
                P(
                    "Repo: https://github.com/hotung9108/utc-sar-oil-detection. Mã mới phải được commit theo ngày thực khi nhóm quyết định bàn giao; báo cáo ghi thêm hash nguồn vì lần chạy có working tree thay đổi."
                ),
                T(
                    "Các vị trí cần tra cứu",
                    [
                        ["Nội dung", "Đường dẫn từ gốc dự án"],
                        ["Môi trường", "pyproject.toml; uv.lock; .python-version"],
                        ["Ví dụ tính tay", "src/tv2/verification.py"],
                        ["Đối chiếu tất cả kết quả", "src/tv2/library_comparison.py"],
                        ["Thực nghiệm và lớp dữ liệu", "src/tv5/experiments.py"],
                        ["Bằng chứng đông cứng", "docs/report/evidence/"],
                        ["Slide và lời trình bày", "docs/slides/"],
                        [
                            "Nhật ký và đánh giá chéo",
                            "docs/management/PHAN_CONG_VA_MINH_CHUNG_BTL.xlsx",
                        ],
                    ],
                ),
                P(
                    "Tại thư mục gốc: uv sync --locked --all-extras; uv run python reproduce.py; uv run --extra docs python scripts/build_report.py; uv run --extra docs python scripts/build_defense_slides.py. Mở demo bằng uv run streamlit run streamlit_app.py. Dùng Python 3.13; script PDF dùng font Times New Roman của Windows để hỗ trợ tiếng Việt."
                ),
                P(
                    "File checksums.json đi kèm evidence cho phép đối chiếu tệp bảng đã dùng. Không chỉnh tay giá trị CSV để thay đổi kết luận. Nếu sửa mã thuật toán hoặc tham số thí nghiệm, chạy lại một lệnh tái lập rồi dựng lại báo cáo và slide."
                ),
            ],
        },
        {
            "title": "Phụ lục B. Mã kiểm chứng ví dụ số",
            "chapter": 7,
            "items": [
                P(
                    "Mã đầy đủ gọi trực tiếp thuật toán đang dùng: https://github.com/hotung9108/utc-sar-oil-detection/blob/main/src/tv2/verification.py. File tương ứng trong repo là src/tv2/verification.py; chạy uv run python -m src.verification. Bảng kết quả có trong docs/report/evidence/verification_hand_examples.json."
                ),
                P(
                    "Ví dụ 4×4 HE: ma trận gồm bốn hàng [0,0,0,0], [1,1,1,1], [2,2,2,2], [3,3,3,3]. Histogram [4,4,4,4], CDF [4,8,12,16]. LUT = round(255·(CDF−4)/(16−4)) = [0,85,170,255]. Cài đặt được gọi là global_histogram_equalization; sai số lớn nhất so kết quả tính tay bằng 0."
                ),
                P(
                    "Ví dụ 5×5 Lee: toàn ma trận bằng 100, riêng ô giữa bằng 200. Cửa sổ 3×3 quanh tâm có tám giá trị 100 và một giá trị 200. μ=1000/9; E[I²]=120000/9; σ²=E[I²]−μ²=80000/81. Với L=4, μ²/L lớn hơn σ² nên K=0; đầu ra tâm round(1000/9)=111. Kết quả đã kiểm chứng bằng NumPy qua custom_lee_filter."
                ),
                P(
                    "Ba fixture còn lại kiểm tra đạo hàm Sobel, diện tích erosion/dilation và ngưỡng Otsu. Kết quả kỳ vọng là hằng số tính trước, không lấy chính hàm đang kiểm tra làm đáp án. Bất kỳ ví dụ sai nào khiến lệnh kiểm chứng dừng với lỗi; không ghi PASS khi chỉ dựng được bảng."
                ),
            ],
        },
        {
            "title": "Phụ lục C. Nhật ký nhóm và sử dụng AI",
            "chapter": 7,
            "items": [
                P(
                    "Nhật ký 8 tuần trong tài liệu cũ là nội dung cần xác minh, không phải bằng chứng công việc đã thực hiện. Khung hồi cứu 16/09–10/11/2026 có 40 dòng TV1–TV5; nội dung đề xuất, ghi nhận cũ và minh chứng Git được tách riêng. Quy định chung ghi 3 tuần thực hiện trong khi phần mã nguồn yêu cầu 8 tuần commit; nhóm cần hỏi giảng viên cách áp dụng."
                ),
                P(
                    "Excel đánh giá chéo có 20 cặp khác người. Họ tên do nhóm cung cấp và tài khoản GitHub được đối chiếu với collaborators; MSSV, phần trăm đóng góp, điểm và chữ ký chờ nhóm điền. Tài liệu học, trình bày và câu hỏi từng người nằm trong docs/thanh_vien/. Khung hồi cứu bổ sung từ 10/08 đến 11/11/2026 ghi đúng ngày lập, không tạo lịch sử Git giả."
                ),
                P(
                    "Công cụ hỗ trợ trong đợt cập nhật: Codex qua ứng dụng. Phạm vi gồm đọc yêu cầu, rà mã, sửa lỗi, tổ chức module, tạo demo, đối chiếu thư viện, chạy thực nghiệm, tổng hợp báo cáo và tạo slide bằng mã. Các công cụ AI được tài liệu cũ nhắc tới cần nhóm xác nhận lại mức sử dụng thực tế; không mặc nhiên coi mọi khai báo cũ đã được kiểm chứng."
                ),
                P(
                    "Cách kiểm tra gồm kiểm thử hồi quy, số liệu đối chiếu từng ca, manifest, hash nguồn, kiểm tra PDF/slide và đối chiếu cấu trúc. Những kiểm tra tự động không thay thế việc sinh viên đọc công thức, hiểu mã, xác nhận nguồn và diễn tập bảo vệ. Nhóm cần ghi rõ những phần đã kiểm tra thực tế, người kiểm tra và ngày xác nhận."
                ),
                P(
                    "Kịch bản bảo vệ: 12 phút trình bày theo slide, 3 phút thao tác demo và 5 phút vấn đáp. Video 5–7 phút chưa tạo theo yêu cầu hiện tại. Các phần cá nhân và video là đầu việc còn lại trước khi nộp bộ hồ sơ đầy đủ."
                ),
            ],
        },
    ]


def styles():
    fonts = Path("C:/Windows/Fonts")
    for name, file in [
        ("TNR", "times.ttf"),
        ("TNR-Bold", "timesbd.ttf"),
        ("TNR-Italic", "timesi.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily(
        "TNR", normal="TNR", bold="TNR-Bold", italic="TNR-Italic", boldItalic="TNR-Bold"
    )
    pdfmetrics.registerFont(
        TTFont("MathFallback", str(Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSerif.ttf"))
    )
    return dict(
        body=ParagraphStyle(
            "Body", fontName="TNR", fontSize=13, leading=16.9, alignment=TA_JUSTIFY, spaceAfter=9
        ),
        cover=ParagraphStyle(
            "Cover",
            fontName="TNR-Bold",
            fontSize=18,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=24,
        ),
        cover_body=ParagraphStyle(
            "CoverBody",
            fontName="TNR",
            fontSize=13,
            leading=16.9,
            alignment=TA_CENTER,
            spaceAfter=24,
        ),
        title=ParagraphStyle("Title", fontName="TNR-Bold", fontSize=16, leading=20, spaceAfter=15),
        chapter=ParagraphStyle(
            "Chapter", fontName="TNR-Bold", fontSize=18, leading=23, spaceAfter=14
        ),
        caption=ParagraphStyle(
            "Caption", fontName="TNR-Italic", fontSize=13, leading=16.9, spaceAfter=7, spaceBefore=5
        ),
        table=ParagraphStyle("Table", fontName="TNR", fontSize=13, leading=16.9, alignment=TA_LEFT),
        algorithm=ParagraphStyle(
            "Algorithm", fontName="TNR", fontSize=13, leading=16.9, spaceAfter=9
        ),
        catalog=ParagraphStyle("Catalog", fontName="TNR", fontSize=13, leading=16.9, spaceAfter=2),
    )


def rich_text(value):
    """Escape text and supply only mathematical glyphs absent from Times New Roman."""
    glyphs = pdfmetrics.getFont("TNR").face.charToGlyph
    return "".join(
        escape(c) if ord(c) in glyphs else '<font name="MathFallback">' + escape(c) + "</font>"
        for c in str(value)
    )


class EquationFlowable(Flowable):
    """Typeset LaTeX math into PDF text and vector rules, never screenshots."""

    def __init__(self, latex, label):
        super().__init__()
        with matplotlib.rc_context({"mathtext.fontset": "stix"}):
            self.formula = MathTextParser("path").parse(
                "$" + latex + r"\qquad (" + label + ")$", dpi=72, prop=FontProperties(size=13)
            )
        self.width = self.formula.width
        self.height = self.formula.height + 12
        self.hAlign = "LEFT"
        if self.width > A4[0] - 5 * cm:
            raise ValueError("Equation is wider than the text area: " + label)

    def draw(self):
        for glyph in self.formula.glyphs:
            font, size, char = glyph[:3]
            x, y = glyph[-2:]
            name = "Equation-" + Path(font.fname).stem
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, font.fname))
            self.canv.setFont(name, size)
            self.canv.drawString(x, y + self.formula.depth + 6, chr(char))
        for x, y, w, h in self.formula.rects:
            self.canv.rect(x, y + self.formula.depth + 6, w, h, stroke=0, fill=1)


class ReportDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, "section_name"):
            self.page_map[flowable.section_name] = self.page


def render_pdf(pages):
    ss = styles()
    story = []
    last_ch = None
    for n, page in enumerate(pages):
        if n:
            story.append(PageBreak())
        ch = page["chapter"]
        if 1 <= ch <= 5 and ch != last_ch:
            story.append(Paragraph(f"CHƯƠNG {ch}. {escape(CHAPTERS[ch].upper())}", ss["chapter"]))
        title = Paragraph(escape(page["title"]), ss["cover"] if n == 0 else ss["title"])
        title.section_name = page["title"]
        story.append(title)
        last_ch = ch
        for item in page["items"]:
            kind = item["type"]
            if kind == "paragraph":
                story.append(
                    Paragraph(rich_text(item["text"]), ss["cover_body"] if n == 0 else ss["body"])
                )
            elif kind == "catalog_entry":
                story.append(Paragraph(rich_text(item["text"]), ss["catalog"]))
            elif kind == "equation":
                story.append(EquationFlowable(item["latex"], item["label"]))
            elif kind == "algorithm":
                story.append(Paragraph(escape(item["caption"]), ss["caption"]))
                story.append(
                    Paragraph(
                        "<br/>".join(rich_text(x) for x in item["text"].splitlines()),
                        ss["algorithm"],
                    )
                )
            elif kind == "table":
                caption = Paragraph(escape(item["caption"]), ss["caption"])
                emphasized = {tuple(c) for c in item.get("bold_cells", [])}
                rows = [
                    [
                        Paragraph(
                            ("<b>" + rich_text(c) + "</b>")
                            if i == 0 or (i, j) in emphasized
                            else rich_text(c),
                            ss["table"],
                        )
                        for j, c in enumerate(r)
                    ]
                    for i, r in enumerate(item["rows"])
                ]
                width = A4[0] - 5 * cm
                if len(rows[0]) == 2:
                    first_col = 0.35
                    if item["caption"] == "Nội dung và trang PDF":
                        first_col = 0.85
                    elif "Lệnh và sản phẩm" in item["caption"]:
                        first_col = 0.62
                    widths = [width * first_col, width * (1 - first_col)]
                elif len(rows[0]) == 4:
                    widths = [width * 0.28, width * 0.3, width * 0.2, width * 0.22]
                else:
                    widths = [width / len(rows[0])] * len(rows[0])
                tab = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
                tab.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6eff4")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#8b9ba7")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                caption.keepWithNext = True
                story.extend([caption, tab, Spacer(1, 10)])
            elif kind == "figure":
                path = ASSETS / item["path"]
                w, h = PILImage.open(path).size
                width = A4[0] - 5 * cm
                height = width * h / w
                if height > 220:
                    width *= 220 / height
                    height = 220
                story.append(
                    KeepTogether(
                        [
                            Image(str(path), width=width, height=height),
                            Paragraph(escape(item["caption"]), ss["caption"]),
                        ]
                    )
                )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("TNR", 10)
        canvas.drawString(3 * cm, 1.35 * cm, "BTL Xử lý ảnh — UTC | NumPy / Streamlit")
        canvas.drawRightString(A4[0] - 2 * cm, 1.35 * cm, str(doc.page))
        canvas.restoreState()

    doc = ReportDoc(
        str(OUT / "BAO_CAO_BTL_XLA.pdf"),
        pagesize=A4,
        leftMargin=3 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title="BTL Xử lý ảnh SAR — NumPy và Streamlit",
        author="; ".join(m["name"] for m in TEAM),
    )
    doc.page_map = {}
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=footer))
    doc.build(story)
    return doc.page_map


def latex_escape(text):
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(c, c) for c in str(text))


def write_latex(pages):
    lines = [
        r"\documentclass[13pt,a4paper]{extreport}",
        r"\usepackage{fontspec}",
        r"\setmainfont{Times New Roman}",
        r"\usepackage{amsmath,amssymb,graphicx,longtable,array,setspace,hyperref}",
        r"\usepackage[left=3cm,right=2cm,top=2.5cm,bottom=2.5cm]{geometry}",
        r"\setstretch{1.3}",
        r"\setlength{\emergencystretch}{3em}",
        r"\begin{document}",
    ]
    for page in pages:
        lines.extend([r"\clearpage", r"\section*{" + latex_escape(page["title"]) + "}"])
        for item in page["items"]:
            if item["type"] in ["paragraph", "catalog_entry"]:
                lines.extend([latex_escape(item["text"]), r"\par"])
            elif item["type"] == "equation":
                lines.append(
                    r"\begin{equation}"
                    + item["latex"]
                    + r"\tag{"
                    + item["label"]
                    + r"}\end{equation}"
                )
            elif item["type"] == "algorithm":
                lines.extend(
                    [r"\textbf{" + latex_escape(item["caption"]) + "}", r"\begin{flushleft}"]
                )
                lines.extend(latex_escape(x) + r"\\" for x in item["text"].splitlines())
                lines.append(r"\end{flushleft}")
            elif item["type"] == "figure":
                lines.extend(
                    [
                        r"\begin{center}\includegraphics[width=\linewidth]{assets/"
                        + item["path"]
                        + "}",
                        latex_escape(item["caption"]),
                        r"\end{center}",
                    ]
                )
            elif item["type"] == "table":
                n = len(item["rows"][0])
                width = round(14.6 / n, 2)
                lines.extend(
                    [
                        r"\noindent\textit{" + latex_escape(item["caption"]) + "}",
                        r"\begin{longtable}{" + "|".join([f"p{{{width}cm}}"] * n) + "}",
                    ]
                )
                lines.extend(
                    " & ".join(latex_escape(c) for c in row) + r"\\\hline" for row in item["rows"]
                )
                lines.append(r"\end{longtable}")
    lines.append(r"\end{document}")
    (OUT / "main.tex").write_text("\n".join(lines), encoding="utf-8")


def write_docx(pages):
    """Minimal editable Word package; text, tables and equations remain native."""

    def para(text, bold=False, size=26):
        return (
            '<w:p><w:pPr><w:spacing w:after="140" w:line="312" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
            + ("<w:b/>" if bold else "")
            + f'<w:sz w:val="{size}"/></w:rPr><w:t xml:space="preserve">'
            + xml_escape(str(text))
            + "</w:t></w:r></w:p>"
        )

    body = []
    images = []
    rels = []
    for i, page in enumerate(pages):
        if i:
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        body.append(para(page["title"], True, 32))
        for item in page["items"]:
            typ = item["type"]
            if typ in ["paragraph", "catalog_entry"]:
                body.append(para(item["text"]))
            elif typ == "algorithm":
                body.append(para(item["caption"], True))
                body.extend(para(line) for line in item["text"].splitlines())
            elif typ == "equation":
                body.append(
                    "<w:p><m:oMathPara><m:oMath><m:r><m:t>"
                    + xml_escape(item["text"] + " (" + item["label"] + ")")
                    + "</m:t></m:r></m:oMath></m:oMathPara></w:p>"
                )
            elif typ == "table":
                body.append(para(item["caption"], True))
                rows = item["rows"]
                tw = int(9070 / len(rows[0]))
                body.append(
                    '<w:tbl><w:tblPr><w:tblW w:w="9070" w:type="dxa"/><w:tblBorders>'
                    + "".join(
                        f'<w:{side} w:val="single" w:sz="4" w:color="8B9BA7"/>'
                        for side in ["top", "left", "bottom", "right", "insideH", "insideV"]
                    )
                    + "</w:tblBorders></w:tblPr>"
                )
                for idx, row in enumerate(rows):
                    body.append(
                        "<w:tr>"
                        + "".join(
                            f'<w:tc><w:tcPr><w:tcW w:w="{tw}" w:type="dxa"/></w:tcPr>'
                            + para(cell, idx == 0)
                            + "</w:tc>"
                            for cell in row
                        )
                        + "</w:tr>"
                    )
                body.append("</w:tbl>")
            elif typ == "figure":
                image = ASSETS / item["path"]
                images.append(image)
                rid = "rImg" + str(len(images))
                w, h = PILImage.open(image).size
                cx = int(16 / 2.54 * 914400)
                cy = int(cx * h / w)
                rels.append(
                    f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{len(images)}.png"/>'
                )
                body.append(
                    f'<w:p><w:r><w:drawing><wp:inline><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{len(images)}" name="Figure {len(images)}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="Figure"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
                )
                body.append(para(item["caption"]))
    body.append(
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1417" w:right="1134" w:bottom="1417" w:left="1701" w:header="708" w:footer="708"/></w:sectPr>'
    )
    ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
    with zipfile.ZipFile(OUT / "BAO_CAO_BTL_XLA.docx", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        )
        z.writestr(
            "_rels/.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rDoc" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        )
        z.writestr(
            "word/document.xml",
            '<?xml version="1.0" encoding="UTF-8"?><w:document '
            + ns
            + "><w:body>"
            + "".join(body)
            + "</w:body></w:document>",
        )
        z.writestr(
            "word/_rels/document.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(rels)
            + "</Relationships>",
        )
        for i, img in enumerate(images, 1):
            z.write(img, f"word/media/{i}.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_data()
    make_figures()
    freeze_evidence()
    body = sections(data)
    pages = front_pages(body) + body + back_pages()
    mapping = render_pdf(pages)
    # Repeat until the contents-page pagination stabilizes.
    for _ in range(4):
        pages = front_pages(body, mapping) + body + back_pages()
        new = render_pdf(pages)
        if new == mapping:
            break
        mapping = new
    else:
        raise RuntimeError("Pagination failed to stabilize")
    write_docx(pages)
    write_latex(pages)
    (OUT / "report_content.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    reader = PdfReader(OUT / "BAO_CAO_BTL_XLA.pdf")
    first = {
        ch: mapping[next(p["title"] for p in body if p["chapter"] == ch)] for ch in range(1, 6)
    }
    main_end = mapping["Tài liệu tham khảo"] - 1
    main_count = main_end - first[1] + 1
    c34 = first[5] - first[3]
    audit = dict(
        total_pages=len(reader.pages),
        chapter_start_pdf_pages=first,
        main_pages=main_count,
        chapter_3_4_pages=c34,
        chapter_3_4_fraction=c34 / main_count,
        page_map=mapping,
        source_sha256=data["manifest"]["source_sha256"],
        body_font="Times New Roman 13 pt",
        line_spacing=1.3,
        margins_cm=dict(left=3, right=2, top=2.5, bottom=2.5),
        limitations=[
            "Names supplied by the team; GitHub logins checked against collaborators. Student IDs, contributions and signatures remain pending.",
            "Video intentionally omitted.",
            "DOCX/LaTeX are editable sources from the same content; their pagination may differ by renderer.",
        ],
    )
    (OUT / "report_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {k: v for k, v in audit.items() if k != "page_map"}, ensure_ascii=False, indent=2
        )
    )
    assert 30 <= len(reader.pages) <= 60
    assert 25 <= main_count <= 40
    assert c34 > main_count / 2


if __name__ == "__main__":
    main()
