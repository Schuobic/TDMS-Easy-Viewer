from tkinter import filedialog
from tkinter import Frame
from tkinter import Label
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from nptdms import TdmsFile


def fd_plot(filename):
    activeChannel = channellist[listbox.curselection()[0]]
    activeGroup = grouplist[listbox.curselection()[0]]

    with TdmsFile.open(filename) as tdms_file:
        activeChannel = tdms_file[activeGroup][activeChannel]
        for chunk in activeChannel.data_chunks():
            channel_chunk_data = chunk[:]

    # the figure that will contain the plot
    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.subplots()
    ax.hold(True)
    ax.set_facecolor("whitesmoke")
    ax.plot(channel_chunk_data, color='darkslategray')
    ax.set_title(("Signal: " + activeChannel.name), size=16, color="black")
    ax.set_ylabel("Channel signal value", color="darkslategrey", size=14)
    ax.set_xlabel("Sample number", color="darkslategrey", size=14)
    ax.grid(color="silver", linestyle="--")
    canvas = FigureCanvasTkAgg(fig, master=PlotFrame, )
    canvas.draw()
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().grid(row=3, column=0)


def browse():
    filepathEntry.delete(0, tk.END)
    filepath = filedialog.askopenfilename()
    filepathEntry.insert(0, filepath)


def get_channels(filename):
    listbox.delete(0,tk.END)
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


root = tk.Tk()
# Main window settings
root.title('TDMS Easy Viewer')
root.geometry("1000x650")
root.resizable(False, False)

FileInputFrame = Frame(root, bg='silver', width=1000, height=50, pady=3, bd=2)
FileInputFrame.grid(row=0, column=0, sticky="ew", columnspan=2)

ChListFrame = Frame(root, bg='white', width=200, height=600, pady=3, bd=2)
ChListFrame.grid(row=1, column=0, sticky="ns", rowspan=3)

PlotFrame = Frame(root, bg='white', width=800, height=600, pady=3, bd=2)
PlotFrame.grid(row=1, column=1, sticky="ew")

FileInputLabel = Label(FileInputFrame, text="File path:", bg="silver", fg="black")
FileInputLabel.pack(side="left")

browseButton = tk.Button(FileInputFrame, text="browse", padx=20, pady=2, command=browse)
browseButton.pack(side="right", padx=40)

filepathEntry = tk.Entry(FileInputFrame, width=130)
filepathEntry.pack(side="left", padx=10)

loadButton = tk.Button(ChListFrame, text="load channel list", padx=30, pady=5,
                       command=lambda: get_channels(filepathEntry.get()))
loadButton.grid(row=0, column=0, columnspan=2, sticky="ew")

c_var = tk.StringVar()
listbox = tk.Listbox(ChListFrame, listvariable=c_var, height=33, width=35, selectmode='browse')
listbox.bind('<<ListboxSelect>>', selectChannel)

scrollbar = tk.Scrollbar(ChListFrame)
scrollbar.grid(row=1, column=0, sticky="ns")
listbox.grid(row=1, column=1, sticky="ns")

listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

plotButton = tk.Button(ChListFrame, text="plot data", padx=30, pady=5, command=lambda: fd_plot(filepathEntry.get()))
plotButton.grid(row=2, column=0, columnspan=2, sticky="ew")

root.mainloop()
