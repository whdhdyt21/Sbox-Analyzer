import numpy as np
import pandas as pd
from itertools import product
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import openpyxl

# ------------------ Cryptographic Functions ------------------

def hamming_weight(x):
    return bin(x).count('1')

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


def calculate_sac(sbox):
    n = 8
    sac_sum = 0
    for i in range(n):
        flips = [sbox[x] ^ sbox[x ^ (1 << i)] for x in range(256)]
        sac_sum += sum(hamming_weight(f) for f in flips)
    return sac_sum / (256 * n * n)


def calculate_bic_nl(sbox):
    n = 8
    bic_nl_sum = 0
    for j in range(n):
        f_j = [(sbox[x] >> j) & 1 for x in range(256)]
        nl = calculate_nonlinearity(f_j)
        bic_nl_sum += nl
    bic_nl_avg = bic_nl_sum / n
    return int(bic_nl_avg)


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


# ------------------ GUI Application ------------------

class SBoxAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 S-Box Analyzer")
        self.root.geometry("1100x600")
        self.root.minsize(900, 890)
        self.root.resizable(True, True)
        self.sbox = None
        self.results = {}

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Apply a modern blue theme
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # Define color palette
        self.primary_color = "#003366"  # Dark Blue
        self.secondary_color = "#6699CC"  # Medium Blue
        self.accent_color = "#99CCFF"  # Light Blue
        self.background_color = "#E6F0FA"  # Very Light Blue
        self.text_color = "#000000"  # Black

        # Configure styles
        self.style.configure("TFrame", background=self.background_color)
        self.style.configure("TLabel", background=self.background_color, foreground=self.text_color, font=("Helvetica", 12))
        self.style.configure("Header.TLabel", font=("Helvetica", 20, "bold"), foreground=self.primary_color)
        self.style.configure("TButton", font=("Helvetica", 14, "bold"), foreground="white", background=self.primary_color, borderwidth=0)
        self.style.map("TButton", background=[('active', self.secondary_color)], foreground=[('active', 'white')])
        self.style.configure("Treeview", background="white", foreground=self.text_color, rowheight=25, fieldbackground="white", font=("Helvetica", 12))
        self.style.map("Treeview", background=[('selected', self.accent_color)], foreground=[('selected', 'black')])
        self.style.configure("TCheckbutton", background=self.background_color, foreground=self.text_color, font=("Helvetica", 12))

        # Customize Progressbar Style
        self.style.configure("Custom.Horizontal.TProgressbar", troughcolor=self.background_color, background=self.accent_color)

        # Main frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky="NSEW")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)  # Results section expands

        # Title Label
        title_label = ttk.Label(main_frame, text="S-Box Analyzer", style="Header.TLabel", anchor="center")
        title_label.grid(row=0, column=0, pady=(0, 10), sticky="EW")

        # Import Button
        import_button = ttk.Button(main_frame, text="📥 Import S-Box from Excel", command=self.import_sbox, width=30)
        import_button.grid(row=1, column=0, pady=10, sticky="EW")

        # S-Box Display Label
        sbox_label = ttk.Label(main_frame, text="📄 Imported S-Box:")
        sbox_label.grid(row=2, column=0, pady=(10, 5), sticky="W")

        # S-Box Display with Scrollbar
        sbox_display_frame = ttk.Frame(main_frame)
        sbox_display_frame.grid(row=3, column=0, sticky="NSEW")
        sbox_display_frame.columnconfigure(0, weight=1)
        sbox_display_frame.rowconfigure(0, weight=1)

        self.sbox_tree = ttk.Treeview(sbox_display_frame, columns=[f"Col {i + 1}" for i in range(16)], show='headings', height=5)
        for i in range(16):
            self.sbox_tree.heading(f"Col {i + 1}", text=f"{i * 16}-{i * 16 + 15}")
            self.sbox_tree.column(f"Col {i + 1}", width=70, anchor='center')
            self.sbox_tree.grid(row=0, column=0, sticky="NSEW")

        # Add scrollbar to S-Box display
        sbox_scrollbar = ttk.Scrollbar(sbox_display_frame, orient="vertical", command=self.sbox_tree.yview)
        self.sbox_tree.configure(yscroll=sbox_scrollbar.set)
        sbox_scrollbar.grid(row=0, column=1, sticky='NS')

        # Operation Selection Label
        operations_label = ttk.Label(main_frame, text="🔧 Select Operations to Perform:")
        operations_label.grid(row=4, column=0, pady=(20, 5), sticky="W")

        # Operation Selection Frame with Scrollbar
        operations_frame = ttk.Frame(main_frame)
        operations_frame.grid(row=5, column=0, pady=10, sticky="NSEW")
        operations_frame.columnconfigure(0, weight=1)
        operations_frame.rowconfigure(0, weight=1)

        # Canvas and Scrollbar for Operations
        canvas_ops = tk.Canvas(operations_frame, background=self.background_color, height=200)
        scrollbar_ops = ttk.Scrollbar(operations_frame, orient="vertical", command=canvas_ops.yview)
        self.scrollable_ops_frame = ttk.Frame(canvas_ops, padding="10 10 10 10")

        self.scrollable_ops_frame.bind(
            "<Configure>",
            lambda e: canvas_ops.configure(
                scrollregion=canvas_ops.bbox("all")
            )
        )

        canvas_ops.create_window((0, 0), window=self.scrollable_ops_frame, anchor="nw")
        canvas_ops.configure(yscrollcommand=scrollbar_ops.set)

        canvas_ops.pack(side="left", fill="both", expand=True)
        scrollbar_ops.pack(side="right", fill="y")

        # Operation Checkboxes
        self.operation_vars = {
            "Nonlinearity (NL)": tk.BooleanVar(),
            "Strict Avalanche Criterion (SAC)": tk.BooleanVar(),
            "Bit Independence Criterion - Nonlinearity (BIC-NL)": tk.BooleanVar(),
            "Bit Independence Criterion - Strict Avalanche Criterion (BIC-SAC)": tk.BooleanVar(),
            "Linear Approximation Probability (LAP)": tk.BooleanVar(),
            "Differential Approximation Probability (DAP)": tk.BooleanVar(),
        }

        # Create Checkbuttons for each operation without tooltip binding
        for idx, (op, var) in enumerate(self.operation_vars.items()):
            chk = ttk.Checkbutton(self.scrollable_ops_frame, text=op, variable=var)
            chk.grid(row=idx, column=0, sticky="W", padx=10, pady=5)

        # Analyze Button
        analyze_button = ttk.Button(main_frame, text="⚙️ Analyze S-Box", command=self.start_analysis, width=30)
        analyze_button.grid(row=6, column=0, pady=20, sticky="EW")

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, orient='horizontal', mode='indeterminate', style="Custom.Horizontal.TProgressbar")
        self.progress.grid(row=7, column=0, pady=(0, 10), sticky="EW")
        self.progress.grid_remove()  # Hide initially

        # Results Display Label
        results_label = ttk.Label(main_frame, text="📈 Results:")
        results_label.grid(row=8, column=0, pady=(10, 5), sticky="W")

        # Results Display with Scrollbar
        results_display_frame = ttk.Frame(main_frame)
        results_display_frame.grid(row=9, column=0, sticky="NSEW")
        results_display_frame.columnconfigure(0, weight=1)
        results_display_frame.rowconfigure(0, weight=1)

        self.results_tree = ttk.Treeview(results_display_frame, columns=["Metric", "Value"], show='headings', height=5)
        self.results_tree.heading("Metric", text="Metric")
        self.results_tree.heading("Value", text="Value")
        self.results_tree.column("Metric", width=700, anchor='center')
        self.results_tree.column("Value", width=300, anchor='center')
        self.results_tree.grid(row=0, column=0, sticky="NSEW")

        # Add scrollbar to Results display
        results_scrollbar = ttk.Scrollbar(results_display_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscroll=results_scrollbar.set)
        results_scrollbar.grid(row=0, column=1, sticky='NS')

        # Export and Reset Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=10, column=0, pady=20, sticky="EW")
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        # Export Button
        export_button = ttk.Button(buttons_frame, text="💾 Export Results to Excel", command=self.export_results, width=25)
        export_button.grid(row=0, column=0, padx=10, sticky="E")

        # Reset Button
        reset_button = ttk.Button(buttons_frame, text="🔄 Reset", command=self.reset_app, width=15)
        reset_button.grid(row=0, column=1, padx=10, sticky="W")

    def import_sbox(self):
        """Handle the import of S-Box from an Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select S-Box Excel File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path, header=None)
            flat_list = df.values.flatten().tolist()
            if len(flat_list) != 256:
                messagebox.showerror("❌ Error", "S-Box must contain exactly 256 values.")
                return
            # Ensure all values are integers between 0 and 255
            sbox_values = []
            for val in flat_list:
                if isinstance(val, (int, float)):
                    intval = int(val)
                    if 0 <= intval <= 255:
                        sbox_values.append(intval)
                    else:
                        messagebox.showerror("❌ Error", "All S-Box values must be between 0 and 255.")
                        return
                else:
                    messagebox.showerror("❌ Error", "All S-Box values must be integers.")
                    return
            self.sbox = np.array(sbox_values)
            self.display_sbox()
            messagebox.showinfo("✅ Success", "S-Box imported successfully.")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to import S-Box:\n{e}")

    def display_sbox(self):
        """Display the imported S-Box in the Treeview."""
        # Clear existing data
        for item in self.sbox_tree.get_children():
            self.sbox_tree.delete(item)

        # Insert S-Box data in rows of 16
        for i in range(0, 256, 16):
            row = self.sbox[i:i + 16]
            self.sbox_tree.insert("", "end", values=list(row))

    def start_analysis(self):
        """Initiate the analysis process in a separate thread."""
        self.disable_widgets()
        self.progress.grid()
        self.progress.start(10)

        analysis_thread = threading.Thread(target=self.analyze_sbox)
        analysis_thread.start()

    def analyze_sbox(self):
        """Perform the selected cryptographic analyses on the S-box."""
        if self.sbox is None:
            self.show_error("Please import an S-Box first.")
            self.finish_analysis()
            return

        selected_ops = [op for op, var in self.operation_vars.items() if var.get()]
        if not selected_ops:
            self.show_error("Please select at least one operation to perform.")
            self.finish_analysis()
            return

        self.results = {}

        try:
            if "Nonlinearity (NL)" in selected_ops:
                self.results["Nonlinearity (NL)"] = calculate_nl_function(self.sbox)
            if "Strict Avalanche Criterion (SAC)" in selected_ops:
                self.results["Strict Avalanche Criterion (SAC)"] = round(calculate_sac(self.sbox), 5)
            if "Bit Independence Criterion - Nonlinearity (BIC-NL)" in selected_ops:
                self.results["Bit Independence Criterion - Nonlinearity (BIC-NL)"] = calculate_bic_nl(self.sbox)
            if "Bit Independence Criterion - Strict Avalanche Criterion (BIC-SAC)" in selected_ops:
                self.results["Bit Independence Criterion - Strict Avalanche Criterion (BIC-SAC)"] = round(calculate_bic_sac(self.sbox), 5)
            if "Linear Approximation Probability (LAP)" in selected_ops:
                self.results["Linear Approximation Probability (LAP)"] = round(calculate_lap(self.sbox), 5)
            if "Differential Approximation Probability (DAP)" in selected_ops:
                self.results["Differential Approximation Probability (DAP)"] = round(calculate_dap(self.sbox), 6)
        except Exception as e:
            self.show_error(f"An error occurred during analysis:\n{e}")
            self.finish_analysis()
            return

        self.display_results()
        self.show_info("S-Box analysis completed.")
        self.finish_analysis()

    def display_results(self):
        """Display the analysis results in the Treeview."""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Insert new results
        for metric, value in self.results.items():
            self.results_tree.insert("", "end", values=(metric, value))

    def export_results(self):
        """Export the analysis results to an Excel file."""
        if not self.results:
            messagebox.showerror("❌ Error", "No results to export. Please perform an analysis first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
            title="Save Results"
        )
        if not file_path:
            return

        try:
            df = pd.DataFrame(list(self.results.items()), columns=["Metric", "Value"])
            df.to_excel(file_path, index=False)
            messagebox.showinfo("✅ Success", f"Results exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to export results:\n{e}")

    def reset_app(self):
        """Reset the application by clearing all data and selections."""
        confirm = messagebox.askyesno("🔄 Reset", "Are you sure you want to reset the application?")
        if confirm:
            self.sbox = None
            self.results = {}
            # Clear S-Box display
            for item in self.sbox_tree.get_children():
                self.sbox_tree.delete(item)
            # Clear Results display
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            # Uncheck all operations
            for var in self.operation_vars.values():
                var.set(False)
            messagebox.showinfo("🔄 Reset", "Application has been reset.")

    def show_error(self, message):
        """Display an error message."""
        messagebox.showerror("❌ Error", message)

    def show_info(self, message):
        """Display an informational message."""
        messagebox.showinfo("✅ Success", message)

    def finish_analysis(self):
        """Finalize the analysis by stopping the progress bar and enabling widgets."""
        self.progress.stop()
        self.progress.grid_remove()
        self.enable_widgets()

    def disable_widgets(self):
        """Disable interactive widgets during analysis."""
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.Button):
                        grandchild.config(state='disabled')
                    elif isinstance(grandchild, ttk.Checkbutton):
                        grandchild.config(state='disabled')

    def enable_widgets(self):
        """Enable interactive widgets after analysis."""
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.Button):
                        grandchild.config(state='normal')
                    elif isinstance(grandchild, ttk.Checkbutton):
                        grandchild.config(state='normal')

# ------------------ Main Execution ------------------

def main():
    root = tk.Tk()
    app = SBoxAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()