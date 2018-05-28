from threading import Thread
import socket 
import sys
from time import sleep
import MySQLdb
import select

from config import HOST_SEND_IP, HOST_LISTEN_IP, HOST_PORT,BUFFER_SIZE, RELAY_STATUS, DOOR_STATUS, TEMP_STATUS, MYSQL_DB, MYSQL_USER,MYSQL_PASSWORD,MYSQL_HOST

class App():
	def __init__():
		try:
			self._conn = MySQLdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DB)
			self._c = conn.cursor()
			self._socket_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self._socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		except Exception as e:
    		print('Failed to init')
    		sys.exit()

    def listener(self):
    	while True:
    		result = select.select([self._socket_listen], [], [])
        	msg = result[0][0].recv(BUFFER_SIZE)
			if (msg[18]==21 && msg[22]==50 && msg[25]==1 && msg[26]==248): #SWITCH
	            self._c.execute("""UPDATE switches (status) VALUES (0);""")
	            self._conn.commit()
	        if (msg[18]==21 && msg[22]==50 && msg[25]==2 && msg[26]==248): #DOOR
	        	self._c.execute("""UPDATE doors (status) VALUES (0);""")
	            self._conn.commit()
	        if (msg[18]==20 && msg[21]==219 and msg[22]==1): #DIGITAL SENSOR
	        	d1=msg[25]
                d2=msg[26]
                lux=msg[27]
                motion=msg[28]
	        	self._c.execute("""UPDATE sensors (status) VALUES (%d);""",d1)
	            self._conn.commit()
	        if(msg[18] == 21 && msg[22] == 52 && msg[25] == 4): #RELAY
	        	if(msg[26]==100):
	        		self._c.execute("""UPDATE switches (status) VALUES (1);""") #CH1
	            	self._conn.commit()
	        	if(msg[27]==100):
	        		self._c.execute("""UPDATE doors (status) VALUES (1);""") #CH2
	            	self._conn.commit()
	        if(msg[18] == 20 && msg[21]==220 && msg[22]==1): #TEMP
	        	t = msg[26]
	        	t = (5/9)*(t-32)
	        	self._c.execute("""INSERT INTO temp_log (temp) VALUES (%d);""",t)
	            self._conn.commit()


	def query(self):
		while True:
			self._socket_send.sendto(DOOR_STATUS ,(HOST_SEND_IP,HOST_PORT))
			self._socket_send.sendto(RELAY_STATUS ,(HOST_SEND_IP,HOST_PORT))
			self._socket_send.sendto(TEMP_STATUS ,(HOST_SEND_IP,HOST_PORT))
			sleep(5)

	def start(self):
		self._socket_listen.bind(HOST_LISTEN_IP,HOST_PORT)
		self._socket_listen.setblocking(0)

		self._socket_send.bind('',HOST_PORT)
		self._socket_send.setblocking(0)

		listen_thread=Thread(target=self.listener, args=())
		listen_thread.start()

		query_thread=Thread(target=self.query, args=())
		query_thread.start()
		return 0


x=App()
x.start()
		