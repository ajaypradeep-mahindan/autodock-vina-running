import os
import re
import csv
import tkinter as tk
from tkinter import filedialog

def parse_pdbqt_files(pdbqt_dir):
    results = []
    for pdbqt_file in os.listdir(pdbqt_dir):
        if pdbqt_file.endswith(".pdbqt"):
            with open(os.path.join(pdbqt_dir, pdbqt_file), "r") as f:
                current_model = None
                for line in f:
                    if line.startswith("MODEL"):
                        current_model = int(line.split()[1])
                    elif current_model is not None and line.startswith("REMARK VINA RESULT:"):
                        match = re.match(r"REMARK VINA RESULT:\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)", line)
                        if match:
                            docking_score = float(match.group(1))
                            rmsd_lower = float(match.group(2))
                            rmsd_mean = float(match.group(3))
                            results.append({"File": pdbqt_file, "Model": current_model,
                                            "Docking Score": docking_score,
                                            "RMSD Lower": rmsd_lower,
                                            "RMSD Mean": rmsd_mean})
    return results

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_var.set(folder_selected)
        process_button.config(state="normal")

def process_folder():
    pdbqt_dir = folder_path_var.get()
    output_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if output_csv:
        results = parse_pdbqt_files(pdbqt_dir)
        write_results_to_csv(results, output_csv)
        tk.messagebox.showinfo("Success", "Results saved to CSV file!")

def write_results_to_csv(results, output_csv):
    with open(output_csv, "w", newline="") as csvfile:
        fieldnames = ["File", "Model", "Docking Score", "RMSD Lower", "RMSD Mean"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({"File": result["File"],
                             "Model": result["Model"],
                             "Docking Score": result["Docking Score"],
                             "RMSD Lower": result["RMSD Lower"],
                             "RMSD Mean": result["RMSD Mean"]})

# GUI setup
root = tk.Tk()
root.title("PDBQT Parser")

folder_path_var = tk.StringVar()

folder_label = tk.Label(root, text="Select Folder containing PDBQT files:")
folder_label.pack()

folder_entry = tk.Entry(root, textvariable=folder_path_var, width=50)
folder_entry.pack()

browse_button = tk.Button(root, text="Browse", command=browse_folder)
browse_button.pack()

process_button = tk.Button(root, text="Process Folder", command=process_folder, state="disabled")
process_button.pack()

root.mainloop()
