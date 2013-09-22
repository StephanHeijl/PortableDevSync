import SimpleHTTPServer
import SocketServer
import threading

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

class InterfaceServer(threading.Thread):
	def __init__(self):
		self.started = False
		self.currentPort = 8000
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