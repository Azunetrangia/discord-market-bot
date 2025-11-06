# Hướng dẫn Push lên GitHub

## Bước 1: Tạo Repository mới trên GitHub
1. Truy cập: https://github.com/new
2. Repository name: **discord-market-bot** (hoặc tên bạn muốn)
3. Description: Discord bot for economic calendar and crypto news aggregation
4. Chọn: **Private** hoặc **Public** (tùy bạn)
5. ❌ KHÔNG tích vào "Add a README file", "Add .gitignore", "Choose a license"
6. Click **Create repository**

## Bước 2: Sau khi tạo xong, chạy các lệnh sau:

```bash
# Đã làm xong:
# ✅ git init
# ✅ git add .
# ✅ git commit -m "..."
# ✅ git branch -m main

# Bạn cần chạy (thay YOUR_USERNAME và YOUR_REPO):
git remote add origin https://github.com/Azunetrangia/discord-market-bot.git
git push -u origin main
```

## Bước 3: Nhập GitHub credentials khi được yêu cầu

Khi push, GitHub sẽ yêu cầu đăng nhập:
- Username: **Azunetrangia**
- Password: **Dùng Personal Access Token** (không dùng password thật)

### Cách tạo Personal Access Token:
1. Vào: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Note: "Discord Bot Push"
4. Expiration: 90 days (hoặc tùy chọn)
5. Scopes: Tích ✅ **repo** (toàn bộ)
6. Click "Generate token"
7. **Copy token** (chỉ hiện 1 lần!)
8. Dùng token này thay cho password khi git push

## Hoặc dùng SSH (khuyến nghị):

```bash
# Tạo SSH key
ssh-keygen -t ed25519 -C "Kg3206722@gmail.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Thêm vào GitHub: https://github.com/settings/keys
# Sau đó dùng SSH URL:
git remote set-url origin git@github.com:Azunetrangia/discord-market-bot.git
git push -u origin main
```

---

**Repository đã sẵn sàng với:**
- ✅ 35 files
- ✅ 7,257 dòng code
- ✅ .gitignore đã cấu hình (ẩn .env, __pycache__, data files)
- ✅ README.md đầy đủ
- ✅ Git config: Azunetrangia / Kg3206722@gmail.com

**Chỉ cần tạo repo trên GitHub và chạy 2 lệnh là xong! 🚀**
