---
name: orca-worktree-setup
description: Cấu hình Setup Script của Orca để mỗi worktree mới tự có các file local bị gitignore (quyền Claude Code, CLAUDE.local.md, .env…) và Orca thôi hỏi cấu hình mỗi lần tạo worktree. Dùng khi Orca hiện gợi ý "Setup Script / When to run" lúc tạo worktree, khi worktree mới thiếu file local, khi agent trong worktree mới hỏi lại quyền, hoặc khi nói "setup script orca", "orca worktree config". Không dùng cho việc quản lý worktree, terminal hay browser của Orca (dùng `orca-cli`).
---

# /orca-worktree-setup

Mỗi worktree Orca tạo ra là một checkout sạch: file gitignore ở repo gốc (`.claude/settings.local.json`, `CLAUDE.local.md`, `.env`…) không đi theo. Setup Script chạy ngay sau khi worktree được tạo, nên copy chúng ở đó.

Đã kiểm trên Orca 1.4.224 (Windows), bằng cách đọc mã trong `resources/app.asar` và chạy thử script. Bản Orca khác có thể đổi: kiểm lại mục "Orca chạy script thế nào" trước khi tin.

## 1. Xem worktree thiếu gì

Chỉ copy file **local thật**, không copy dữ liệu runtime:

```bash
git status --ignored --short | grep '^!!'
```

Thường cần: `.claude/settings.local.json` (quyền đã cho phép, thiếu thì agent hỏi lại từ đầu), `CLAUDE.local.md`, `.env*`. Không cần: identity git, remote, hook trong `.git/hooks` (worktree dùng chung `.git`); `__pycache__`, `build/`, `dist/`, thư mục data.

Nếu repo có cài deps theo thư mục (`node_modules`, `.venv`) thì thêm lệnh cài vào script; nếu deps cài global thì bỏ.

## 2. Orca chạy script thế nào (quan trọng)

| Nền | Cách chạy | Hệ quả |
|---|---|---|
| Windows | Ghi script ra `.git/orca/setup-runner.cmd`, **mỗi dòng không rỗng thành `call <dòng>`** rồi `if errorlevel 1 exit /b`, chạy bằng `cmd.exe` | Không phải bash. Biến là `%ORCA_ROOT_PATH%`, không phải `$ORCA_…`. Dòng đầu bắt đầu bằng `#!` → Orca từ chối và báo cần Git Bash. `call` không chạy được `if`/`for`. Lệnh nào trả errorlevel ≠ 0 (kể cả `copy`/`xcopy` khi thiếu file nguồn, `robocopy` khi *có* copy) là setup dừng. |
| macOS/Linux | Ghi ra `.git/orca/setup-runner.sh` với `#!/usr/bin/env bash` + `set -e` | Bash bình thường; lệnh lỗi là dừng. |
| Windows + WSL runtime | Chạy qua `wsl.exe … sh -c` | Viết theo POSIX sh. |

Biến có sẵn: `ORCA_ROOT_PATH` (repo gốc), `ORCA_WORKTREE_PATH` (worktree mới), `ORCA_WORKSPACE_NAME`.

Vì vậy trên Windows, gói toàn bộ logic vào **một dòng** PowerShell.

## 3. Script mẫu

Sửa danh sách file trong `foreach (...)`. Script bỏ qua file không có ở repo gốc, không ghi đè file đã có ở worktree, chạy lại nhiều lần vẫn an toàn.

**Windows** (một dòng, paste nguyên):

```
powershell -NoProfile -ExecutionPolicy Bypass -Command "foreach ($f in '.claude\settings.local.json','CLAUDE.local.md') { $s = Join-Path $env:ORCA_ROOT_PATH $f; $d = Join-Path $env:ORCA_WORKTREE_PATH $f; if ((Test-Path $s) -and -not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path (Split-Path $d) | Out-Null; Copy-Item $s $d; Write-Output ('Copied ' + $f) } }"
```

**macOS/Linux**:

