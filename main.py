from tkinter import filedialog
from tkinter import Frame
from tkinter import Label
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from nptdms import TdmsFile
import numpy as np


# M. Zlobinski - TDMS Easy Viewer
# Version 1.00
# Version 1.10 - option to plot multiple lines on one plot
# Version 1.11 - improved looks
# Version 1.20 - added custom x axis and statistical info
# Version 1.30 - added filtering capabilities
# Version 1.40 - added cursors and improved interface

def fd_plot(filename, clear_plot, xminval, xmaxval):
    ch_num = int(ch_indexEntry.get())
    active_channel = channellist[ch_num]
    active_group = grouplist[ch_num]
    curL = int(cursorL_Entry.get())
    curR = int(cursorR_Entry.get())
    if curL > curR or curL < 0: curL = 0
    if curR < 0: curR = 0
    if xminval > xmaxval: xminval = 0
    with TdmsFile.open(filename) as tdms_file:
        active_channel = tdms_file[active_group][active_channel]
        for chunk in active_channel.data_chunks():
            if xmaxval == 0:
                xmaxval = int(len(chunk))
            data = chunk[xminval:xmaxval]

    stat_info = f'min: {round(min(data), 3)} | max: {round(max(data), 3)} | avg: {round(np.average(data), 3)}'
    statistic_infoLabel.configure(text=stat_info)
    if (clear_plot == 0) and (ax.lines is not None):
        for i in range(len(ax.lines)):
            ax.lines[0].remove()

    ax.set_xlim([xminval, xmaxval])
    y_lim_min = min(data) - 0.2 * np.average(data)
    y_lim_max = max(data) + 0.2 * np.average(data)
    if y_lim_min == 0 and y_lim_max == 0:
        y_lim_min = -1
        y_lim_max = 1
    ax.set_ylim([y_lim_min, y_lim_max])
    if curL > xminval and curR < xmaxval:
        if curL != curR:
            curData = data[curL:curR]
            cur_min = round(min(curData), 3)
            cur_max = round(max(curData), 3)
            cur_avg = round(np.average(curData), 3)
            cur_stat_info = f'min: {cur_min} | max: {cur_max} | avg: {cur_avg}'
            cursor_infoLabel.configure(text=cur_stat_info)
            ax.vlines([curL, curR], y_lim_min, y_lim_max, color="grey", linestyle="dashed")
    ax.plot(data, label=active_channel.name)
    ax.legend()
    canvas.draw()


def browse():
    filepathEntry.delete(0, tk.END)
    filepath = filedialog.askopenfilename()
    filepathEntry.insert(0, filepath)
    filterEntry.insert(0, "<filter>")


def get_channels(filename):
    global channellist
    global grouplist
    listbox.delete(0, tk.END)
    channellist = []
    grouplist = []
    index = []
    i = 0
    filter = filterEntry.get()
    init_cond = False
    if np.size(filter) == 0: init_cond = True
    if filter == "<filter>": init_cond = True
    with TdmsFile.open(filename) as tdms_file:  # read file but do not load
        groups = tdms_file.groups()
        for group in groups:
            channels = group.channels()
            for channel in channels:
                if (init_cond == True) or (filter in channel.name):
                    index.append(i)
                    channellist.append(channel.name)
                    grouplist.append(group.name)
                    listbox.insert(i, channel.name)
                    i += 1


def select_channel(event):
    ch_indexEntry.delete(0, tk.END)
    # widget = event.widget
    # selection = widget.curselection()
    # picked = widget.get(selection[0]) get name
    ch_indexEntry.insert(0, listbox.curselection()[0])


def filter_applying(event):
    get_channels(filepathEntry.get())


# --------------------------GUI------------------------------------------------------------------------------------------
# Main window settings
root = tk.Tk()
root.title('TDMS Easy Viewer')
root.geometry("1125x720")
root.resizable(False, False)

# define Frames
FileInputFrame = Frame(root, bg='silver', height=50, borderwidth=0, highlightthickness=0)
OptionsFrame = Frame(root, bg="whitesmoke", height=50, borderwidth=0, highlightthickness=0)
ChListFrame = Frame(root, bg='whitesmoke', borderwidth=0, highlightthickness=0)
PlotFrame = Frame(root, bg='whitesmoke', borderwidth=0, highlightthickness=0)
FooterFrame = Frame(root, bg='grey', borderwidth=0, highlightthickness=0)
# Distribute Frames
FileInputFrame.grid(row=0, column=0, sticky="ew", columnspan=2)
OptionsFrame.grid(row=1, column=0, sticky="ew", columnspan=2)
ChListFrame.grid(row=2, column=0, sticky="wns")
PlotFrame.grid(row=2, column=1, sticky="ew")
FooterFrame.grid(row=3, column=0, columnspan=2, sticky="sew")

