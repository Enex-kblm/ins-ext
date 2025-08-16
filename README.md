# 🔍 InsExt - Instagram Data Extractor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

**Tool ekstraksi data Instagram yang powerful untuk analisis OSINT dan investigasi digital**

[Fitur](#-fitur) • [Instalasi](#-instalasi) • [Penggunaan](#-penggunaan) • [Contoh Output](#-contoh-output) • [OSINT Mode](#-osint-mode)

</div>

---

## 📋 Deskripsi

**InsExt** adalah tool Python yang dirancang khusus untuk mengekstrak dan menganalisis data dari akun Instagram. Tool ini mendukung mode publik dan terautentikasi, serta dilengkapi dengan fitur OSINT (Open Source Intelligence) untuk investigasi digital.

### ✨ Fitur Utama

- 🔐 **Mode Login & Publik** - Akses dengan atau tanpa login
- 👤 **Informasi Profil Lengkap** - Data detail akun Instagram
- 📸 **Ekstraksi Post** - Analisis post individual atau semua post
- 🕵️ **Mode OSINT** - Deteksi email, nomor telepon, link eksternal, dan mention
- 🌍 **Deteksi Bahasa** - Identifikasi bahasa dari bio dan caption
- 📱 **Instagram Stories** - Informasi story aktif
- 💾 **Export JSON** - Simpan hasil dalam format JSON
- 📥 **Download Media** - Unduh gambar profil dan media post
- 🔄 **Session Management** - Simpan sesi login untuk penggunaan berulang

## 🚀 Instalasi

### Persyaratan Sistem
- Python 3.7 atau lebih tinggi
- Koneksi internet yang stabil

### Langkah Instalasi

1. **Clone repository**
```bash
git clone https://github.com/username/insext.git
cd insext
```

2. **Install dependencies**
```bash
pip install requests langdetect
```

3. **Jalankan tool**
```bash
python insext.py -h
```

## 📖 Penggunaan

### Sintaks Dasar
```bash
python insext.py -u <username> [options]
```

### Parameter Utama

| Parameter | Deskripsi | Contoh |
|-----------|-----------|---------|
| `-u, --user` | Username target (wajib) | `-u instagram` |
| `-l, --login` | Login dengan akun Instagram | `-l myuser mypass` |
| `-i, --info` | Tampilkan info profil | `-i` |
| `-p, --post` | Tampilkan post (index atau -1 untuk semua) | `-p 0` atau `-p -1` |
| `-dp, --download` | Download media | `-dp` |
| `--osint` | Aktifkan mode OSINT | `--osint` |
| `--osint-posts` | Jumlah post untuk scan OSINT | `--osint-posts 10` |
| `--osint-comments` | Jumlah komentar per post untuk scan | `--osint-comments 100` |
| `--json` | Export ke file JSON | `--json hasil.json` |

### Contoh Penggunaan

#### 1. Informasi Profil Dasar
```bash
python insext.py -u cristiano -i
```

#### 2. Analisis dengan Login
```bash
python insext.py -u target_user -l username password -i -p -1
```

#### 3. Mode OSINT Lengkap
```bash
python insext.py -u target_user --osint --osint-posts 20 --osint-comments 50
```

#### 4. Download Media + Export JSON
```bash
python insext.py -u target_user -i -p -1 -dp --json hasil_analisis.json
```

## 🖥️ Contoh Output

### Informasi Profil
```
$$$$$$\                                                   $$\     
\_$$  _|                                                  $$ |    
  $$ |  $$$$$$$\   $$$$$$$\          $$$$$$\  $$\   $$\ $$$$$$\   
  $$ |  $$  __$$\ $$  _____|        $$  __$$\ \$$\ $$  |\_$$  _|  
  $$ |  $$ |  $$ |\$$$$$$\  $$$$$$\ $$$$$$$$ | \$$$$  /   $$ |    
  $$ |  $$ |  $$ | \____$$\ \______|$$   ____| $$  $$<    $$ |$$\ 
$$$$$$\ $$ |  $$ |$$$$$$$  |        \$$$$$$$\ $$  /\$$\   \$$$$  |
\______|\__|  \__|\_______/          \_______|\__/  \__|   \____/ 

                          author : jull

✅ Login successful as @myaccount

[+] USER INFO

=============================================================
ID                       : 173560420
Username                 : cristiano
Full Name                : Cristiano Ronaldo
Profile Picture          : https://tinyurl.com/profile-pic-url
Bio                      : ⚽ Manchester United \n 🇵🇹 @selecaoportugal
External URL             : https://www.nike.com/cristiano
Private Account          : No
Verified                 : Yes
Category                 : Athlete
New Account              : No
Account Type             : Creator
Followers                : 615,000,000
Following                : 578
Posts                    : 3,456
Videos                   : 234
Reels                    : 45
Tagged Posts             : 12,345
Account Created At       : 2012-06-12 10:30
Active Stories           : 3
Last Active At           : 2024-01-15 14:22
Language                 : en
Business Email           : business@cristiano.com
Business Phone           : +351-xxx-xxx-xxx
Business Category        : Sports
```

### Mode OSINT
```
[+] OSINT RESULTS

=============================================================
Emails Found             : business@cr7.com, contact@cristianoronaldo.com
Phones Found             : +351-912-345-678, +44-20-1234-5678
External Links           : https://www.nike.com/cristiano, https://cr7.com
Top Mentions             : @nike (15), @manchesterunited (12), @selecaoportugal (8)
```

### Informasi Post
```
[+] POST #1 INFO

=============================================================
ID                       : 3234567890123456789
Shortcode                : CxYzAbC123D
Timestamp                : 2024-01-15 20:30
Likes                    : 2,500,000
Comments Disabled        : No
Pinned                   : No
Comments                 : 45,678
Stats                    : Saves: 125,000 | Views: 15,000,000 | Shares: 8,500
Location                 : Old Trafford, Manchester
Caption                  : Great victory today! 🔥⚽ Thank you for all the support! #MUFC #CR7...

MEDIA 1
Media URL                : https://tinyurl.com/post-image-url
Type                     : Image
Dimensions               : 1080x1350
```

## 🕵️ OSINT Mode

Mode OSINT memungkinkan Anda untuk:

- **🔍 Scan Email**: Deteksi alamat email dalam bio dan caption
- **📞 Scan Nomor Telepon**: Identifikasi nomor telepon format internasional
- **🔗 Scan Link Eksternal**: Temukan link ke website lain
- **👥 Analisis Mention**: Hitung frekuensi mention ke akun lain
- **💬 Scan Komentar**: Analisis komentar untuk data tambahan
- **🌍 Deteksi Bahasa**: Identifikasi bahasa yang digunakan

### Contoh Penggunaan OSINT
```bash
# Scan 50 post terbaru dengan 100 komentar per post
python insext.py -u target_user --osint --osint-posts 50 --osint-comments 100

# OSINT mode dengan download media dan export JSON
python insext.py -u target_user --osint -dp --json osint_results.json
```

## ⚠️ Disclaimer

Tool ini dibuat untuk tujuan:
- ✅ Penelitian dan edukasi
- ✅ Analisis OSINT yang legal
- ✅ Investigasi digital yang sah
- ✅ Audit keamanan dengan izin

**TIDAK untuk:**
- ❌ Stalking atau harassment
- ❌ Pelanggaran privasi
- ❌ Aktivitas ilegal
- ❌ Spam atau abuse

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository ini
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -am 'Tambah fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

## 📄 Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 👨‍💻 Author

**@jull** - Developer & Security Researcher

---

<div align="center">

**⭐ Jika tool ini berguna, berikan star pada repository ini! ⭐**

Made with ❤️ for the OSINT community

</div>