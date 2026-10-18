---
name: sdlc
description: Chuỗi artifact intent → plan → build → verify → ship cho mọi việc đủ lớn trong repo. Dùng khi bạn bắt đầu feature mới, refactor lớn, hoặc nói "viết intent", "làm theo plan", "/sdlc". Không dùng cho sửa một dòng, chẩn đoán nhanh, hay việc vận hành một lần.
---

# /sdlc

Mỗi phase kết thúc bằng một artifact commit vào repo. Session sau (hoặc agent khác) chỉ cần đọc file đó, không cần lịch sử chat.

Bạn vừa là người đặt yêu cầu vừa là người build — mọi cổng duyệt gom thành: **bạn duyệt artifact trước khi phase kế chạy.**

Chuỗi nằm trong thư mục `intent/` của repo:

```
intent/
  2026-09-01-dark-mode.md        # WHY + WHAT (intent, đã duyệt)
  2026-09-01-dark-mode.plan.md   # HOW (plan, tự đủ nghĩa)
```

Spec trước code sau; verify từng lớp thay vì đọc từng dòng.

---

## Phase 1 — Intent (why + what)

Khi bạn mô tả feature hoặc vấn đề: agent hỏi vài câu sắc (3–6 câu) cho tới khi phạm vi rõ — ràng buộc kỹ thuật, hệ thống bị ảnh hưởng, cái gì **không** làm. Rồi viết `intent/<yyyy-mm-dd>-<slug>.md`:

```markdown
---
status: draft   # draft → approved → planned → building → verified → shipped (PR #n)
---
# <Title>
**Problem** — cái gì đang đau, bằng lời của bạn.
**Outcome** — khi xong thì có gì; tiêu chí thành công (đo được).
**Constraints** — tech, ngân sách, chính sách (lean, không thêm dependency, …).
**Out of scope** — việc này cố ý KHÔNG làm.
**Open questions** — chưa chốt (trống = sẵn sàng duyệt).
```

Bạn sửa → `status: approved`, commit. **Không viết plan trước khi intent được duyệt.**

Nếu là sản phẩm mới: intent phải nêu đường kiếm tiền (ai trả, trả vì gì).

---

## Phase 2 — Plan (how)

Chỉ feed file intent vào chế độ plan. Việc lớn hoặc kiến trúc: tách review sản phẩm và review kỹ thuật trước khi chốt. Hỏi: "cái gì có thể gãy?" Output `intent/<slug>.plan.md`:

- **Files** — mọi file sẽ chạm, theo thứ tự làm.
- **Risks** — có thể gãy gì, và cách kiểm bắt được.
- **Proof** — lệnh/bằng chứng chứng minh xong (test, build, screenshot, curl). "Xong" được định nghĩa ở đây, trước khi gõ code.

Bạn chấp nhận plan → `status: planned`, commit. Plan là hợp đồng bàn giao: agent implement chỉ đọc plan, không đọc chat.

---

## Phase 3 — Build

Quy tắc repo bình thường (một logical unit một lúc; worktree nếu song song). Thêm:

- Lệch plan → **cập nhật plan.md trong cùng commit**. Diff phải khớp plan.
- Bắt đầu code → `status: building`.

---

## Phase 4 — Verify

Chạy đúng mục **Proof** trong plan. Người viết **không** tự duyệt: pass review độc lập (`code-reviewer` hoặc agent review khác) với intent + plan làm hợp đồng. Proof xanh → `status: verified`.

Lỗi lặp lần thứ hai ở bất kỳ repo nào → ghi ngay vào `CLAUDE.md` hoặc `lessons.md` của repo đó.

---

## Phase 5 — Ship

Merge theo flow repo (feature branch → PR → main; hoặc uat → main nếu repo bạn đặt như vậy). Sau merge: `status: shipped (PR #n)` trong intent — chuỗi đóng, git history là audit trail.

---

## Phase 6 — Maintain (vòng lặp)

Health check, cron, email cảnh báo có thể tự flag issue. Quy ước: issue đáng làm và lớn hơn sửa một dòng → bắt đầu bằng intent file mới trong repo sở hữu. Sửa nhỏ, bounded → PR thẳng, bỏ qua chuỗi.

---

## Evals — regression cho quy trình

Thư mục `evals/` per repo: mỗi file một case — **Task** (prompt thật) + **Expect** (kết quả kiểm được). Mỗi incident production và mỗi lần "agent làm sai" → thêm case vĩnh viễn.

Chạy evals **trước khi merge** thay đổi `CLAUDE.md`, skill, hoặc hook — config làm pass rate tụt thì không merge. 5 case đã tốt hơn 0.

---

## Quy ước đã dùng thật

- **Chấm độ khó trước khi giao việc.** Đánh giá bốn mặt: độ mơ hồ, các quyết
  định dính nhau, dễ kiểm hay không, và giá phải trả nếu sai. Không mặt nào
  cao là **EASY**: giao cho agent làm, không cần review. Một mặt cao là
  **MEDIUM**: giao cho agent build, rồi cho agent review. Từ hai mặt cao trở
  lên là **HARD**: phiên chính tự làm. `CLAUDE.md` của từng repo ghi ví dụ
  riêng cho ba mức.
- **Một ticket một nhánh, một phase một PR.** Intent là một PR, chờ duyệt rồi
  mới viết plan. Không push thẳng vào `main`, không merge khi chưa được bảo.
- **Ticket có ở hai nơi** (tracker và GitHub issue), trỏ link qua lại. Tiêu
  đề issue có mã ticket, ví dụ `[AGD-2]`. Chuyển ticket sang project khác thì
  đóng ticket cũ, để lại comment trỏ sang chỗ mới.
- **Một sản phẩm một repo.** Thư viện dùng chung thì phụ thuộc theo semver
  tag, không trỏ vào nhánh.
- **Sản phẩm đi ra từ teardown:** intent trỏ tới `docs/spec/SPEC.md` làm
  phần WHAT, không viết lại spec. Gặp khoảng trống về hành vi thì hỏi người
  giữ spec, không tự quyết.
- **Trước khi push, kiểm đúng tài khoản GitHub** bằng `gh api user --jq .login`.
  Đừng đổi tài khoản đang active; dùng `GH_TOKEN=$(gh auth token -u <account>)`.
- **Proof phải là bằng chứng đã chạy** (lệnh, số test, ảnh chụp), không phải
  lời khẳng định. Reviewer chấm proof dựa trên intent và plan.

---

## Khi KHÔNG dùng

Sửa một dòng, chẩn đoán, ops một lần — chuỗi là overhead. Nghi ngờ: nếu đáng feature branch thì đáng intent file.
