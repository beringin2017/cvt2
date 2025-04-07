import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import sys



INSTAGRAM_IMG = None
GITHUB_IMG = None
total_converted_files = 0


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller .exe """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



def log_message(message):
    log_text.configure(state="normal")
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    log_text.configure(state="disabled")
    root.update_idletasks()

def convert_unicore_to_korepi(input_path, output_folder):
    global total_converted_files
    output_prefix = "rtg"
    try:
        with open(input_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        messagebox.showerror("JSON Error", f"Failed to parse JSON:\n{e}")
        return
    except Exception as e:
        messagebox.showerror("File Error", f"Error reading file:\n{e}")
        return

    if not isinstance(data, list):
        messagebox.showerror("Invalid Format", "Input JSON must be a list of coordinate dictionaries.")
        return

    if not os.path.isdir(output_folder):
        messagebox.showerror("Output Error", "Please select a valid output directory.")
        return

    log_message(f"Converting: {os.path.basename(input_path)}")
    count = 0
    for i, coord in enumerate(data):
        if all(k in coord for k in ("x", "y", "z")):
            korepi_data = {
                "name": f"{output_prefix}{i+1:03}",
                "position": [coord["x"], coord["y"], coord["z"]],
                "description": ""
            }
            filename = f"{output_prefix}{i+1:03}.json"
            filepath = os.path.join(output_folder, filename)
            try:
                with open(filepath, "w") as out_file:
                    json.dump(korepi_data, out_file, indent=4)
                count += 1
                total_converted_files += 1
            except Exception as e:
                log_message(f"[ERROR] Writing {filepath}: {e}")
        else:
            log_message(f"[SKIP] Entry {i+1} missing x/y/z")

    log_message(f"[DONE] {count} file(s) created from {os.path.basename(input_path)}\n")

def process_directory(root_dir):
    log_message(f"Starting bulk conversion from:\n{root_dir}\n")
    total_converted = 0
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".json"):
                full_path = os.path.join(dirpath, file)
                try:
                    with open(full_path, "r") as f:
                        data = json.load(f)
                    if isinstance(data, list) and all("x" in d and "y" in d and "z" in d for d in data):
                        convert_unicore_to_korepi(full_path, dirpath)
                        os.remove(full_path)
                        log_message(f"[DELETE] {file}")
                        total_converted += 1
                except Exception as e:
                    log_message(f"[ERROR] {file}: {e}")
    log_message(f"[COMPLETE] Total files converted: {total_converted}")
    log_message(f"[SUMMARY] Total waypoints: {total_converted_files}\n")


def select_input_file():
    filepath = filedialog.askopenfilename(
        title="Select unicore JSON File",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if filepath:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, filepath)

def select_output_folder():
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder)

def start_conversion():
    input_path = input_entry.get()
    output_folder = output_entry.get()
    if not input_path:
        messagebox.showerror("Error", "Please select an input JSON file.")
        return
    if not output_folder:
        messagebox.showerror("Error", "Please select an output folder.")
        return
    convert_unicore_to_korepi(input_path, output_folder)
    log_message(f"[SUMMARY] Total files converted overall: {total_converted_files}\n")


def browse_bulk_folder():
    folder = filedialog.askdirectory(title="Select Root Folder")
    if folder:
        bulk_entry.delete(0, tk.END)
        bulk_entry.insert(0, folder)

def start_bulk_conversion():
    folder = bulk_entry.get()
    if not folder:
        messagebox.showerror("Error", "Please select a folder.")
        return
    process_directory(folder)

def open_url(url):
    webbrowser.open_new(url)

def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("350x150")
    about_window.resizable(False, False)

    insta_frame = tk.Frame(about_window)
    insta_frame.pack(pady=10)

    global INSTAGRAM_IMG
    try:
        INSTAGRAM_IMG = tk.PhotoImage(file=resource_path("ig_icon.png"))
    except:
        INSTAGRAM_IMG = None

    insta_label = tk.Label(insta_frame, text=" elyanritonga", font=("Arial", 12), fg="blue", cursor="hand2")
    if INSTAGRAM_IMG:
        insta_label.config(image=INSTAGRAM_IMG, compound="left")
    insta_label.pack(side="left")
    insta_label.bind("<Button-1>", lambda e: open_url("https://www.instagram.com/elyanritonga/"))

    github_frame = tk.Frame(about_window)
    github_frame.pack(pady=10)

    global GITHUB_IMG
    try:
        GITHUB_IMG = tk.PhotoImage(file=resource_path("github_icon.png"))
    except:
        GITHUB_IMG = None

    github_label = tk.Label(github_frame, text=" beringin2017", font=("Arial", 12), fg="blue", cursor="hand2")
    if GITHUB_IMG:
        github_label.config(image=GITHUB_IMG, compound="left")
    github_label.pack(side="left")
    github_label.bind("<Button-1>", lambda e: open_url("https://github.com/beringin2017"))

# GUI Setup
root = tk.Tk()
root.title("Unicore ➜ Korepi JSON Converter")
root.geometry("700x500")

menu_bar = tk.Menu(root)
menu_bar.add_cascade(label="About", command=show_about)
root.config(menu=menu_bar)

# Input file selection
input_label = tk.Label(root, text="Unicore JSON File:")
input_label.pack(pady=(10, 0))
input_entry = tk.Entry(root, width=70)
input_entry.pack(pady=(0, 5))
input_btn = tk.Button(root, text="Browse Input File", command=select_input_file)
input_btn.pack(pady=(0, 10))

# Output folder selection
output_label = tk.Label(root, text="Output Folder:")
output_label.pack(pady=(10, 0))
output_entry = tk.Entry(root, width=70)
output_entry.pack(pady=(0, 5))
output_btn = tk.Button(root, text="Browse Output Folder", command=select_output_folder)
output_btn.pack(pady=(0, 10))

# Convert button
convert_btn = tk.Button(root, text="Convert", command=start_conversion, bg="#4CAF50", fg="white", width=20, height=2)
convert_btn.pack(pady=(10, 20))

# Bulk folder selection
bulk_label = tk.Label(root, text="Bulk Conversion: Root Folder with JSON Files (will delete the original file)")
bulk_label.pack(pady=(10, 0))
bulk_entry = tk.Entry(root, width=70)
bulk_entry.pack(pady=(0, 5))
bulk_btn_browse = tk.Button(root, text="Browse Bulk Folder", command=browse_bulk_folder)
bulk_btn_browse.pack(pady=(0, 5))
bulk_btn_convert = tk.Button(root, text="Convert All", command=start_bulk_conversion, bg="#f57c00", fg="white", width=20)
bulk_btn_convert.pack(pady=(5, 15))

# --- Progress Log Area ---
log_frame = tk.LabelFrame(root, text="Progress Log", padx=10, pady=5)
log_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

log_text = tk.Text(log_frame, height=8, wrap="word", state="disabled")
log_text.pack(side="left", fill="both", expand=True)

log_scroll = tk.Scrollbar(log_frame, command=log_text.yview)
log_scroll.pack(side="right", fill="y")
log_text.configure(yscrollcommand=log_scroll.set)

root.mainloop()
