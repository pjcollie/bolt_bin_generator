import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tempfile
import platform
import subprocess
from datetime import datetime

class BoltBinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bolt Bin Generator - Touchscreen")
        self.root.geometry("800x480")  # For 7-inch Raspberry Pi touchscreen
        self.root.attributes("-fullscreen", True)  # Fullscreen mode
        self.bolts = []  # List of (size, lengths, items) tuples
        self.max_lengths = 4
        self.max_items = 4
        self.current_screen = None
        self.bin_size = tk.StringVar(value="56")
        self.material = tk.StringVar(value="Grade 5 Zinc")
        self.pdf_dir = "/home/pi/bolt_bin_pdfs"  # Default PDF save directory
        os.makedirs(self.pdf_dir, exist_ok=True)  # Create directory if it doesn't exist
        self.setup_bin_size_screen()

    def clear_screen(self):
        """Clear the current screen."""
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = tk.Frame(self.root)
        self.current_screen.pack(fill="both", expand=True)

    def setup_bin_size_screen(self):
        """Screen 1: Choose bin size (56 or 72 holes)."""
        self.clear_screen()
        tk.Label(self.current_screen, text="Select Bin Size", font=("Helvetica", 24, "bold")).pack(pady=20)
        tk.Button(self.current_screen, text="56 Holes", font=("Helvetica", 20), bg="#4CAF50", fg="white",
                 width=15, height=3, command=lambda: self.set_bin_size("56")).pack(pady=20)
        tk.Button(self.current_screen, text="72 Holes", font=("Helvetica", 20), bg="#4CAF50", fg="white",
                 width=15, height=3, command=lambda: self.set_bin_size("72")).pack(pady=20)
        tk.Button(self.current_screen, text="Exit", font=("Helvetica", 16), bg="#F44336", fg="white",
                 width=10, height=2, command=self.root.quit).pack(pady=20)

    def set_bin_size(self, size):
        """Set bin size and move to material selection."""
        self.bolts = []  # Reset bolts on bin size change
        self.bin_size.set(size)
        self.setup_material_screen()

    def setup_material_screen(self):
        """Screen 2: Choose material."""
        self.clear_screen()
        tk.Label(self.current_screen, text="Select Material", font=("Helvetica", 24, "bold")).pack(pady=20)
        materials = ["Grade 5 Zinc", "Grade 5 Plain", "Grade 8 Plain", "Grade 8 Yellow Zinc", "304 Stainless Steel"]
        for mat in materials:
            tk.Button(self.current_screen, text=mat, font=("Helvetica", 16), bg="#2196F3", fg="white",
                     width=25, height=2, command=lambda m=mat: self.set_material(m)).pack(pady=10)
        tk.Button(self.current_screen, text="Back", font=("Helvetica", 16), bg="#F44336", fg="white",
                 width=10, height=2, command=self.setup_bin_size_screen).pack(pady=20)

    def set_material(self, material):
        """Set material and move to main screen."""
        self.bolts = []  # Reset bolts on material change
        self.material.set(material)
        self.setup_main_screen()

    def setup_main_screen(self):
        """Screen 3: Main interface for adding bolts and previewing."""
        self.clear_screen()
        main_frame = self.current_screen
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Bin and material display
        tk.Label(main_frame, text=f"Bin: {self.bin_size.get()} Holes | Material: {self.material.get()}",
                 font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        # Bolt size selection (buttons)
        tk.Label(main_frame, text="Bolt Size:", font=("Helvetica", 16)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.size_var = tk.StringVar()
        sizes = ["1/4", "5/16", "3/8", "1/2", "5/8", "3/4"]  # Common bolt sizes
        size_frame = tk.Frame(main_frame)
        size_frame.grid(row=1, column=1, padx=10, pady=10)
        for size in sizes:
            tk.Button(size_frame, text=size, font=("Helvetica", 14), bg="#FFC107", fg="black",
                     width=8, height=2, command=lambda s=size: self.size_var.set(s)).pack(side="left", padx=5)

        # Length selection (buttons)
        tk.Label(main_frame, text="Length:", font=("Helvetica", 16)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.length_var = tk.StringVar()
        lengths = ["1/2", "3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2", "3"]  # Common lengths
        length_frame = tk.Frame(main_frame)
        length_frame.grid(row=2, column=1, padx=10, pady=10)
        for length in lengths:
            tk.Button(length_frame, text=length, font=("Helvetica", 14), bg="#FFC107", fg="black",
                     width=8, height=2, command=lambda l=length: self.length_var.set(l)).pack(side="left", padx=5)

        # Action buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Add Bolt", font=("Helvetica", 16), bg="#4CAF50", fg="white",
                 width=12, height=2, command=self.add_bolt).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Add Blank", font=("Helvetica", 16), bg="#4CAF50", fg="white",
                 width=12, height=2, command=self.add_blank_space).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Remove Last", font=("Helvetica", 16), bg="#F44336", fg="white",
                 width=12, height=2, command=self.remove_last_item).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Clear All", font=("Helvetica", 16), bg="#F44336", fg="white",
                 width=12, height=2, command=self.clear_all).pack(side="left", padx=10)

        # PDF buttons
        tk.Button(main_frame, text="Save PDF", font=("Helvetica", 16), bg="#2196F3", fg="white",
                 width=12, height=2, command=self.save_pdf).grid(row=4, column=0, pady=10)
        tk.Button(main_frame, text="Print PDF", font=("Helvetica", 16), bg="#2196F3", fg="white",
                 width=12, height=2, command=self.print_pdf).grid(row=4, column=1, pady=10)

        # Canvas for grid preview
        self.canvas = Canvas(main_frame, width=600, height=200, bg="white")
        self.canvas.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        self.update_grid()

        # Navigation buttons
        tk.Button(main_frame, text="Back", font=("Helvetica", 16), bg="#F44336", fg="white",
                 width=10, height=2, command=self.setup_material_screen).grid(row=6, column=0, pady=10)
        tk.Button(main_frame, text="Exit", font=("Helvetica", 16), bg="#F44336", fg="white",
                 width=10, height=2, command=self.root.quit).grid(row=6, column=1, pady=10)

    def parse_fraction(self, text):
        """Convert fraction like 1-1/2 to decimal."""
        text = text.strip()
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
        popup.title(f"Items for {size}\"")
        popup.geometry("400x300")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text=f"Add items for {size}\"?", font=("Helvetica", 16)).pack(pady=10)
        nut_var = tk.BooleanVar()
        flatwasher_var = tk.BooleanVar()
        lockwasher_var = tk.BooleanVar()
        locknut_var = tk.BooleanVar()
        tk.Checkbutton(popup, text="Nut", variable=nut_var, font=("Helvetica", 14)).pack(anchor="w", padx=20, pady=5)
        tk.Checkbutton(popup, text="Flatwasher", variable=flatwasher_var, font=("Helvetica", 14)).pack(anchor="w", padx=20, pady=5)
        tk.Checkbutton(popup, text="Lockwasher", variable=lockwasher_var, font=("Helvetica", 14)).pack(anchor="w", padx=20, pady=5)
        tk.Checkbutton(popup, text="Locknut", variable=locknut_var, font=("Helvetica", 14)).pack(anchor="w", padx=20, pady=5)

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

        tk.Button(popup, text="OK", font=("Helvetica", 14), bg="#4CAF50", fg="white", width=10, height=2, command=confirm).pack(pady=10)
        tk.Button(popup, text="Cancel", font=("Helvetica", 14), bg="#F44336", fg="white", width=10, height=2, command=popup.destroy).pack(pady=5)
        self.root.wait_window(popup)
        return selected_items[0] if selected_items else set()

    def add_bolt(self):
        """Add a bolt with selected size and length."""
        size = self.size_var.get()
        length = self.length_var.get()
        if not size or not length:
            messagebox.showerror("Error", "Please select a size and length.", parent=self.current_screen)
            return
        size_val = self.parse_fraction(size)
        length_val = self.parse_fraction(length)
        
        if size_val is None or length_val is None:
            messagebox.showerror("Error", "Invalid size or length format.", parent=self.current_screen)
            return

        for bolt in self.bolts:
            if abs(bolt[0] - size_val) < 0.001:
                row_capacity = self.max_items + self.max_lengths
                if len(bolt[2]) + len(bolt[1]) + 1 > row_capacity:
                    messagebox.showerror("Error", f"Cannot add more items or lengths for size {size}. Row capacity ({row_capacity}) reached.", parent=self.current_screen)
                    return
                if length_val not in bolt[1]:
                    bolt[1].append(length_val)
                    bolt[1].sort()
                break
        else:
            items = self.show_item_popup(size)
            if len(items) > self.max_items:
                messagebox.showerror("Error", f"Cannot add more than {self.max_items} items for size {size}.", parent=self.current_screen)
                return
            self.bolts.append((size_val, [length_val], items))
            self.bolts.sort(key=lambda x: x[0])

        self.update_grid()

    def add_blank_space(self):
        """Add a blank space for a selected size."""
        size = self.size_var.get()
        if not size:
            messagebox.showerror("Error", "Please select a size.", parent=self.current_screen)
            return
        size_val = self.parse_fraction(size)
        
        if size_val is None:
            messagebox.showerror("Error", "Invalid size format.", parent=self.current_screen)
            return

        for bolt in self.bolts:
            if abs(bolt[0] - size_val) < 0.001:
                row_capacity = self.max_items + self.max_lengths
                if len(bolt[2]) + len(bolt[1]) + 1 > row_capacity:
                    messagebox.showerror("Error", f"Cannot add more items or lengths (including blanks) for size {size}. Row capacity ({row_capacity}) reached.", parent=self.current_screen)
                    return
                if "Blank" not in bolt[2]:
                    bolt[2].add("Blank")
                break
        else:
            items = self.show_item_popup(size)
            items.add("Blank")
            if len(items) > self.max_items:
                messagebox.showerror("Error", f"Cannot add more than {self.max_items} items (including blank) for size {size}.", parent=self.current_screen)
                return
            self.bolts.append((size_val, [], items))
            self.bolts.sort(key=lambda x: x[0])

        self.update_grid()

    def remove_last_item(self):
        """Remove the last added bolt length or item."""
        if not self.bolts:
            messagebox.showinfo("Info", "No bolts or items to remove!", parent=self.current_screen)
            return
        last_bolt = self.bolts[-1]
        if last_bolt[1]:
            last_bolt[1].pop()
        elif last_bolt[2]:
            items_list = list(last_bolt[2])
            last_bolt[2].remove(items_list[-1])
        if not last_bolt[1] and not last_bolt[2]:
            self.bolts.pop()
        self.update_grid()
        messagebox.showinfo("Success", "Last item removed.", parent=self.current_screen)

    def clear_all(self):
        """Clear all bolts and items."""
        self.bolts = []
        self.canvas.delete("all")
        self.update_grid()
        messagebox.showinfo("Success", "All items cleared.", source=self.current_screen)

    def format_number(self, num):
        """Convert decimal to fraction if needed."""
        if num.is_integer():
            return str(int(num))
        whole = int(num)
        frac = num - whole
        for denom in range(2, 8):
            num_frac = round(frac * denom)
            if abs(frac * denom - num_frac) < 0.001:
                if whole == 0:
                    return f"{num_frac}/{denom}"
                return f"{whole}-{num_frac}/{denom}"
        return f"{num:.2f}"

    def update_grid(self):
        """Update the canvas grid preview."""
        self.canvas.delete("all")
        bin_slots = int(self.bin_size.get())
        max_rows = 7 if bin_slots == 56 else 9
        rows = max_rows if not self.bolts else min(len(self.bolts), max_rows)
        cols = self.max_items + self.max_lengths
        cell_width = 60
        cell_height = 25
        grid_width = cols * cell_width
        grid_height = rows * cell_height
        offset_x = (600 - grid_width) / 2
        offset_y = (200 - grid_height) / 2

        # Draw grid
        for i in range(rows + 1):
            y = offset_y + i * cell_height
            self.canvas.create_line(offset_x, y, offset_x + cols * cell_width, y, fill="black")
        for j in range(cols + 1):
            x = offset_x + j * cell_width
            self.canvas.create_line(x, offset_y, x, offset_y + rows * cell_height, fill="black")

        # Label rows with sizes or placeholders
        for i in range(rows):
            if i < len(self.bolts):
                size = self.bolts[i][0]
                size_str = self.format_number(size)
            else:
                size_str = f"Row {i+1}"
            self.canvas.create_text(offset_x - 30, offset_y + i * cell_height + cell_height / 2,
                                   text=size_str, anchor="e", font=("Helvetica", 12), fill="black")

        # Draw item and length cells
        for i, (size, lengths, items) in enumerate(self.bolts[:rows], 0):
            item_list = [item for item in ["Nut", "Flatwasher", "Lockwasher", "Locknut", "Blank"] if item in items]
            for j, item in enumerate(item_list[:self.max_items]):
                if item != "Blank":
                    item_char = {"Nut": "N", "Flatwasher": "F", "Lockwasher": "L", "Locknut": "LN"}[item]
                    self.canvas.create_text(offset_x + j * cell_width + cell_width / 2,
                                           offset_y + i * cell_height + cell_height / 2,
                                           text=item_char, anchor="center", font=("Helvetica", 12), fill="black")
            start_col = len(item_list)
            for j, length in enumerate(lengths[:self.max_lengths]):
                length_str = self.format_number(length)
                self.canvas.create_text(offset_x + (j + start_col) * cell_width + cell_width / 2,
                                       offset_y + i * cell_height + cell_height / 2,
                                       text=length_str, anchor="center", font=("Helvetica", 12), fill="black")

        # Add column headers
        item_labels = ["Nut", "Flatwasher", "Lockwasher", "Locknut"]
        for j in range(self.max_items):
            self.canvas.create_text(offset_x + j * cell_width + cell_width / 2,
                                   offset_y - 10, text=item_labels[j][0], anchor="center", font=("Helvetica", 10))
        for j in range(self.max_lengths):
            self.canvas.create_text(offset_x + (j + self.max_items) * cell_width + cell_width / 2,
                                   offset_y - 10, text=f"Len {j+1}", anchor="center", font=("Helvetica", 10))
