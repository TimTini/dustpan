# Tài liệu gia cường hót rác

Tra cứu ngày 2026-10-15. Phạm vi: đáy; nối đáy–thành; thành; nối thành–tay cầm.
Đây là hồ sơ khảo sát ở preset `a42c5f2`. Mô tả gân XZ và ứng viên thiết kế bên dưới
thuộc checkpoint đó. Bản hiện hành dùng gân YZ ngoài khay, đáy chuyển tiếp quintic
và vành liền góc; xem [README](../README.md) và [tóm tắt kiểm chứng public](validation-summary.md).
Quy trình public chỉ giữ các ràng buộc và giới hạn có thể tái lập từ source; checkpoint/workspace
riêng không thuộc snapshot này.
Lượt hợp nhất ngày15/10/2026 đối chiếu source và report local; các nguồn web bên dưới
giữ ngày tra cứu ban đầu và phạm vi mô tả của hồ sơ khảo sát.

## Mức bằng chứng và nhận định cần sửa

Preset tại commit `a42c5f2` đã được kiểm tra hình học; thử độ bền giữ trạng thái `not_run`.
Solid kín và thêm 6,95% thể tích là số đo hình học; tải hữu ích cần phép thử riêng.
Tăng dày có thể hữu ích; quyết định phải dựa vào tải, hướng uốn và đường truyền lực.
Các phương án ứng dụng dưới đây là suy luận thiết kế; kích thước giữ trạng thái đề xuất.

## 1. Đáy

[Rutland Plastics Design Guide](https://www.rutlandplastics.co.uk/wp-content/uploads/2021/01/Design-Guide-Rutland-Plastics-2019.pdf), mục Design for Stiffness, trang in 5–6:
giới thiệu gân, rãnh chữ V và dạng sóng; nhấn mạnh chiều cao tiết diện và hướng
bố trí theo bài toán uốn. Tấm chịu nhiều hướng cần xét cấu trúc gân tương ứng.

Áp dụng đề xuất: so sánh gân dọc theo nhịp từ phần sau ra phía trước với lưới gân
hai hướng. Đầu gân phải truyền lực vào vùng đỡ. Gân dưới đáy có thể cản tiếp xúc
sàn; gân trong lòng cản rác và vệ sinh. Giữ mép hót là ràng buộc bắt buộc khi so sánh.

## 2. Nối đáy–thành

[Avient — Best Practices for Reducing Stress Cracking in Molded Plastic Parts](https://careers.polyone.com/sites/default/files/2022-08/Environmental%20Stress%20Cracking%20Resistance%20_ESCR_%20Design%20Guide%20%281%29.pdf), mục Contour/Gussets, hình 3 và 12–14:
bo chuyển tiếp giảm tập trung ứng suất; ke tam giác nối thành/trụ đứng với sàn.
Các tỷ lệ co ngót/draft trong tài liệu thuộc ép phun.

Áp dụng đề xuất: xét ke trong mặt phẳng vuông góc thành, một cạnh bám thành và
một cạnh bám đáy, kết hợp bo chân. Source gốc đã có `floor_fillet=5`; cần đánh giá
bo hiện có trước khi bổ sung. Ke có thể làm giảm chỗ chứa rác.

## 3. Thành

[Covestro — Part and Mold Design](https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1557222937.pdf#page=69), trang in 68, hình 3-17–3-19:
minh họa thành dạng sóng, thành cong và biên dạng làm cứng mép tự do.

Áp dụng đề xuất: so sánh thành có gân đứng, thành cong nhẹ và mép có gờ/tiết diện
gập. Vành của preset khảo sát là ứng viên làm cứng mép; hiệu quả chịu tải toàn
khay cần phép thử riêng. Chọn theo biến dạng cần giảm: banh mép, uốn mặt thành
hay xoắn toàn khay.

## 4. Nối thành–tay cầm

[Protolabs — Design Stronger Moulded Parts](https://www.protolabs.com/en-gb/resources/design-tips/design-stronger-moulded-parts/), mục Ribs/Gussets/Fillets:
gân và ke hỗ trợ chân trụ, thành và liên kết xuống sàn; bo giúp giảm tập trung
ứng suất ở các chỗ nối.

Áp dụng đề xuất: coi chân cán là điểm đưa mômen vào khay. Cần khảo sát ke nối từ
đoạn cán cao hơn thành xuống vùng đáy/thành rộng, trong mặt phẳng trước–sau khi
kiểm tra uốn theo hướng này. Uốn ngang và xoắn cần ca tải riêng. Hai gân XZ ở preset
`a42c5f2` nằm tại Z5..45, dưới mép thành Z50. Hiệu quả của chúng với tải trước–sau
giữ trạng thái `unverified`; chốt ưu tiên sau phân tích hoặc thử tải cùng điều kiện.

## 5. Điều kiện riêng của in FDM

[Stratasys FDM Design Guide](https://www.stratasys.com/siteassets/sdm/content---website-storage/design-guides/dg_sdm_fdm_0725a.pdf?v=490918#page=7), mục 3.7–3.8:
gân/ke đỡ trụ và bo chuyển tiếp có ích; chọn bề dày gân theo điều kiện FDM.
Quy tắc tránh lõm co ngót của ép phun giữ phạm vi công nghệ ép phun.

[Protolabs Network — Designing for FDM](https://www.hubs.com/knowledge-base/how-design-parts-fdm-3d-printing/), mục Build direction:
FDM có tính dị hướng; hướng lớp ảnh hưởng đến đáp ứng khi chịu tải.

Áp dụng đề xuất: mọi so sánh hình học phải cố định vật liệu, hướng in, thông số
in và cách đặt tải. Phải phân biệt độ võng, tải phá hỏng và độ bền sau nhiều lần dùng.

## Trước khi sửa thiết kế tiếp

- Tách hai tình huống: giữ/đẩy khi khay đang tựa sàn và nhấc khay chứa rác.
- Khi nhấc, xét đường lực: rác → đáy → nối đáy–thành → thành sau/chân cán → tay.
- Xác định tải dự kiến, vị trí cầm, hướng tác lực và mức võng chấp nhận được.
- So sánh từng thay đổi với bản gốc cùng điều kiện; ghi riêng mesh validity và thử tải.
- Giữ nhãn thử nghiệm cho preset Cân bằng đến khi có bằng chứng tải phù hợp.

Giới hạn truy cập: một số lần mở PDF Covestro/Rutland bị timeout; các đoạn liên
quan vẫn truy xuất được qua nội dung đã lập chỉ mục trên miền chính hãng.
Dùng nguồn primary cho nguyên lý và phép đo/thử của mẫu cho kích thước áp dụng.
