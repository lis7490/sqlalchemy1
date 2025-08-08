import tkinter as tk
from tkinter import messagebox
from math import acos, tan, cos

def calculate():
    try:
        Pp = float(entry1.get())
        Сos = float(entry2.get())
        result = round((Pp*1000)/((3**0.5)*380*Сos), 2)
        messagebox.showinfo("Результат", f"Ток: {result} А")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите числа, разделитель - точка!")

root = tk.Tk()
root.title("Ток")

tk.Label(root, text="Расчетная мощность, Рр, кВт:").pack()
entry1 = tk.Entry(root)
entry1.pack()

tk.Label(root, text="Косинус, сos:").pack()
entry2 = tk.Entry(root)
entry2.pack()

tk.Button(root, text="Вычислить ток", command=calculate).pack()

root.mainloop()