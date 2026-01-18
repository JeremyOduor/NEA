import csv  # for simple CSV persistence

class Investment:
    def __init__(self, ticker, price, quantity, date, asset_type="Unknown"):
        self.ticker = ticker.upper()        # ticker
        self.price = float(price)           # store as float for math
        self.quantity = int(quantity)       # store as int 
        self.date = date                    # keep as string (YYYY-MM-DD)
        self.asset_type = asset_type        # NEW: store asset type (e.g. Stock, Crypto)

    def __str__(self):
        return f"{self.ticker} ({self.asset_type}): {self.quantity} shares at {self.price} each on {self.date}"  # UPDATED to show asset type


class Portfolio:
    def __init__(self):
        self.items = []                     # holds Investment objects

    def add_investment(self, ticker, price, quantity, date, asset_type="Unknown"):
        self._validate(ticker, price, quantity, date)  # raise if bad input
        inv = Investment(ticker, price, quantity, date, asset_type)  # UPDATED: pass asset_type
        self.items.append(inv)              # add to portfolio
        print(f"Investment added: {inv}")
        return inv

    def edit_investment(self, index, new_price=None, new_quantity=None, new_asset_type=None):
        self._validate_index(index)         # makes ensure index exists
        inv = self.items[index]
        if new_price is not None:
            inv.price = float(new_price)    # update price if provided
        if new_quantity is not None:
            inv.quantity = int(new_quantity)
        if new_asset_type is not None:       # NEW: allow updating asset type
            inv.asset_type = new_asset_type
        print(f"Investment updated: {inv}")
        return inv

    def delete_investment(self, index):
        self._validate_index(index)         # makes sure ensure index exists
        removed = self.items.pop(index)     # remove and return the object
        print(f"Deleted investment: {removed}")
        return removed

    def list_investments(self):
        if not self.items:                   # check if list is empty
            print("No investments found.")
            return
        print("\nCurrent Investments:")
        for idx, inv in enumerate(self.items):# loop through all Investment objects
            print(f"[{idx}] {inv}")           # print index + investment details

    #   persistence (CSV) 
    def save_csv(self, filename="data/investments.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ticker", "price", "quantity", "date", "asset_type"])  # UPDATED header
            for inv in self.items:
                writer.writerow([inv.ticker, inv.price, inv.quantity, inv.date, inv.asset_type])  # UPDATED row

    def load_csv(self, filename="data/investments.csv"):
        self.items.clear()                  # reset current list
        try:
            with open(filename, "r") as f:
                reader = csv.DictReader(f)  # read by column names
                for row in reader:
                    self.add_investment(    # reuse validation + creation
                        row["ticker"],
                        row["price"],
                        row["quantity"],
                        row["date"],
                        row.get("asset_type", "Unknown")  # NEW: safe fallback for old CSVs
                    )
        except FileNotFoundError:
            # ok to start empty if file doesn't exist yet
            pass

    #  helpers 
    def _validate_index(self, index):
        if index < 0 or index >= len(self.items):
            raise IndexError("Invalid investment index.")

    def _validate(self, ticker, price, quantity, date):
        if not ticker or not ticker.isalpha():      # letters only
            raise ValueError("Ticker must be letters only.")
        try:
            p = float(price)
            if p <= 0:
                raise ValueError("Price must be greater than 0.")
        except ValueError:
            raise ValueError("Price must be a number greater than 0.")
        try:
            q = int(quantity)
            if q <= 0:
                raise ValueError("Quantity must be greater than 0.")
        except ValueError:
            raise ValueError("Quantity must be an integer greater than 0.")
        if not date:
            raise ValueError("Date cannot be empty.")


# manual test 
if __name__ == "__main__":
    pf = Portfolio()
    pf.add_investment("AAPL", 150.0, 10, "2025-10-07", "Stock")   # UPDATED test
    pf.add_investment("TSLA", 250.0, 5, "2025-10-06", "Stock")   # UPDATED test
    pf.list_investments()
    pf.edit_investment(0, new_price=160.0)
    pf.list_investments()
    pf.delete_investment(1)
    pf.list_investments()

    # uncomment this
    pf.save_csv()
    pf2 = Portfolio(); pf2.load_csv(); pf2.list_investments()
