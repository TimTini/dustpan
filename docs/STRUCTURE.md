# Cấu trúc dự án dustpan

Điểm bắt đầu: [README](../README.md). Source chính và script chạy giữ ở thư mục gốc. Chuẩn thư mục áp dụng ngày 26/10/2026.

## File và thư mục hiện có

Source: `dustpan.scad`.

- `reference/`: input STEP local; không thuộc public snapshot mặc định.
- [exports/](../exports/): đầu ra CAD, preview và report theo pipeline.
- [docs/](../docs/): tài liệu project và ảnh minh họa.
- [fusion/](../fusion/): script/manifest, hướng dẫn và test Fusion.
- [tests/](../tests/): kiểm thử project.
- `work/`: checkpoint và khảo sát local; bị loại khỏi public snapshot.
- [validation-summary.md](validation-summary.md): tóm tắt kiểm chứng đã sanitize, không chứa log/runtime payload.

Input STEP là prerequisite local tùy chọn cho đối chiếu Fusion; kiểm thử source offline không cần file này.
Môi trường `.venv` là local và `requirements.txt` khai báo dependency.

## Quy ước dùng chung

- `exports/` chứa đầu ra; README/manifest xác định bộ hiện hành và revision nguồn.
- `reference/` chứa input/provenance local; không đưa vào public snapshot nếu chưa xác nhận quyền phát hành.
- `docs/` chứa tài liệu public; `work/` và `backups/` chứa checkpoint/snapshot local, không phải release input.
- `archive/` giữ phiên bản lịch sử khi project dùng cơ chế đó. Các thư mục chuyên biệt tiếp tục theo pipeline hiện có.
- Kiểm source, render, native Fusion, slicer và thử vật lý có trạng thái bằng chứng riêng; public summary giữ rõ phần nào chưa chạy.

## Tra đường dẫn lịch sử

Các vị trí dữ liệu hiện tại được giữ trong đợt chuẩn hóa này. Report, snapshot và log cũ giữ thông tin tại thời điểm chạy; áp dụng bản đồ trên khi tra locator cũ. Tài liệu và script đang dùng tham chiếu vị trí hiện hành.
