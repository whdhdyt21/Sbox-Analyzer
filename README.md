![S-Box Analyzer GUI](assets/main_gui.png)

# 🔐 S-Box Analyzer

**S-Box Analyzer** is a Python-based GUI application designed for cryptographic analysis of S-Boxes (Substitution Boxes). The application provides various cryptographic metrics, such as **Nonlinearity**, **Strict Avalanche Criterion (SAC)**, **Bit Independence Criterion (BIC-NL & BIC-SAC)**, **Linear Approximation Probability (LAP)**, and **Differential Approximation Probability (DAP)**.

---

## 🚀 Features

- **S-Box Analysis**: Evaluate cryptographic metrics for any given S-Box.
- **Modern GUI**: Responsive and intuitive interface built with Tkinter.
- **Excel Integration**: Import/export S-Boxes and results seamlessly.
- **Multi-Metric Support**: Analyze multiple metrics simultaneously.
- **Threading**: Smooth performance with non-blocking operations.

---

## 🛠️ Implementation Steps

The implementation of **S-Box Analyzer** involves the following major steps:

### 1. **Environment Setup and Dependencies**

- **Python Installation**: Ensure Python 3.x is installed.
- **Install Required Libraries**:

    ```bash
    pip install numpy pandas openpyxl
    ```

---

### 2. **Core Cryptographic Functions**

Below are the main cryptographic metrics implemented:

#### 🔹 **Hamming Weight**

Calculates the number of '1' bits in a binary number, used in SAC calculation.

```python
def hamming_weight(x):
    return bin(x).count('1')
```

#### 🔹 **Nonlinearity**

Measures how far a boolean function deviates from linearity.

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

#### 🔹 **Strict Avalanche Criterion (SAC)**

Evaluates how a single bit change in the input propagates through the output.

```python
def calculate_sac(sbox):
    n = 8
    sac_sum = 0
    for i in range(n):
        flips = [sbox[x] ^ sbox[x ^ (1 << i)] for x in range(256)]
        sac_sum += sum(hamming_weight(f) for f in flips)
    return sac_sum / (256 * n * n)
```

#### 🔹 **Bit Independence Criterion (BIC)**

Analyzes bit independence across S-Box input and output for Nonlinearity (BIC-NL) and SAC (BIC-SAC).

```python
def calculate_bic_nl(sbox):
    n = 8
    bic_nl_sum = 0
    for j in range(n):
        f_j = [(sbox[x] >> j) & 1 for x in range(256)]
        nl = calculate_nonlinearity(f_j)
        bic_nl_sum += nl
    return bic_nl_sum / n
```

---

### 3. **User Interface with Tkinter**

#### 🔹 **Design Highlights**:
- **Modern Theme**: `ttk.Style` for polished UI.
- **File Import/Export**: Simple dialogs to load/save S-Box data.
- **Treeview Tables**: Clean, tabular display for S-Boxes and results.

#### 🔹 **Threading**:
Ensures analysis does not freeze the GUI:

```python
analysis_thread = threading.Thread(target=self.analyze_sbox)
analysis_thread.start()
```

---

### 4. **Testing and Debugging**

- **Functionality Testing**: Verify accuracy of all metrics with diverse S-Box inputs.
- **GUI Testing**: Ensure all UI elements are responsive and intuitive.
- **Error Handling**: Robust handling for invalid inputs or runtime errors.

---

## 📦 Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/username/sbox-analyzer.git
    cd sbox-analyzer
    ```

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:

    ```bash
    python main.py
    ```

---

## 📋 Usage

1. **Import S-Box**:
   - Click "📥 Import S-Box from Excel" and select a file.

2. **Select Metrics**:
   - Choose analysis metrics (e.g., Nonlinearity, SAC, etc.).

3. **Analyze**:
   - Click "⚙️ Analyze S-Box" to start.

4. **View Results**:
   - Results are displayed in the "📈 Results" section.

5. **Export Results**:
   - Save results by clicking "💾 Export Results to Excel".

6. **Reset Application**:
   - Use "🔄 Reset" to start fresh.

---

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **Fork the Repo**
2. **Create a Feature Branch**:

    ```bash
    git checkout -b new-feature
    ```

3. **Commit Changes**:

    ```bash
    git commit -m "Add new feature"
    ```

4. **Push Changes**:

    ```bash
    git push origin new-feature
    ```

5. **Submit a Pull Request**

---

## 📞 Contact

Questions? Feedback? Reach out to us:

- **Email**: wahidh776@gmail.com
- **GitHub**: [@whdhdyt21](https://github.com/whdhdyt21), [@arshandariza](https://github.com/arshandariza), [@raaapiiip](https://github.com/raaapiiip)
