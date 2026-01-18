# main.py
# Entry point for the Investment Management System

from gui.interface import InvestmentGUI
import tkinter as tk

# create the main application window
if __name__ == "__main__":
    root = tk.Tk()
    app = InvestmentGUI(root)  # create instance of the GUI
    root.mainloop()            # start the Tkinter event loop
