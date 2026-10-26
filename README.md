# Hót rác — OpenSCAD có tham số

Cấu trúc thư mục và vai trò dữ liệu: [docs/STRUCTURE.md](docs/STRUCTURE.md).

Mở `dustpan.scad` trong OpenSCAD. Source tự dựng profile/CSG độc lập.
Đơn vị mm; đáy đặt tại Z0. Các quy tắc và trạng thái kiểm chứng public nằm trong
[tóm tắt kiểm chứng](docs/validation-summary.md); checkpoint workspace và log local không nằm trong snapshot.

## Bản thử gọn hiện tại

Dùng cho phương án hốt cát/đất/cát vệ sinh thú cưng. Giữ hình dáng khay gốc và
lối quét giữa lòng; các chi tiết gia cường là giả thuyết thiết kế. Thử tải giữ trạng thái `not_run`.

- `reinforce_floor`: tăng riêng phần đáy phía sau từ3 lên4,2mm; bắt đầu ở
  `floor_start=0.1*depth` (Y20), chuyển tiếp cong chữ S trong `floor_ramp=30`mm.
  Đáy và bo nối đáy–thành R5 cùng nâng dần theo quintic, độ dốc và độ cong bằng0
  ở hai đầu công thức; mesh chia đoạn theo `fillet_steps`. Bo nâng cùng mặt đáy;
  phần đắp đặc nối vào thân và giữ mặt dưới phẳng.
- `reinforce_handle`: hai gân ngoài thành sau, trong mặt phẳng trước–sau, dày
  `brace_thickness=3`mm, nhô sau khay `brace_reach=15`mm, cao tới15mm trên mép thành
  (`brace_rise=15`). Gân có chân đặt trên Z0, thu dần lên cán và nằm ngoài lòng khay.
- `reinforce_walls`: hai gân ngoài mỗi thành bên, nhô3mm, rộng4mm, góc R1.
  Vị trí Y=-0.05depth và0.25depth, giữ trên vùng thành thẳng.
- `reinforce_rim`: gờ vát liên tục từ thành bên qua hai góc sau tới thành sau, nhô ra ngoài3mm, cao6mm;
  đỉnh ngang mép thành, toàn bộ tiết diện phát triển ra ngoài và xuống dưới.
  Mặt dưới vát; `outer_body()` dựng thành và vành chung tại góc theo tọa độ cung gốc.
  Hai tiếp tuyến góc sau thuộc đoạn mép ngang theo assertion của source. Gờ bên giữ
  nguyên20mm đầu mép hót và thuôn trong20mm tiếp theo.

Bốn option mặc định `true`, bật/tắt độc lập. Tắt cả bốn để về bản đối chiếu STEP.
Bao tổng bản gọn **206 × 215 × 250mm**, thể tích hình học từ STL tăng **7,79%**.
Tỷ lệ trên lấy từ mesh export trong report; các nhận định về độ bền, tải và lượng nhựa
không phải bằng chứng public đã tái lập và vẫn cần ca thử riêng.
Mép hót, phần giữa đáy và mặt dưới phẳng giữ nguyên. Phía sau nhô thêm6,5mm so
với bao cán cũ; lòng phía sau nâng1,2mm nên có giảm dung tích cục bộ.

Contract hiện hành gồm bốn switch và kích thước ở đầu SCAD. Các tham số
`reinforce_back`, `back_thickness`, `gusset_*`, `rim_rise` và đáy lõi/ô rỗng thuộc lịch sử đã thay thế.

## In FDM và support

Tư thế đề xuất để đánh giá là đáy khay đặt trên bàn, cán đứng theo Z. Chân gân
phía sau nằm Z0, gân thu dần lên cao; các gờ mới dùng tiết diện tam giác có độ
cao6mm qua bề ngang3,5mm (kể overlap0,5mm), với mặt dưới vát ra ngoài.

