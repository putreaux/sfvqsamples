import hydra
import hydra.utils as utils
import os
import sys
import json
import tkinter as tk
import torchaudio
import math
import random
import re
from copy import copy
from hydra import utils
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sounddevice as sd

samples = open('codebooksamples.json')
samples_f = open('codebooksamples_f.json')
samples_m = open('codebooksamples_m.json')
metadata = open('speakerdata.json')

data = json.load(samples)
data_f = json.load(samples_f)
data_m = json.load(samples_m)
md = json.load(metadata)

distmatrix = np.load('distancesboth.npy')
distmatrixf = np.load('distancesf.npy')
distmatrixm = np.load('distancesm.npy')

current_samples = data

distmatrices = [distmatrix, distmatrixf, distmatrixm]
datasets = [data, data_f, data_m]

timit_path = sys.argv[1]


root = tk.Tk()
 
root.geometry("640x640")
root.title("Play speech samples from TIMIT")


def to_metric(h):
	feet_as_cm = 30.48
	inches_as_cm = 2.54
	feet_inches = re.findall(r'[\d]+', h)
	feet = int(feet_inches[0])
	inches = int(feet_inches[1])
	return str(round(feet * feet_as_cm + inches * inches_as_cm, 2)) + " cm"

def dialect_info(d):
	dialects = {'1': 'New England', '2': 'Northern', '3': 'North Midland', '4': 'South Midland',
	'5': 'Southern', '6': 'New York City', '7': 'Western', '8': 'Army Brat(moved around)'}
	return dialects[d]


def display_md(text, textfield, ind):
	textfield.delete(1.0, tk.END)
	textfield.insert(tk.END, "Codebook index: {},\n".format(ind))
	textfield.insert(tk.END, text)


def play_sound(index):
	try:
		sound_paths = current_samples[str(index)]
		ind = random.randint(0, len(sound_paths)-1)
		random_sound = sound_paths[ind]
	except KeyError:
		return "No sample at this codebook index."
	sound_path = random_sound.replace("/work/t405/T40571/sounds/", timit_path)
	signal, fs = torchaudio.load(sound_path)
	signal = signal.numpy().flatten()
	sd.play(signal, fs)
	fnind = sound_path.rindex('/')
	speaker_id = sound_path[fnind-4:fnind]
	attrs = (item for item in md if item["id"] == speaker_id)
	attrs = list(attrs)
	height = to_metric(attrs[0]['height'])
	dialect = dialect_info(attrs[0]['dialect'])
	attrs_final = copy(attrs[0])
	attrs_final['height'] = height
	attrs_final['dialect'] = dialect
	return str(attrs_final)
	

T = tk.Text(root, height = 5, width = 80)
T.insert(tk.END, "Click on the canvas above at any coordinate you like to play audio and get speaker metadata. Left mouse button plays a sample from x coordinate and right mouse button plays a sample from the y coordinate.")

def get_coords(event):
	txt = "X: " + play_sound(math.floor(event.x/2))
	display_md(txt, T, math.floor(event.x/2))

def play_correlated(event):
	txt = "Y: " + play_sound(math.floor((event.y)*(512/476)/2))
	display_md(txt, T, math.floor((event.y)*(512/476)/2))

def distance(x, y):
	dmatrix = distmatrices[datasets.index(current_samples)]
	try:
		d = "%.2f" % round(dmatrix[x][y], 2)
	except IndexError:
		d = np.nan
	return d
	
def mouse_pos(event):
	xc = math.floor(event.x/2)
	yc = math.floor((event.y)*(512/476)/2)
	w.itemconfigure(tag, text="Codebook index X: {}, Y: {}\nDistance between codebooks: {}".format(xc, yc, distance(xc, yc)))

def change_bg(image, samples):
	global current_samples, tag
	w.create_image(0, 0, image=image,
				 anchor="nw")
	tag = w.create_text(220, 10, text="Codebook index: X: , Y: \nDistance between codebooks:", anchor="nw", font="Arial 11 bold")
	current_samples = samples
	

w = tk.Canvas(root, width=512, height=476, bg='skyblue')

bg_both = tk.PhotoImage(file = "distscb.png")
bg_f = tk.PhotoImage(file = "distscb_f.png")
bg_m = tk.PhotoImage(file = "distscb_m.png")

w.create_image(0, 0, image=bg_both,
			   anchor="nw")

button1=tk.Button(root, text="Male", command=lambda: change_bg(bg_m, data_m))
button1.pack(side=tk.BOTTOM, fill="both", expand=False)
button2=tk.Button(root, text="Female", command=lambda: change_bg(bg_f, data_f))
button2.pack(side=tk.BOTTOM, fill="both", expand=False)
button3=tk.Button(root, text="Both", command=lambda: change_bg(bg_both, data))
button3.pack(side=tk.BOTTOM, fill="both", expand=False)

tag = w.create_text(220, 10, text="Codebook index: X: , Y: \nDistance between codebooks:", anchor="nw", font="Arial 11 bold")



w.bind('<Button-1>', get_coords)
w.bind('<Button-3>', play_correlated)
w.bind("<Motion>", mouse_pos)

w.pack()
T.pack()


	

root.mainloop()





	
	

	
