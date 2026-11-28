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

`curbs.py` làm lại lề đường toàn bản đồ (cần `shapely`): bỏ các dải lề chạy theo đường và đảo lát giữa đường, đổi mặt đất nằm giữa đường và nhà sang màu nhựa (cách đường tối đa 14 m, cách nhà tối đa 16 m), rồi viền một dải lề hẹp 0,6 m ôm chân từng công trình. Sân lát rộng, nền và hiên riêng của công trình giữ nguyên; khu cầu thang chợ (`design.ZONE_E`) không đụng tới. Tệp này cũng gỡ dãy bạt xanh dương quanh khối rạp Hòa Bình.

Lưới `h` chỉ có một tầng (mặt đất, kể cả đường dưới gầm cầu). Lối đi nằm phía trên mặt đất được ghi riêng trong `world_cho.js`:

- `decks`: các mảng lồi phẳng `{ p:[[x,z],…], a, b, c, s:[đầu,cuối] }`, cao độ `y = a + b·x + c·z`; `s` là các đoạn của chuỗi mốc đi qua mảng đó.
- `deckPath`: chuỗi mốc `[x,z,y]` cho chạm-để-đi (mốc 0 nằm dưới đất ở đầu cầu, mốc cuối trên sân thượng).
- `deckProps`: vật cản trên tầng trên `[x, z, bán kính, cao độ]` (chậu cây).

Trong `index.html`, người chơi đứng trên mặt gần cao độ đang đứng nhất (`deckAt`, `pStep`), camera chui dưới gầm khi người chơi ở dưới bản sàn (`desiredCam`). Map không có `decks` thì chạy như cũ.

Hình dáng khu này dựng theo hai ảnh thực tế do chủ dự án cung cấp; biển hiệu trong game là chữ chung (KHÁCH SẠN, NGÂN HÀNG, ĐẶC SẢN ĐÀ LẠT), không dùng tên hay logo thương hiệu thật.

## Khu sau lưng chợ (thư mục `rear/`)

`rear/rear.py` dựng lại khu sau lưng Chợ Đà Lạt theo bốn ảnh chụp từ trên cao (11.2026). Chạy trên `market.glb` và `world_cho.js` hiện có, không cần các bước ở trên:

    python3 rear/rear.py <market.glb vào> <world_cho.js vào> <market.glb ra> <world_cho.js ra>

Cần `numpy`, `scipy`, `pillow`, `shapely`. Các tệp:

- `fr.py`: hệ trục riêng của chợ (s dọc tường sau về đông bắc, t vuông góc về phía Khu Hòa Bình).
- `plan.py`: mặt bằng các khối mới theo (s, t).
- `tiles.py`: 8 ô vân mới ở hàng 6 và 7 của atlas (tôn sóng, băng cửa kính, lam đứng, taluy, tôn cũ, mặt ki-ốt, bạt sọc, cửa cuốn).
- `common.py`: mặt đất thấp nhất theo lưới 0,5 m, hàm dựng tường chia đoạn theo ô vân.
- `rear.py` (phần 1 đến 3), `rearB.py` (phần 4 đến 7), `rear2.py` (ghi tệp, lưới đi lại, bản đồ nhỏ); `loop.npy` là tuyến xe vòng quanh chợ.

Những gì được dựng: cánh đông bắc của chợ cũ (hai băng cửa kính, mái đón, sạp có bạt, dải mái tôn xanh, tháp thang lam đứng, dãy nhà phụ thấp), khối B mái đỏ, mặt sau và sân thượng khối trước (bỏ nhà cửa vòm, thêm hai mái tôn xanh và bảng hiệu), sân trên có dãy ki-ốt và mái taluy bê tông ô vuông phía tây cầu, vườn cây và dãy nhà phố phía đông cầu, bồn nước trên nhà góc bùng binh.

Đoạn tường sau nằm giữa cửa cầu và thang lên mái (s từ -1,2 đến 17,2) giữ nguyên kiểu cũ vì dính với cầu thang và lối đi trên mái. Mái taluy bị chặn trong lưới đi lại; sân trên, nền lát quanh chợ và vườn cây đi lại được.

Các tấm phủ mới (cỏ vườn cây, nền lát quanh chợ, nền lát quanh dãy nhà phố, sân trên, mái taluy) thay hẳn mặt nền cũ bên dưới: mọi tam giác nền cũ trong vùng phủ bị cắt đúng theo mép vùng (phần 8 của `rearB.py`). Lý do: lưới nền gốc có nhiều lớp chồng nhau, lại thủng dưới các nhà cũ, nên nếu chỉ phủ lên trên thì nền cũ đâm xuyên qua cỏ và nền lát.

### Đất dốc: bậc thang có kè (`rear/rearC.py`)

Nguyên tắc của chủ dự án: không để đất dốc tràn ra đường hay ăn vào chân nhà; chênh cao giải quyết bằng bờ kè. `rearC.py` áp dụng cho sườn đồi phía đông cầu đi bộ và cho mọi bãi cỏ dốc khác của bản đồ (lấy từ lưới loại nền `k == 1`, từ 30 m2):

