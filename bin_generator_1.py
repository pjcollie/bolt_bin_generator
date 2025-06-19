import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Canvas
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Tooltip class for hover messages
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tip(self, event):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# Main app class
class BoltBinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bolt Bin Generator - Active Bolt & Screw")
        self.bolts = []  # List of (size, [lengths]) tuples
        self.max_lengths = 8  # Max lengths per size
        self.setup_gui()

    def setup_gui(self):
        # Bin size selection
        tk.Label(self.root, text="Choose Bin Size:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.bin_size = tk.StringVar(value="56")
        bin_menu = ttk.Combobox(self.root, textvariable=self.bin_size, values=["56", "72"], width=10)
        bin_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        Tooltip(bin_menu, "Select 56 or 72 slot bin")

        # Bolt size and length inputs
        tk.Label(self.root, text="Bolt Size (e.g., 1/4):").grid(row=1, column=5, padx=0, pady=5, sticky="e")
        self.size_entry = tk.Entry(self.root, width=10)
        self.size_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        Tooltip(self.size_entry, "Enter bolt diameter like 1/4 or 1-1/2")

        tk.Label(self.root, text="Length (e.g., 1-1/2):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.length_entry = tk.Entry(self.root, width=10)
        self.length_entry.grid(row=2, column=5, padx=1, sticky="w")
        Tooltip(self.length_entry, "Enter bolt length like 1 or 2-1/4")

        # Buttons frame
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)

        # Add bolt button
        add_btn = tk.Button(btn_frame, text="Add Bolt", command=self.add_bolt)
        add_btn.grid(row=0, column=0, padx=5)
        Tooltip(add_btn, "Add this bolt size and length to your bin")

        # Clear all button
        clear_btn = tk.Button(btn_frame, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=0, column=1, padx=5)
        Tooltip(clear_btn, "Reset all bolts and start over")

        # Save as PDF button
        pdf_btn = tk.Button(self.root, text="Save as PDF", command=self.save_pdf)
        pdf_btn.grid(row=4, column=0, columnspan=2, pady=5)
        Tooltip(pdf_btn, "Save your bolt bin layout as a PDF file")

        # Output display (text)
        self.output = tk.Text(self.root, height=5, width=40)
        self.output.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        Tooltip(self.output, "Your bolt bin layout (text)")

        # Grid display (canvas)
        tk.Label(self.root, text="Bin Layout Preview:").grid(row=6, column=0, columnspan=2, pady=5)
        self.canvas = Canvas(self.root, width=400, height=200, bg="white")
        self.canvas.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        Tooltip(self.canvas, "Visual preview of your bolt bin (rows = sizes, columns = lengths)")

    def parse_fraction(self, text):
        """Convert fraction like 1-1/2 to decimal."""
        text = text.strip()
        if not re.match(r"^\d*[-/\d]*$", text):
            return None
        try:
            if "-" in text:
                whole, frac = text.split("-")
                num, denom = frac.split("/")
                return float(whole or 0) + float(num) / float(denom)
            elif "/" in text:
                num, denom = text.split("/")
                return float(num) / float(denom)
            else:
                return float(text)
        except (ValueError, ZeroDivisionError):
            return None

    def add_bolt(self):
        size = self.size_entry.get()
        length = self.length_entry.get()
        size_val = self.parse_fraction(size)
        length_val = self.parse_fraction(length)
        
        if size_val is None or length_val is None:
            messagebox.showerror("Error", "Invalid size or length. Use formats like 1/4 or 1-1/2.")
            return

        # Find or create size group
        for bolt in self.bolts:
            if abs(bolt[0] - size_val) < 0.001:
                if len(bolt[1]) >= self.max_lengths:
                    messagebox.showerror("Error", f"Cannot add more than {self.max_lengths} lengths for size {size}.")
                    return
                if length_val not in bolt[1]:
                    bolt[1].append(length_val)
                    bolt[1].sort()
                break
        else:
            self.bolts.append((size_val, [length_val]))
            self.bolts.sort(key=lambda x: x[0])

        self.size_entry.delete(0, tk.END)
        self.length_entry.delete(0, tk.END)
        self.update_output()
        self.update_grid()

    def clear_all(self):
        """Clear all bolts and reset output."""
        self.bolts = []
        self.output.delete(1.0, tk.END)
        self.canvas.delete("all")
        messagebox.showinfo("Cleared", "All bolts cleared. Start fresh!")

    def format_number(self, num):
        """Convert decimal to fraction if needed, including common bolt fractions."""
        if num.is_integer():
            return str(int(num))
        whole = int(num)
        frac = num - whole
        for denom in range(2, 17):  # Check up to 16 for 5/16, 7/16, 9/16
            num_frac = round(frac * denom)
            if abs(frac * denom - num_frac) < 0.001:  # Tighter tolerance
                if whole == 0:
                    return f"{num_frac}/{denom}"
                return f"{whole}-{num_frac}/{denom}"
        return f"{num:.2f}"  # Fallback to decimal if no fraction matches

    def update_output(self):
        self.output.delete(1.0, tk.END)
        for i, (size, lengths) in enumerate(self.bolts, 1):
            size_str = self.format_number(size)
            length_str = ", ".join(self.format_number(l) for l in lengths)
            self.output.insert(tk.END, f"Row {i}: {size_str}\" ({length_str}\")\n")

    def update_grid(self):
        self.canvas.delete("all")
        bin_slots = int(self.bin_size.get())
        rows = 7 if bin_slots == 56 else 9
        cols = self.max_lengths
        cell_width = 40
        cell_height = 25
        offset_x, offset_y = 50, 30

        # Draw grid
        for i in range(rows + 1):
            y = offset_y + i * cell_height
            self.canvas.create_line(offset_x, y, offset_x + cols * cell_width, y)
        for j in range(cols + 1):
            x = offset_x + j * cell_width
            self.canvas.create_line(x, offset_y, x, offset_y + rows * cell_height)

        # Label rows with sizes
        for i, (size, _) in enumerate(self.bolts[:rows], 0):
            size_str = self.format_number(size)
            self.canvas.create_text(offset_x - 30, offset_y + i * cell_height + cell_height / 2,
                                   text=f"{size_str}\"", anchor="e")

        # Fill cells with lengths
        for i, (size, lengths) in enumerate(self.bolts[:rows], 0):
            for j, length in enumerate(lengths[:cols]):
                length_str = self.format_number(length)
                self.canvas.create_text(offset_x + j * cell_width + cell_width / 2,
                                       offset_y + i * cell_height + cell_height / 2,
                                       text=length_str, anchor="center")

    def save_pdf(self):
        if not self.bolts:
            messagebox.showerror("Error", "No bolts to save! Add some bolts first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Bolt Bin Layout"
        )
        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Bolt Bin Layout - Active Bolt & Screw")
        c.drawString(100, 730, f"Bin Size: {self.bin_size.get()} slots")
        c.drawString(100, 710, "Material: Grade 5 Zinc, Coarse Threads")

        # List bolts
        y = 690
        for i, (size, lengths) in enumerate(self.bolts, 1):
            size_str = self.format_number(size)
            length_str = ", ".join(self.format_number(l) for l in lengths)
            text = f"Row {i}: {size_str}\" ({length_str}\")"
            c.drawString(100, y, text)
            y -= 20
            if y < 400:  # Reserve space for grid
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 750

        # Draw grid layout
        c.drawString(100, y, "Bin Layout:")
        y -= 20
        bin_slots = int(self.bin_size.get())
        rows = 7 if bin_slots == 56 else 9
        cols = self.max_lengths
        cell_width = 30
        cell_height = 20
        offset_x, offset_y = 100, y - 20
        text_height = 5  # Approximate text height for centering

        # Draw grid lines
        for i in range(rows + 1):
            y_pos = offset_y - i * cell_height
            c.line(offset_x, y_pos, offset_x + cols * cell_width, y_pos)
        for j in range(cols + 1):
            x_pos = offset_x + j * cell_width
            c.line(x_pos, offset_y, x_pos, offset_y - rows * cell_height)

        # Label rows with sizes
        c.setFont("Helvetica", 10)
        for i, (size, _) in enumerate(self.bolts[:rows], 0):
            size_str = self.format_number(size)
            c.drawString(offset_x - 40, offset_y - i * cell_height - cell_height / 2 - text_height,
                         f"{size_str}\"")

        # Fill cells with lengths
        for i, (size, lengths) in enumerate(self.bolts[:rows], 0):
            for j, length in enumerate(lengths[:cols]):
                length_str = self.format_number(length)
                c.drawCentredString(offset_x + j * cell_width + cell_width / 2,
                                   offset_y - i * cell_height - cell_height / 2 - text_height,
                                   length_str)

        c.save()
        messagebox.showinfo("Success", f"Layout saved as PDF: {os.path.basename(file_path)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BoltBinApp(root)
    root.mainloop()
    
