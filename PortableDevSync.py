# Dropbox Auto Directory Sync Script

import os
import webbrowser
import urllib2
import ctypes
import InstallModule
from Dialog import Dialog

class PortableDevSync():
	def __init__(self):
		self.__app_key = 'INSERT_APP_KEY'
		self.__app_secret = 'INSERT_APP_SECRET'

		self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(self.__app_key, self.__app_secret)
	
	def start(self,gui=True):
		authorize_url = self.flow.start()
		Dialog().message("Authorization needed.","You will need to authorize PortableDevSync to use your Dropbox account.\nA webpage with the authorization options will open now.")
		webbrowser.open(authorize_url)
		

def getDropboxAPI():
	im = InstallModule()
	im.url( "https://www.dropbox.com/static/developers/dropbox-python-sdk-1.6.zip" )
	im.unzip()
	im.setup()
	im.test()
		
if __name__ == "__main__": # AutoRun!
	# Detect wether or not the dropbox client was installed.
	try:
		import dropbox
		Dialog().message("Dropbox is available.", "Dropbox API was downloaded and installed succesfully.")
		dropboxAvailable = True
		
	except ImportError:	
		retry = True
		while retry:
			dropboxAvailable = getDropboxAPI()
			if not dropboxAvailable:
				retry = Dialog.retrycancel("Dropbox could not be installed.", "There was an error while downloading/installing the Dropbox API.")
			else:
				retry = False
	
	
	ads = PortableDevSync()
	ads.start(gui=True)
