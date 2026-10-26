# Tóm tắt kiểm chứng

Bản công khai gồm source SCAD, builder Fusion, tám test contract độc lập và artifact gia cường được chọn.

## Source và artifact

- `dustpan.scad`: SHA-256 `9f8a284a37d630a114eb1b5773fc276a5a30d8fef1dacd14db03247d8cb54db2`.
- Builder `fusion/Dustpan/geometry.py` và test source hash đối chiếu cùng revision này.
- [dustpan-reinforced.stl](../exports/dustpan-reinforced.stl): SHA-256 `264fdfeafb70c1867f159f24fed92b74c0215b4343dac95e5d10fdfc4f18c2b0`, bao `206 × 215 × 250 mm`, bounds `[-103,-100,0]` đến `[103,115,250]` mm.
- Mesh được đọc lại có20.252 facet và60.756 vertex record trong STL ASCII.

## Kiểm chứng công khai

`python -m unittest discover -s tests -v` đạt **8/8 test** trên bộ source bàn giao. Các test kiểm tra source hash/default, chuyển tiếp đáy quintic, profile cán, gờ/vành, cung gân và miền tham số.

Source SCAD và builder giữ các kích thước chức năng; bước chuẩn bị bản công khai sửa tài liệu, locator và khả năng chạy test độc lập.

## Bằng chứng native và giới hạn

Project có hồ sơ local trước đây cho bảy cấu hình native Fusion. Các kết quả đó thuộc revision và môi trường được ghi tại checkpoint; bản công khai giữ source Add-In để dựng lại. Các F3D/STEP/STL native mở rộng tại `exports/fusion-corrected/` là dữ liệu local, nằm ngoài bộ artifact công khai mặc định.

Lần công khai này đã chạy lại test offline; native Fusion mới, slicer/toolpath, in thật, fit, tải, độ bền và kiểm tra tự giao mesh độc lập giữ trạng thái `not_run`.

## Đầu vào local

`reference/dustpan.step` là đầu vào khảo sát STEP của project local. Source tham số và tám test bàn giao chạy độc lập với file đó. Người dùng có input phù hợp có thể đặt file tại vị trí này cho quy trình đối chiếu STEP riêng.
