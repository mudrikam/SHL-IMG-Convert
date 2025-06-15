# SHL Image Converter

Aplikasi konverter gambar sederhana dengan antarmuka grafis yang mudah digunakan. Mendukung berbagai format gambar termasuk AVIF, JPEG, PNG, WebP, dan lainnya.

## 📥 Cara Install

### Prasyarat
- Git sudah terinstal di komputer Anda
- Python 3.8 atau versi yang lebih baru

### Langkah Install

1. **Buka Command Prompt di folder yang diinginkan**
   - Buka File Explorer
   - Masuk ke folder tempat Anda ingin menginstall (misalnya: `D:\Aplikasi\`)
   - Klik di address bar dan ketik `cmd`, lalu Enter
   
   *Atau cara lain:*
   - Tekan `Win + R`, ketik `cmd`, lalu Enter
   - Pindah ke folder: `cd D:\Aplikasi\`

2. **Clone (unduh) aplikasi dari Git**
   ```bash
   git clone https://github.com/username/SHL-IMG-Convert.git
   ```

3. **Jalankan aplikasi**
   - Masuk ke folder `SHL-IMG-Convert`
   - Double-click file `Launcher.bat` untuk menjalankan aplikasi
   
   *Launcher akan otomatis menginstall dependency yang diperlukan*

## 🔄 Cara Update

Untuk mendapatkan versi terbaru dari aplikasi:

1. **Buka Command Prompt di folder aplikasi**
   - Buka File Explorer
   - Masuk ke folder aplikasi (misalnya: `D:\Aplikasi\SHL-IMG-Convert`)
   - Klik di address bar dan ketik `cmd`, lalu Enter
   
   *Atau cara lain:*
   - Tekan `Win + R`, ketik `cmd`, lalu Enter
   - Pindah ke folder: `cd D:\Aplikasi\SHL-IMG-Convert`

2. **Tarik update terbaru dari Git**
   ```bash
   git pull
   ```

3. **Jalankan aplikasi versi terbaru**
   - Double-click file `Launcher.bat`
   
   *Launcher akan otomatis menghandle dependency yang diperlukan*

## 🚀 Cara Menggunakan

1. Jalankan aplikasi dengan double-click `Launcher.bat`
2. Drag and drop file gambar ke dalam aplikasi
3. Pilih format output yang diinginkan
4. Pilih folder tujuan
5. Klik "Convert" untuk memulai konversi

## 📋 Format yang Didukung

- **Input**: JPEG, PNG, BMP, TIFF, WebP, AVIF, dan lainnya
- **Output**: JPEG, PNG, WebP, AVIF

## ⚠️ Troubleshooting

Jika mengalami error saat install:

1. **Pastikan Python sudah terinstal**
   ```bash
   python --version
   ```

2. **Update pip ke versi terbaru**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Install ulang requirements**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```
