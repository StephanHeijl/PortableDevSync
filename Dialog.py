import Tkinter
import tkMessageBox
import tkSimpleDialog
import os

class Dialog():
	def __init__(self, v=True):
		self.visual = v
		if v:
			root = Tkinter.Tk()
			root.withdraw()
			
	def clearScreen(self):
		if os.system("clear") == 1:
			os.system("cls")
	
	def drawConsoleDialog(self, type, title, message, buttons={}, fields={} ):
		dialog = []
		width = 42
		textwidth = width-2
		lines = message.split("\n")
		print "+" + ("-"*width) + "+"
		
		lineN = 0
		lineAmount = len(lines)
		
		while lineN < lineAmount:
			lineAmount = len(lines)
			
			if len( lines[lineN] ) > textwidth:
				line = lines[lineN]
				del lines[lineN]
				while len(line) > textwidth:
					if " " in line:
						nl = " ".join( line[0:textwidth].split(" ")[0:-1] )
					else:
						nl = line[0:textwidth]
					
					line = line[len(nl):]
					lines.insert(lineN, nl)
					
					lineAmount += 1
					lineN+=1
				
				lines.insert(lineN, line)
				lineAmount += 1
				
			else:
				lineN+=1
		
		header = "%s - %s" % (type, title)
		
		if len(header) > width:
			header = header[:width-5] + "..."
			
		centerspace = ((width-len(header))/2)-1
		
		top = "| %s %s " % ("="*centerspace, header)
		top = top.ljust(width,"=")
		top+=" |"
		print top
		
			
		print "+" + ("-"*width) + "+"
		for line in lines:
			print "| %s |" % line.strip().ljust(width-2, " ")
		
		
		if len( fields ) > 0:
			print "|" + (" "*width) + "|"
			for k,v in fields.items():
				space = textwidth-len(k)-4
				print "| %s: [%s] |" % (k, "_"*space)
		
		
		buttonsText = []
		if len(buttons) > 0:
			print "|" + (" "*width) + "|"
			for k,v in buttons.items():
				buttonsText.append( "[ %s ]" % k )
				
			buttonsLine = "  ".join(buttonsText)
			centerspace = ((width-len(buttonsLine))/2)
				
			b = "|%s%s" % (" "*centerspace, buttonsLine)
			b = b.ljust(width+1," ")
			b+="|"
			print b
			
		print "+" + ("-"*width) + "+"
		print
		
		if len(buttons) > 0:
			response = ""
			while response not in buttons:
				response = raw_input("Response: ")
			print "'%s' was selected." % response
			return buttons[response]
		
		if len(fields) > 0:
			for f in fields:
				fields[f] = raw_input("%s: " % f)
				
			return fields
		
									
	def message(self, title, message):
		if self.visual:
			tkMessageBox.showinfo(title, message)
		else:
			self.drawConsoleDialog("Message",title, message)
		
	
	def warning(self, title, message):	
		if self.visual:
			tkMessageBox.showwarning(title, message)
		else:
			self.drawConsoleDialog("Warning",title, message)
	
	def error(self, title, message):
		if self.visual:
			tkMessageBox.showerror("Error",title, message)
		else:
			self.drawConsoleDialog("Error",title, message)
			
	
	def yesno(self, title, message):
		if self.visual:
			return tkMessageBox.askyesno(title, message)
		else:
			return self.drawConsoleDialog("Yes/No",title, message, buttons={'yes':True, 'no': False})
	
	def okcancel(self, title, message):	
		if self.visual:
			return tkMessageBox.askokcancel(title, message)
		else:
			return self.drawConsoleDialog("OK/Cancel",title, message, buttons={'ok':True, 'cancel': False})
	
	def retrycancel(self, title, message):
		if self.visual:
			return tkMessageBox.retrycancel(title, message)
		else:
			return self.drawConsoleDialog("Retry/Cancel",title, message, buttons={'retry':True, 'cancel': False})
	
	def prompt(self, title, message):
		if self.visual:
			return tkSimpleDialog.askstring(title, message)
		else:
			return self.drawConsoleDialog("Prompt",title, message, fields={'Response':''})['Response']