- chia khối đất thành các bậc phẳng cách nhau 1,8 m theo mặt đất đã làm mượt; mỗi bậc có kè đá đứng bao quanh và gờ kè cao 28 cm;
- sát đường và sát nhà là vỉa lát đi theo mặt đường (bãi nhỏ dưới 400 m2 thì không chừa vỉa);
- cầu thang khoét vào bậc trên, đặt ở đoạn kè có mặt dưới phẳng và đi được; bậc không có chỗ đặt cầu thang thành bồn cây;
- lưới đi lại: mặt bậc phẳng, cầu thang là dốc đều, kè cao hơn 0,52 m nên tự chặn.

Khung làm việc của `common.py` nay là cả bản đồ.

## festival.py — cây và hoa mùa Festival
`python3 festival.py ../../world_cho.js ../../world_cho.js [ảnh_mặt_bằng.png]` điền `trees`, `pots`, `flowers` vào world_cho.js (thảm hoa ở sân rộng, mai anh đào và phượng tím dọc vỉa hè, chậu hoa, hoa trên các bậc cỏ). Chạy lại sau mỗi lần chạy `rear/rear.py`, vì rear.py dựng world_cho.js lại từ bản sao lưu. Sau đó nhớ đổi `BUILD_V` trong index.html.

## Sửa cầu, dọn nền, bó vỉa (28.11.2026)

Thứ tự chạy sau `rear/rear.py` và `festival.py`:

    git show 29459f9:market.glb > /tmp/market_truoc_khu_sau_cho.glb      # bản trước khi dựng khu sau chợ
    git show 11d1603:market.glb > market.glb; git show e2a5daf:world_cho.js > world_cho.js   # đầu vào: bản trước khi bó vỉa (không chạy chồng lên kết quả đã bó vỉa)
    python3 bridgefix.py market.glb /tmp/market_truoc_khu_sau_cho.glb m1.glb
    python3 groundfix.py m1.glb m2.glb
    python3 kerbs.py m2.glb world_cho.js market.glb world_cho.js

Sau đó đổi `BUILD_V` trong index.html.

- `bridgefix.py`: các bước dựng khu sau chợ đã xoá nhầm một đoạn mặt cầu đi bộ (thủng thấy cả mặt dưới), toàn bộ lan can, bồn cây, cột đèn phía taluy, và để một bờ kè nhô ngang mặt cầu. Tệp này lấy lại đúng các phần đó từ bản cũ và hạ bờ kè xuống dưới mặt cầu.
- `groundfix.py`: bỏ các mảng lát nhỏ nằm trơ trọi giữa sân nhựa (mép sàn của khối rạp Hòa Bình ló lên khỏi mặt nhựa 1 đến 3 cm) và đổi màu các đỉnh địa hình sáng lọt giữa vùng nhựa (nêm sáng trên sân, ví dụ ở đầu cầu).
- `kerbs.py`: lề và vỉa lát nằm sát mặt đường nhựa có mép cao hơn mặt đường 10 cm và có mặt đứng bó vỉa. Chỉ nâng, không hạ: lề gạch quanh chân nhà vốn cao 14 đến 20 cm thì giữ nguyên, chỉ thêm mặt đứng. Vỉa lát quanh chợ vốn thấp hơn dải đường 13 đến 19 cm được kéo lên, rồi trở về cao độ cũ với độ dốc không quá 6%. Lưới đi lại `h` và cao độ các vật đặt trên nền (cây, chậu, hoa, gian, mốc check-in) đi theo.

Bài học từ bản bó vỉa đầu tiên (đã gỡ): bản đó coi mọi tam giác màu xám nhạt là vỉa lát, nên các ô địa hình 2,5 m có màu pha giữa đất và nhựa, kể cả ô nằm chìm dưới mặt đường, bị nâng lên thành những tấm nổi giữa đường; ô nâng dở chừng trùng mặt với đường sinh sọc nhấp nháy. `kerbs.py` hiện tại vì thế:

- chỉ nhận tấm lát thật: gạch kem (ô 2,2 của atlas) hoặc lát xám đều màu ở cả ba đỉnh;
- cắt tấm lát đúng theo mép dải đường phủ lên nó (so hình học chính xác), không nâng phần nằm dưới đường;
- không coi sân nhựa của dãy ki-ốt là mặt đường (sân đó có bờ riêng, vỉa quanh sân thấp hơn sân là đúng thiết kế);
- vá mối nối chữ T và chia tấm theo cạnh (hai tam giác chung cạnh luôn chia giống nhau) để không hở khe; mọi cạnh biên bị nâng đều có mặt đứng che xuống vị trí cũ;
- in ra số đo kiểm tra: phân bố độ cao mép lề, diện tích mặt đường bị lề trồi lên che, lỗ hổng sau khi chia.

Cách kiểm tra đã dùng: so số ô đi tới được trước và sau (`rear` có `chk.py`), dựng ảnh mặt bằng lớp nền trước và sau, chụp dọc 8 tuyến đường trong game ở góc nhìn người chơi.
