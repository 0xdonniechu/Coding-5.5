# Changelog

## 0.2.0 · 2026-10-16

- Thêm `orca-worktree-setup`: copy file local gitignore vào mỗi worktree Orca mới qua Setup Script; ghi lại cách Orca 1.4.224 chạy script (Windows: `cmd.exe`, mỗi dòng `call`, `#!` bị từ chối; macOS/Linux: bash `set -e`), nơi đặt script (local hay `orca.yaml`), và cách kiểm bản đã lưu chỉ đọc.

## 0.1.0 · 2026-10-11

Tách thành bộ skill riêng từ `sonpiaz/bto-skills` 0.0.7 (bản cục bộ, gồm các sửa đổi chưa gửi upstream):

- `market-research`: thêm agent hồ sơ công ty và biểu đồ Giá trị × Tính năng (kèm script); hợp đồng cho agent bắt buộc lấy giá US/USD và ghi sẵn nguồn review thay thế (Trustpilot lọc sao, Algolia API của HN); chạy 4 agent khi nghiên cứu cả Mac lẫn Windows.
- `teardown`: phép thử bức tường chạy thành vòng lặp CHẶN/NHỎ, với 2 agent độc lập ở cuối; thư mục đội A nằm ngoài repo; cảnh báo license copyleft; app desktop dùng `system-interfaces.md`; audit dạng bảng; `V0.1-TASKS.md`; checklist trước khi qua tường.
- `sdlc`: thêm mục quy ước đã dùng thật: chấm độ khó, ticket ở hai nơi, nhánh/PR, sản phẩm từ teardown, kiểm tài khoản GitHub, proof là bằng chứng.
- Bỏ các tham chiếu tới khoá học; giữ ghi công trong README và LICENSE.
