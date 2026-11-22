# Công cụ dựng khu cầu thang chợ (map Chợ Đà Lạt)

Các tệp Python đã dùng để dựng lại chi tiết khu cầu thang chợ trong `market.glb` và cập nhật `world_cho.js`.
Không cần cho game chạy; giữ lại để lần sau sửa tiếp khu này hoặc làm khu khác theo cùng cách.

Thứ tự chạy (cần `numpy`, `scipy`, `pillow`; đường dẫn làm việc đặt ở đầu mỗi tệp):

1. `glbio.py`: giải mã `market.glb` (đỉnh lượng tử hoá) thành mảng số và tách atlas.
2. `atlas.py`: mở rộng atlas 1024×1024 thành 1024×2048, thêm 16 ô vân mới (cửa sổ, kính, biển hiệu, tán cây, đá kè).
3. `stage1.py`: xoá công trình cũ trong vùng, tính lại địa hình (cao độ thiết kế + nội suy điều hoà), dời mặt đường theo địa hình.
4. `stage2.py`: dựng hình khối mới (`geom.py`, thông số trong `design.py`) và ghi `market.glb`.
5. `stage3.py`: tính lại lưới đi lại `h`, lưới `top`, loại nền `k`, cao độ tuyến xe, điểm check-in và bản đồ nhỏ trong `world_cho.js`.

Hình dáng khu này dựng theo hai ảnh thực tế do chủ dự án cung cấp; biển hiệu trong game là chữ chung (KHÁCH SẠN, NGÂN HÀNG, ĐẶC SẢN ĐÀ LẠT), không dùng tên hay logo thương hiệu thật.
