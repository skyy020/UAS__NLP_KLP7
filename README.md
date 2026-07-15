# SiklusCare AI 🌸
> **Chatbot Edukasi Menstruasi & Kesehatan Reproduksi Wanita**

SiklusCare AI adalah aplikasi web chatbot interaktif yang dirancang untuk menjawab berbagai pertanyaan seputar menstruasi, siklus haid, nyeri haid (dismenore), kehamilan, dan kesehatan reproduksi wanita lainnya. Chatbot ini dibangun menggunakan pencarian semantik (Semantic Search) berbasis model Deep Learning bahasa Indonesia (**IndoBERT**) dan **Sentence-BERT (SBERT)**.

Aplikasi ini mengintegrasikan model-model yang telah dilatih pada Jupyter Notebook (`Uas_NLP.ipynb`) ke dalam antarmuka website berbasis web (Flask API & HTML/CSS/JS modern).

---

## ✨ Fitur Utama
1. **Interactive Chat Assistant**: Antarmuka percakapan modern dengan micro-animations, loading indicators, dan bubble chat yang elegan.
2. **Dual-Model NLP Engine**:
   - **IndoBERT** (`indobenchmark/indobert-base-p1`): Akurasi sangat tinggi (F1-Score ~82.2%) dengan representasi bahasa Indonesia yang mendalam.
   - **SBERT** (`paraphrase-multilingual-MiniLM-L12-v2`): Cepat, ringan, dan efisien (F1-Score ~76.7%).
3. **Similarity Details**: Menampilkan persentase kemiripan (Similarity Score) dan mendeteksi pertanyaan referensi yang paling cocok dari database.
4. **Adaptive Thresholding**: Slider dinamis untuk mengatur batas minimal kemiripan (threshold) secara langsung dari UI.
5. **Knowledge Base Explorer**: Fitur pencarian dan penelusuran database Q&A (tanya-jawab) secara langsung lengkap dengan paginasi.
6. **Dual Theme (Gelap & Terang)**: Peralihan tema visual yang halus untuk kenyamanan mata pengguna.
7. **Responsive Design**: Tampilan optimal baik di desktop maupun perangkat mobile.

---

## 🛠️ Prasyarat & Instalasi

Pastikan Anda telah menginstal **Python (versi 3.8 - 3.12)** pada sistem Anda.

### 1. Klon atau Buka Folder Project
Buka terminal/command prompt pada direktori project ini:
```bash
cd D:\Joki\Fandy_NLP
```

### 2. Instal Dependensi Python
Instal seluruh library yang diperlukan dengan menjalankan perintah berikut:
```bash
pip install -r requirements.txt
```

> **Catatan**: Unduhan library PyTorch (`torch`) dan Transformers cukup besar. Pastikan koneksi internet Anda stabil saat melakukan instalasi.

---

## 🚀 Menjalankan Website Chatbot

### 1. Jalankan Server Flask
Jalankan file `app.py` untuk mengaktifkan backend Flask API:
```bash
python app.py
```

Saat pertama kali dijalankan, server akan secara otomatis:
1. Membaca database Q&A dari file `knowledge_base_bert.csv` dan `knowledge_base.csv`.
2. Memuat tensor embeddings dari `model_indobert.pkl` dan `model_sbert.pkl`.
3. Mengunduh model pretrained NLP (`indobenchmark/indobert-base-p1` dan `paraphrase-multilingual-MiniLM-L12-v2`) dari Hugging Face Hub (proses ini hanya terjadi satu kali saat pertama kali dijalankan).

### 2. Akses Aplikasi di Browser
Setelah server berhasil berjalan dan memuat model, buka browser Anda dan akses alamat berikut:
```
http://localhost:5000/
```

---

## 📂 Struktur File Website

* `app.py` - Script server utama Flask yang menangani pemuatan model NLP, embedding input, kalkulasi cosine similarity, dan menyediakan RESTful API.
* `templates/`
  * `index.html` - Struktur halaman website (Chat, Explorer, dan Informasi Model).
* `static/`
  * `style.css` - Desain visual aplikasi web dengan efek glassmorphism, responsive grid, serta transisi light/dark mode.
  * `script.js` - Logika frontend untuk interaksi API, manipulasi DOM chat, paginasi database, dan slider threshold.
* `requirements.txt` - Daftar pustaka/dependencies Python.
* `model_indobert.pkl` & `model_sbert.pkl` - File bobot embeddings representasi pangkalan data.
* `knowledge_base_bert.csv` & `knowledge_base.csv` - Pangkalan data tanya-jawab kesehatan reproduksi.

---

## 📊 Hasil Evaluasi Model (Berdasarkan Notebook)

Berdasarkan hasil pengujian pada dataset pengujian (`testing.csv`) menggunakan metrik evaluasi **BERTScore**, diperoleh perbandingan akurasi sebagai berikut:

| Model NLP | Precision | Recall | F1-Score | Karakteristik |
| :--- | :---: | :---: | :---: | :--- |
| **IndoBERT** | **0.8209** | **0.8240** | **0.8221** | Sangat akurat dalam memahami sinonim dan tata bahasa lokal Indonesia. |
| **SBERT** | 0.7651 | 0.7706 | 0.7674 | Sangat cepat dalam inferensi kalimat, multibahasa. |

---

## ⚠️ Disclaimer Medis
Informasi kesehatan reproduksi dan menstruasi yang disajikan oleh chatbot ini bertujuan **hanya untuk edukasi dan informasi umum**. Chatbot ini bukan merupakan pengganti saran medis profesional, diagnosis, atau perawatan medis dari dokter atau tenaga kesehatan terlatih.
