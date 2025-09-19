
import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os

CSV_FILE = 'expenses.csv'

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Personal Expense Tracker')
        self.root.geometry('800x500')

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True)

        # --- Add Expense Tab ---
        add_tab = ttk.Frame(notebook)
        notebook.add(add_tab, text='Add Expense')
        tk.Label(add_tab, text='Date (YYYY-MM-DD):').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.date_entry = tk.Entry(add_tab)
        self.date_entry.insert(0, '2025-09-19')
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_tab, text='Category:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.category_var = tk.StringVar(add_tab)
        categories = ['Food', 'Transport', 'Groceries', 'Utilities', 'Entertainment']
        self.category_var.set(categories[0])
        self.category_menu = tk.OptionMenu(add_tab, self.category_var, *categories)
        self.category_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_tab, text='Amount:').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.amount_entry = tk.Entry(add_tab)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_tab, text='Description (optional):').grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.description_entry = tk.Entry(add_tab)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(add_tab, text='Add Expense', command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=15)

        # --- View Expenses Tab ---
        view_tab = ttk.Frame(notebook)
        notebook.add(view_tab, text='View Expenses')
        self.expense_tree = ttk.Treeview(view_tab, columns=('Date', 'Category', 'Amount', 'Description'), show='headings')
        for col in ('Date', 'Category', 'Amount', 'Description'):
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, width=120)
        self.expense_tree.pack(fill='both', expand=True, padx=10, pady=10)
        tk.Button(view_tab, text='Refresh', command=self.load_expenses_table).pack(pady=5)

        # --- Summary Tab ---
        summary_tab = ttk.Frame(notebook)
        notebook.add(summary_tab, text='Summary & Charts')
        tk.Button(summary_tab, text='Monthly/Yearly Summary', command=self.open_summary_viewer).pack(pady=10)
        tk.Button(summary_tab, text='View Monthly Chart', command=self.show_monthly_chart).pack(pady=2)
        tk.Button(summary_tab, text='View Yearly Chart', command=self.show_yearly_chart).pack(pady=2)
        tk.Button(summary_tab, text='View Category Pie Chart', command=self.show_category_pie_chart).pack(pady=2)

        # --- Budget Tab ---
        budget_tab = ttk.Frame(notebook)
        notebook.add(budget_tab, text='Budget Management')
        tk.Button(budget_tab, text='Manage Monthly Budget', command=self.open_budget_manager).pack(pady=20)

    def load_expenses_table(self):
        for row in self.expense_tree.get_children():
            self.expense_tree.delete(row)
        try:
            with open(CSV_FILE, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # skip header
                for row in reader:
                    self.expense_tree.insert('', 'end', values=row)
        except Exception:
            pass

    def get_current_month(self):
        import datetime
        return datetime.datetime.now().strftime('%Y-%m')

    def get_monthly_budget(self, month):
        try:
            with open('budget.csv', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if len(row) == 2 and row[0] == month:
                        return float(row[1])
        except FileNotFoundError:
            pass
        return None

    def set_monthly_budget(self, month, amount):
        budgets = {}
        try:
            with open('budget.csv', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if len(row) == 2:
                        budgets[row[0]] = row[1]
        except FileNotFoundError:
            pass
        budgets[month] = str(amount)
        with open('budget.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for m, a in budgets.items():
                writer.writerow([m, a])

    def get_monthly_expense(self, month=None):
        import pandas as pd
        if month is None:
            month = self.get_current_month()
        try:
            df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
            df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
            total = df[df['YearMonth'] == month]['Amount'].sum()
            return float(total)
        except Exception:
            return 0.0

    def open_budget_manager(self):
        bm_win = tk.Toplevel(self.root)
        bm_win.title('Monthly Budget Manager')
        bm_win.geometry('350x200')
        month = self.get_current_month()
        current_budget = self.get_monthly_budget(month)
        current_expense = self.get_monthly_expense(month)
        tk.Label(bm_win, text=f'Month: {month}').pack(pady=5)
        tk.Label(bm_win, text=f'Current Budget: {current_budget if current_budget is not None else "Not set"}').pack(pady=5)
        tk.Label(bm_win, text=f'Current Expense: {current_expense:.2f}').pack(pady=5)
        tk.Label(bm_win, text='Set New Budget:').pack(pady=5)
        budget_entry = tk.Entry(bm_win)
        budget_entry.pack(pady=5)
        def set_budget():
            try:
                amt = float(budget_entry.get())
                self.set_monthly_budget(month, amt)
                messagebox.showinfo('Success', f'Budget for {month} set to {amt}')
                bm_win.destroy()
            except ValueError:
                messagebox.showerror('Error', 'Please enter a valid number.')
        tk.Button(bm_win, text='Set Budget', command=set_budget).pack(pady=10)

    def show_monthly_chart(self):
        import pandas as pd
        import matplotlib.pyplot as plt
        try:
            df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
            df['YearMonth'] = df['Date'].dt.to_period('M')
            monthly = df.groupby('YearMonth')['Amount'].sum()
            monthly.plot(kind='bar', title='Monthly Expenses')
            plt.ylabel('Amount ($)')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror('Error', f'Could not display chart: {e}')

    def show_yearly_chart(self):
        import pandas as pd
        import matplotlib.pyplot as plt
        try:
            df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
            df['Year'] = df['Date'].dt.year
            yearly = df.groupby('Year')['Amount'].sum()
            yearly.plot(kind='bar', title='Yearly Expenses')
            plt.ylabel('Amount ($)')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror('Error', f'Could not display chart: {e}')

    def show_category_pie_chart(self):
        import pandas as pd
        import matplotlib.pyplot as plt
        try:
            df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
            category_totals = df.groupby('Category')['Amount'].sum()
            category_totals.plot(kind='pie', autopct='%1.1f%%', title='Expenses by Category')
            plt.ylabel('')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror('Error', f'Could not display chart: {e}')

    def open_summary_viewer(self):
        import pandas as pd
        import matplotlib.pyplot as plt
        summary = tk.Toplevel(self.root)
        summary.title('Monthly/Yearly Summary')
        summary.geometry('500x400')

        # Load data
        try:
            df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
        except Exception as e:
            tk.Label(summary, text=f'Error loading data: {e}').pack()
            return

        # Monthly summary
        df['YearMonth'] = df['Date'].dt.to_period('M')
        monthly = df.groupby('YearMonth')['Amount'].sum()
        tk.Label(summary, text='Monthly Totals:').pack()
        for ym, amt in monthly.items():
            tk.Label(summary, text=f'{ym}: ${amt:.2f}').pack()

        # Yearly summary
        df['Year'] = df['Date'].dt.year
        yearly = df.groupby('Year')['Amount'].sum()
        tk.Label(summary, text='\nYearly Totals:').pack()
        for y, amt in yearly.items():
            tk.Label(summary, text=f'{y}: ${amt:.2f}').pack()

        # Plot buttons
        def show_monthly_chart():
            monthly.plot(kind='bar', title='Monthly Expenses')
            plt.ylabel('Amount ($)')
            plt.tight_layout()
            plt.show()

        def show_yearly_chart():
            yearly.plot(kind='bar', title='Yearly Expenses')
            plt.ylabel('Amount ($)')
            plt.tight_layout()
            plt.show()

        tk.Button(summary, text='Show Monthly Chart', command=show_monthly_chart).pack(pady=5)
        tk.Button(summary, text='Show Yearly Chart', command=show_yearly_chart).pack(pady=5)

    def open_expense_viewer(self):
        viewer = tk.Toplevel(self.root)
        viewer.title('Expense Viewer & Filter')
        viewer.geometry('700x400')

        # Filter controls
        tk.Label(viewer, text='Date (YYYY-MM-DD):').grid(row=0, column=0, padx=5, pady=5)
        date_filter = tk.Entry(viewer)
        date_filter.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(viewer, text='Category:').grid(row=0, column=2, padx=5, pady=5)
        category_filter_var = tk.StringVar(viewer)
        categories = ['All', 'Food', 'Transport', 'Groceries', 'Utilities', 'Entertainment']
        category_filter_var.set(categories[0])
        category_filter_menu = tk.OptionMenu(viewer, category_filter_var, *categories)
        category_filter_menu.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(viewer, text='Min Amount:').grid(row=0, column=4, padx=5, pady=5)
        min_amount_filter = tk.Entry(viewer)
        min_amount_filter.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(viewer, text='Max Amount:').grid(row=0, column=6, padx=5, pady=5)
        max_amount_filter = tk.Entry(viewer)
        max_amount_filter.grid(row=0, column=7, padx=5, pady=5)

        # Table (Listbox)
        table = tk.Listbox(viewer, width=100)
        table.grid(row=1, column=0, columnspan=8, padx=5, pady=5)

        def load_expenses():
            table.delete(0, tk.END)
            with open(CSV_FILE, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                table.insert(tk.END, f'{header[0]:<15} {header[1]:<15} {header[2]:<10} {header[3]:<30}')
                for row in reader:
                    # Apply filters
                    if date_filter.get() and row[0] != date_filter.get():
                        continue
                    if category_filter_var.get() != 'All' and row[1] != category_filter_var.get():
                        continue
                    try:
                        amt = float(row[2])
                    except:
                        amt = 0
                    if min_amount_filter.get():
                        try:
                            if amt < float(min_amount_filter.get()):
                                continue
                        except:
                            pass
                    if max_amount_filter.get():
                        try:
                            if amt > float(max_amount_filter.get()):
                                continue
                        except:
                            pass
                    table.insert(tk.END, f'{row[0]:<15} {row[1]:<15} {row[2]:<10} {row[3]:<30}')

        # Load button
        tk.Button(viewer, text='Apply Filters', command=load_expenses).grid(row=2, column=0, columnspan=8, pady=5)
        load_expenses()

    def add_expense(self):
        date = self.date_entry.get().strip()
        category = self.category_var.get().strip()
        amount = self.amount_entry.get().strip()
        description = self.description_entry.get().strip()

        # Basic validation
        if not date or not category or not amount:
            messagebox.showerror('Error', 'Date, Category, and Amount are required!')
            return
        try:
            float(amount)
        except ValueError:
            messagebox.showerror('Error', 'Amount must be a number!')
            return

        # Append to CSV
        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.stat(CSV_FILE).st_size == 0:
                writer.writerow(['Date', 'Category', 'Amount', 'Description'])
            writer.writerow([date, category, amount, description])

        # Budget alert
        month = date[:7]
        budget = self.get_monthly_budget(month)
        if budget is not None:
            import pandas as pd
            try:
                df = pd.read_csv(CSV_FILE, parse_dates=['Date'])
                df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
                total = df[df['YearMonth'] == month]['Amount'].sum()
                if total >= budget:
                    messagebox.showwarning('Budget Alert', f'You have reached or exceeded your budget for {month}!')
                elif total >= 0.9 * budget:
                    messagebox.showinfo('Budget Alert', f'You are close to reaching your budget for {month}.')
            except Exception:
                pass

        messagebox.showinfo('Success', 'Expense added!')
        self.date_entry.delete(0, tk.END)
        self.category_var.set('Food')
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

# --- Authentication system ---
def login_window():
    login_root = tk.Tk()
    login_root.title('Login')
    login_root.geometry('300x220')

    tk.Label(login_root, text='Username:').pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack(pady=5)

    tk.Label(login_root, text='Password:').pack(pady=5)
    password_entry = tk.Entry(login_root, show='*')
    password_entry.pack(pady=5)

    def check_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        try:
            with open('users.csv', newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if len(row) == 2 and row[0] == username and row[1] == password:
                        login_root.destroy()
                        main_app_window()
                        return
            messagebox.showerror('Login Failed', 'Invalid username or password.')
        except FileNotFoundError:
            messagebox.showerror('Error', 'User database not found.')

    def open_register():
        reg_win = tk.Toplevel(login_root)
        reg_win.title('Register')
        reg_win.geometry('300x180')
        tk.Label(reg_win, text='New Username:').pack(pady=5)
        new_user_entry = tk.Entry(reg_win)
        new_user_entry.pack(pady=5)
        tk.Label(reg_win, text='New Password:').pack(pady=5)
        new_pass_entry = tk.Entry(reg_win, show='*')
        new_pass_entry.pack(pady=5)
        def register():
            new_user = new_user_entry.get().strip()
            new_pass = new_pass_entry.get().strip()
            if not new_user or not new_pass:
                messagebox.showerror('Error', 'Username and password required.')
                return
            # Check if user exists
            try:
                with open('users.csv', newline='', encoding='utf-8') as f:
                    for row in csv.reader(f):
                        if row and row[0] == new_user:
                            messagebox.showerror('Error', 'Username already exists.')
                            return
            except FileNotFoundError:
                pass
            with open('users.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([new_user, new_pass])
            messagebox.showinfo('Success', 'Registration complete!')
            reg_win.destroy()
        tk.Button(reg_win, text='Register', command=register).pack(pady=10)

    def open_change_password():
        cp_win = tk.Toplevel(login_root)
        cp_win.title('Change Password')
        cp_win.geometry('300x220')
        tk.Label(cp_win, text='Username:').pack(pady=5)
        cp_user_entry = tk.Entry(cp_win)
        cp_user_entry.pack(pady=5)
        tk.Label(cp_win, text='Old Password:').pack(pady=5)
        cp_old_pass_entry = tk.Entry(cp_win, show='*')
        cp_old_pass_entry.pack(pady=5)
        tk.Label(cp_win, text='New Password:').pack(pady=5)
        cp_new_pass_entry = tk.Entry(cp_win, show='*')
        cp_new_pass_entry.pack(pady=5)
        def change_password():
            user = cp_user_entry.get().strip()
            old_pass = cp_old_pass_entry.get().strip()
            new_pass = cp_new_pass_entry.get().strip()
            if not user or not old_pass or not new_pass:
                messagebox.showerror('Error', 'All fields required.')
                return
            try:
                with open('users.csv', newline='', encoding='utf-8') as f:
                    users = list(csv.reader(f))
            except FileNotFoundError:
                messagebox.showerror('Error', 'User database not found.')
                return
            found = False
            for i, row in enumerate(users):
                if len(row) == 2 and row[0] == user and row[1] == old_pass:
                    users[i][1] = new_pass
                    found = True
                    break
            if not found:
                messagebox.showerror('Error', 'Invalid username or password.')
                return
            with open('users.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(users)
            messagebox.showinfo('Success', 'Password changed!')
            cp_win.destroy()
        tk.Button(cp_win, text='Change Password', command=change_password).pack(pady=10)

    tk.Button(login_root, text='Login', command=check_login).pack(pady=10)
    tk.Button(login_root, text='Register', command=open_register).pack(pady=2)
    tk.Button(login_root, text='Change Password', command=open_change_password).pack(pady=2)
    login_root.mainloop()

def main_app_window():
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()

if __name__ == '__main__':
    login_window()
