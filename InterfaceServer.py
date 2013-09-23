import SimpleHTTPServer
import SocketServer
import threading
import urllib
import json
import subprocess

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if "?" in args[0]:
			print args[0]
			
			start = args[0].find("?") + 1
			arguments = args[0][start:]
			end = min( *[i for i in [arguments.find(" "), arguments.find("/")] if i > 0] )
			if end > 0:
				arguments = arguments[:end]
			
			print arguments
			
			command =["python PortableDevSync.py -text"]
			for pair in arguments.split("&"):
				pair = pair.split("=")
				command.append("-"+pair[0])
				if len(pair) > 1:
					value = urllib.unquote(pair[1]).decode('utf8')
					value = json.dumps(value)
					command.append( value )
					
			command = " ".join(command)
			print command
			subprocess.Popen(command)

class InterfaceServer(threading.Thread):
	def __init__(self, pds):
		self.started = False
		self.currentPort = 8000
		self.pds = pds
		super(InterfaceServer, self).__init__()
		
	def run(self):
		Handler = MyHandler
		while not self.started:
			try:
				httpd = SocketServer.TCPServer(("127.0.0.1", self.currentPort), Handler)
				self.started=True
			except:
				self.currentPort+=1
		httpd.serve_forever()