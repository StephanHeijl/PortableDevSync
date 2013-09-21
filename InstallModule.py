# Install Module Python
# Provides methods for automatically installing Python modules from the web.

import tempfile
import urllib
import os

class InstallModule():
	def __init__(self, name):
		self.name = name
		self.installed = False
		
	def url(url):
		# Retreive a file from an url, store it in a temp directory
		filename = url.split("/")[-1]
		tempfile = open( os.path.join( tempfile.gettempdir() , filename ))
		print tempfile
		
		
	def pip(name):
		# TODO: Implement pip code
		pass
		
	def easy_install(name):
		# TODO: Implement easy_install code
		pass
		
	def test(name=False):
		if not name:
			name = self.name
			
		try:
			__import__(name)
			if name == self.name():
				self.installed = True
			return True
		except:
			if name == self.name():
				self.installed = False
			return False
		