import sys
import tkinter as tk
import mcpt
import subprocess
import mcpp_parser

overrided_namespace = ""

def compile():
    if overrided_namespace:
        mcpt.namespace = overrided_namespace
    result:list[str] = []
    parser = mcpp_parser.ParseTaskInfo()
    preparsed = raw.get(0., tk.END).splitlines()
    for i in range(len(preparsed)):
        result += [parser.parse_assignment(preparsed[i])]
    subprocess.run("clip", input="\n".join(result), text=True)

def setting():
    def apply_setting():
        global overrided_namespace
        overrided_namespace = override_namespace_entry.get()
        mcpt.is_raw_variable_name = do_optimize_variablename.get()

    setting = tk.Tk()
    setting.title("Setting")
    setting.geometry("400x300")
    
    tk.Label(setting, text="---Compatibility---").pack(anchor="nw", padx=10)
    tk.Label(setting, text="Override namespace (Default:MCPP.var)").pack(anchor="nw", padx=10)
    override_namespace_entry = tk.Entry(setting)
    override_namespace_entry.insert(0, overrided_namespace)
    override_namespace_entry.pack(anchor="nw", padx=10)

    do_optimize_variablename = tk.BooleanVar(root)
    variablename_optimization = tk.Checkbutton(setting, text="Don't optimize variable names", variable=do_optimize_variablename)
    do_optimize_variablename = mcpt.is_raw_variable_name
    variablename_optimization.pack(anchor="nw", padx=10)

    apply_button = tk.Button(setting, text="Apply Setting", command=apply_setting)
    apply_button.pack(side=tk.BOTTOM, pady=20)

    setting.mainloop()

root = tk.Tk()
root.title("Formula Parser")
root.geometry("550x420")
root.iconbitmap("C:\Projects\MC++\mcpp.ico")

tk.Label(root, text="2024/12/8 by Kinokov Shotaskovich\nFormula Parser").pack()
raw:tk.Text = tk.Text(root)
setting_button = tk.Button(root, text="Setting", command=setting)
compile_button = tk.Button(root, text="Compile and Copy", command=compile)

raw.pack(pady=10, padx=10)
compile_button.pack(pady=10, padx=10, side=tk.LEFT)
setting_button.pack(padx=2, side=tk.LEFT)

root.mainloop()