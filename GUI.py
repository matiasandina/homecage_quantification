import tkinter
from tkinter import messagebox as tkMessageBox
import os
import pandas as pd
import numpy as np
import tkinter.ttk as ttk
import datetime
import multiprocessing as mp
#import main
import trigger_thermal
import preview_camera

class App():
	def __init__(self, window, window_title):
		self.window = window
		self.window.title(window_title)
		self.bg_color = "#FFC284"
		self.window.configure(bg=self.bg_color)
		self.button_color = "#FF8758"

		# menu left -------
		self.menu_left = tkinter.Frame(self.window, width=80, bg=self.bg_color)
		self.menu_left_upper = tkinter.Frame(self.menu_left, width=80, height=80, bg=self.bg_color)
		self.menu_left_lower = tkinter.Frame(self.menu_left, width=80, bg=self.bg_color)

		self.menu_left_title = tkinter.Label(self.menu_left_upper,
		 text="Experiment Setup",
		 font=("Helvetica", 16), bg=self.bg_color)
		self.menu_left_title.grid(row=0,column=0)

		self.menu_left_upper.pack(side="top", fill="both", expand=True)
		self.menu_left_lower.pack(side="top", fill="both", expand=True)


		self.animal_id = tkinter.Label(self.menu_left_upper,
		 text="Animal ID:", pady=5, bg=self.bg_color, width=10)
		self.id_entry = tkinter.Entry(self.menu_left_upper, width=20)
		self.treatment_label = tkinter.Label(self.menu_left_upper,
		 text="Treatment:", pady=5, bg=self.bg_color, width=10)
		self.treatment_entry = tkinter.Entry(self.menu_left_upper, width=20)
		self.dose_label = tkinter.Label(self.menu_left_upper,
		 text="Dose:", pady=5, bg=self.bg_color, width=10)
		self.dose_entry = tkinter.Entry(self.menu_left_upper, width=20)
		self.comment_label = tkinter.Label(self.menu_left_upper,
		 text="Comment:", pady=5, bg=self.bg_color, width=10)
		self.comment_entry = tkinter.Entry(self.menu_left_upper, width=20)


		# make the grid of entries
		self.animal_id.grid(row=1, column=0,sticky="ne")
		self.treatment_label.grid(row=2,column=0,sticky="ne")
		self.dose_label.grid(row=3, column=0, sticky="ne")
		self.comment_label.grid(row=4,column=0,padx=1, sticky="ne")
		self.id_entry.grid(row=1,column=1, sticky='ew',padx=1)
		self.treatment_entry.grid(row=2,column=1, sticky='ew',padx=1)
		self.dose_entry.grid(row=3,column=1, sticky='ew',padx=1)
		self.comment_entry.grid(row=4,column=1, sticky='ew',padx=1)

		# insert and delete stuff -------
		self.insert_button = tkinter.Button(self.menu_left_upper, text="Insert",
		                                    command=self.insert_data,
		                                    width=4, bg=self.button_color,
		                                    highlightbackground="black")
		self.delete_button = tkinter.Button(self.menu_left_upper, text='Delete',
                                       command=self.delete_entry,
                                       state=tkinter.DISABLED,
                                       width=4, bg=self.button_color,
                                       highlightbackground="black")
		# make an empty label for space
		self.spacer_label = tkinter.Label(self.menu_left_upper,
		 text="", pady=5, bg=self.bg_color, width=2)
		self.spacer_label.grid(row=0,column=2, pady=5)
		self.insert_button.grid(row=4,column=3, pady=5)
		self.delete_button.grid(row=4,column=4, sticky='nsew', pady=5)

		# right area ----------
		self.frame = tkinter.Frame(self.window, bg=self.bg_color)

		self.menu_right_title = tkinter.Label(self.frame,
		 text="Experiment Control", bg=self.bg_color, font=("Helvetica", 16))
		self.menu_right_title.pack()

		#self.canvas_area = tkinter.Canvas(self.window, width=500, height=400, background="#ffffff")
		#self.canvas_area.grid(row=1, column=1)



		#self.frame = tkinter.Frame(window, bg="#FFC284")
		#self.frame.pack(pady=15)
		# start thermal
		self.thermal_button = tkinter.Button(self.frame,
		 text="Start Thermal",
		 command=self.start_thermal,
		 pady=20, bg=self.button_color, highlightbackground="black")
		self.thermal_button.pack(pady=5)

		# preview camera button
		self.cam_button = tkinter.Button(self.frame,
		 text="Preview Camera",
		 command=self.preview_camera,
		 pady=20, bg=self.button_color, highlightbackground="black")
		self.cam_button.pack(pady=5)

		# start experiment
		self.exp_button = tkinter.Button(self.frame,
		 text="Start Experiment",
		 command=self.start_experiment,
		 state=tkinter.DISABLED,
		 pady=20, bg=self.button_color, highlightbackground="black")
		self.exp_button.pack(pady=5)
		self.exp_button.pack(pady=5)

		# stop experiment
		self.stop_exp_button = tkinter.Button(self.frame,
		 text="Stop Experiment",
		 command=self.stop_experiment,
		 state=tkinter.DISABLED,
		 pady=20, bg=self.button_color, highlightbackground="black")
		self.stop_exp_button.pack(pady=5)

		# on closing, ask before closing
		self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
		# Define the different GUI widgets

		# Set the treeview
		self.treeview_columns = ['mac', 'date', 'ID', 'Treatment', 'Dose', 'Comment']
		self.tree = ttk.Treeview(self.menu_left_lower,
		                         columns=self.treeview_columns,
		                         height=3)
		self.tree.heading('mac', text='mac', anchor=tkinter.W)
		self.tree.heading('date', text="date", anchor=tkinter.W)
		self.tree.heading("ID", text="ID", anchor=tkinter.W)
		self.tree.heading('Treatment', text='Treatment', anchor=tkinter.W)
		self.tree.heading('Dose', text='Dose', anchor=tkinter.W)
		self.tree.heading('Comment', text='Comment', anchor=tkinter.W)
		self.tree.column('mac', stretch=tkinter.NO, width=120)
		self.tree.column('date', stretch=tkinter.NO, width=200)
		self.tree.column('ID', stretch=tkinter.NO, width=60)
		self.tree.column('Treatment', stretch=tkinter.NO, width=120)
		self.tree.column('Dose', stretch=tkinter.NO, width=60)
		self.tree.column('Comment', stretch=tkinter.NO, width=100)
		# only show headings, this removes nasty first empty column
		self.tree['show'] = 'headings'
		# position on grid
		self.tree.grid(row=1, columns=1, sticky='nsew')
		# scroll bar
		self.vsb = ttk.Scrollbar(self.menu_left_lower,
		 orient="vertical", command=self.tree.yview)
		self.vsb.grid(row=1,column=4, sticky="EW")
		self.tree.configure(yscrollcommand=self.vsb.set)

		self.treeview = self.tree



		self.menu_left.grid(row=0, column=0, sticky="nsew")
		self.frame.grid(row=0, column=1, sticky="nsew")
		#self.canvas_area.grid(row=1, column=1, sticky="nsew") 
		#self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

		# this gives priority to entry boxes
		# because of this, they will resize and fill space with the menu_left_upper
		self.menu_left_upper.grid_columnconfigure(1, weight=1)
		# Processes for controlling other code (thermal, preview, main)
		# to run a process, use process.start()
		# to end a process peacefully, use process.join(), this will wait for it to be done
		# to end a process immediately (for infinite loops), use process.terminate(), gives it a SIGTERM signal which you can use to close the loop peacefully,
		#   see https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully for example
		self.thermal_process = mp.Process(target=trigger_thermal.run, args=())
		self.preview_camera_process = mp.Process(target=preview_camera.run, args=())
		self.main_process = mp.Process(target=main.run, args=())

	def get_mac(self):
		# This is good for Raspberry PIs, not good for other OS !
		# possible interfaces ['wlan0', 'eth0']
		#try:
		path_to_mac = '/sys/class/net/'+ 'wlan0' +'/address'
		mac = open(path_to_mac).readline()
		mac = mac.replace("\n", "")
		#except:
		#	try:
				# interface wlp2s0 for debugging outside of Pi
		#		mac=open('/sys/class/net/wlp2s0/address').readline()
		#	except:
		#		mac = "00:00:00:00:00:00"
		# mac = mac[0:17]
		return mac


	def insert_data(self):
		"""
		Insertion method.
		"""
		self.treeview.insert('', 'end',
		                     values=(
		                     	self.get_mac(),
		                     	datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
		                     	self.id_entry.get(),
		                     	self.treatment_entry.get(),
		                        self.dose_entry.get(),
		                        self.comment_entry.get()))
		# enable button to delete
		self.delete_button.configure(state=tkinter.NORMAL)

	def delete_entry(self):
		selected_items = self.treeview.selection()        
		for selected_item in selected_items:          
			self.treeview.delete(selected_item)

	# button callbacks ------
	def start_thermal(self):
		#os.system("python3 /home/pi/homecage_quantification/start_thermal.py")
		self.stop_exp_button.config(state="normal")
		self.thermal_process.start()

	def preview_camera(self):
		#os.system("python3 /home/pi/homecage_quantification/preview_camera.py")
		self.preview_camera_process.start()
		# only now we enable the experiment button
		self.exp_button.config(state="normal") 
		# we have to restart the process after it gets terminated by user
		self.preview_camera_process = mp.Process(target=preview_camera.run, args=())

	def start_experiment(self):
		all_set = self.check_input()
		if all_set:
			self.save_data()
			#os.system("python3 /home/pi/homecage_quantification/main.py")
			self.main_process.start()
		else:
			tkinter.messagebox.showinfo("Config File Missing",
			 "Please make sure you have entered at least animal ID.\nDelete entries with empty values and begin again.")

	def stop_experiment(self):
		# delete entries
		self.treeview.delete(*self.treeview.get_children())
		print("Stop thermal camera in process")
		self.thermal_process.terminate()
		# initiate new one
		self.thermal_process = mp.Process(target=trigger_thermal.run, args=())
		print("Thremal camera stopped. Ready to start again.") 
		print("Stop optic flow in process")
		self.main_process.terminate()
		self.main_process = mp.Process(target=main.run, args=())
		print("Optic flow stopped. Ready to start again :)")

	def check_input(self):
		# this function checks whether we have a correct config file
		print("checking config file")
		children = self.treeview.get_children()
		if len(children) > 0:
			# make a data frame
			values = pd.DataFrame(None, 
					columns=self.treeview_columns)
			for row in children:
				values = values.append(pd.DataFrame([self.treeview.item(row)["values"]], 
					columns=self.treeview_columns))
			# non completed values will be ""
			print(values)
			if any(values["ID"] == ""):
				return False
			else:
				return True
		else:
			return False

	def on_closing(self):
		if tkMessageBox.askyesno("Quit", "Do you want to quit?"):
			self.window.destroy()

	def save_data(self):
		# initialize empty df
		# if too big you can preallocate but probably not needed
		treeview_df = pd.DataFrame(None,
		columns=self.treeview_columns)
		
		for row in self.treeview.get_children():
			# each row will come as a list under name "values"
			values = pd.DataFrame([self.treeview.item(row)["values"]], 
				columns=self.treeview_columns)
			# print(values)
			treeview_df = treeview_df.append(values)

		# just take the first name and the first mouse ID 
		first_date = treeview_df["date"][0]
		first_id = treeview_df["ID"][0]
		#print(first_date, first_id)
		filename = f'{first_date}_{first_id}_config.csv'
		#print(filename)
		treeview_df.to_csv(filename, index=False)
		print("Config file saved")



def create_app(root):
	App(window = root, window_title = "Experiment GUI")

if __name__ == '__main__':
	# hard-coded current directory
	os.chdir("/home/pi/homecage_quantification")
	root = tkinter.Tk()
	# widthxheight+300+300 pxposition from the leftcorner of the monitor
	root.geometry("800x350+300+300")
	# resize columns with window
	root.columnconfigure(0, weight=1, minsize=200)
	root.columnconfigure(1, weight=1, minsize=200)
	# set minimum height for row 0 and 2
	root.rowconfigure(0, minsize=50)
	root.rowconfigure(2, minsize=20)
	# set window min size
	root.minsize(520, 40)
	root.after(0, create_app, root)
	root.mainloop()
	
