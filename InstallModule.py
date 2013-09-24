# Install Module Python
# Provides methods for automatically installing Python modules from the web.

import tempfile
import urllib
import os
import zipfile
import tarfile
import gzip
import urllib2
import shutil
import subprocess
import sys

class InstallModule():
	def __init__(self, name):
		self.name = name
		if not self.checkSetupTools() and name != "setuptools":
			self.installSetupTools()
		
		self.installed = False
		self.tmpfile = None
		self.tmp_extract_dir = None
	
	def checkSetupTools(self):
		try:
			import setuptools
			return True
		except ImportError:
			return False
			
	def installSetupTools(self):
		with InstallModule(name="setuptools") as im:
			im.url("https://pypi.python.org/packages/source/s/setuptools/setuptools-1.1.6.tar.gz")
			im.extract()
			im.setup(setup="ez_setup.py")
		
	
	def url(self,url):
		# Retreive a file from an url, store it in a temp directory
		filename = url.split("/")[-1]
		path = os.path.join( tempfile.gettempdir() , filename )
		self.tmpfile = path
		if not os.path.exists(path):
			tmpfile = open( path , "wb")
			download = urllib2.urlopen(url)
			tmpfile.write(download.read())
			download.close()
			tmpfile.close()
	
	def extract(self):
		if not self.tmpfile:
			raise Exception, "No temporary file available to unzip."
		
		self.tmp_extract_dir_name = "pds_tmp_extract_" + ".".join(os.path.basename(self.tmpfile).split(".")[:-1])
		os.chdir( os.path.dirname(self.tmpfile) )
		
		compressions = { 	"gz" : self.ungz,
							"zip" : self.unzip,
							"tar" : self.untar	}
		try:
			compressions[ self.tmpfile.split(".")[-1] ]()
		except KeyError:
			raise Exception, "Can't extract this filetype."
		
		self.tmp_extract_dir = os.path.join( os.path.dirname(self.tmpfile), self.tmp_extract_dir_name )
	
	def unzip(self):
		if not os.path.exists(self.tmp_extract_dir_name):
			os.mkdir(self.tmp_extract_dir_name )
		os.chdir( self.tmp_extract_dir_name )
		
		with zipfile.ZipFile(self.tmpfile, 'r') as archive:
			archive.extractall()

	def ungz(self):			
		with gzip.GzipFile(self.tmpfile, 'rb') as archive:
			outName = ".".join(self.tmpfile.split(".")[:-1])
			out = open(outName, "wb")
			out.write(archive.read())
			out.close()
			archive.close()
			self.tmpfile = outName
		if self.tmpfile.split(".")[-1] == "tar": # tar.gz files are common
			self.untar()
	
	def untar(self):
		if not os.path.exists(self.tmp_extract_dir_name):
			os.mkdir( self.tmp_extract_dir_name )
		os.chdir( self.tmp_extract_dir_name )	
		with tarfile.TarFile(self.tmpfile, 'r') as archive:
			archive.extractall()
	
	def __find_setup(self, dir, setup="setup.py"):
		contents = os.listdir(dir)
		if setup in contents:
			return os.path.join(dir, setup)
		
		for f in contents:
			if os.path.isdir(f):
				found = self.__find_setup(os.path.join(dir,f) )
				if found:
					return found
					
		return False		
	
	def setup(self, build=False, install=True, setup="setup.py"):
		if not self.tmp_extract_dir:
			raise Exception, "No extracted files found, please use extract() first."
		
		setuppath = self.__find_setup(self.tmp_extract_dir)
		if not setuppath:
			raise Exception, "No setup.py file found in this directory. Your downloaded file may be corrupted."
		
		python_executable = sys.executable
		
		command = " ".join([python_executable, setuppath])
		
		os.chdir( os.path.dirname( setuppath ) ) 
		
		if build:
			build = subprocess.Popen(command + " build")
			build.communicate()		
		if install:		
			install = subprocess.Popen(command + " install")
			install.communicate()
			
		self.installed = True
		
	def pip(self,name):
		# TODO: Implement pip code
		pass
		
	def easy_install(self,name):
		# TODO: Implement easy_install code
		pass
		
	def test(self,name=False):
		if not name:
			name = self.name
			
		try:
			__import__(name)
			if name == self.name:
				self.installed = True
			return True
		except:
			if name == self.name:
				self.installed = False
			return False
			
	def __enter__(self):
		return self
	
	def __exit__(self, type, value, traceback):
		if self.tmpfile:
			os.remove(self.tmpfile)
		if self.tmp_extract_dir:
			try:
				shutil.rmtree(self.tmp_extract_dir)
			except:
				try:
					os.rmdir(self.tmp_extract_dir)
				except:
					pass
		