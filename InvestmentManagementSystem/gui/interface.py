# gui/interface.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import random
from logic.data_handler import Portfolio
from logic.algorithms import ema  # EMA algorithm
from logic.algorithms import z_score_normalisation
from logic.algorithms import recursive_min_max  # import recursive min/max

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

  
class InvestmentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Investment Management System")
        self.root.geometry("1200x700")

        # backend
        self.portfolio = Portfolio()
        self.portfolio.load_csv()  # load saved data if any

        # keep last plotted series for overlays
        self.last_dates = None      # cache dates from last simulation/plot
        self.last_prices = None     # cache prices from last simulation/plot

        # layout weights
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=3)
        self.root.rowconfigure(1, weight=2)

        #  LEFT: Investment Management 
        self.frame_investment = ttk.LabelFrame(self.root, text="Investment Management", padding=10)
        self.frame_investment.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        for c in range(4):
            self.frame_investment.columnconfigure(c, weight=1)
        self.frame_investment.rowconfigure(0, weight=1)

        columns = ("Ticker", "Quantity", "Price", "Date", "Value")
        self.tree = ttk.Treeview(self.frame_investment, columns=columns, show="headings", height=14)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.grid(row=0, column=0, columnspan=4, padx=5, pady=10, sticky="nsew")

        self.btn_add = ttk.Button(self.frame_investment, text="Add", width=12, command=self.focus_add_form)
        self.btn_add.grid(row=1, column=0, padx=5, pady=5)

        self.btn_edit = ttk.Button(self.frame_investment, text="Edit", width=12, command=self.open_edit_window)
        self.btn_edit.grid(row=1, column=1, padx=5, pady=5)

        self.btn_delete = ttk.Button(self.frame_investment, text="Delete", width=12, command=self.delete_selected)
        self.btn_delete.grid(row=1, column=2, padx=5, pady=5)

        self.btn_simulate = ttk.Button(self.frame_investment, text="Simulate Graph", width=12, command=self.simulate_and_plot)
        self.btn_simulate.grid(row=1, column=3, padx=5, pady=5)

        self.label_value = ttk.Label(self.frame_investment, text="Total Portfolio Value: £0.00")
        self.label_value.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        self.label_profit = ttk.Label(self.frame_investment, text="Total Portfolio Profit: £0.00")
        self.label_profit.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        #  Add Investment 
        self.frame_add = ttk.LabelFrame(self.root, text="Add Investment", padding=10)
        self.frame_add.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.frame_add.columnconfigure(1, weight=1)

        ttk.Label(self.frame_add, text="Ticker Symbol:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(self.frame_add, text="Asset Type:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Label(self.frame_add, text="Quantity:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Label(self.frame_add, text="Buy Price (£):").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Label(self.frame_add, text="Date (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", pady=5)

        # NEW: Asset Type dropdown
        self.asset_types = ["Stock", "ETF", "Crypto", "Bond", "Other"]
        self.combo_asset_type = ttk.Combobox(
             self.frame_add,
             values=self.asset_types,
             state="readonly",
             width=23
             )
        self.combo_asset_type.set("Stock")
        self.combo_asset_type.grid(row=1, column=1, pady=5, sticky="ew")

        self.entry_ticker = ttk.Entry(self.frame_add, width=25)
        self.entry_ticker.grid(row=0, column=1, pady=5, sticky="ew")
        self.entry_quantity = ttk.Entry(self.frame_add, width=25)
        self.entry_quantity.grid(row=2, column=1, pady=5, sticky="ew")
        self.entry_price = ttk.Entry(self.frame_add, width=25)
        self.entry_price.grid(row=3, column=1, pady=5, sticky="ew")
        self.entry_date = ttk.Entry(self.frame_add, width=25)
        self.entry_date.grid(row=4, column=1, pady=5, sticky="ew")

        self.btn_submit = ttk.Button(self.frame_add, text="Add Investment", command=self.add_investment)
        self.btn_submit.grid(row=5, column=0, columnspan=2, pady=10)

        # ========== BOTTOM: Performance (Matplotlib) ==========
        self.frame_graph = ttk.LabelFrame(self.root, text="Performance", padding=10)
        self.frame_graph.grid(row=1, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        self.frame_graph.columnconfigure(0, weight=1)
        self.frame_graph.rowconfigure(1, weight=1)

        # controls row (EMA input + buttons)
        ctrl = ttk.Frame(self.frame_graph)
        ctrl.grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(ctrl, text="EMA period:").grid(row=0, column=0, padx=(0, 6))
        self.entry_ema_period = ttk.Entry(ctrl, width=8)
        self.entry_ema_period.insert(0, "12")  # sensible default
        self.entry_ema_period.grid(row=0, column=1, padx=(0, 10))
        ttk.Button(ctrl, text="Overlay EMA", command=self.overlay_ema).grid(row=0, column=2, padx=5)
        ttk.Button(ctrl, text="Clear Plot", command=self.clear_plot).grid(row=0, column=3, padx=5)
        ttk.Button(ctrl, text="Normalise (Z-Score)", command=self.normalise_prices).grid(row=0, column=4, padx=5)  
        ttk.Button(ctrl, text="Find Min/Max (Recursive)", command=self.find_min_max_recursive).grid(row=0, column=5, padx=5)  # button to run recursive min/max


        # Matplotlib fig/canvas
        self.figure = Figure(figsize=(8, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Price (£)")
        self.ax.grid(True, alpha=0.3)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_graph)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

        # initial table/totals
        self.populate_from_portfolio()
        self.refresh_totals()

        # save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # table helpers 
    def populate_from_portfolio(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for inv in self.portfolio.items:
            value = inv.price * inv.quantity
            self.tree.insert("", "end", values=(inv.ticker, inv.quantity, inv.price, inv.date, f"{value:.2f}"))

    def refresh_totals(self):
        total_value = sum(inv.price * inv.quantity for inv in self.portfolio.items)
        self.label_value.config(text=f"Total Portfolio Value: £{total_value:.2f}")
        self.label_profit.config(text="Total Portfolio Profit: £0.00")  # stays 0 until current prices available

    def clear_form(self):
        self.entry_ticker.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)
        self.combo_asset_type.set("Stock")  # asset type


    def focus_add_form(self):
        self.entry_ticker.focus_set()

    # ---------- core actions ----------
    def add_investment(self):
        ticker = self.entry_ticker.get()
        asset_type = self.combo_asset_type.get()  #asser type 
        qty = self.entry_quantity.get()
        price = self.entry_price.get()
        date = self.entry_date.get()
        try:
            inv = self.portfolio.add_investment(ticker, price, qty, date)
            value = inv.price * inv.quantity
            self.tree.insert("", "end", values=(inv.ticker, inv.quantity, inv.price, inv.date, f"{value:.2f}"))
            self.clear_form()
            self.refresh_totals()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an investment to delete.")
            return
        index = self.tree.index(sel[0])
        self.portfolio.delete_investment(index)
        self.tree.delete(sel[0])
        self.refresh_totals()

    def open_edit_window(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an investment to edit.")
            return
        index = self.tree.index(sel[0])
        inv = self.portfolio.items[index]

        win = tk.Toplevel(self.root)
        win.title("Edit Investment")
        win.geometry("320x210")
        win.resizable(False, False)

        ttk.Label(win, text="Ticker:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        ttk.Label(win, text="Quantity:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        ttk.Label(win, text="Price (£):").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        ttk.Label(win, text="Date:").grid(row=3, column=0, sticky="w", padx=10, pady=8)

        e_ticker = ttk.Entry(win); e_ticker.grid(row=0, column=1, padx=10, pady=8); e_ticker.insert(0, inv.ticker)
        e_qty = ttk.Entry(win);    e_qty.grid(row=1, column=1, padx=10, pady=8);    e_qty.insert(0, str(inv.quantity))
        e_price = ttk.Entry(win);  e_price.grid(row=2, column=1, padx=10, pady=8);  e_price.insert(0, str(inv.price))
        e_date = ttk.Entry(win);   e_date.grid(row=3, column=1, padx=10, pady=8);   e_date.insert(0, inv.date)

        def save_changes():
            try:
                inv.ticker = e_ticker.get().upper()
                inv.date = e_date.get()
                self.portfolio.edit_investment(index, new_price=e_price.get(), new_quantity=e_qty.get())
                value = inv.price * inv.quantity
                self.tree.item(self.tree.get_children()[index],
                               values=(inv.ticker, inv.quantity, inv.price, inv.date, f"{value:.2f}"))
                self.refresh_totals()
                win.destroy()
            except (ValueError, IndexError) as e:
                messagebox.showerror("Edit Error", str(e))

        ttk.Button(win, text="Save", command=save_changes).grid(row=4, column=0, columnspan=2, pady=12)

    #  simulated series + plotting 
    def simulate_and_plot(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an investment to simulate.")
            return
        index = self.tree.index(sel[0])
        inv = self.portfolio.items[index]

        dates, prices = self.generate_price_series(start_price=inv.price, days=30, max_pct_change=2.0)
        self.last_dates, self.last_prices = dates, prices  # cache for overlays

        self.ax.clear()
        self.ax.plot(dates, prices, linewidth=2, label=f"{inv.ticker} (Simulated)")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Price (£)")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper left")
        self.figure.autofmt_xdate()
        self.canvas.draw()
    

    def generate_price_series(self, start_price, days=30, max_pct_change=2.0):
        base = datetime.today().date()
        dates = [base - timedelta(days=(days - 1 - i)) for i in range(days)]  # ascending dates
        prices = [float(start_price)]
        for _ in range(1, days):
            pct = random.uniform(-max_pct_change, max_pct_change)  # random daily change
            next_p = prices[-1] * (1 + pct / 100.0)
            prices.append(round(max(next_p, 0.01), 2))  # clamp to positive, 2dp
        return dates, prices

    def overlay_ema(self):
        if not self.last_prices or not self.last_dates:
            messagebox.showinfo("Info", "Simulate a series first, then overlay EMA.")
            return
        try:
            period = int(self.entry_ema_period.get())
            if period <= 0:
                raise ValueError("EMA period must be greater than 0.")
            ema_vals = ema(self.last_prices, period)
        except ValueError as e:
            messagebox.showerror("EMA Error", str(e))
            return

        self.ax.plot(self.last_dates, ema_vals, linewidth=2, label=f"EMA({period})")
        self.ax.legend(loc="upper left")
        self.canvas.draw()

    def normalise_prices(self):
        if not self.last_prices or not self.last_dates:
            messagebox.showwarning("Warning", "Simulate or plot a price series first.")
            return
        try:
            z_vals = z_score_normalisation(self.last_prices)
        except Exception as e:
            messagebox.showerror("Normalisation Error", str(e))
            return

        self.ax.clear()
        self.ax.plot(self.last_dates, z_vals, linewidth=2, label="Z-Score Normalised")
        self.ax.axhline(0, linestyle="--", linewidth=1)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Z-score")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper left")
        self.figure.autofmt_xdate()
        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Price (£)")
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()

    # NEW recursive min/max and mark results 
    def find_min_max_recursive(self):
        if not self.last_prices or not self.last_dates:
            messagebox.showwarning("Warning", "Please simulate prices first.")
            return

        try:
            min_val, max_val = recursive_min_max(self.last_prices)
            min_idx = self.last_prices.index(min_val)
            max_idx = self.last_prices.index(max_val)
            min_date = self.last_dates[min_idx]
            max_date = self.last_dates[max_idx]

            # mark min (red) and max (green) points on current plot
            self.ax.plot(min_date, min_val, "ro", label="Min (Recursive)")
            self.ax.plot(max_date, max_val, "go", label="Max (Recursive)")
            self.ax.legend(loc="upper left")
            self.canvas.draw()

            messagebox.showinfo(
                "Recursive Min/Max Found",
                f"Lowest Price: £{min_val:.2f} on {min_date}\n"
                f"Highest Price: £{max_val:.2f} on {max_date}"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
    # -- NEW --

    #  save on close 
    def on_close(self):
        try:
            self.portfolio.save_csv()
        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = InvestmentGUI(root)
    root.mainloop()
