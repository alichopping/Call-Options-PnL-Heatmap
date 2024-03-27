import sys
import pandas as pd
import tkinter
from tkinter import messagebox
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


datalist=[]
def enter_data():
    stocksymbol=stocksymbol_entry.get()
    expirydate=expiry_date_entry.get()
    contracts=contracts_entry.get()
    spacing=spacing_entry.get()
    datalist.append(stocksymbol)
    datalist.append(expirydate)
    datalist.append(contracts)
    datalist.append(spacing)
    return datalist

def expiry_dates():
    if len(yf.Ticker(stocksymbol_entry.get()).options)==0:
        messagebox.showinfo("Error", "No Expiry dates available for this ticker. Did you spell the ticker correctly?") 
    if str(expiry_date_entry.get()) not in list(yf.Ticker(stocksymbol_entry.get()).options):
         messagebox.showinfo("Error", f"Expiry not available. Did you enter the correct date format? Available dates: {yf.Ticker(stocksymbol_entry.get()).options}")
    if contracts_entry.get().isdigit() is not True:
         messagebox.showinfo("Error", "Number of contracts is not an integer") 
    if spacing_entry.get().isdigit() is not True:
         messagebox.showinfo("Error", "Tick spacing is not an integer") 
         
    if ((len(yf.Ticker(stocksymbol_entry.get()).options)!=0) and (str(expiry_date_entry.get()) in list(yf.Ticker(stocksymbol_entry.get()).options))
        and contracts_entry.get().isdigit() and spacing_entry.get().isdigit()):
        enter_data()
        window.destroy()

#Build the window & the frame within it
window=tkinter.Tk()
window.title("European Call Option Heatmap")

frame=tkinter.Frame(window)
frame.pack()

#Build a frame within the above "frame" for input
entry_frame=tkinter.LabelFrame(frame,text="Input")
entry_frame.grid(row= 0, column= 0, padx=20, pady=20)

#Populate the entry frame with widgets for the user to input data
stocksymbol_label=tkinter.Label(entry_frame, text="Stock Symbol (All Caps):")
stocksymbol_label.grid(row=0, column=0)

expiry_date_label=tkinter.Label(entry_frame, text="Expiry Date (YYYY-MM-DD):")
expiry_date_label.grid(row=0, column=1)

contracts_label=tkinter.Label(entry_frame, text="Number of Contracts (1 contract = 100 options):")
contracts_label.grid(row=2, column=0)

spacing_label=tkinter.Label(entry_frame, text="Plot tick spacing (Integer):")
spacing_label.grid(row=2, column=1)

stocksymbol_entry = tkinter.Entry(entry_frame)
expiry_date_entry = tkinter.Entry(entry_frame)
contracts_entry = tkinter.Entry(entry_frame)
spacing_entry = tkinter.Entry(entry_frame)

stocksymbol_entry.grid(row=1,column=0)
expiry_date_entry.grid(row=1,column=1)
contracts_entry.grid(row=3,column=0)
spacing_entry.grid(row=3,column=1)

#Button
button = tkinter.Button(frame, text="Generate Heatmap", command=lambda:[expiry_dates()])
button.grid(row=3, column=0, sticky="news", padx=20, pady=20)

for widget in entry_frame.winfo_children():
    widget.grid_configure(padx=10,pady=5)
    
window.mainloop()


#########HEATMAP START
symbol = datalist[0]
expiry = datalist[1]
contracts = datalist[2]
tickspacing = datalist[3]

# Get option chain for the user-provided stock symbol and expiry date
chain = yf.Ticker(symbol).option_chain(expiry)
# Filter option chain for puts and calls
puts = chain.puts.sort_values(by='lastPrice')
calls = chain.calls.sort_values(by='lastPrice')
puts.index=pd.to_datetime(puts["lastTradeDate"])
calls.index=pd.to_datetime(calls["lastTradeDate"])

#Download underlying data to give an indication of range of possible stock prices
#underlying=yf.Ticker(symbol)
#underlying=yf.Ticker(symbol)
#underlying=underlying.history(period="1y", auto_adjust=False)
#underlying=underlying.drop(columns=["Dividends", "Stock Splits", "Open", "High", "Low", "Volume", "Adj Close"])
#undermin=underlying.Close.tail(50).min()
#undermax=underlying.Close.tail(50).max()

#Take potential stock prices to be a range between the half the min, and the max+median
stockprice=np.arange(round(0.5*calls["strike"].min()), calls["strike"].max()+calls["strike"].median(), 5) 

#PnL for a call option is the price of the underlying, minus the strike price, minus the premium. Use the last price
#the option traded at as the option premium.
pnl=[]
for i in range(len(stockprice)):
    for j in range(len(calls)):
        pnl.append((stockprice[i]-calls["strike"][j]-calls["lastPrice"][j])*int(contracts)*100)

pnlgrid=np.array(pnl).reshape(len(stockprice),len(calls["strike"]))

# Create heatmap
plt.imshow(pnlgrid, cmap='YlOrRd_r', interpolation='nearest', extent=[stockprice.min(), stockprice.max(), calls["strike"].min(), calls["strike"].max()])
plt.colorbar(label='Profit & Loss (USD)')
plt.table(cellText=[[symbol, expiry, int(contracts)]],
                  colWidths = [1]*3,
                  colLabels=["Stock", "Expiry", "No. Contracts"],
                  loc='center',
                  bbox=[0.25, 1.2, 0.5, 0.2])

plt.xlabel('Underlying Price (USD)')
plt.ylabel('Strike Price (USD)')
plt.xticks(np.arange(stockprice.min(), stockprice.max(),int(tickspacing)))
plt.yticks(np.arange(calls["strike"].min(), calls["strike"].max(), int(tickspacing)))
plt.title(f"PnL Heatmap, {symbol}")
plt.show()

sys.exit()