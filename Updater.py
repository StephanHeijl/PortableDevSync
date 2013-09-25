import zipfile
import cStringIO
import urllib2

class Updater():
	def update():
		if self.checkForUpdate():
			f = self.downloadUpdate()
			if f:
				if self.installUpdate(f):
					self.removeOld()
			
		
	def checkForUpdates(self):
		githubUrl = "https://api.github.com/repos/StephanHeijl/PortableDevSync/commits"
		request = urllib2.urlopen(githubUrl)
		commits = json.load(request)
		
		versions = []
		for commit in commits:
			versions.append(commit['sha'])
		
		if 'version' not in self.settings:
			self.adjustSettings(version=versions[0])
			
		currentVersion = self.settings['version']
		if currentVersion != versions[0] or currentVersion != "dev":
			Dialog(visual).yesno("Update available", "An update is available. Would you like to download and install it now?")
		
		if self.downloadUpdate():
			self.adjustSettings(version=versions[0])
		else:
			Dialog(visual).error("Update error", "Update could not be downloaded or applied.")
		
	def downloadUpdate(self):
		updateUrl = "https://github.com/StephanHeijl/PortableDevSync/archive/master.zip"
		r = urllib2.urlopen(updateUrl)
		
		f = cStringIO.StringIO()
		f.write(r.read())
		f.seek(0)
		r.close()
		
		return unpackName
		
	def installUpdate(self,f):
		unpackName = "PortableDevSync-master"
		with zipfile.ZipFile(f, 'r') as archive:
			archive.extractall()
		# move all the old files
		for file in os.listdir(unpackName):
			print file
		
	def removeOld(self):
		pass