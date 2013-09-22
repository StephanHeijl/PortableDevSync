# Dropbox Auto Directory Sync Script

import os
import webbrowser
import urllib2
import json
import hashlib
import sys
import subprocess
import threading
import time
import datetime
from InstallModule import InstallModule
from Dialog import Dialog
from InterfaceServer import *
		

class PortableDevSync():
	def __init__(self):
		self.client = None
		try:
			app_key, app_secret = self.__getAppKeyAndSecret()
		except Exception as e:
			Dialog(visual).error("Could not contact key server", "Could not contact key server, unable to verify app. \n%s" % e)
			return
		self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
		
	def __getAppKeyAndSecret(self):
		request = urllib2.urlopen("http://cytosine.nl/~stephan/PortableDevSync/DBAppSecret.py")
		response = json.loads(request.read())
		return response['app_key'],response['app_secret']
	
	def __authenticate(self):
		authorize_url = self.flow.start()
		Dialog(visual).message("Authorization needed.","You will need to authorize PortableDevSync to use your Dropbox account.\nA webpage with the authorization options will open now.")
		if Dialog(visual).yesno("Open browser","Would you like PortableDevSync to the link in your browser for you?"):
			webbrowser.open(authorize_url)
		else:
			Dialog(visual).message("Authorize", "Please visit \n%s\n to authorize the app." % authorize_url)
		
		code = Dialog(visual).prompt("Authorization code", "Once you have allowed PortableDevSync, please insert your code here:")
		
		access_token, user_id = self.flow.finish(code)
		
		settingsconf = open("settings.config", "w")
		settingsconf.write(json.dumps({"access_token": access_token, "user_id":user_id, "max_size": 2 * 1024 * 1024, "monitors":{}}))
		settingsconf.close()
		
	def __startServer(self):
		IS = InterfaceServer()
		IS.daemon = True # Make sure the server stops once the application stops
		IS.start()
		
		while not IS.started:
			time.sleep(0.1)
			
		#Dialog(visual).yesno("Server started.", "Server started on port %s. Navigate to http://localhost:%s/ ?" % (IS.currentPort, IS.currentPort))
	
	def start(self):	
		if not os.path.exists("settings.config"):
			self.__authenticate()
		
		Dialog(visual).message("Dropbox authenticated.", "Dropbox access authenticated, connecting to Dropbox...")
		self.settings = json.load(open("settings.config"))
		access_token, user_id = self.settings['access_token'], self.settings['user_id']
		
		self.client = dropbox.client.DropboxClient(access_token)
		account_info = self.client.account_info()
		name = account_info['display_name']
		Dialog(visual).message("Logged in.", "Succesfully logged in as %s." % name)
		Dialog(visual).message("Start interface", "Starting interface.")
		self.__startServer()
		
		self.addMonitor("M:\PyQt")
		
		#self.__uploadFile("C:\Users\Stephan\Documents\GitHub\PortableDevSync\LICENSE")
		#self.__fileParentRev("LICENSE")
			
	def __checkFile(self, rel):
		rel = rel.replace(os.path.sep, "/")
		
		response = self.client.metadata(rel)
		return response
	
	def __uploadFile(self, abs, rel, rev=False):
		try:
			f = open(abs, 'rb')
		except IOError:
			return False
			
		rel = rel.replace(os.path.sep, "/")
		
		if rev:
			response = self.client.put_file(rel, f, parent_rev=rev)
		else:
			response = self.client.put_file(rel, f)
				
	def addMonitor(self, dir):
	
		if not os.path.exists(dir):		
			Dialog(visual).error("Could not add monitor","Could not add monitor as this directory does not exist.")
			return False
		if not os.path.isdir(dir):		
			Dialog(visual).error("Could not add monitor","Could not add monitor as this is not a directory.")
			return False
			
		monitors = self.settings["monitors"]		
		n = 1		
		name = dir.split(os.sep)[-1]
		
		for m in monitors:
			mon = Monitor().fromJSON(monitors[m])
			if mon.name == name:
				n+=1
			if mon.absolutePath == dir:
				Dialog(visual).warning("Could not add monitor", "Could not add monitor, this directory is already being monitored.")
				return False
		
		monitor = Monitor()
		monitor.absolutePath = dir
		monitor.name = name
		
		monitor.latestCheck = datetime.datetime.now()
		self.check( monitor, upload = False )		
		
		self.settings["monitors"]["%s_%s" % (monitor.name, n)] = monitor.toJSON()
		s = open("settings.config", "w")
		s.write( json.dumps( self.settings ) )
		s.close()
		
		
		
	def check(self, monitor, upload=False):
		dir = monitor.absolutePath
		onehour = datetime.timedelta(0, 3600) # 3600 seconds
		
		for root, dirs, files in os.walk(dir):
			for f in files:
				full = os.path.join(root, f)
				stat = os.stat( full )
				size = stat.st_size
				mtime = stat.st_mtime
				rel = "".join([ monitor.name, full.split(monitor.name)[-1] ])
				difference = monitor.latestCheck - datetime.datetime.fromtimestamp(mtime)
				
				if size > self.settings["max_size"]:
					continue
				
				if rel not in monitor.files:
					monitor.files.append(rel)
					metadata = self.__checkFile(rel)
					
					if not metadata:
						self.__uploadFile( full, rel, rev=None)
						Dialog(visual).message("Uploading", "Uploading new file '%s'. " % f)
					elif difference < onehour:
						self.__uploadFile( full, rel, rev=metadata['rev'])
						Dialog(visual).message("Updating", "Updating file '%s'. " % f)
				else:
					if difference < onehour:
						metadata = self.__checkFile(rel)
						self.__uploadFile( full, rel, rev=metadata['rev'])
						Dialog(visual).message("Updating", "Updating file '%s'. " % f)				
				
		monitor.latestCheck = datetime.datetime.now()


