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

# 6 and 4 bit samples, m and f, euclidean

samples_4bit_f = open('codebooksamples_4f.json')
samples_4bit_m = open('codebooksamples_4m.json')
samples_6bit_f = open('codebooksamples_6f.json')
samples_6bit_m = open('codebooksamples_6m.json')

# 6 and 4 bit samples, m and f, cosine

samples_4bit_f_c = open('codebooksamples_4fc.json')
samples_4bit_m_c = open('codebooksamples_4mc.json')
samples_6bit_f_c = open('codebooksamples_6fc.json')
samples_6bit_m_c = open('codebooksamples_6mc.json')
samples_8bit_f_c = open('codebooksamples_8fc.json')
samples_8bit_m_c = open('codebooksamples_8mc.json')

data = json.load(samples)
data_f = json.load(samples_f)
data_m = json.load(samples_m)
data_f4 = json.load(samples_4bit_f)
data_m4 = json.load(samples_4bit_m)
data_f6 = json.load(samples_6bit_f)
data_m6 = json.load(samples_6bit_m)
data_f4c = json.load(samples_4bit_f_c)
data_m4c = json.load(samples_4bit_m_c)
data_f6c = json.load(samples_6bit_f_c)
data_m6c = json.load(samples_6bit_m_c)
data_f8c = json.load(samples_8bit_f_c)
data_m8c = json.load(samples_8bit_m_c)
md = json.load(metadata)

distmatrix = np.load('distancesboth.npy')
distmatrixf = np.load('distancesf.npy')
distmatrixm = np.load('distancesm.npy')

distmatrixf6 = np.load('distancesf6.npy')
distmatrixm6 = np.load('distancesm6.npy')

distmatrixf4 = np.load('distancesf4.npy')
distmatrixm4 = np.load('distancesm4.npy')

distmatrixf8c = np.load('distancesf8c.npy')
distmatrixm8c = np.load('distancesm8c.npy')

distmatrixf6c = np.load('distancesf6c.npy')
distmatrixm6c = np.load('distancesm6c.npy')

distmatrixf4c = np.load('distancesf4c.npy')
distmatrixm4c = np.load('distancesm4c.npy')

current_samples = data
current_index = 0

current_factor = 1 # for correct indexing at lower bitrates

sound_ind_x = 0
sound_ind_y = 0

current_x = 0
current_y = 0

vary = True 

distmatrices = [distmatrix, distmatrixf, distmatrixm, distmatrixf6, distmatrixm6, distmatrixf4, distmatrixm4, distmatrixf6c, distmatrixm6c, distmatrixf4c, distmatrixm4c, distmatrixf8c, distmatrixm8c]
datasets = [data, data_f, data_m]

timit_path = sys.argv[1]


root = tk.Tk()
 
root.geometry("680x680")
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
		s_ind = sound_ind % (len(sound_paths))
		timit_ind = sound_paths[s_ind].index("timit/")
		random_sound = sound_paths[s_ind][timit_ind:]
		if button4["state"] == "disabled":
			button4["state"] = "normal"
			button5["state"] = "normal"
	except KeyError:
		return "No sample at this codebook index.", 0, 0
	sound_path = timit_path+random_sound
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
	return str(attrs_final), s_ind+int(vary), len(sound_paths)
	

T = tk.Text(root, height = 5, width = 80)
T.insert(tk.END, "Click on the canvas above at any coordinate you like to choose indices (x, y) to compare. After this, use the 'Play Next Sample' buttons to play samples from the coordinates. If the 'Play Same Sample' checkmark is checked, the samples played on x and y will stay the same.")

def mouse_pos(event):
	xc = math.floor(event.x/(2**current_factor))
	yc = math.floor((event.y)*(512/476)/(2**current_factor))
	w.itemconfigure(tag, text="Codebook index X: {}, Y: {}\nDistance between codebooks: {}".format(xc, yc, distance(xc, yc)))
	return xc, yc

def get_coords(event):
	global sound_ind_x, sound_ind_y, current_x, current_y
	sound_ind_x = 0
	sound_ind_y = 0
	w.delete("marker")
	event_ind = math.floor(event.x / (2**current_factor))
	md, ind, n = play_sound(event_ind, sound_ind_x)
	txt = "X: " + md
	display_md(txt, T, math.floor(event.x/(2**current_factor)), n)
	w.create_oval(max(0,event.x-3), max(0,event.y-3), event.x+3, event.y+3, fill='black', stipple="gray50", tags="marker")
	xp, yp = mouse_pos(event)
	current_x = xp
	current_y = yp

def play_correlated(event):
	global sound_ind_x, sound_ind_y, current_x, current_y
	sound_ind_x = 0
	sound_ind_y = 0
	w.delete("marker")
	md, ind, n = play_sound(math.floor((event.y)*(512/476)/(2**current_factor)), sound_ind_y)
	txt = "Y: " + md
	display_md(txt, T, math.floor((event.y)*(512/476)/(2**current_factor)), n)
	w.create_oval(max(0, event.x - 3), max(0, event.y - 3), event.x + 3, event.y + 3, fill='black', stipple="gray50", tags="marker")
	xp, yp = mouse_pos(event)
	current_x = xp
	current_y = yp

