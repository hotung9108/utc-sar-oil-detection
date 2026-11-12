"""Update the supplied roster and add an explicitly retrospective evidence template.

Keeps student IDs, scores, contribution percentages, signatures and old Git snapshots.
Does not create commits, modify Git authors, or assert past work was performed.
"""

import json
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
MANAGEMENT = ROOT / "docs/management"
TEAM = json.loads((MANAGEMENT / "thanh_vien.json").read_text(encoding="utf-8"))


def main():
    """Apply confirmed names and generate blank retrospective rows without erasing evidence."""
    path = MANAGEMENT / "PHAN_CONG_VA_MINH_CHUNG_BTL.xlsx"
    workbook = load_workbook(path)
    before = {s.title: list(s.values) for s in workbook}
    members = workbook["Thanh_vien"]
    members["A1"] = "THÀNH VIÊN VÀ PHÂN CÔNG HIỆN TẠI"
    members["A2"] = (
        "Họ tên do nhóm cung cấp; GitHub đối chiếu collaborators. MSSV, tỷ lệ đóng góp và xác nhận thực tế để nhóm điền."
    )
    members["A3"] = "Cập nhật 11/11/2026; không gán lại tác giả Git hoặc xác nhận đóng góp quá khứ."
    members["G6"] = "Module / file hiện tại"
    for index, member in enumerate(TEAM, 7):
        assert members.cell(index, 1).value == member["id"]
        for col, value in [(2, member["name"]), (4, member["github"]), (7, member["modules"])]:
            members.cell(index, col, value)
    peer = workbook["Danh_gia_cheo"]
    peer["A3"] = (
        "Họ tên/GitHub ở sheet Thanh_vien đã cập nhật; điểm, nhận xét, minh chứng và chữ ký vẫn do từng người tự điền."
    )

    raw = subprocess.check_output(
        ["git", "log", "--reverse", "--format=%H%x09%cI%x09%an%x09%s"], cwd=ROOT
    ).decode("utf-8")
    commits = [line.split("\t", 3) for line in raw.splitlines()]
    start, end = date(2026, 8, 10), date(2026, 11, 11)
    weeks = []
    cursor = start
    while cursor <= end:
        stop = min(cursor + timedelta(days=6), end)
        evidence = [c for c in commits if cursor <= datetime.fromisoformat(c[1]).date() <= stop]
        weeks.append((cursor, stop, evidence))
        cursor = stop + timedelta(days=1)

    sheet_name = "Hoi_cuu_1008_1111"
    if sheet_name not in workbook.sheetnames:
        sheet = workbook.create_sheet(sheet_name)
        sheet.append(["HỒI CỨU 10/08–11/11/2026 — LẬP NGÀY 11/11, CHƯA XÁC NHẬN CÔNG VIỆC"])
        sheet.append(
            [
                "94 ngày, 14 khoảng tuần. Ô trống là thiếu minh chứng, không phải khẳng định đã làm. Commit là của cả repo, chưa quy cho từng người."
            ]
        )
        sheet.append(
            [
                "Khoảng",
                "Từ",
                "Đến",
                "TV",
                "Họ tên",
                "GitHub",
                "Công việc thực tế",
                "Link sản phẩm/minh chứng",
                "Commit thật trong tuần (toàn repo)",
                "Ngày bổ sung",
                "Người xác nhận",
                "Trạng thái",
            ]
        )
        for index, (begin, stop, evidence) in enumerate(weeks, 1):
            git_evidence = (
                "; ".join(c[0][:7] for c in evidence)
                or "Không thấy commit; công việc ngoài Git chưa xác minh"
            )
            for member in TEAM:
                sheet.append(
                    [
                        f"K{index}",
                        begin.isoformat(),
                        stop.isoformat(),
                        member["id"],
                        member["name"],
                        member["github"],
                        None,
                        None,
                        git_evidence,
                        None,
                        None,
                        "Chưa xác minh",
                    ]
                )
        sheet.freeze_panes = "G4"
        sheet.auto_filter.ref = f"A3:L{sheet.max_row}"
        widths = [12, 15, 15, 8, 24, 20, 45, 45, 65, 18, 24, 20]
        for index, width in enumerate(widths, 1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        for row in sheet:
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        for cell in sheet[3]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="16324F")
        for index in range(4, sheet.max_row + 1):
            sheet.row_dimensions[index].height = 45
    workbook.save(path)
    reopened = load_workbook(path)
    for name, values in before.items():
        if name not in {"Thanh_vien", "Danh_gia_cheo"}:
            assert list(reopened[name].values) == values, name
    for row_before, row_after in zip(
        before["Thanh_vien"][6:], list(reopened["Thanh_vien"].values)[6:]
    ):
        assert row_before[2] == row_after[2]  # Student IDs.
        assert row_before[9:] == row_after[9:]  # Contributions and evidence.
    assert before["Danh_gia_cheo"][6:] == list(reopened["Danh_gia_cheo"].values)[6:]

    lines = [
        "# Khung hồi cứu từ 10/08 đến 11/11/2026",
        "",
        "Lập ngày 11/11/2026 từ lịch sử Git hiện có. Đây là 94 ngày, gồm 13 tuần trọn vẹn và 3 ngày, không phải 8 tuần. Không sửa ngày commit, không giả tác giả hoặc chia commit cho người chưa thực hiện.",
        "",
        "Excel có sheet `Hoi_cuu_1008_1111` với 70 dòng = 14 khoảng ×5 thành viên. Công việc thực tế, sản phẩm, ngày bổ sung và người xác nhận để trống. Nhóm có thể bổ sung lịch sử chat, bản nháp, file gốc hoặc commit thật; phải ghi ngày bổ sung thật và không coi bảng mới lập là kế hoạch có từ tháng 8.",
        "",
        "Các commit dưới đây thuộc toàn repo, chưa dùng để xác nhận đóng góp từng thành viên. Danh sách collaborators chỉ chứng minh quyền truy cập hiện tại.",
        "",
        "| Khoảng | Từ ngày | Đến ngày | Commit thật theo ngày committer |",
        "| --- | --- | --- | --- |",
    ]
    for index, (begin, stop, evidence) in enumerate(weeks, 1):
        links = ", ".join(
            f"[{c[0][:7]}](https://github.com/hotung9108/utc-sar-oil-detection/commit/{c[0]})"
            for c in evidence
        )
        lines.append(
            f"| K{index} | {begin:%d/%m/%Y} | {stop:%d/%m/%Y} | {links or 'Không thấy commit trong khoảng này'} |"
        )
    lines += [
        "",
        "Không có commit không chứng minh không có công việc ngoài Git. Ngược lại, số commit không đủ chứng minh chất lượng hoặc tỷ lệ đóng góp. Nhóm cần giải trình thật với giảng viên và hoàn thiện minh chứng còn thiếu.",
        "",
    ]
    (MANAGEMENT / "HOI_CUU_TU_10_08.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        "Updated five names/accounts; preserved IDs, peer scores and historical sheets; retrospective template has 70 rows."
    )


if __name__ == "__main__":
    main()
