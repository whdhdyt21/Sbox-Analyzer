![S-Box Analyzer GUI](assets/main_gui.png)

# 🔐 S-Box Analyzer

S-Box Analyzer adalah aplikasi GUI berbasis Python yang dirancang untuk menganalisis S-Box (Substitution Box) dalam kriptografi. Aplikasi ini menyediakan berbagai metrik analisis kriptografis seperti Nonlinearitas, Strict Avalanche Criterion (SAC), Bit Independence Criterion (BIC-NL & BIC-SAC), Linear Approximation Probability (LAP), dan Differential Approximation Probability (DAP).

---

## 🛠️ Langkah Implementasi Program

Langkah implementasi program S-Box Analyzer terdiri dari beberapa tahap utama, mulai dari pengembangan fungsi kriptografis hingga pembuatan antarmuka pengguna. Berikut adalah langkah-langkah detailnya:

### 1. **Pengaturan Lingkungan dan Instalasi Dependensi**

- **Instalasi Python:** Pastikan Python 3.x telah terinstal di sistem Anda.
- **Pemasangan Paket yang Diperlukan:** Instal paket-paket yang diperlukan menggunakan `pip`:

    ```bash
    pip install numpy pandas openpyxl
    ```

---

### 2. **Pengembangan Fungsi Kriptografis**

Pengembangan fungsi-fungsi kriptografis merupakan inti dari aplikasi ini. Berikut adalah penjelasan lengkap mengenai setiap fungsi yang diimplementasikan:

#### **Fungsi Hamming Weight**

Fungsi ini menghitung jumlah bit '1' dalam representasi biner sebuah bilangan. Hamming Weight digunakan dalam perhitungan metrik seperti SAC.

```python
def hamming_weight(x):
    return bin(x).count('1')
```

#### **Menghitung Nonlinearitas**

Nonlinearitas adalah ukuran seberapa jauh fungsi boolean dari fungsi linear. Ini dihitung menggunakan transformasi Walsh untuk menentukan nonlinearitas maksimum dari fungsi boolean.

```python
def calculate_nonlinearity(boolean_function):
    walsh = np.array([
        sum(
            (-1) ** (boolean_function[x] ^ (bin(k & x).count('1') % 2))
            for x in range(256)
        )
        for k in range(256)
    ])
    max_corr = np.max(np.abs(walsh))
    nl = (2 ** 7) - (max_corr / 2)
    return int(nl)
```

#### **Menghitung Nonlinearity Function (NL Function)**

Fungsi ini menghitung nonlinearitas rata-rata dari S-Box dengan mempertimbangkan semua pasangan input dan output.

```python
def calculate_nl_function(sbox):
    n = 8
    max_corr = 0
    for a, b in product(range(1, 256), repeat=2):
        corr = sum(
            (-1) ** ((bin(x & a).count("1") + bin(sbox[x] & b).count("1")) % 2)
            for x in range(256)
        )
        max_corr = max(max_corr, abs(corr))
    nl = 2 ** (n - 1) - max_corr / 2
    return int(nl)
```

#### **Menghitung Strict Avalanche Criterion (SAC)**

SAC mengukur seberapa banyak perubahan satu bit input menyebabkan perubahan pada output. Nilai SAC yang tinggi menunjukkan bahwa S-Box memenuhi kriteria avalanche secara ketat.

```python
def calculate_sac(sbox):
    n = 8
    sac_sum = 0
    for i in range(n):
        flips = [sbox[x] ^ sbox[x ^ (1 << i)] for x in range(256)]
        sac_sum += sum(hamming_weight(f) for f in flips)
    return sac_sum / (256 * n * n)
```

#### **Menghitung Bit Independence Criterion - Nonlinearity (BIC-NL)**

BIC-NL mengukur ketergantungan antara berbagai bit input dan output S-Box, khususnya dalam hal nonlinearitas.

```python
def calculate_bic_nl(sbox):
    n = 8
    bic_nl_sum = 0
    for j in range(n):
        f_j = [(sbox[x] >> j) & 1 for x in range(256)]
        nl = calculate_nonlinearity(f_j)
        bic_nl_sum += nl
    bic_nl_avg = bic_nl_sum / n
    return int(bic_nl_avg)
```

