# Hót rác — Fusion native từ SCAD

Gói `Dustpan/` gồm `Dustpan.py`, `geometry.py` và `Dustpan.manifest`. Script dựng sketch có cung tròn thật cùng các feature Extrude, Loft, Revolve và Combine trong timeline parametric. Source là `../dustpan.scad`, SHA256 `9f8a284a37d630a114eb1b5773fc276a5a30d8fef1dacd14db03247d8cb54db2`.

## Chạy và chỉnh sửa

1. Sao chép nguyên thư mục `Dustpan` đến đường dẫn muốn dùng.
2. Mở Fusion, vào Utilities → Add-Ins → Scripts and Add-Ins → Scripts → +, chọn thư mục `Dustpan` rồi Run.
3. Mỗi lần Run tạo document mới. Bắt đầu từ document mới để dùng defaults trong `geometry.py`.
4. Bốn cờ `REINFORCE_FLOOR`, `REINFORCE_HANDLE`, `REINFORCE_WALLS`, `REINFORCE_RIM` ở đầu `Dustpan.py` chọn các gia cường khi Run.
5. Giữ document Dustpan đang hoạt động khi muốn dựng lại theo giá trị trong Change Parameters. Run đọc giá trị hiện tại và tạo bản mới; document trước giữ nguyên để đối chiếu.

## Đường cập nhật tham số

- **Recompute:** `total_height` liên kết với chiều sâu Extrude của cán. Kiểm chứng native thay+10mm, đo bao/thể tích và phục hồi expression gốc.
- **Rebuild:** kích thước thân, bo, góc dốc và kích thước gia cường tạo tiết diện bằng Python lúc Run. Nhập giá trị trong Change Parameters rồi Run để dựng đồng bộ tiết diện.
- `floor_start` giữ expression `0.1 * depth` ở cấu hình chuẩn. `ramp_angle` dùng độ; các tham số chiều dài dùng mm.
- Sketch tiết diện dùng constraints Fix để lưu tọa độ đã tính của lần dựng. Feature Extrude giữ expression được builder khai báo. Phạm vi recompute được đánh giá theo toàn chuỗi phụ thuộc.

## Hình học và độ chính xác

- Cove đáy–thành R5 được dựng bằng Loft, gồm vùng quanh cán. Tiết diện đầu dùng−89,9° để xử lý arc bán kính0; thay đổi tọa độ tại R5 dưới0,009mm.
- Đáy sau nâng1,2mm theo quintic trong đoạn30mm; bo hai bên nâng cùng đáy. Pad sau dùng footprint offset vào giữa thành và cavity nâng tương ứng.
- Gân thành dùng hull của ba tâm tròn qua các cung tiếp tuyến R1, cắt theo envelope mép hót.
- Vành bên theo cao độ mép dốc, góc sau là Revolve tam giác, vành sau là Extrude tam giác. Mép trên ngang thành và mặt dưới vát.
- Điểm sketch được xác nhận nằm trên plane; offset/chiều extrusion theo normal thực tế; mỗi góc Revolve được kiểm tra quadrant trước Combine.

## Kiểm chứng và artifact

Artifact local mở rộng nằm tại `../exports/fusion-corrected/`, mỗi cấu hình có `.f3d`, `.step`, `.stl`, `.png`; bộ công khai mặc định gồm source Add-In và artifact gia cường được chọn trong README chính.
Kết quả public đã sanitize được tóm tắt trong [validation summary](../docs/validation-summary.md);
report/runtime payload local không thuộc snapshot.

Ma trận gồm `original`, `floor`, `handle`, `walls`, `rim`, `compact`, `scaled`. Bản scaled dùng width/depth220mm, thickness4mm, total_height270mm, floor_start22mm. Tolerance đặt trước audit: bao0,05mm, thể tích tương đối0,25%, bề mặt lấy mẫu0,15mm, cao độ cục bộ0,05mm. Sampling giữ ý nghĩa phép lấy mẫu; số điểm và max sai lệch nằm trong report.

**Bằng chứng local trước đây:** report đã ghi chín test offline, bảy cấu hình native và audit độc lập đạt; các F3D được mở lại và thay chiều cao cán+10mm đã được đo/phục hồi. Report không thuộc public snapshot, nên phải chạy lại trong Fusion trước khi coi đây là release gate hiện tại.

Sai lệch bề mặt lấy mẫu lớn nhất so SCAD: STL0,132116mm, STEP0,126818mm; ngưỡng0,15mm. Sai lệch thể tích lớn nhất: STL0,002519%, STEP0,004205%; ngưỡng0,25%. Bản scaled có bất đồng properties giữa STEP và native VeryHigh0,01654%; giữ đây là diagnostic, không phải chứng nhận vật lý. Slicer, bản in, thử tải và mesh self-intersection độc lập giữ trạng thái `not_run`.

```powershell
Set-Location '<project-root>'
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Script Add-In chạy trong Fusion; test source public ở trên không cần MCP hoặc bất kỳ runtime endpoint local nào.

## Nguyên nhân sai và hướng dẫn dùng lại

Các checkpoint và bằng chứng chi tiết của lần dựng trước là local-only. Public snapshot chỉ giữ
source, Add-In, artifact được chọn và [validation summary](../docs/validation-summary.md).
