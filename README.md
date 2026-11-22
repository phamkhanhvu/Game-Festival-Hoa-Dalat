# DalatEvent — Từ xe đẩy thành thương hiệu

Game 3D chạy trên trình duyệt: kinh doanh quầy hàng trên Quảng trường Lâm Viên, Đà Lạt.

- `index.html`: toàn bộ luật chơi và giao diện
- `world.js`: lưới độ cao, vùng đi được và vị trí quầy, tem, cây, đèn (nướng từ mô hình quảng trường)
- `model.glb`: quảng trường; `character.glb`: nhân vật chính; `cast/`: nhân vật đám đông
- `decor.json`: cây, hoa, đèn đường, xe cộ; `bgm.mp3`: nhạc nền

## Bản đồ Chợ Đà Lạt
Mạng đường và đường bao nhà khu Chợ Đà Lạt – Khu Hòa Bình lấy từ OpenStreetMap (© OpenStreetMap contributors, giấy phép ODbL). Cao độ, mặt đứng nhà và các dãy nhà phố lấp thêm là dựng ước lượng.

Khu cầu thang chợ (bậc thang sáu nhịp, cây bách tán, toà nhà trắng đầu cong có sân thượng, cửa hàng đặc sản, hàng liễu, dãy khách sạn và tháp viễn thông phía trên) dựng chi tiết theo ảnh thực tế do chủ dự án cung cấp. Công cụ dựng nằm ở `tools/map-cho/`.

Cầu đi bộ từ Khu Hòa Bình vào tầng trên chợ (mặt cầu lát gạch, lan can trắng, cột đèn, cửa chợ mái bạt sọc xanh trắng, cầu thang trắng hai nhịp lên sân thượng, nhà sân thượng cửa vòm) cũng dựng theo ảnh thực tế. Người chơi đi được trên cầu, lên thang ra sân thượng, và đi dưới gầm cầu; phần này dùng tầng đi bộ thứ hai (`decks` trong `world_cho.js`).
