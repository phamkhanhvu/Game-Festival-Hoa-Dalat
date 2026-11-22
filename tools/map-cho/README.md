# Công cụ dựng khu cầu thang chợ và cầu đi bộ vào chợ (map Chợ Đà Lạt)

Các tệp Python đã dùng để dựng lại chi tiết khu cầu thang chợ trong `market.glb` và cập nhật `world_cho.js`.
Không cần cho game chạy; giữ lại để lần sau sửa tiếp khu này hoặc làm khu khác theo cùng cách.

Thứ tự chạy (cần `numpy`, `scipy`, `pillow`; đường dẫn làm việc đặt ở đầu mỗi tệp):

1. `glbio.py`: giải mã `market.glb` (đỉnh lượng tử hoá) thành mảng số và tách atlas.
2. `atlas.py`: mở rộng atlas 1024×1024 thành 2048×2048, thêm các ô vân mới (cửa sổ, kính, biển hiệu, tán cây, đá kè, tường xám cũ, mảng lam, tấm bê tông, bồn hoa).
3. `stage1.py`: xoá công trình cũ trong vùng, tính lại địa hình (cao độ thiết kế + nội suy điều hoà), dời mặt đường theo địa hình.
4. `stage2.py`: dựng hình khối mới (`geom.py`, thông số trong `design.py`) và ghi `market.glb`.
5. `stage3.py`: tính lại lưới đi lại `h`, lưới `top`, loại nền `k`, cao độ tuyến xe, điểm check-in và bản đồ nhỏ trong `world_cho.js`.

`bridge.py` (gọi từ `stage1.py`, `stage2.py`, `stage3.py`) dựng cầu đi bộ từ Khu Hòa Bình sang tầng trên chợ: mặt cầu lát gạch, lan can trắng, cột đèn, cửa chợ có mái bạt sọc dưới chữ CHỢ ĐÀ LẠT, cầu thang trắng hai nhịp lên sân thượng và nhà sân thượng cửa vòm.

`plaza.py` dựng khu đầu cầu phía Khu Hòa Bình theo 7 ảnh góc nhìn quanh số 31 Khu Hòa Bình: nhà xám cũ ba tầng có hàng quán dưới mái hiên, ki-ốt bên phải lối lên cầu, đảo cây bách có hàng rào cắt tỉa, cột đèn, cột điện, sân nhựa trước cầu, băng lam và tường tấm bê tông của khối rạp Hòa Bình. Atlas mở rộng thành 2048×2048 (8×8 ô), các ô mới nằm ở cột 4 đến 7.

`curbs.py` làm lại lề đường khu Hòa Bình (cần `shapely`): bỏ các dải lề chạy theo đường và đảo lát giữa đường, đổi mặt đất trong vùng sang màu nhựa, rồi viền một dải lề hẹp (0,6 m) ôm chân từng công trình. Nền và hiên riêng của công trình (sân trước rạp, hành lang dưới mái hiên) giữ nguyên. Vùng áp dụng là đa giác `ZONE` trong tệp.

Lưới `h` chỉ có một tầng (mặt đất, kể cả đường dưới gầm cầu). Lối đi nằm phía trên mặt đất được ghi riêng trong `world_cho.js`:

- `decks`: các mảng lồi phẳng `{ p:[[x,z],…], a, b, c, s:[đầu,cuối] }`, cao độ `y = a + b·x + c·z`; `s` là các đoạn của chuỗi mốc đi qua mảng đó.
- `deckPath`: chuỗi mốc `[x,z,y]` cho chạm-để-đi (mốc 0 nằm dưới đất ở đầu cầu, mốc cuối trên sân thượng).
- `deckProps`: vật cản trên tầng trên `[x, z, bán kính, cao độ]` (chậu cây).

Trong `index.html`, người chơi đứng trên mặt gần cao độ đang đứng nhất (`deckAt`, `pStep`), camera chui dưới gầm khi người chơi ở dưới bản sàn (`desiredCam`). Map không có `decks` thì chạy như cũ.

Hình dáng khu này dựng theo hai ảnh thực tế do chủ dự án cung cấp; biển hiệu trong game là chữ chung (KHÁCH SẠN, NGÂN HÀNG, ĐẶC SẢN ĐÀ LẠT), không dùng tên hay logo thương hiệu thật.
