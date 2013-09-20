# Dropbox Auto Directory Sync Script

import os
import webbrowser
import urllib2

class PortableDevSync():
	def __init__(self):
		self.__app_key = 'INSERT_APP_KEY'
		self.__app_secret = 'INSERT_APP_SECRET'

		self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(self.__app_key, self.__app_secret)
	
	def start(self,gui=True):
		authorize_url = self.flow.start()
		webbrowser.open(authorize_url)
		

if __name__ == "__main__": # AutoRun!
	# Detect wether or not the dropbox client was installed.
	try:
		import dropbox
	except ImportError:
		im = InstallModule()
		im.url( "https://www.dropbox.com/static/developers/dropbox-python-sdk-1.6.zip" )
		im.unzip()
		im.
	
	
	ads = DropboxAutoDirSync()
	ads.start(gui=True)