def play_from_index(x, y, coord):
	global sound_ind_x, sound_ind_y
	if coord == "x":
		md, ind, n = play_sound(x, sound_ind_x)
		sound_ind_x = ind
		txt = "X: " + md
		display_md(txt, T, math.floor(x), n)
	if coord == "y":
		md2, ind2, n2 = play_sound(y, sound_ind_y)
		txt = "Y: " + md2
		sound_ind_y = ind2
		display_md(txt, T, math.floor(y), n2)
	w.itemconfigure(tag, text="Codebook index X: {}, Y: {}\nDistance between codebooks: {}".format(x, y, distance(x, y)))

def distance(x, y):
	dmatrix = distmatrices[current_index]
	try:
		d = "%.3f" % round(dmatrix[x][y], 3)
	except IndexError:
		d = np.nan
	return d


def change_bg(image, samples, factor, index):
	global current_samples, tag, current_factor, current_index
	current_factor = factor
	current_index = index
	w.delete('all')
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

bg_f8c = tk.PhotoImage(file = "distscbf8c.png")
bg_m8c = tk.PhotoImage(file = "distscbm8c.png")

bg_f6 = tk.PhotoImage(file = "distscbf6.png")
bg_m6 = tk.PhotoImage(file = "distscbm6.png")

bg_f4 = tk.PhotoImage(file = "distscbf4.png")
bg_m4 = tk.PhotoImage(file = "distscbm4.png")

bg_f6c = tk.PhotoImage(file = "distscbf6c.png")
bg_m6c = tk.PhotoImage(file = "distscbm6c.png")

bg_f4c = tk.PhotoImage(file = "distscbf4c.png")
bg_m4c = tk.PhotoImage(file = "distscbm4c.png")

'''images = [bg_both, bg_f, bg_m, bg_f8c, bg_m8c, bg_f6, bg_m6, bg_f4, bg_m4, bg_f6c, bg_m6c, bg_f4c, bg_m4c]

for image in images:
	image = image.resize((512, 512))
'''
w.create_image(0, 0, image=bg_both,
			   anchor="nw")


w.bind('<Button-1>', get_coords)
w.bind('<Button-3>', play_correlated)
w.bind("<Motion>", mouse_pos)

w.pack()
T.pack()

buttonframe = tk.Frame(root)
buttonframe.pack(side=tk.BOTTOM, pady=2)


button3=tk.Button(buttonframe, bg="#dcb0eb", text="Both 8 bit euc", command=lambda: change_bg(bg_both, data, 1, 0))
button3.pack(side=tk.LEFT)

buttonframe1 = tk.Frame(root)
buttonframe1.pack(side=tk.BOTTOM, pady=2)

button11=tk.Button(buttonframe1, bg="#7ad9e6", text="Male 4 bit euc", command=lambda: change_bg(bg_m4, data_m4, 5, 6))
button11.pack(side=tk.LEFT)
button12=tk.Button(buttonframe1, bg="#7ad9e6", text="Male 6 bit euc", command=lambda: change_bg(bg_m6, data_m6, 3, 4))
button12.pack(side=tk.LEFT)
button1=tk.Button(buttonframe1, bg="#7ad9e6", text="Male 8 bit euc", command=lambda: change_bg(bg_m, data_m, 1, 2))
button1.pack(side=tk.LEFT)
button21=tk.Button(buttonframe1, bg="#e89287", text="Female 4 bit euc", command=lambda: change_bg(bg_f4, data_f4, 5, 5))
button21.pack(side=tk.LEFT)
button22=tk.Button(buttonframe1, bg="#e89287", text="Female 6 bit euc", command=lambda: change_bg(bg_f6, data_f6, 3, 3))
button22.pack(side=tk.LEFT)
button2=tk.Button(buttonframe1, bg="#e89287", text="Female 8 bit euc", command=lambda: change_bg(bg_f, data_f, 1, 1))
button2.pack(side=tk.LEFT)

buttonframe11 = tk.Frame(root)
buttonframe11.pack(side=tk.BOTTOM, pady=2)

button31=tk.Button(buttonframe11, bg="#7ad9e6", text="Male 4 bit cos", command=lambda: change_bg(bg_m4c, data_m4c, 5, 10))
button31.pack(side=tk.LEFT)
button32=tk.Button(buttonframe11, bg="#7ad9e6", text="Male 6 bit cos", command=lambda: change_bg(bg_m6c, data_m6c, 3, 8))
button32.pack(side=tk.LEFT)
button51=tk.Button(buttonframe11, bg="#7ad9e6", text="Male 8 bit cos", command=lambda: change_bg(bg_m8c, data_m8c, 1, 12))
button51.pack(side=tk.LEFT)
button41=tk.Button(buttonframe11, bg="#e89287", text="Female 4 bit cos", command=lambda: change_bg(bg_f4c, data_f4c, 5, 9))
button41.pack(side=tk.LEFT)
button42=tk.Button(buttonframe11, bg="#e89287", text="Female 6 bit cos", command=lambda: change_bg(bg_f6c, data_f6c, 3, 7))
button42.pack(side=tk.LEFT)
button52=tk.Button(buttonframe11, bg="#e89287", text="Female 8 bit cos", command=lambda: change_bg(bg_f8c, data_f8c, 1, 11))
button52.pack(side=tk.LEFT)

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





# 8 bit male & female euc, 8 bit male & female cos etöisyydet bugaa.

	

root.mainloop()





	
	

	