"""

    def save_pdf(self):
        """Save the layout as a PDF with a timestamped filename."""
        if not self.bolts:
            messagebox.showerror("Error", "No bolts or items to save!", parent=self.current_screen)
            return

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(self.pdf_dir, f"bolt_bin_{timestamp}.pdf")

        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Bolt Bin Layout - Active Bolt & Screw")
        c.drawString(100, 730, f"Bin Size: {self.bin_size.get()} slots")
        c.drawString(100, 710, f"Material: {self.material.get()}")

        y = 690
        for i, (size, lengths, items) in enumerate(self.bolts, 1):
            size_str = self.format_number(size)
            items_str = ", ".join(sorted([item for item in items if item != "Blank"] + ["Blank" for _ in items if item == "Blank"]))
            lengths_str = ", ".join(self.format_number(l) for l in lengths)
            contents = ", ".join(filter(None, [items_str, lengths_str]))
            text = f"Row {i}: {size_str}\" ({contents})"
            c.drawString(100, y, text)
            y -= 20
            if y < 400:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 750

        c.drawString(100, y, "Bin Layout:")
        y -= 20
        bin_slots = int(self.bin_size.get())
        rows = 7 if bin_slots == 56 else 9
        cols = self.max_items + self.max_lengths
        cell_width = 25
        cell_height = 20
        offset_x, offset_y = 100, y - 20
        text_height = 5

        for i in range(rows + 1):
            y_pos = offset_y - i * cell_height
            c.line(offset_x, y_pos, offset_x + cols * cell_width, y_pos)
        for j in range(cols + 1):
            x_pos = offset_x + j * cell_width
            c.line(x_pos, offset_y, x_pos, offset_y - rows * cell_height)

        c.setFont("Helvetica", 10)
        for i, (size, _, _) in enumerate(self.bolts[:rows], 0):
            size_str = self.format_number(size)
            c.drawString(offset_x - 40, offset_y - i * cell_height - cell_height / 2 - text_height,
                         f"{size_str}\"")
        for i, (size, lengths, items) in enumerate(self.bolts[:rows], 0):
            item_list = [item for item in ["Nut", "Flatwasher", "Lockwasher", "Locknut", "Blank"] if item in items]
            for j, item in enumerate(item_list[:self.max_items]):
                if item != "Blank":
                    item_char = {"Nut": "N", "Flatwasher": "F", "Lockwasher": "L", "Locknut": "LN"}[item]
                    c.drawCentredString(offset_x + j * cell_width + cell_width / 2,
                                       offset_y - i * cell_height - cell_height / 2 - text_height, item_char)
            start_col = len(item_list)
            for j, length in enumerate(lengths[:self.max_lengths]):
                length_str = self.format_number(length)
                c.drawCentredString(offset_x + (j + start_col) * cell_width + cell_width / 2,
                                   offset_y - i * cell_height - cell_height / 2 - text_height, length_str)

        c.save()
        messagebox.showinfo("Success", f"PDF saved to: {file_path}", parent=self.current_screen)

    def print_pdf(self):
        """Print the layout as a PDF."""
        if not self.bolts:
            messagebox.showerror("Error", "No bolts or items to print!", parent=self.current_screen)
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            file_path = tmp_file.name
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, "Bolt Bin Layout - Active Bolt & Screw")
            c.drawString(100, 730, f"Bin Size: {self.bin_size.get()} slots")
            c.drawString(100, 710, f"Material: {self.material.get()}")

            y = 690
            for i, (size, lengths, items) in enumerate(self.bolts, 1):
                size_str = self.format_number(size)
                items_str = ", ".join(sorted([item for item in items if item != "Blank"] + ["Blank" for _ in items if item == "Blank"]))
                lengths_str = ", ".join(self.format_number(l) for l in lengths)
                contents = ", ".join(filter(None, [items_str, lengths_str]))
                text = f"Row {i}: {size_str}\" ({contents})"
                c.drawString(100, y, text)
                y -= 20
                if y < 400:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = 690

            c.drawString(100, y, "Bin Layout:")
            y -= 20
            bin_slots = int(self.bin_size.get())
            rows = 7 if bin_slots == 56 else 9
            cols = self.max_items + self.max_lengths
            cell_width = 25
            cell_height = 20
            offset_x, offset_y = 100, y - 20
            text_height = 5

            for i in range(rows + 1):
                y_pos = offset_y - i * cell_height
                c.line(offset_x, y_pos, offset_x + cols * cell_width, y_pos)
            for j in range(cols + 1):
                x_pos = offset_x + j * cell_width
                c.line(x_pos, offset_y, x_pos, offset_y - rows * cell_height)

            c.setFont("Helvetica", 10)
            for i, (size, _, _) in enumerate(self.bolts[:rows], 0):
                size_str = self.format_number(size)
                c.drawString(offset_x - 40, offset_y - i * cell_height - cell_height / 2 - text_height,
                             f"{size_str}\"")
            for i, (size, lengths, items) in enumerate(self.bolts[:rows], 0):
                item_list = [item for item in ["Nut", "Flatwasher", "Lockwasher", "Locknut", "Blank"] if item in items]
                for j, item in enumerate(item_list[:self.max_items]):
                    if item != "Blank":
                        item_char = {"Nut": "N", "Flatwasher": "F", "Lockwasher": "L", "Locknut": "LN"}[item]
                        c.drawCentredString(offset_x + j * cell_width + cell_width / 2,
                                           offset_y - i * cell_height - cell_height / 2 - text_height, item_char)
                start_col = len(item_list)
                for j, length in enumerate(lengths[:self.max_lengths]):
                    length_str = self.format_number(length)
                    c.drawCentredString(offset_x + (j + start_col) * cell_width + cell_width / 2,
                                       offset_y - i * cell_height - cell_height / 2 - text_height, length_str)

            c.save()

        try:
            subprocess.run(["lp", file_path], check=True)
            messagebox.showinfo("Success", "PDF sent to printer.", parent=self.current_screen)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print PDF: {str(e)}", parent=self.current_screen)
        finally:
            try:
                os.unlink(file_path)
            except Exception:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = BoltBinApp(root)
    root.mainloop()