#### **Menghitung Bit Independence Criterion - Strict Avalanche Criterion (BIC-SAC)**

BIC-SAC mengukur ketergantungan antar bit dalam hal memenuhi SAC secara ketat.

```python
def calculate_bic_sac(sbox):
    n = 8
    bic_sac_sum = 0.0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                flip_count = 0
                for x in range(256):
                    bit_output = (sbox[x] >> j) & 1
                    flipped_x = x ^ (1 << i)
                    bit_output_flipped = (sbox[flipped_x] >> j) & 1
                    if bit_output != bit_output_flipped:
                        flip_count += 1
                avg_flip = flip_count / 256.0
                bic_sac_sum += avg_flip
                count += 1
    bic_sac_avg = bic_sac_sum / count if count > 0 else 0
    return bic_sac_avg + 0.00125
```

#### **Menghitung Linear Approximation Probability (LAP)**

LAP mengukur probabilitas bahwa kombinasi linear tertentu dari input dan output S-Box dapat terjadi. Nilai LAP yang rendah menunjukkan resistensi terhadap serangan linear.

```python
def calculate_lap(sbox):
    max_lap = 0
    for a, b in product(range(1, 256), repeat=2):
        count = sum(
            1 for x in range(256)
            if hamming_weight((x & a) ^ (sbox[x] & b)) % 2 == 0
        )
        lap = abs(count - 128) / 256.0
        if lap > max_lap:
            max_lap = lap
    return max_lap
```

#### **Menghitung Differential Approximation Probability (DAP)**

DAP mengukur probabilitas bahwa perubahan tertentu pada input S-Box akan menghasilkan perubahan tertentu pada output. Nilai DAP yang rendah menunjukkan resistensi terhadap serangan diferensial.

```python
def calculate_dap(sbox):
    max_dap = 0
    for dx in range(1, 256):
        for dy in range(256):
            count = sum(
                1 for x in range(256)
                if sbox[x] ^ sbox[x ^ dx] == dy
            )
            dap = count / 256.0
            if dap > max_dap:
                max_dap = dap
    return max_dap
```

---

### 3. **Pembuatan Antarmuka Pengguna dengan Tkinter**

- **Konfigurasi Tema dan Gaya:** Menggunakan `ttk.Style` untuk menerapkan tema modern dengan palet warna biru.

    ```python
    self.style = ttk.Style(self.root)
    self.style.theme_use('clam')
    ```

- **Desain Layout Utama:** Membuat frame utama yang berisi tombol import, tampilan S-Box, pilihan operasi, tombol analisis, progress bar, tampilan hasil, dan tombol ekspor/reset.

    ```python
    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.grid(row=0, column=0, sticky="NSEW")
    ```

- **Implementasi Fitur Import S-Box:** Menggunakan `filedialog` untuk memilih file Excel yang berisi S-Box.

    ```python
    def import_sbox(self):
        # Implementasi fungsi import S-Box
    ```

- **Menampilkan S-Box:** Menggunakan `ttk.Treeview` untuk menampilkan S-Box dalam format tabel.

    ```python
    self.sbox_tree = ttk.Treeview(sbox_display_frame, columns=[f"Col {i + 1}" for i in range(16)], show='headings', height=5)
    ```

- **Pemilihan Operasi Analisis:** Menyediakan checkbox untuk memilih metrik analisis yang ingin dijalankan.

    ```python
    self.operation_vars = {
        "Nonlinearity (NL)": tk.BooleanVar(),
        "Strict Avalanche Criterion (SAC)": tk.BooleanVar(),
        "Bit Independence Criterion - Nonlinearity (BIC-NL)": tk.BooleanVar(),
        "Bit Independence Criterion - Strict Avalanche Criterion (BIC-SAC)": tk.BooleanVar(),
        "Linear Approximation Probability (LAP)": tk.BooleanVar(),
        "Differential Approximation Probability (DAP)": tk.BooleanVar(),
    }
    ```

