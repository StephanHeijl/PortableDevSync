import zipfile
import cStringIO
import urllib2
import os
import hashlib
import json
from Dialog import Dialog

class Updater():
	def update(self,pds, v):
		global visual
		visual = v
		if self.checkForUpdates(pds):
			f = self.downloadUpdate()
			if f:
				if self.installUpdate(f):
					self.removeOld()
			
		
	def checkForUpdates(self, pds):
		githubUrl = "https://api.github.com/repos/StephanHeijl/PortableDevSync/commits"
		request = urllib2.urlopen(githubUrl)
		commits = json.load(request)
		
		versions = []
		for commit in commits:
			versions.append(commit['sha'])
		
		if 'version' not in pds.settings:
			pds.adjustSettings(version=versions[0])
			
		currentVersion = pds.settings['version']
		if currentVersion != versions[0] or currentVersion != "dev":
			if Dialog(visual).yesno("Update available", "An update is available. Would you like to download and install it now?"):
				return True
		
		return False
		
		
		
	def downloadUpdate(self):
		updateUrl = "https://github.com/StephanHeijl/PortableDevSync/archive/master.zip"
		r = urllib2.urlopen(updateUrl)
		
		f = cStringIO.StringIO()
		f.write(r.read())
		f.seek(0)
		r.close()
		
		return f
		
	def installUpdate(self,f):
		unpackName = "PortableDevSync-master"
		with zipfile.ZipFile(f, 'r') as archive:
			archive.extractall()
		
		for root, dirs, file in os.walk(unpackName):
			print root,
			print root.strip(unpackName+"/")
			print file
		
	
	def hashfile(afile, blocksize=65536):
		hasher = hashlib.md5()
		buf = afile.read(blocksize)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(blocksize)
		return hasher.digest()
		
	def removeOld(self):
		pass