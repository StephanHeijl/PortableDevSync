import Tkinter
import tkMessageBox

class Dialog():
	def __init__(self):				
		root = Tkinter.Tk()
		root.withdraw()
	
	def message(self, title, message):	
		tkMessageBox.showinfo(title, message)
		
	def warning(self, title, message):	
		tkMessageBox.showwarning(title, message)
		
	def error(self, title, message):	
		tkMessageBox.showerror(title, message)
		
	def yesno(self, title, message):	
		tkMessageBox.askyesno(title, message)
		
	def okcancel(self, title, message):	
		tkMessageBox.askokcancel(title, message)
		
	def retrycancel(self, title, message):	
		tkMessageBox.retrycancel(title, message)