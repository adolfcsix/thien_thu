# Xi Game Universe — Thiên Thủ

Nền tảng trò chơi web cài đặt được (PWA). Không cần tài khoản GitHub, không cần tải mã nguồn, không cần cài Node.js để chơi.

**[Mở game tại đây](https://adolfcsix.github.io/thien_thu/)**

> Trạng thái: bản công khai hiện tại là Thiên Thủ V9.0. Bản nâng cấp đa trò chơi F1.6 đang nghiệm thu tại [Pull Request #1](https://github.com/adolfcsix/thien_thu/pull/1). Các hướng dẫn thư viện đa trò chơi bên dưới áp dụng sau khi bản nâng cấp được triển khai.

## Danh mục trò chơi của bản nâng cấp

| Trò chơi | Thể loại |
|---|---|
| Thiên Thủ — Legacy of Kingdoms | Thủ thành 2D |
| CUBIQ — Mobile Edition | Giải đố không gian 3D |
| BLOCK NOVA | Xếp khối, giải đố |

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
- Sau khi merge, chạy workflow Xi Foundation — Validate and Deploy bằng Run workflow trên nhánh main; chỉ triển khai khi mọi job bắt buộc đạt. Sau đó thử trên iPhone thật.
- [GitHub Actions](https://github.com/adolfcsix/thien_thu/actions) · [Báo lỗi](https://github.com/adolfcsix/thien_thu/issues)

Đây là ứng dụng web PWA, chưa phải ứng dụng native IPA/APK/EXE. Hỗ trợ cài đặt tùy trình duyệt và hệ điều hành. Các nền tảng ngoài iPhone cần nghiệm thu trên thiết bị thật.
