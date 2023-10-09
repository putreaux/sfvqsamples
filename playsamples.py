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

sound_ind_x = 0
sound_ind_y = 0

current_x = 0
current_y = 0

vary = True 

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


def display_md(text, textfield, ind, numsounds):
	index = 0
	textfield.delete(1.0, tk.END)
	if text[0] == "X":
		index = str(sound_ind_x+1)
	if text[0] == "Y":
		index = str(sound_ind_y+1)
	textfield.insert(tk.END, "Codebook index: {},\n".format(ind))
	textfield.insert(tk.END, text + ", sample {} / {}".format(index, numsounds))


def play_sound(index, sound_ind):
	try:
		sound_paths = current_samples[str(index)]
		s_ind = sound_ind % len(sound_paths)
		random_sound = sound_paths[s_ind]
		if button4["state"] == "disabled":
			button4["state"] = "normal"
			button5["state"] = "normal"
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
	return str(attrs_final), s_ind, len(sound_paths)
	

T = tk.Text(root, height = 5, width = 80)
T.insert(tk.END, "Click on the canvas above at any coordinate you like to choose indices (x, y) to compare. After this, use the 'Play Next Sample' buttons to play samples from the coordinates. If the 'Play Same Sample' checkmark is checked, the samples played on x and y will stay the same.")

def mouse_pos(event):
	xc = math.floor(event.x/2)
	yc = math.floor((event.y)*(512/476)/2)
	w.itemconfigure(tag, text="Codebook index X: {}, Y: {}\nDistance between codebooks: {}".format(xc, yc, distance(xc, yc)))
	return xc, yc

def get_coords(event):
	global sound_ind_x, sound_ind_y, current_x, current_y
	sound_ind_x = 0
	sound_ind_y = 0
	w.delete("marker")
	md, ind, n = play_sound(math.floor(event.x / 2), sound_ind_x)
	txt = "X: " + md
	display_md(txt, T, math.floor(event.x/2), n)
	w.create_oval(max(0,event.x-3), max(0,event.y-3), event.x+3, event.y+3, fill='black', stipple="gray50", tags="marker")
	xp, yp = mouse_pos(event)
	current_x = xp
	current_y = yp

def play_correlated(event):
	global sound_ind_x, sound_ind_y, current_x, current_y
	sound_ind_x = 0
	sound_ind_y = 0
	w.delete("marker")
	md, ind, n = play_sound(math.floor((event.y)*(512/476)/2), sound_ind_y)
	txt = "Y: " + md
	display_md(txt, T, math.floor((event.y)*(512/476)/2), n)
	w.create_oval(max(0, event.x - 3), max(0, event.y - 3), event.x + 3, event.y + 3, fill='black', stipple="gray50", tags="marker")
	xp, yp = mouse_pos(event)
	current_x = xp
	current_y = yp

def play_from_index(x, y, coord):
	global sound_ind_x, sound_ind_y
	print(sound_ind_x, sound_ind_y)
	if coord == "x":
		md, ind, n = play_sound(x, sound_ind_x)
		sound_ind_x = ind+int(vary)
		txt = "X: " + md
		display_md(txt, T, math.floor(x), n)
		print("x, " , sound_ind_x, sound_ind_y)
	if coord == "y":
		md2, ind2, n2 = play_sound(y, sound_ind_y)
		txt = "Y: " + md2
		sound_ind_y = ind2+int(vary)
		display_md(txt, T, math.floor(y), n2)
		print("y, ", sound_ind_x, sound_ind_y)
	w.itemconfigure(tag, text="Codebook index X: {}, Y: {}\nDistance between codebooks: {}".format(x, y, distance(x, y)))
	print("nyt??", sound_ind_x, sound_ind_y)


def distance(x, y):
	dmatrix = distmatrices[datasets.index(current_samples)]
	try:
		d = "%.2f" % round(dmatrix[x][y], 2)
	except IndexError:
		d = np.nan
	return d


def change_bg(image, samples):
	global current_samples, tag
	w.create_image(0, 0, image=image,
				 anchor="nw")
	tag = w.create_text(220, 10, text="Codebook index: X: , Y: \nDistance between codebooks:", anchor="nw", font="Arial 11 bold")
	button4["state"] = "disabled"
	button5["state"] = "disabled"
	current_samples = samples


var = tk.IntVar()

def toggle_freeze():
	global vary
	vary = 1-bool(var.get())
	
	

w = tk.Canvas(root, width=512, height=476, bg='skyblue')

bg_both = tk.PhotoImage(file = "distscb.png")
bg_f = tk.PhotoImage(file = "distscb_f.png")
bg_m = tk.PhotoImage(file = "distscb_m.png")

w.create_image(0, 0, image=bg_both,
			   anchor="nw")


w.bind('<Button-1>', get_coords)
w.bind('<Button-3>', play_correlated)
w.bind("<Motion>", mouse_pos)

w.pack()
T.pack()

buttonframe = tk.Frame(root)
buttonframe.pack(side=tk.BOTTOM, pady=10)

button1=tk.Button(buttonframe, bg="#7ad9e6", text="Male", command=lambda: change_bg(bg_m, data_m))
button1.pack(side=tk.LEFT)
button2=tk.Button(buttonframe, bg="#e89287", text="Female", command=lambda: change_bg(bg_f, data_f))
button2.pack(side=tk.LEFT)
button3=tk.Button(buttonframe, bg="#dcb0eb", text="Both", command=lambda: change_bg(bg_both, data))
button3.pack(side=tk.LEFT)

buttonframe2 = tk.Frame(root)
buttonframe2.pack(side=tk.BOTTOM)


button4=tk.Button(buttonframe2, text="Play Next Sample (x)", command=lambda: play_from_index(current_x, current_y, "x"))
button4.pack(side=tk.LEFT)
button4["state"] = "disabled"
button5=tk.Button(buttonframe2, text="Play Next Sample (y)", command=lambda: play_from_index(current_x, current_y, "y"))
button5.pack(side=tk.LEFT)
button5["state"] = "disabled"
check=tk.Checkbutton(buttonframe2, text="Play Same Samples", variable=var, onvalue=1, offvalue=0, command=toggle_freeze)
check.pack(side=tk.RIGHT)

tag = w.create_text(220, 10, text="Codebook index: X: , Y: \nDistance between codebooks:", anchor="nw", font="Arial 11 bold")







	

root.mainloop()





	
	

	
