# Xi Universe

Nền tảng trò chơi web cài đặt được (PWA). Không cần tài khoản GitHub, không cần tải mã nguồn, không cần cài Node.js để chơi.

**[Mở game tại đây](https://adolfcsix.github.io/thien_thu/)**

> Bản công khai: Xi F1.7 (bốn trò chơi). F1.8 — cá nhân hóa và tùy chỉnh game đang nghiệm thu.

## Danh mục trò chơi của bản nâng cấp

| Trò chơi | Thể loại |
|---|---|
| Thiên Thủ — Legacy of Kingdoms | Thủ thành 2D |
| CUBIQ — Mobile Edition | Giải đố không gian 3D |
| BLOCK NOVA | Xếp khối, giải đố |
| FEATHER FURY — Sky Islands 10.1 | Kéo ná, vật lý 2D (F1.7) |

## Cài đặt và chơi

Dùng kết nối Internet trong lần mở đầu tiên. Mỗi thiết bị và hồ sơ trình duyệt lưu tiến trình riêng; chưa có đồng bộ đám mây.

### iPhone / iPad (iOS / iPadOS)

1. Mở Safari và truy cập https://adolfcsix.github.io/thien_thu/
2. Nhấn Chia sẻ (nếu không thấy, mở menu của Safari).
3. Chọn Thêm vào màn hình chính (Add to Home Screen).
4. Bật Mở dưới dạng ứng dụng web nếu tùy chọn này xuất hiện.
5. Nhấn Thêm, sau đó mở Xi từ màn hình chính.
6. Khi sảnh đa trò chơi được phát hành, vào Thư viện, chọn game và tải offline. Chờ tải xong trước khi tắt mạng.

Nếu nhận link từ Zalo/Messenger, mở bằng Safari thay vì trình duyệt trong ứng dụng. Không mở file HTML bằng Xem nhanh trong Tệp để cài PWA. Không cần App Store hay file IPA.

### Android

1. Mở Google Chrome và truy cập link game.
2. Nhấn menu ba chấm.
3. Chọn Cài đặt ứng dụng hoặc Thêm vào màn hình chính, tùy phiên bản Chrome.
4. Xác nhận cài đặt và mở biểu tượng game.
5. Tải game muốn chơi offline trong Thư viện sau khi sảnh mới được phát hành.

Không cần file APK. Nếu tùy chọn cài đặt không xuất hiện, vẫn có thể chơi trong Chrome.

### Windows 10/11

1. Mở Microsoft Edge hoặc Google Chrome, truy cập link game.
2. Edge: menu ba chấm > Ứng dụng (Apps) > Cài đặt trang web này dưới dạng ứng dụng, hoặc dùng biểu tượng cài đặt trên thanh địa chỉ.
3. Chrome: nhấn biểu tượng cài đặt trên thanh địa chỉ, nếu có; hoặc tìm tùy chọn cài đặt trang dưới dạng ứng dụng trong menu.
4. Mở ứng dụng từ Start hoặc shortcut nếu trình duyệt tạo.
5. Có thể chơi trực tiếp trong trình duyệt nếu không muốn cài.

### macOS (MacBook, iMac)

1. Mở Safari và truy cập link game.
2. Trên macOS Sonoma trở lên, chọn File > Add to Dock (Thêm vào Dock), nếu được hỗ trợ.
3. Xác nhận rồi mở từ Dock hoặc Applications.
4. Có thể dùng Chrome và tùy chọn cài đặt ứng dụng web nếu Safari không hỗ trợ.
5. Trên hệ điều hành cũ, chơi trực tiếp trong trình duyệt.

### Linux / ChromeOS

Mở link bằng Chromium/Chrome tương thích. Chọn cài đặt ứng dụng nếu trình duyệt cung cấp; nếu không, chơi trực tiếp trên web.

## Chơi offline và quản lý thư viện

Sau khi có sảnh Xi:
- Mở ứng dụng khi đang có mạng, vào Thư viện và tải tài nguyên game muốn chơi.
- Chờ thông báo sẵn sàng offline rồi mở thử trò chơi.
- Đóng game, bật chế độ máy bay (đồng thời tắt Wi-Fi), mở lại và kiểm tra.
- Gỡ tài nguyên trong Thư viện chỉ nhằm giải phóng dung lượng game, không phải xóa tiến trình.
- Không xóa dữ liệu trang web, bộ nhớ trình duyệt hoặc gỡ ứng dụng nếu chưa sao lưu.

PWA phụ thuộc vào bộ nhớ trình duyệt. Hệ điều hành có thể thu hồi tài nguyên offline. Nếu repository hoặc website bị xóa, việc cài lại, tải lại và cập nhật có thể không thực hiện được.

## Cập nhật và bảo vệ tiến trình

- Giữ nguyên biểu tượng ứng dụng đã cài, không cần gỡ bản cũ.
- Kết nối mạng, về sảnh và đóng/mở ứng dụng khi có bản cập nhật.
- Chờ bản mới tải xong. Có thể cần mở lại lần nữa để Service Worker mới hoạt động.
- Sao lưu tiến trình Thiên Thủ qua chức năng xuất dữ liệu trong game nếu có. Giữ file sao lưu bên ngoài trình duyệt.
- Tiến trình giữa các thiết bị hoặc giữa các website khác nhau không tự chuyển sang Xi.
- Không xóa cache toàn bộ trình duyệt để ép cập nhật khi chưa sao lưu.

## Xử lý lỗi

| Hiện tượng | Cách xử lý |
|---|---|
| Không thấy nút cài | Dùng Safari trên iOS, Chrome/Edge trên máy khác; thoát trình duyệt trong ứng dụng nhắn tin. |
| Vẫn thấy bản cũ | Kết nối Internet, đóng ứng dụng hoàn toàn rồi mở lại; kiểm tra trạng thái triển khai. |
| Không chơi được offline | Kết nối lại, tải đủ tài nguyên trong Thư viện, kiểm tra dung lượng trống. |
| Màn hình trắng | Kiểm tra mạng và đóng/mở lại; không xóa dữ liệu nếu chưa sao lưu. |
| Không thấy tiến trình từ máy khác | Dữ liệu lưu cục bộ theo thiết bị và trình duyệt. |

## Dành cho người phát triển

- `Thien_Thu_V9_0_Web_Deploy.zip`: baseline đang phát hành; giữ nguyên để kiểm thử nâng cấp.
- `Xi_Foundation_1_6_Release_Candidate.zip`: bản ứng viên chứa website trong thư mục `site/` và bộ kiểm thử.
- `.github/workflows/pages.yml`: kiểm tra SHA-256, unit/UI và Service Worker trên Chromium/WebKit.
- Không xóa baseline hoặc thay đổi file ZIP ứng viên nếu chưa cập nhật checksum và chạy lại CI.
- Chỉ merge khi validate, browser (chromium) và browser (webkit) cùng đạt trên bản mới nhất.
- Khi merge vào main, workflow tự triển khai sau khi toàn bộ job bắt buộc đạt; kiểm tra trên thiết bị thật.
- F1.7: `updates/feather-fury/` chứa HTML 10.1 nguyên gốc, cover SVG và script tạo module trên baseline F1.6 bất biến. CI tạo một gói duy nhất và dùng chính gói đó cho kiểm thử và phát hành.
- [GitHub Actions](https://github.com/adolfcsix/thien_thu/actions) · [Báo lỗi](https://github.com/adolfcsix/thien_thu/issues)

Đây là ứng dụng web PWA, chưa phải ứng dụng native IPA/APK/EXE. Hỗ trợ cài đặt tùy trình duyệt và hệ điều hành. Các nền tảng ngoài iPhone cần nghiệm thu trên thiết bị thật.


## Cá nhân hóa sảnh Xi (F1.8)

- Chọn Cài đặt → Không gian của bạn: sáu bảng màu, ảnh nền riêng, chế độ Khám phá thu gọn.
- Ảnh JPEG/PNG/WebP tối đa 12 MB, được tối ưu và lưu trên thiết bị; không gửi lên máy chủ. Có thể gỡ ảnh hoặc khôi phục mặc định.
- Tìm game tại Khám phá; nút Cập nhật tải bản module mới mà không xóa bản lưu. Nếu đang dùng bản offline cũ, cập nhật module để nhận chức năng mới.
- Các tùy chỉnh riêng trong cài đặt trò chơi chỉ dành cho dữ liệu offline, không phải quyền bảo mật máy chủ. Mã mở khóa không phải biện pháp chống người đọc mã nguồn.
- Nghiệm thu bắt buộc: cả Chromium và WebKit, nâng cấp từ V9.0 và F1.7, giữ tiến trình từng game.

## F1.9 — Xi Universe
Tên cài đặt mới: Xi Universe, giữ nguyên biểu tượng, định danh và phạm vi PWA. Các thiết bị đã cài có thể giữ nhãn cũ do iOS quản lý; không xóa ứng dụng hoặc dữ liệu để ép đổi tên. Sảnh mới có Nổi bật, Tiếp tục chơi, bộ lọc thể loại, tìm kiếm, Hoạt động, lưới thu gọn và sáu chủ đề F1.8. Bản này đang nghiệm thu; chỉ phát hành sau khi cả hai trình duyệt đạt.

## F1.10 — Startup & secondary tabs
Intro che sảnh từ HTML đầu tiên; chạm vào màn hình hoặc đợi tự chuyển, không còn nút Bỏ qua. Thư viện có bộ lọc trạng thái, sắp xếp theo gần đây/tên/dung lượng. Hoạt động tách lịch sử mở game và cập nhật. Cài đặt nhóm theo chức năng, giữ nguyên cá nhân hóa F1.9. Không đổi định danh PWA hay phiên bản từng game. Bản ứng viên chỉ phát hành sau khi nghiệm thu Chromium và WebKit.

## F1.11 — Xi Liquid Surface
Nút có ánh sáng mềm và phản hồi nhấn; thanh điều hướng kính nổi và chỉ báo trượt theo tab; công tắc gạt; hiệu ứng đồng bộ sáu chủ đề. Có tùy chọn Hiệu ứng kính trong Cài đặt, lưu cục bộ. Chỉ một lớp backdrop-filter ở thanh điều hướng, có nền dự phòng và tôn trọng reduced-motion. Không thay đổi định danh PWA, dữ liệu lưu hay module game. Bộ mô phỏng Cache API chụp snapshot byte của Response để tránh lỗi clone stream trong Node; không bỏ assertion. Chưa nghiệm thu thiết bị thật.

## F1.12 — Adaptive Layout
Chống tràn khung bằng intrinsic sizing, xuống dòng cho tiêu đề và nút, lưới thích ứng, đo chiều cao thanh điều hướng và giữ safe area. Kiểm thử Chromium mô phỏng gồm 9 kích thước 280–1280 px × 4 tab × 2 bố cục × 2 trạng thái kính, có chữ dài và nút tăng cỡ chữ. Giữ nguyên các module game, artwork, manifest, save keys. Nghiệm thu nâng cấp trên Chromium và WebKit trước khi phát hành; chưa kiểm chứng iPhone thật.

## F1.13 — Adaptive Devices & Surface Tuning
Điều hướng dưới cho điện thoại dọc; thanh bên thích ứng khi xoay ngang từ 700px; bố cục máy tính bảng và lưới thư viện rộng cho desktop. Thanh chỉnh độ trong kính và mức hiện ảnh nền giới hạn để duy trì khả năng đọc, lưu riêng trên thiết bị. Giữ manifest, tất cả module và artwork nguyên byte. Kiểm thử 144 tổ hợp khung và 32 lần chuyển tab trong 8 lần resize liên tiếp; nghiệm thu thật Chromium/WebKit và iPhone vẫn là cổng phát hành. Không khóa hướng xoay của ứng dụng.

## F1.14 — Premium Interaction
Hộp thoại gỡ tài nguyên dùng native dialog top layer với bề mặt Xi, nút hủy mặc định, Escape, giới hạn chiều cao theo viewport và bảo toàn save. Fallback confirm chỉ dùng nếu trình duyệt không hỗ trợ dialog. Công tắc chuyển động độc lập với hiệu ứng kính và giảm chuyển động hệ điều hành. Giữ nguyên module game, ảnh bìa, manifest và các khóa lưu. Kiểm thử UI mô phỏng 14/14, layout 144/144, resize/tab 32/32; CI nghiệm thu thật hai trình duyệt và bảo toàn cache/save. Chưa xác nhận thiết bị iPhone vật lý.

## F1.15 — Smart Personalization
Ghim game bằng nút sao, lọc Yêu thích tại Khám phá và Thư viện. Ba mức hiệu ứng Nhẹ/Cân bằng/Cao cấp; hai vị trí lưu và áp dụng màu, bố cục, kính và chuyển động. Không nhân bản ảnh nền, không thay đổi dữ liệu game. Local 33 unit, 15 UI mock, 144 layout stress và 32 resize/tab checks. CI thêm kiểm tra lưu offline và bảo toàn cache. Chưa nghiệm thu trên iPhone thật.

## F1.16 — Final Experience / đóng phạm vi nền tảng
Ánh sáng nền tĩnh theo theme (không animation liên tục), công tắc riêng, tự giảm cùng kính/chuyển động. Hộp thoại Chi tiết game có artwork, mô tả, phiên bản, trạng thái offline và điều hướng. Bộ lọc Gần đây/Cập nhật, hàng nút tránh tràn màn 280px. Bảo toàn 4 game, manifest, artwork và các khóa lưu. Local 33 unit, 16 UI mock, 144 layout stress và 32 resize/tab checks; kiểm tra PIN, upload ảnh, save isolation và preflight đạt. CI bắt buộc nghiệm thu Chromium/WebKit, bao gồm F1.15 -> F1.16. Đây là mốc khóa tính năng; chỉ sửa lỗi nghiệm thu, không mở rộng phạm vi; kiểm tra thiết bị thật sau triển khai. Không tuyên bố bản công khai F1.16 trước khi deploy thành công.

## F1.17 — Offline Resilience & Discovery
Mở lại phạm vi nền tảng theo phản hồi người dùng. Quản lý từ Khám phá, Hoạt động và Chi tiết trỏ đúng game, đưa thẻ vào tầm nhìn và giữ focus theo ID. Nổi bật tự chuyển 6 giây, có điều khiển thủ công, vuốt, dừng khi tương tác/ẩn tab/giảm chuyển động. Cài đặt tải tất cả game còn thiếu, yêu cầu StorageManager.persist, xuất/nhập JSON bản lưu theo allowlist (xác nhận ghi đè). ZIP bộ game độc lập được precache cùng shell; có Python 3, giải nén và chạy `python -m http.server 8765 --bind 127.0.0.1 --directory site`, mở http://localhost:8765/; xuất bản lưu từ origin cũ rồi nhập vào origin cục bộ. ZIP không chứa dữ liệu riêng, không tự lồng ZIP. Không cần GitHub khi dùng bộ cục bộ. PWA không thể bảo đảm tồn tại vĩnh viễn nếu hệ điều hành xóa cache, browser storage hoặc người dùng gỡ ứng dụng; chưa có native package iOS. Đừng xóa bản đang cài. 34 unit, 18 UI mock, 144 layout stress, 32 resize/tab; yêu cầu CI thật Chromium/WebKit, kiểm tra 404 và mạng ngắt, xuất/nhập save và checksum ZIP trước khi phát hành.

## F1.18 — Save Hardening
Chỉ ổn định bản web/PWA; không triển khai đóng gói native trừ khi có yêu cầu mới. Nhật ký hoàn tác ghi trước khi nhập, xác minh ghi từng khóa, phục hồi lần nhập dang dở khi mở lại sảnh; không ghi đè dữ liệu nếu không lưu được nhật ký. Nếu chưa phục hồi được, không mở game qua sảnh hoặc nhập thêm; giữ nhật ký để thử lại. Đóng các tab game khác và xuất sao lưu trước khi nhập; không bảo đảm an toàn khi hệ điều hành xóa toàn bộ storage hoặc khi nhiều tab cùng ghi. Kiểm thử cục bộ 34/34 unit, 20 UI, 144 layout và 32 resize/tab, preflight đạt; CI giữ các gate cũ và thêm phục hồi journal khi mở lại offline. Không thay đổi game, manifest, artwork, khóa lưu.

## F1.19 — FEATHER FURY 12.2 Sky Odyssey integration
Nguồn gốc Feather-Fury-12.2.html từ người dùng, SHA256 cố định; chỉ adapter namespace, về sảnh và tùy chỉnh PIN. Giữ nguyên bốn khóa cũ; thêm riêng ff12.2-progress và ff12.1-progress. Game 10.2 vẫn chơi offline khi chưa cập nhật, cache cũ chỉ thay thế sau khi xác minh đủ. Ba module khác, artwork và manifest nguyên byte. Kiểm thử cục bộ 34/34 nền tảng, PIN, mock migration/roster và preflight đạt; điều hướng HTTP cục bộ bị môi trường chặn, CI thật là điều kiện merge. Không triển khai đóng gói native.

### Game touch-policy revision
Khóa zoom ở bốn trang game bằng viewport 1:1, touch-action cho canvas và menu, chặn gesture Safari và touch đa điểm; giữ cuộn menu một ngón và hướng xoay. Không áp dụng khóa zoom cho sảnh. Legacy 9.2, CUBIQ 1.2, BLOCK NOVA 1.2, FEATHER FURY 12.2; bản cũ vẫn chơi offline cho đến khi người dùng cập nhật từng game. Căn lại HUD, đội hình, canvas 16:10 của Sky Odyssey, safe area và landscape. Local 34/34 unit, 4/4 CDP pinch, 7/7 layout Feather. CI thêm double tap, gesture cancellation và cập nhật cache của cả bốn module. WebKit mô phỏng không thay thế kiểm tra iPhone vật lý.

### Sky Odyssey — iPhone safe-area correction
Theo phản hồi ảnh iPhone: dành vùng an toàn trên/dưới, dùng inset thực tế với dự phòng 60/24 px khi iOS standalone dọc; HUD tách khỏi canvas ở hướng dọc, 4 cột đội hình trên màn dọc đủ cao; giữ tỷ lệ canvas 16:10, không thay đổi dữ liệu game. Màn ngắn cho phép cuộn, không ép cỡ nút. Local kiểm tra 7 hình học safe area mô phỏng, CI thêm cùng kiểm thử Chromium/WebKit. Chưa nghiệm thu iPhone vật lý.

## F1.20 — FEATHER FURY 14.1 Stability Update
Nguồn chính xác `Feather-Fury-14.1.html`, SHA256 9d53c91aff9b9ce38d8f442e7cc58f4c68f756c3f804266550c5a4a7e8ccac80 (15.7 MB, 21 mảnh UTF-8 nối nguyên byte tại build). Bảo toàn toàn bộ ảnh nhúng; bổ sung adapter Xi, khóa zoom, safe area, canvas 16:10; không đổi ba game khác/manifest. Khóa mới ff14.1-progress và backup, đọc dự phòng khóa 12.2 và các khóa cũ, không ghi đè bản lưu trước. Local 34/34 unit, preflight, PIN/cá nhân hóa, 8/8 hình học và mô phỏng migration 12.2 đạt. CI giữ tất cả gate cũ và thêm real migration F1.19 -> F1.20 Chromium/WebKit. Chưa kiểm chứng thiết bị iPhone thật và dung lượng RAM thực tế của artwork lớn.

## F1.21 — Six Games Integration

Adds KỲ VIỆN 1.0 (Imperial Jade) and Garden Through Time 0.79.2 (Final Stability RC3). Original HTML files pinned by SHA-256; adapter adds namespaced saves, same-origin legacy copy, viewport and return to Xi. Old four module bytes and PWA identity preserved. Existing F1.20 acceptance remains intact; separate Chromium/WebKit acceptance tests the exact F1.21 release artifact before Pages deployment. New covers are simple local SVG art. No native packaging.

## Final architecture consolidation — F1.21

The six-game release is independently unit-tested and frozen as a complete source tree with its own catalog baseline, browser acceptance and SHA-256 inventory. Historical four-game candidate and upgrade checks remain mandatory. The exact archive is verified before browser tests and Pages packaging. Only after all required browser jobs pass does CI create a separate consolidation branch containing source under `canonical/`; no automatic merge or overwrite of main. No new games or native packaging.
