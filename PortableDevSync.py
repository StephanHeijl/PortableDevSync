# Dropbox Auto Directory Sync Script

import os
import webbrowser
import urllib2
import json
import hashlib
from InstallModule import InstallModule
from Dialog import Dialog

class PortableDevSync():
	def __init__(self):
		try:
			app_key, app_secret = self.__getAppKeyAndSecret()
		except Exception as e:
			Dialog().error("Could not contact key server", "Could not contact key server, unable to verify app. \n%s" % e)
			return
		self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
		
	def __getAppKeyAndSecret(self):
		request = urllib2.urlopen("http://cytosine.nl/~stephan/PortableDevSync/DBAppSecret.py")
		response = json.loads(request.read())
		return response['app_key'],response['app_secret']
	
	def start(self):
		authorize_url = self.flow.start()
		Dialog().message("Authorization needed.","You will need to authorize PortableDevSync to use your Dropbox account.\nA webpage with the authorization options will open now.")
		webbrowser.open(authorize_url)		

def getDropboxAPI():
	try:
		with InstallModule(name="dropbox") as im:
			im.url( "https://www.dropbox.com/static/developers/dropbox-python-sdk-1.6.zip" )
			im.unzip()
			im.setup()
			return im.test()
	except Exception as e:
		Dialog().error("Exception", str(e))
		return False
	
if __name__ == "__main__": # AutoRun!
	# Detect wether or not the dropbox client was installed.
		
	im = InstallModule(name="dropbox")
	if im.test():
		import dropbox
		#Dialog().message("Dropbox is available.", "Dropbox API was downloaded and installed succesfully.")
		dropboxAvailable = True
	else:	
		retry = True
		while retry:
			dropboxAvailable = getDropboxAPI()
			if not dropboxAvailable:
				retry = Dialog.retrycancel("Dropbox could not be installed.", "There was an error while downloading/installing the Dropbox API.")
			else:
				retry = False	
	
	
	#ads = PortableDevSync()
	#ads.start()
