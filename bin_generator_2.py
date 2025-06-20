import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Canvas
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Main app class
class BoltBinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bolt Bin Generator - Active Bolt & Screw")
        self.bolts = []  # List of (size, lengths, items) tuples
        self.max_lengths = 4  # Max lengths per size
        self.max_items = 4    # Max items (Nut, Flatwasher, Lockwasher, Locknut, Blank)
        self.root.geometry("600x700")  # Wider and taller window
        self.setup_gui()

    def setup_gui(self):
        # Center the main frame
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Bin size selection
        tk.Label(main_frame, text="Choose Bin Size:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.bin_size = tk.StringVar(value="56")
        bin_menu = ttk.Combobox(main_frame, textvariable=self.bin_size, values=["56", "72"], width=10)
        bin_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        bin_menu.bind("<<ComboboxSelected>>", self.reset_on_material_or_size_change)

        # Material selection
        tk.Label(main_frame, text="Choose Material:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.material = tk.StringVar(value="Grade 5 Zinc")
        material_menu = ttk.Combobox(main_frame, textvariable=self.material,
                                     values=["Grade 5 Zinc", "Grade 5 Plain", "Grade 8 Plain",
                                             "Grade 8 Yellow Zinc", "304 Stainless Steel"], width=20)
        material_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        material_menu.bind("<<ComboboxSelected>>", self.reset_on_material_or_size_change)

        # Bolt size and length inputs
        tk.Label(main_frame, text="Bolt Size (e.g., 1/4):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.size_entry = tk.Entry(main_frame, width=12)
        self.size_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.size_entry.bind("<Return>", lambda event: self.length_entry.focus_set())

        tk.Label(main_frame, text="Length (e.g., 1-1/2):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.length_entry = tk.Entry(main_frame, width=12)
        self.length_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        self.length_entry.bind("<Return>", lambda event: self.add_bolt())

        # Buttons frame
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Add bolt button
        add_bolt_btn = tk.Button(btn_frame, text="Add Bolt", command=self.add_bolt)
        add_bolt_btn.grid(row=0, column=0, padx=10)

        # Add blank space button
        add_blank_btn = tk.Button(btn_frame, text="Add Blank Space", command=self.add_blank_space)
        add_blank_btn.grid(row=0, column=1, padx=10)

        # Remove last item button
        remove_btn = tk.Button(btn_frame, text="Remove Last Item", command=self.remove_last_item)
        remove_btn.grid(row=0, column=2, padx=10)

        # Clear all button
        clear_btn = tk.Button(btn_frame, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=0, column=3, padx=10)

        # Save as PDF button
        pdf_btn = tk.Button(main_frame, text="Save as PDF", command=self.save_pdf)
        pdf_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Output display (text)
        self.output = tk.Text(main_frame, height=5, width=50)
        self.output.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Grid display (canvas)
        tk.Label(main_frame, text="Bin Layout Preview:").grid(row=7, column=0, columnspan=2, pady=10)
        self.canvas = Canvas(main_frame, width=550, height=300, bg="white")
        self.canvas.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def reset_on_material_or_size_change(self, event):
        """Reset bolts and items when material or bin size changes."""
        if self.bolts:
            self.bolts = []
            self.output.delete(1.0, tk.END)
            self.canvas.delete("all")
            messagebox.showinfo("Reset", "Bolts and items cleared due to material or bin size change.")

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

    def show_item_popup(self, size):
        """Show a pop-up to select items for a new size."""
        popup = tk.Toplevel(self.root)
        popup.title("Select Items")
        popup.geometry("300x200")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text=f"Add items for size {size}?").pack(pady=10)
        nut_var = tk.BooleanVar()
        flatwasher_var = tk.BooleanVar()
        lockwasher_var = tk.BooleanVar()
        locknut_var = tk.BooleanVar()
        tk.Checkbutton(popup, text="Nut", variable=nut_var).pack(anchor="w", padx=20)
        tk.Checkbutton(popup, text="Flatwasher", variable=flatwasher_var).pack(anchor="w", padx=20)
        tk.Checkbutton(popup, text="Lockwasher", variable=lockwasher_var).pack(anchor="w", padx=20)
        tk.Checkbutton(popup, text="Locknut", variable=locknut_var).pack(anchor="w", padx=20)

        selected_items = []
        def confirm():
            items = set()
            if nut_var.get():
                items.add("Nut")
            if flatwasher_var.get():
                items.add("Flatwasher")
            if lockwasher_var.get():
                items.add("Lockwasher")
            if locknut_var.get():
                items.add("Locknut")
            selected_items.append(items)
            popup.destroy()

        tk.Button(popup, text="OK", command=confirm).pack(pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)
        self.root.wait_window(popup)
        return selected_items[0] if selected_items else set()

    def add_bolt(self):
        size = self.size_entry.get()
        length = self.length_entry.get()
        size_val = self.parse_fraction(size)
        length_val = self.parse_fraction(length)
        
        if size_val is None or length_val is None:
            messagebox.showerror("Error", "Invalid size or length. Use formats like 1/4 or 1-1/2.")
            return

        # Check if size exists
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
            # New size, show item pop-up
            items = self.show_item_popup(size)
            if len(items) > self.max_items:
                messagebox.showerror("Error", f"Cannot add more than {self.max_items} items for size {size}.")
                return
            self.bolts.append((size_val, [length_val], items))
            self.bolts.sort(key=lambda x: x[0])

        self.size_entry.delete(0, tk.END)
        self.length_entry.delete(0, tk.END)
        self.update_output()
        self.update_grid()
        self.size_entry.focus_set()

    def add_blank_space(self):
        size = self.size_entry.get()
        size_val = self.parse_fraction(size)
        
        if size_val is None:
            messagebox.showerror("Error", "Invalid size. Use formats like 1/4 or 1-1/2.")
            return

        # Check if size exists
        for bolt in self.bolts:
            if abs(bolt[0] - size_val) < 0.001:
                if len(bolt[2]) >= self.max_items:
                    messagebox.showerror("Error", f"Cannot add more than {self.max_items} items (including blanks) for size {size}.")
                    return
                if "Blank" not in bolt[2]:
                    bolt[2].add("Blank")
                break
        else:
            # New size, show item pop-up
            items = self.show_item_popup(size)
            items.add("Blank")
            if len(items) > self.max_items:
                messagebox.showerror("Error", f"Cannot add more than {self.max_items} items (including blank) for size {size}.")
                return
            self.bolts.append((size_val, [], items))
            self.bolts.sort(key=lambda x: x[0])

        self.size_entry.delete(0, tk.END)
        self.length_entry.delete(0, tk.END)
        self.update_output()
        self.update_grid()
        self.size_entry.focus_set()

    def remove_last_item(self):
        """Remove the last added bolt length or item."""
        if not self.bolts:
            messagebox.showinfo("Info", "No bolts or items to remove!")
            return
        last_bolt = self.bolts[-1]
        if last_bolt[1]:  # Remove last length if present
            last_bolt[1].pop()
        elif last_bolt[2]:  # Remove last item if no lengths
            last_bolt[2].pop()
        if not last_bolt[1] and not last_bolt[2]:  # Remove size if empty
            self.bolts.pop()
        self.update_output()
        self.update_grid()
        messagebox.showinfo("Success", "Last item removed.")

    def clear_all(self):
        """Clear all bolts and items."""
        self.bolts = []
        self.output.delete(1.0, tk.END)
        self.canvas.delete("all")
        messagebox.showinfo("Cleared", "All bolts and items cleared. Start fresh!")

    def format_number(self, num):
        """Convert decimal to fraction if needed."""
        if num.is_integer():
            return str(int(num))
        whole = int(num)
        frac = num - whole
        for denom in range(2, 17):
            num_frac = round(frac * denom)
            if abs(frac * denom - num_frac) < 0.001:
                if whole == 0:
                    return f"{num_frac}/{denom}"
                return f"{whole}-{num_frac}/{denom}"
        return f"{num:.2f}"

    def update_output(self):
        self.output.delete(1.0, tk.END)
        for i, (size, lengths, items) in enumerate(self.bolts, 1):
            size_str = self.format_number(size)
            items_str = ", ".join(sorted([items for items in items if items != "Blank"] + ["Blank" for _ in items if items == "Blank"]))
            lengths_str = ", ".join(self.format_number(l) for l in lengths)
            contents = ", ".join(filter(None, [items_str, lengths_str]))
            self.output.insert(tk.END, f"Row {i}: {size_str}\" ({contents})\n")

    def update_grid(self):
        self.canvas.delete("all")
        bin_slots = int(self.bin_size.get())
        rows = 7 if bin_slots == 56 else 9
        cols = self.max_items + self.max_lengths  # Up to 4 items + 4 lengths
        cell_width = 40
        cell_height = 30
        offset_x, offset_y = 60, 40

        # If no bolts, display a message
        if not self.bolts:
            self.canvas.create_text(275, 150, text="No bolts or items added yet.", font=("TkDefaultFont", 12), anchor="center")
            return

        # Draw grid
        for i in range(rows + 1):
            y = offset_y + i * cell_height
            self.canvas.create_line(offset_x, y, offset_x + cols * cell_width, y, fill="black")
        for j in range(cols + 1):
            x = offset_x + j * cell_width
            self.canvas.create_line(x, offset_y, x, offset_y + rows * cell_height, fill="black")

        # Label rows with sizes
        for i, (size, _, _) in enumerate(self.bolts[:rows], 0):
            size_str = self.format_number(size)
            self.canvas.create_text(offset_x - 20, offset_y + i * cell_height + cell_height / 2,
                                   text=f"{size_str}\"", anchor="e", font=("TkDefaultFont", 11), fill="black")

        # Draw item and length cells
        for i, (size, lengths, items) in enumerate(self.bolts[:rows], 0):
            # Items in columns 0 to 3, in order
            item_list = [item for item in ["Nut", "Flatwasher", "Lockwasher", "Locknut", "Blank"] if item in items]
            for j, item in enumerate(item_list[:self.max_items]):
                if item != "Blank":
                    item_char = {"Nut": "N", "Flatwasher": "F", "Lockwasher": "L", "Locknut": "LN"}[item]
                    self.canvas.create_text(offset_x + j * cell_width + cell_width / 2,
                                           offset_y + i * cell_height + cell_height / 2,
                                           text=item_char, anchor="center", font=("TkDefaultFont", 11), fill="black")
                # Blank cells are left empty
            # Lengths start after items
            start_col = len(item_list)
            for j, length in enumerate(lengths[:self.max_lengths]):
                length_str = self.format_number(length)
                self.canvas.create_text(offset_x + (j + start_col) * cell_width + cell_width / 2,
                                       offset_y + i * cell_height + cell_height / 2,
                                       text=length_str, anchor="center", font=("TkDefaultFont", 11), fill="black")

        # Debug text
        #self.canvas.create_text(275, offset_y - 20, text="Preview", font=("TkDefaultFont", 10), anchor="center", fill="blue")

    def save_pdf(self):
        if not self.bolts:
            messagebox.showerror("Error", "No bolts or items to save! Add some first.")
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
        c.drawString(100, 710, f"Material: {self.material.get()}")

        # List bolts and items
        y = 690
        for i, (size, lengths, items) in enumerate(self.bolts, 1):
            size_str = self.format_number(size)
            items_str = ", ".join(sorted([items for items in items if items != "Blank"] + ["Blank" for _ in items if items == "Blank"]))
            lengths_str = ", ".join(self.format_number(l) for l in lengths)
            contents = ", ".join(filter(None, [items_str, lengths_str]))
            text = f"Row {i}: {size_str}\" ({contents})"
            c.drawString(100, y, text)
            y -= 20
            if y < 400:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 750

        # Draw grid layout
        c.drawString(100, y, "Bin Layout:")
        y -= 20
        bin_slots = int(self.bin_size.get())
        rows = 7 if bin_slots == 56 else 9
        cols = self.max_items + self.max_lengths
        cell_width = 25
        cell_height = 20
        offset_x, offset_y = 100, y - 20
        text_height = 5

        # Draw grid lines
        for i in range(rows + 1):
            y_pos = offset_y - i * cell_height
            c.line(offset_x, y_pos, offset_x + cols * cell_width, y_pos)
        for j in range(cols + 1):
            x_pos = offset_x + j * cell_width
            c.line(x_pos, offset_y, x_pos, offset_y - rows * cell_height)

        # Label rows with sizes
        c.setFont("Helvetica", 10)
        for i, (size, _, _) in enumerate(self.bolts[:rows], 0):
            size_str = self.format_number(size)
            c.drawString(offset_x - 40, offset_y - i * cell_height - cell_height / 2 - text_height,
                         f"{size_str}\"")

        # Draw item and length cells
        for i, (size, lengths, items) in enumerate(self.bolts[:rows], 0):
            item_list = [item for item in ["Nut", "Flatwasher", "Lockwasher", "Locknut", "Blank"] if item in items]
            for j, item in enumerate(item_list[:self.max_items]):
                if item != "Blank":
                    item_char = {"Nut": "N", "Flatwasher": "F", "Lockwasher": "L", "Locknut": "LN"}[item]
                    c.drawCentredString(offset_x + j * cell_width + cell_width / 2,
                                       offset_y - i * cell_height - cell_height / 2 - text_height, item_char)
                # Blank cells are left empty
            start_col = len(item_list)
            for j, length in enumerate(lengths[:self.max_lengths]):
                length_str = self.format_number(length)
                c.drawCentredString(offset_x + (j + start_col) * cell_width + cell_width / 2,
                                   offset_y - i * cell_height - cell_height / 2 - text_height, length_str)

        c.save()
        messagebox.showinfo("Success", f"Layout saved as PDF: {os.path.basename(file_path)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BoltBinApp(root)
    root.mainloop()
    
