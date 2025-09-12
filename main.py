import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load data
df = pd.read_csv('expenses.csv', parse_dates=['Date'])

# 2. Clean data (basic example)
df.dropna(subset=['Date', 'Category', 'Amount'], inplace=True)
df['Amount'] = df['Amount'].astype(float)

# 3. Basic analysis
print("Total expenses: $", df['Amount'].sum())
print("\nExpenses by category:")
print(df.groupby('Category')['Amount'].sum())

print("\nAverage daily expense: $", df.groupby('Date')['Amount'].sum().mean())

# 4. Visualization
df.groupby('Date')['Amount'].sum().plot(kind='line', marker='o', title='Daily Expenses')
plt.xlabel('Date')
plt.ylabel('Amount ($)')
plt.tight_layout()
plt.show()

df.groupby('Category')['Amount'].sum().plot(kind='pie', autopct='%1.1f%%', title='Expenses by Category')
plt.ylabel('')
plt.tight_layout()
plt.show()