```bash
for f in .claude/settings.local.json CLAUDE.local.md; do
  if [ -f "$ORCA_ROOT_PATH/$f" ] && [ ! -f "$ORCA_WORKTREE_PATH/$f" ]; then
    mkdir -p "$(dirname "$ORCA_WORKTREE_PATH/$f")"
    cp "$ORCA_ROOT_PATH/$f" "$ORCA_WORKTREE_PATH/$f" && echo "Copied $f"
  fi
done
```

Thử trước khi đưa cho người dùng: tạo hai thư mục tạm `root/` và `wt/`, đặt biến môi trường, chạy script đúng cách Orca chạy (Windows: ghi vào file `.cmd` với `@echo off`, `call <dòng>`, `if errorlevel 1 exit /b %errorlevel%`, chạy bằng `cmd /c`). Chạy hai lần: lần đầu copy, lần hai không lỗi, file thiếu không làm hỏng.

## 4. Đặt script ở đâu

- **Local (khuyên dùng cho file cá nhân)**: Orca → **Settings** → thanh trái, mục **Projects** → chọn repo → phần Setup Script. Chỉ trên máy này. Cấu hình theo **repo**, không theo từng worktree.
- **`orca.yaml` ở gốc repo** (`scripts.setup`, `scripts.archive`, `setupAgentStartupPolicy: wait-for-setup`, `worktree.sharedDirectories`): dùng chung cả team, được commit. Không hợp khi repo public, khi script chỉ chạy trên một hệ điều hành mà team dùng nhiều hệ, hoặc khi nó nhắc tới file cá nhân. Khi cả hai cùng có, "Advanced" trong trang đó chọn local-only / orca.yaml only / run both.

Các ô còn lại:
- **When to run**: *Run by default*.
- **Wait for setup to complete before starting agent**: **bật**, để agent khởi động là đã có quyền và file local.
- **Archive Script**, **Custom GitHub Issue Command**: để trống nếu không có gì cần dọn hay ticket không nằm trên GitHub.

Gợi ý cấu hình lúc tạo worktree chỉ hiện khi repo chưa có setup script (hoặc khi When to run là *Ask every time*). Lưu script xong và chọn *Run by default* là thôi hiện.

## 5. Không tự ghi cấu hình

Orca không có lệnh CLI cho hook settings. Cấu hình nằm trong `%APPDATA%\orca\profiles\<profile>\profile-state.db` (SQLite, WAL, bảng `profile_state_documents`, domain `repos`, trường `hookSettings`) do app đang chạy ghi liên tục, có revision và content hash. **Không sửa DB từ ngoài**: app ghi đè hoặc hỏng state. Để người dùng nhập trong UI.

## 6. Kiểm sau khi người dùng lưu

Ô nhập có thể làm mất một phần chuỗi khi paste (đã gặp: mất `powershell -NoProfile -ExecutionPolicy ` ở đầu, setup sẽ lỗi `'Bypass' is not recognized`). Đọc lại bản đã lưu, **chỉ đọc**, qua bản sao:

```bash
python -I -c "
import sqlite3,sys,json
src=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True); dst=sqlite3.connect(sys.argv[2]); src.backup(dst)
repos=json.loads(dst.execute(\"select payload from profile_state_documents where domain='repos'\").fetchone()[0])
for r in repos:
  if sys.argv[3] in r['path']: print(json.dumps(r.get('hookSettings'),indent=1))
" "$APPDATA/orca/profiles/local-default/profile-state.db" "<scratch>/ps.db" "<tên repo>"
```

Đạt khi: `scripts.setup` giống từng ký tự bản đã thử, `setupRunPolicy: run-by-default`, `setupAgentStartupPolicy: wait-for-setup`. Xoá bản sao sau khi đọc.

Bước cuối do người dùng làm: tạo một worktree thật, thấy dòng `Copied …` trong tab setup và agent không hỏi lại quyền. Chưa thấy thì báo "chưa chạy thật", đừng báo xong.
