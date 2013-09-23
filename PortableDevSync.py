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
import multiprocessing
from InstallModule import InstallModule
from Dialog import Dialog
from InterfaceServer import *		

class PortableDevSync():
	def __init__(self):
		self.client = None
		self.__loadMonitors()
		try:
			app_key, app_secret = self.__getAppKeyAndSecret()
		except Exception as e:
			Dialog(visual).error("Could not contact key server", "Could not contact key server, unable to verify app. \n%s" % e)
			return
		self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
		
	def checkForUpdates(self):
		
		
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
		IS = InterfaceServer(self)
		IS.daemon = True # Make sure the server stops once the application stops
		IS.start()
		
		while not IS.started:
			time.sleep(0.1)
			
		if Dialog(visual).yesno("Server started.", "Server started on port %s. Navigate to http://localhost:%s/ ?" % (IS.currentPort, IS.currentPort)):
			webbrowser.open("http://localhost:%s/" % IS.currentPort)
	
	def setup(self):
		if not os.path.exists("settings.config"):
			self.__authenticate()
			
		Dialog(visual).message("Dropbox authenticated.", "Dropbox access authenticated, connecting to Dropbox...")
		self.settings = json.load(open("settings.config"))
		access_token, user_id = self.settings['access_token'], self.settings['user_id']
		
		self.client = dropbox.client.DropboxClient(access_token)
		account_info = self.client.account_info()
		name = account_info['display_name']
		Dialog(visual).message("Logged in.", "Succesfully logged in as %s." % name)
		
		self.checkAll()
	
	def start(self):	
		self.setup()
		self.__startServer()
		Dialog(False).prompt("Server running", "Press enter to stop the server.")
		Dialog(visual).message("Starting service", "Starting PortableDevSync service.")

		#subprocess.Popen("pythonw PortableDevSync.py -service", shell=True)
		
	def service(self):
		stdout = open("service.out", "a")
		stderr = open("service.err", "a")		
		self.__startServer()		
			
	def __checkFile(self, rel):
		rel = rel.replace(os.path.sep, "/")
		try:
			response = self.client.metadata(rel)
		except dropbox.rest.ErrorResponse:
			return False
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
			
	def __loadMonitors(self):
		monitorsConfig = "monitors.config"
		if not os.path.exists(monitorsConfig):	
			try:
				mf = open(monitorsConfig,"w")
				mf.write("{}")
				mf.close()
			except:
				Dialog("Monitors could not be loaded on this system")
				return False
				
		mf = open( monitorsConfig, "r" )
		self.monitors = []
		for m in json.load(mf):
			self.monitors.append( Monitor().fromJSON(m) )
		mf.close()
			
	def __saveMonitors(self):
		monitorsConfig = "monitors.config"
		mf = open( monitorsConfig, "w" )
		mf.write("[")
		mf.write( ",\n".join( [ mon.toJSON() for mon in self.monitors ] ) )
		mf.write("]")
		mf.close()
		
	def __verifyMonitor(self, dir):
		if not os.path.exists(dir):		
			Dialog(visual).error("Could not add monitor","Could not add monitor as this directory does not exist.")
			return False
		if not os.path.isdir(dir):		
			Dialog(visual).error("Could not add monitor","Could not add monitor as this is not a directory.")
			return False
			
		n = 1		
		name = dir.split(os.sep)[-1]
		
		for mon in self.monitors:
			if mon.name == name:
				n+=1
			if mon.absolutePath == dir:
				Dialog(visual).warning("Could not add monitor", "Could not add monitor, this directory is already being monitored.")
				return False
				
		return True
		
		
	def addMonitorJSON(self, jsons):
		monitor = Monitor().fromJSON(jsons)
		
		if not self.__verifyMonitor(monitor.absolutePath):
			return False
		
		self.check(monitor, upload=True )
		monitor.latestCheck = datetime.datetime.now()
		
		self.monitors.append(monitor)
		self.__saveMonitors()	
	
	def addMonitor(self, dir, updateInterval=None):	
		if not self.__verifyMonitor(dir):
			return False
		
		monitor = Monitor()		
		monitor.absolutePath = dir
		monitor.name = name
		
		monitor.latestCheck = datetime.datetime.now()
		if updateInterval:
			monitor.updateInterval = datetime.timedelta(*updateInterval)
		self.check( monitor, upload=True )
		self.monitors.append(monitor)
		
		self.__saveMonitors()
	
	def checkAll(self):
		for monitor in self.monitors:
			self.check(monitor, upload=True)
		self.__saveMonitors()
		
	def check(self, monitor, upload=False):
		dir = monitor.absolutePath
		
		for root, dirs, files in os.walk(dir):
			for f in files:
				full = os.path.join(root, f)
				stat = os.stat( full )
				size = stat.st_size
				mtime = stat.st_mtime
				rel = "".join([ monitor.name, full.split(monitor.name)[-1] ])
				difference = datetime.datetime.fromtimestamp(mtime) - monitor.latestCheck
				
				if size > self.settings["max_size"]:
					continue
				
				if rel not in monitor.files:
					monitor.files.append(rel)

					if not upload:
						continue
					metadata = self.__checkFile(rel)
					
					if not metadata:
						self.__uploadFile( full, rel, rev=None)
						Dialog(visual).message("Uploading", "Uploading new file '%s'. " % f)
					elif difference < monitor.updateInterval:
						self.__uploadFile( full, rel, rev=metadata['rev'])
						Dialog(visual).message("Uploading", "Updating file '%s'. " % f)
				else:
				
					# if the latest modification time is later then the latest check
					# and if the difference between the two previous times is longer than the interval
					
					if datetime.datetime.fromtimestamp(mtime) > monitor.latestCheck and difference > monitor.updateInterval: 
						metadata = self.__checkFile(rel)
						self.__uploadFile( full, rel, rev=metadata['rev'])
						Dialog(visual).message("Updating", "Updating file '%s'. " % f)				
				
		monitor.latestCheck = datetime.datetime.now()


