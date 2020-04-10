import tkinter
from tkinter import messagebox as tkMessageBox
import os


class App():
	def __init__(self, window, window_title):
		self.window = window
		self.window.title(window_title)
		self.window.configure(bg="#FFC284")
		self.button_color = "#FF8758"
		self.frame = tkinter.Frame(window, bg="#FFC284")
		self.frame.pack(pady=15)
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
		# on closing, ask before closing
		self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

	# button callbacks ------
	def start_thermal(self):
		os.system("python3 /home/choilab/homecage_quantification/start_thermal.py")

	def preview_camera(self):
		os.system("python3 /home/choilab/homecage_quantification/preview_camera.py")
		# only now we enable the experiment button
		self.exp_button.config(state="normal") 

	def start_experiment(self):
		os.system("python3 /home/choilab/homecage_quantification/main.py")


	def on_closing(self):
		if tkMessageBox.askyesno("Quit", "Do you want to quit?"):
			self.window.destroy()


def create_app(root):
	App(window = root, window_title = "Experiment GUI")

if __name__ == '__main__':
	root = tkinter.Tk()
	# widthxheight+300+300 pxposition from the leftcorner of the monitor
	root.geometry("300x300+300+300")
	root.after(0, create_app, root)
	root.mainloop()
	
