from tkinter import filedialog
from tkinter import Frame
from tkinter import Label
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from nptdms import TdmsFile

#M. Zlobinski - Light TDMS viewer
#Version 1.00
#Version 1.10 - option to plot multiple lines on one plot
#Version 1.11 - improved looks

def fd_plot(filename,var1):
    activeChannel = channellist[listbox.curselection()[0]]
    activeGroup = grouplist[listbox.curselection()[0]]
    with TdmsFile.open(filename) as tdms_file:
        activeChannel = tdms_file[activeGroup][activeChannel]
        for chunk in activeChannel.data_chunks():
            channel_chunk_data = chunk[:]
    if (var1==0) and (ax.lines != None):
        for i in range(len(ax.lines)):
            ax.lines[0].remove()
    ax.plot(channel_chunk_data, label=activeChannel.name)
    ax.legend()
    canvas.draw()

def browse():
    filepathEntry.delete(0, tk.END)
    filepath = filedialog.askopenfilename()
    filepathEntry.insert(0, filepath)


def get_channels(filename):
    listbox.delete(0, tk.END)
    global channellist
    global grouplist
    channellist = []
    grouplist = []
    c = []
    index = []
    i = 0
    with TdmsFile.open(filename) as tdms_file:  # read file but do not load
        groups = tdms_file.groups()
        for group in groups:
            channels = group.channels()
            for channel in channels:
                index.append(i)
                channellist.append(channel.name)
                grouplist.append(group.name)
                c.append(channel.name)
                i += 1
                listbox.insert(i, channel.name)


def selectChannel(event):
    widget = event.widget
    selection = widget.curselection()
    picked = widget.get(selection[0])
    # print("Picked signal: " + picked)


# Main window settings
root = tk.Tk()
root.title('TDMS Easy Viewer')
root.geometry("1000x720")
root.resizable(False, False)

# define Frames
FileInputFrame = Frame(root, bg='silver', height=50, borderwidth=0, highlightthickness=0)
OptionsFrame = Frame(root, bg="whitesmoke", height=50, borderwidth=0, highlightthickness=0)
ChListFrame = Frame(root, bg='whitesmoke', borderwidth=0, highlightthickness=0)
PlotFrame = Frame(root, bg='white', borderwidth=0, highlightthickness=0)
FooterFrame = Frame(root, bg='grey', borderwidth=0, highlightthickness=0)
# Distribute
FileInputFrame.grid(row=0, column=0, sticky="ew", columnspan=2)
OptionsFrame.grid(row=1, column=0, sticky="ew", columnspan=2)
ChListFrame.grid(row=2, column=0, sticky="wns")
PlotFrame.grid(row=2, column=1, sticky="e")
FooterFrame.grid(row=3, column=0,columnspan=2, sticky="sew")


# define elements - file input frame
FileInputLabel = Label(FileInputFrame, text="File path:", bg="silver", fg="black")
browseButton = tk.Button(FileInputFrame, text="browse", padx=20, pady=2, command=browse)
filepathEntry = tk.Entry(FileInputFrame, width=130)
# distribute elements for file input frame
FileInputLabel.pack(side="left")
browseButton.pack(side="right", padx=40)
filepathEntry.pack(side="left", padx=10)

# define elements - options frame
OptionsLabel = Label(OptionsFrame, text="Plotting options:", bg="whitesmoke", fg="black")
var1 = tk.IntVar()
keep_graph_cb = tk.Checkbutton(OptionsFrame, text='Add Graph', variable=var1, onvalue=1, offvalue=0)

# distribute elements in options frame
OptionsLabel.pack(side="left")
keep_graph_cb.pack(side="left")

# define elements - channel list frame
c_var = tk.StringVar()
loadButton = tk.Button(ChListFrame, text="load channel list", height=2,
                       command=lambda: get_channels(filepathEntry.get()))
plotButton = tk.Button(ChListFrame, text="plot data", height=2, command=lambda: fd_plot(filepathEntry.get(),var1.get()))
listbox = tk.Listbox(ChListFrame, listvariable=c_var, selectmode='browse', width=30, height=35)
listbox.bind('<<ListboxSelect>>', selectChannel)
scrollbar = tk.Scrollbar(ChListFrame)

# distrubte elements in channel list frame
loadButton.grid(row=0, column=0, sticky="ew", columnspan=2)
scrollbar.grid(row=1, column=0, sticky="nesw")
listbox.grid(row=1, column=1, sticky="nesw")
plotButton.grid(row=2, column=0, columnspan=2, sticky="sew")
scrollbar.config(command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)

#bottom
FooterLabel = Label(FooterFrame, text="Version: 1.11", bg="grey", fg="black")
FooterLabel.pack(side="left")

# Predefine figure
fig = Figure(figsize=(8, 6), dpi=100)
ax = fig.subplots()
ax.set_ylabel("Channel signal value", color="darkslategrey", size=14)
ax.set_xlabel("Sample number", color="darkslategrey", size=14)
ax.grid(color="silver", linestyle="--")
ax.set_facecolor("whitesmoke")
canvas = FigureCanvasTkAgg(fig, master=PlotFrame)
canvas.get_tk_widget().pack(side="left")

root.mainloop()