class Monitor():
	def __init__(self):
		self.absolutePath = ""
		self.name = ""
		self.latestCheck = None
		self.updateInterval = datetime.timedelta(0, 3600)
		self.timeFormat = "%d-%m-%y %H:%M"
		self.files = []				
		
	def toJSON(self):
		vars = {}
		vars["absolutePath"] = self.absolutePath
		vars["name"] = self.name
		vars["latestCheck"] = self.latestCheck.strftime(self.timeFormat)
		vars["files"] = self.files
		vars["updateInterval"] = [self.updateInterval.days, self.updateInterval.seconds,self.updateInterval.microseconds]
		
		return json.dumps(vars)		
		
	def fromJSON(self, fjson):
		if type(fjson) == type(''):
			vars = json.loads(fjson)
		else:
			vars = fjson
			
		self.absolutePath = vars["absolutePath"]
		self.latestCheck = datetime.datetime.strptime(vars["latestCheck"], self.timeFormat)
		self.name = vars["name"]
		self.files = vars["files"]
		self.updateInterval = datetime.timedelta(*vars["updateInterval"])
		
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
	# Parse command line arguments into a proper dictionary
	args = {}
	for a in range(len(sys.argv)):
		arg = sys.argv[a]
		if arg[0] == "-":
			args[arg[1:]] = None
		
		try:
			v = sys.argv[a+1]
			if v[0] != "-":
				args[arg[1:]] = v
		except:
			pass
			
	print args
		
	
	visual = True if "text" not in args else False
	
	if "service" in args:
		import dropbox
		pds = PortableDevSync()
		pds.service()
		sys.exit()
		
	elif "addMonitor" in args:
		import dropbox
		pds = PortableDevSync()
		pds.setup()
		print args
		pds.addMonitorJSON( args['addMonitor'] )
		
	else:
		# Detect wether or not the dropbox client was installed.
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
		
		pds = PortableDevSync()
		pds.start()