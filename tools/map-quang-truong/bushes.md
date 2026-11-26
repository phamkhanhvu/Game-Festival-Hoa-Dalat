# Bụi cây ở quảng trường

Mô hình gốc có 255 khối bụi cây đa giác thô (vật liệu FOLIAGE, mỗi khối 66 đến 78 tam giác). `world.js` giữ danh sách này trong `WORLD.bushes`
(mỗi mục: x, z, cao độ chân, rộng x, rộng z, cao). Lúc tải, game gỡ các tam giác của những khối đó khỏi lưới FOLIAGE và dựng bụi cẩm tú cầu
vào đúng chỗ (hàm `buildBushes` trong `index.html`). Danh sách lấy từ `exp_tris.py` rồi tách theo thành phần liên thông: khối 60 đến 80 tam giác, cao 0,9 đến 1,9 m, rộng 1,5 đến 3,2 m.