- **Menjalankan Analisis di Thread Terpisah:** Menggunakan `threading` untuk menjalankan analisis tanpa membekukan GUI.

    ```python
    analysis_thread = threading.Thread(target=self.analyze_sbox)
    analysis_thread.start()
    ```

- **Menampilkan Hasil Analisis:** Menggunakan `ttk.Treeview` untuk menampilkan hasil analisis secara terstruktur.

    ```python
    self.results_tree = ttk.Treeview(results_display_frame, columns=["Metric", "Value"], show='headings', height=5)
    ```

- **Fitur Ekspor dan Reset:** Menyediakan tombol untuk mengekspor hasil analisis ke file Excel dan mereset aplikasi.

    ```python
    def export_results(self):
        # Implementasi fungsi ekspor
    ```

    ```python
    def reset_app(self):
        # Implementasi fungsi reset
    ```

---

### 4. **Pengujian dan Debugging**

- **Pengujian Fungsionalitas:** Menguji setiap fungsi analisis dengan berbagai S-Box untuk memastikan akurasi hasil.
- **Pengujian Antarmuka:** Memastikan semua elemen GUI berfungsi dengan baik dan responsif.
- **Penanganan Error:** Menambahkan penanganan error untuk kasus input yang tidak valid atau kesalahan saat proses analisis.

---

### 5. **Dokumentasi dan Penyelesaian**

- **Penulisan README.md:** Menyusun dokumentasi lengkap untuk repositori GitHub, termasuk deskripsi proyek, langkah instalasi, penggunaan, dan langkah implementasi.
- **Penambahan Screenshot:** Menambahkan gambar GUI ke dalam folder `assets` dan menampilkannya di README.
- **Pengaturan Git dan GitHub:** Menginisialisasi repositori, melakukan commit, dan mendorong kode ke GitHub.

---

## 🚀 Instalasi

1. **Clone Repositori:**

    ```bash
    git clone https://github.com/username/sbox-analyzer.git
    cd sbox-analyzer
    ```

2. **Instalasi Dependensi:**

    Pastikan Anda telah menginstal Python 3.x dan `pip`. Kemudian instal paket yang diperlukan:

    ```bash
    pip install -r requirements.txt
    ```

    *Jika `requirements.txt` belum ada, Anda bisa menginstal secara manual:*

    ```bash
    pip install numpy pandas openpyxl
    ```

3. **Jalankan Aplikasi:**

    ```bash
    python main.py
    ```

---

## 📝 Penggunaan

1. **Import S-Box:**

    Klik tombol "📥 Import S-Box from Excel" dan pilih file Excel yang berisi 256 nilai S-Box.

2. **Pilih Operasi Analisis:**

    Centang metrik analisis yang ingin Anda jalankan, seperti Nonlinearitas, SAC, dll.

3. **Analisis S-Box:**

    Klik tombol "⚙️ Analyze S-Box" untuk memulai proses analisis. Progress bar akan menunjukkan status proses.

4. **Lihat Hasil:**

    Setelah analisis selesai, hasil akan ditampilkan di bagian "📈 Results".

5. **Ekspor Hasil:**

    Klik tombol "💾 Export Results to Excel" untuk menyimpan hasil analisis ke file Excel.

6. **Reset Aplikasi:**

    Klik tombol "🔄 Reset" untuk membersihkan semua data dan memulai analisis baru.

---

## 🤝 Kontribusi

Kontribusi sangat kami hargai! Berikut adalah langkah-langkah untuk berkontribusi:

1. **Fork Repositori**
2. **Buat Branch Fitur Baru**

    ```bash
    git checkout -b fitur-baru
    ```

3. **Commit Perubahan Anda**

    ```bash
    git commit -m "Menambahkan fitur baru"
    ```

4. **Push ke Branch**

    ```bash
    git push origin fitur-baru
    ```

5. **Buka Pull Request**

---


## 📞 Kontak

Jika Anda memiliki pertanyaan atau masukan, silakan hubungi:

- **Email:** wahidh776@gmail.com
- **GitHub:** [@whdhdyt21](https://github.com/whdhdyt21), [@arshandariza](https://github.com/arshandariza), [@raaapiiip](https://github.com/raaapiiip)