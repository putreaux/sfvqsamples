import hydra
import hydra.utils as utils
import os
import sys
import json
import tkinter as tk
import torchaudio
import torch
from hydra import utils
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sounddevice as sd

samples = open('codebooksamples.json')
metadata = open('speakerdata.json')


data = json.load(samples)
md = json.load(metadata)


timit_path = sys.argv[1]


root = tk.Tk()
 
root.geometry("500x400")
root.title("Play speech samples (one per each codebook index)")

def display_md(text, textfield, ind):
	textfield.delete(1.0, tk.END)
	textfield.insert(tk.END, "Codebook index: {},\n".format(ind))
	textfield.insert(tk.END, text)


def play_sound(index):
	try:
		sound_path = data[str(index)]
	except KeyError:
		return "No sample at this codebook index."
	sound_path = sound_path.replace("/work/t405/T40571/sounds/", timit_path)
	print(sound_path)
	signal, fs = torchaudio.load(sound_path)
	signal = signal.numpy().flatten()
	sd.play(signal, fs)
	fnind = sound_path.rindex('/')
	speaker_id = sound_path[fnind-4:fnind]
	attrs = (item for item in md if item["id"] == speaker_id)
	attrs = list(attrs)
	return attrs[0]
	

T = tk.Text(root, height = 5, width = 52)
T.insert(tk.END, "Click on the canvas above at any coordinate you like to play audio and get speaker metadata.")

def get_coords(event):
	txt = play_sound(event.x)
	display_md(txt, T, event.x)
	
def mouse_pos(event):
	w.itemconfigure(tag, text="Codebook index: %r" % event.x)
	

w = tk.Canvas(root, width=256, height=128, bg='skyblue')

tag = w.create_text(10, 10, text="Codebook index: ", anchor="nw")  

w.bind('<Button-1>', get_coords)
w.bind("<Motion>", mouse_pos)

w.pack()
T.pack()

root.mainloop()
