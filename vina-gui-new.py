import tkinter as tk
from tkinter import filedialog
import os
import csv

# Function to run AutoDock Vina
def run_autodock_vina(vina_executable, receptor_pdbqt, ligand_pdbqt, output_dir, config):
    ligand_name = os.path.splitext(os.path.basename(ligand_pdbqt))[0]
    output_file = os.path.join(output_dir, f"{ligand_name}_result.pdbqt")
    log_file = os.path.join(output_dir, f"{ligand_name}_log.txt")
    
    command = f"{vina_executable} --receptor {receptor_pdbqt} --ligand {ligand_pdbqt} --out {output_file} --config {config} --log {log_file}"
    os.system(command)

# Function to select file for Vina executable
def select_vina_executable():
    vina_executable = filedialog.askopenfilename()
    vina_executable_entry.delete(0, tk.END)
    vina_executable_entry.insert(0, vina_executable)

# Function to select file for receptor PDBQT
def select_receptor_pdbqt():
    receptor_pdbqt = filedialog.askopenfilename()
    receptor_pdbqt_entry.delete(0, tk.END)
    receptor_pdbqt_entry.insert(0, receptor_pdbqt)

# Function to select file for ligand PDBQT or folder containing ligand files
def select_ligands():
    if file_var.get():
        ligand_path = filedialog.askopenfilename()
    else:
        ligand_path = filedialog.askdirectory()
    ligand_entry.delete(0, tk.END)
    ligand_entry.insert(0, ligand_path)

# Function to select file for configuration
def select_config():
    config_file = filedialog.askopenfilename()
    config_entry.delete(0, tk.END)
    config_entry.insert(0, config_file)

# Function to run AutoDock Vina for multiple ligands
def run_vina_for_multiple_ligands():
    vina_executable = vina_executable_entry.get()
    receptor_pdbqt = receptor_pdbqt_entry.get()
    config = config_entry.get()
    ligand_path = ligand_entry.get()
    output_dir = output_dir_entry.get()

    if os.path.isdir(ligand_path):
        ligands = [f for f in os.listdir(ligand_path) if f.endswith(".pdbqt")]
        ligands = [os.path.join(ligand_path, ligand) for ligand in ligands]
    elif os.path.isfile(ligand_path):
        ligands = [ligand_path]

    for ligand in ligands:
        run_autodock_vina(vina_executable, receptor_pdbqt, ligand, output_dir, config)

    generate_csv(output_dir)

# Function to generate CSV file
def generate_csv(output_dir):
    results = []
    for file in os.listdir(output_dir):
        if file.endswith("_log.txt"):
            with open(os.path.join(output_dir, file), "r") as f:
                for line in f:
                    if line.startswith("REMARK VINA RESULT:"):
                        docking_score, rmsd_lower, rmsd_mean = map(float, line.split()[3:])
                        results.append({"File": file[:-8], "Docking Score": docking_score,
                                        "RMSD Lower": rmsd_lower, "RMSD Mean": rmsd_mean})

    output_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if output_csv:
        with open(output_csv, "w", newline="") as csvfile:
            fieldnames = ["File", "Docking Score", "RMSD Lower", "RMSD Mean"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

# Create GUI
root = tk.Tk()
root.title("AutoDock Vina GUI")

# Labels and Entries
tk.Label(root, text="Vina Executable:").grid(row=0, column=0)
vina_executable_entry = tk.Entry(root)
vina_executable_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=select_vina_executable).grid(row=0, column=2)

tk.Label(root, text="Receptor PDBQT:").grid(row=1, column=0)
receptor_pdbqt_entry = tk.Entry(root)
receptor_pdbqt_entry.grid(row=1, column=1)
tk.Button(root, text="Browse", command=select_receptor_pdbqt).grid(row=1, column=2)

tk.Label(root, text="Config File:").grid(row=2, column=0)
config_entry = tk.Entry(root)
config_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=select_config).grid(row=2, column=2)

tk.Label(root, text="Select Ligands:").grid(row=3, column=0)
file_var = tk.BooleanVar(value=False)
file_check = tk.Checkbutton(root, text="Single File", variable=file_var)
file_check.grid(row=3, column=1)
ligand_entry = tk.Entry(root)
ligand_entry.grid(row=3, column=2)
tk.Button(root, text="Browse", command=select_ligands).grid(row=3, column=3)

tk.Label(root, text="Output Directory:").grid(row=4, column=0)
output_dir_entry = tk.Entry(root)
output_dir_entry.grid(row=4, column=1)

# Run Button
run_button = tk.Button(root, text="Run Vina for Ligands", command=run_vina_for_multiple_ligands)
run_button.grid(row=5, column=0, columnspan=2)

root.mainloop()
