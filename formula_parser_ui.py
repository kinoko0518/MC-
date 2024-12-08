import sys
import tkinter as tk
import subprocess
import mcpp_parser

def compile():
    result:list[str] = []
    parser = mcpp_parser.ParseTaskInfo()
    preparsed = raw.get(0., tk.END).splitlines()
    for i in range(len(preparsed)):
        result += [parser.parse_assignment(preparsed[i])]
    subprocess.run("clip", input="\n".join(result), text=True)

root = tk.Tk()
root.title("Formula Parser")
root.geometry("550x450")

tk.Label(root, text="2024/12/8 by Kinokov Shotaskovich\nFormula Parser").pack()
raw:tk.Text = tk.Text(root)
compile_button = tk.Button(root, text="Compile and Copy", command=compile)

raw.pack(pady=10, padx=10)
compile_button.pack(pady=10, padx=10)

root.mainloop()