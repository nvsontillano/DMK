import json
import pyowm
import psycopg2
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):

	UNAME = "nvsontillano"

	def do_GET(self):
		if self.path=="/mobile":
			print("mobile")
			conn = self.db_connect()
			table_name = self.get_table_name(conn, None, self.UNAME, 1)
			data = self.get_table_data(conn, table_name, 1)
			data = self.format_data(data)
			data = self.to_json(data)
			self.send_json(data)
			print(data)

		elif self.path=="/arduino":
			print("arduino")
			conn = self.db_connect()
			table_name = self.get_table_name(conn, self.client_address[0], None, 2)
			data = self.get_table_data(conn, table_name, 2)
			self.send_data(data)
			print(data)

	def do_POST(self):
		if self.path=="/newuser":
			print("new user")
			conn = self.db_connect()


	def db_connect(self):
		conn = None
		try:
			conn = psycopg2.connect("dbname=Garments user=postgres password=banana4")
			return conn

		except (Exception, psycopg2.DatabaseError) as error:
			print(error)

#	def add_table_name(self, conn, ip, uname):
#		cur = conn.cursor()
 #       cur.execute('INSERT INTO "IP_UName" (uname, ip) VALUES (' + self.UNAME + ', ' + str(self.client_address[0]) + ')') 
  #      cur.commit()

	def get_table_name(self, conn, ip, uname, client):
		cur = conn.cursor()
		if client==1:
			cur.execute('SELECT userid FROM "IP_UName" WHERE uname=' + "'" + uname + "'")
		elif client==2:
			cur.execute('SELECT userid FROM "IP_UName" WHERE ip=' + "'" + str(ip) + "'")
        
		t_name = cur.fetchone()
		cur.close()
		print(t_name[0])
		return t_name[0]

	def get_table_data(self, conn, t_name, client):
		cur = conn.cursor()

		if client==1:
			cur.execute('SELECT * FROM "' + str(t_name) + '"')      
		if client==2:
			cur.execute('SELECT garmentid, status FROM "' + str(t_name) + '"')      

		data = cur.fetchall()
		cur.close()

		return data

	def format_data(self, data):
		owm = pyowm.OWM('cd88f059cca0bac095172c6191735140')
		curr = owm.weather_at_place('Quezon City,PH')
		w = curr.get_weather()

		new_data = {}
		weather_data = {}
		db_data = []
		columns = ["garmentid", "status", "class", "subclass", "brand", "material", "color", "weather"]

		weather_data["time"] = str(datetime.fromtimestamp(w.get_reference_time()))
		weather_data["status"] = w.get_status()
		weather_data["det_status"] = w.get_detailed_status()
		weather_data["temp"] = str(w.get_temperature('celsius')['temp'])

		for i in range(0, len(data)):
			row_data = {}
			for j in range(0, len(columns)):
				row_data[columns[j]] = data[i][j]
			db_data.append(row_data)

		new_data["weather"] = weather_data
		new_data["records"] = db_data

		return new_data

	def to_json(self, data):
		new_data = json.dumps(data, ensure_ascii=False, indent=4)
		
		#with open('data.txt', 'w') as f:
		#	json.dump(data, f, ensure_ascii=False, indent=4)

		return new_data

	def send_data(self, data):
		self.send_response(200)
		self.send_header("Content-type", "text/plain")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		#self.wfile.write(page.encode("utf-8"))

	def send_json(self, data):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()

if __name__ == '__main__':
	serverAddress = ('', 8080)
	print(serverAddress)
	server = HTTPServer(serverAddress, RequestHandler)
	server.serve_forever()