Verifier có sàng lọc mặt dưới mới theo ngưỡng45° so với mặt phẳng ngang, loại
vùng0,3mm đầu sát bàn. Screen áp dụng cho bản tổ hợp mặc định; cấu hình đổi kích thước
được kiểm tra hình học riêng. Diện tích mặt mới dưới ngưỡng khoảng8,14e-14mm²;
assertion chấp nhận tổng diện tích dưới8mm². Góc/bo nhỏ sát chân cần xem preview lớp.
Slicing, support/toolpath và profile máy/nozzle/vật liệu giữ trạng thái `not_run`.

Cán đứng thuận tiện cho tư thế in nhưng phải xét độ bền liên kết lớp khi bẻ cán.
Xác nhận support, tải tối đa, độ võng và bền lặp bằng các ca slicing/thử tải tương ứng.

## Kích thước gốc

`width=200`, `depth=200`, `wall_height=50`, `thickness=3`,
`handle_diameter=20`, `total_height=250`. Bao gốc200×208,5×250mm.
`rear_radius=23` cho bo lòng R20; `floor_fillet=5`, `handle_fillet=5`,
`ramp_angle=30`, `ramp_radius=100`. `arc_steps`, `fillet_steps`, `$fn` chỉnh độ mịn.
STEP gốc tịnh tiến +25Z để đối chiếu. Có relief0,01mm cạnh cán để tránh mặt trùng.
Các assertions bảo vệ quan hệ cơ bản; miền đã thử được ghi theo ma trận trong report.

## Fusion native

Gói script và hướng dẫn: [fusion/README.md](fusion/README.md). Nguồn SCAD được dựng bằng sketch cung tròn và các feature Extrude/Loft/Revolve/Combine. Chiều cao cán dùng expression để recompute; tiết diện và cờ gia cường dùng đường Run rebuild đã công bố.

Artifact native mở rộng tại `exports/fusion-corrected/` là dữ liệu local ngoài bộ công khai mặc định. Các kết quả đã sanitize và giới hạn kiểm chứng
được tóm tắt trong [validation summary](docs/validation-summary.md); report/runtime payload local bị loại.

## File bàn giao và lịch sử

- `exports/dustpan-reinforced.stl`: bản gọn hiện tại.
- `exports/reinforced-front.png`, `exports/reinforced-back.png`, `exports/reinforced-side.png`: ảnh hiện tại.
- `exports/reinforced-floor-section.png`: ảnh cắt minh họa từ STL cuối tạiY70.
- `exports/floor-transition-detail.png`: ảnh cận đoạn chuyển tiếp đáy/bo thành.
- `exports/preview.png`: preview public của source.
- `reference/dustpan.step`: prerequisite local, không mặc định phát hành.
- `docs/reinforcement-research.md`: nguồn kỹ thuật và giới hạn suy luận.
- `docs/validation-summary.md`: summary public; không thay thế hồ sơ Fusion/runtime local.

`exports/dustpan-reinforced.stl` là artifact gia cường được chọn cho bản công khai. Các bản render khảo sát khác được giữ trong workspace local; mỗi biến thể cần được nhận diện bằng source, tham số và hash riêng.

## Chạy lại trên Windows

Kiểm thử source public không cần STEP và không ghi vào repo. Chạy từ thư mục project;
đặt `OPENSCAD_BIN` nếu executable không có trong `PATH`. Output render nên đặt vào thư mục
tạm ngoài repo, không ghi đè artifact bàn giao.

```powershell
Set-Location '<project-root>'
python -m venv .venv
& .venv\Scripts\python.exe -m pip install -r requirements.txt
& .venv\Scripts\python.exe -m unittest discover -s tests -v
$scad = if ($env:OPENSCAD_BIN) { $env:OPENSCAD_BIN } else { 'openscad' }
$out = Join-Path ([IO.Path]::GetTempPath()) 'dustpan-preview.png'
& $scad --backend Manifold --render -o $out --imgsize '1200,1100' --viewall --autocenter dustpan.scad
```

Các kiểm chứng native/Fusion, slicer, thử tải, in thật và mesh self-intersection độc lập
được ghi theo trạng thái trong [validation summary](docs/validation-summary.md). Chi tiết
Fusion cần môi trường Fusion và input STEP riêng; không được suy ra từ test source offline.