class Monitor():
	def __init__(self):
		self.absolutePath = ""
		self.name = ""
		self.latestCheck = None
		self.timeFormat = "%d/%m/%y %H:%M"
		self.files = []
				
		
	def toJSON(self):
		vars = {}
		vars["absolutePath"] = self.absolutePath
		vars["name"] = self.name
		vars["latestCheck"] = self.latestCheck.strftime(self.timeFormat)
		vars["files"] = self.files
		
		return json.dumps(vars)		
		
	def fromJSON(self, fjson):
		vars = json.loads(fjson)
		self.absolutePath = vars["absolutePath"]
		self.latestCheck = datetime.datetime.strptime(vars["latestCheck"], self.timeFormat)
		self.name = vars["name"]
		self.files = vars["files"]
		
		return self
		

def getDropboxAPI():
	try:
		with InstallModule(name="dropbox") as im:
			im.url( "https://www.dropbox.com/static/developers/dropbox-python-sdk-1.6.zip" )
			im.unzip()
			im.setup()
			return im.test()
	except Exception as e:
		Dialog(visual).error("Exception", str(e))
		return False
	
if __name__ == "__main__": # AutoRun!
	# Detect wether or not the dropbox client was installed.
	visual = True if "-text" not in sys.argv else False
	
	if "-silent" in sys.argv:
		subprocess.Popen("python "+__file__+" -text")
		sys.exit()
	
	Dialog(visual).clearScreen()
	
	im = InstallModule(name="dropbox")
	try:
		import dropbox
		Dialog(visual).message("Dropbox is available.", "Dropbox API was downloaded and installed succesfully.")
		dropboxAvailable = True
	except ImportError:	
		retry = True
		while retry:
			dropboxAvailable = getDropboxAPI()
			if not dropboxAvailable:
				retry = Dialog.retrycancel("Dropbox could not be installed.", "There was an error while downloading/installing the Dropbox API.")
			else:
				retry = False
		
		Dialog(visual).error("PortableDevSync could not be installed.", "PortableDevSync needs the Dropbox API to function. Installation was canceled.")
	
	if not dropboxAvailable:
		sys.exit()
		
	ads = PortableDevSync()
	ads.start()