# define elements - file input frame
FileInputLabel = Label(FileInputFrame, text="File path:", bg="silver", fg="black")
browseButton = tk.Button(FileInputFrame, text="browse", padx=20, pady=2, command=browse)
filepathEntry = tk.Entry(FileInputFrame, width=150)
# distribute elements for file input frame
FileInputLabel.pack(side="left")
browseButton.pack(side="right", padx=30)
filepathEntry.pack(side="left", padx=10)

# define elements - options frame
optionsLabel = Label(OptionsFrame, text="Plotting options:", bg="whitesmoke", fg="black")
var1 = tk.IntVar()
keep_graph_cb = tk.Checkbutton(OptionsFrame, text='Add Graph', variable=var1, onvalue=1, offvalue=0)
statistic_infoLabel = Label(OptionsFrame, bg="whitesmoke", fg="blue")
optionsLabel2 = Label(OptionsFrame, text="  |  xscale  from:", bg="whitesmoke", fg="black")
xminEntry = tk.Entry(OptionsFrame, width=8)
xminEntry.insert(0, 0)

optionsLabel3 = Label(OptionsFrame, text="to: ", bg="whitesmoke", fg="black")
xmaxEntry = tk.Entry(OptionsFrame, width=8)
xmaxEntry.insert(0, 0)

optionsLabel4 = Label(OptionsFrame, text="  |   cursor:  left: ", bg="whitesmoke", fg="black")
cursorL_Entry = tk.Entry(OptionsFrame, width=8)
cursorL_Entry.insert(0, 0)

optionsLabel5 = Label(OptionsFrame, text=" right: ", bg="whitesmoke", fg="black")
cursorR_Entry = tk.Entry(OptionsFrame, width=8)
cursorR_Entry.insert(0, 0)
cursor_infoLabel = Label(OptionsFrame, bg="whitesmoke", fg="blue")

updButton = tk.Button(OptionsFrame, text="update", padx=2, pady=0, command=lambda: fd_plot(filepathEntry.get(),
                                                                                           var1.get(),
                                                                                           int(xminEntry.get()),
                                                                                           int(xmaxEntry.get())
                                                                                           )
                      )

# distribute elements in options frame
optionsLabel.pack(side="left")
keep_graph_cb.pack(side="left")
optionsLabel2.pack(side="left")
xminEntry.pack(side="left")
optionsLabel3.pack(side="left")
xmaxEntry.pack(side="left")
statistic_infoLabel.pack(side="left")
optionsLabel4.pack(side="left")
cursorL_Entry.pack(side="left")
optionsLabel5.pack(side="left")
cursorR_Entry.pack(side="left")
cursor_infoLabel.pack(side="left")
updButton.pack(side="left")
# define elements - channel list frame
c_var = tk.StringVar()
loadButton = tk.Button(ChListFrame, text="load channel list", height=2,
                       command=lambda: get_channels(filepathEntry.get()))
filterEntry = tk.Entry(ChListFrame)
plotButton = tk.Button(ChListFrame, text="plot data", height=2,
                       command=lambda: fd_plot(filepathEntry.get(),
                                               var1.get(),
                                               int(xminEntry.get()),
                                               int(xmaxEntry.get())
                                               )
                       )
listbox = tk.Listbox(ChListFrame, listvariable=c_var, selectmode='browse', width=30, height=34, exportselection=False)
ch_indexEntry = tk.Entry(ChListFrame)
listbox.bind("<<ListboxSelect>>", select_channel)
scrollbar = tk.Scrollbar(ChListFrame)

# distrubte elements in channel list frame
loadButton.grid(row=0, column=0, sticky="ew", columnspan=2)
filterEntry.grid(row=1, column=0, sticky="ew", columnspan=2)
scrollbar.grid(row=2, column=0, sticky="nesw")
listbox.grid(row=2, column=1, sticky="nesw")
plotButton.grid(row=3, column=0, columnspan=2, sticky="sew")
scrollbar.config(command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)
filterEntry.bind("<Key>", filter_applying)
# bottom
FooterLabel = Label(FooterFrame, text="Version: release 1.40", bg="grey", fg="black")
FooterLabel.pack(side="left")

# Predefine figure
fig = Figure(figsize=(8, 6), dpi=100)
ax = fig.subplots()
ax.set_ylabel("Channel signal value", color="darkslategrey", size=14)
ax.set_xlabel("Sample number", color="darkslategrey", size=14)
ax.grid(color="silver", linestyle="--")
ax.set_facecolor("whitesmoke")
canvas = FigureCanvasTkAgg(fig, master=PlotFrame)
canvas.get_tk_widget().pack(side="left", padx=0, pady=0)

root.mainloop()
