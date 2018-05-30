from threading import Thread
import socket 
import sys
from time import sleep
import MySQLdb
import select
import pymysql.cursors
from datetime import datetime

from config import HOST_SEND_IP, HOST_LISTEN_IP, HOST_PORT,BUFFER_SIZE, RELAY_STATUS, DOOR_STATUS, TEMP_STATUS, MYSQL_DB, MYSQL_USER,MYSQL_PASSWORD,MYSQL_HOST

class App():
    def __init__(self):
        try:
            self._conn = pymysql.connect(host=MYSQL_HOST,
                             user=MYSQL_USER,
                             password=MYSQL_PASSWORD,
                             db=MYSQL_DB,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

            self._c = self._conn.cursor()
            self._socket_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #self._socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        except Exception as e:
            print('Failed to init')
            print(e)
            sys.exit()

    def listener(self):

        while True:
            result = select.select([self._socket_listen], [], [])
            
            msg = result[0][0].recv(BUFFER_SIZE)
            print(msg[18],msg[22],msg[25])
            # if (msg[18]=='\x15' and msg[22]=='\x32' and msg[25]=='\x01' and msg[26]=='\xf8'): #SWITCH
            #     self._c.execute("""UPDATE switches SET status = 0 WHERE id = 1""")
            #     self._conn.commit()
            #     print('switch status = 0')
            # if (msg[18]=='\x15' and msg[22]=='\x32' and msg[25]=='\x02' and msg[26]=='\xf8'): #DOOR
            #     self._c.execute("""UPDATE doors SET status = 0 WHERE id = 1""")
            #     self._conn.commit()
            #     print('door status = 0')
            if (msg[18]=='\x14' and msg[21]=='\xdb' and msg[22]=='\x01'): #DIGITAL SENSOR
                d2=msg[26]
                motion=msg[28]
                if(msg[25] == '\x00'):
                    d1=0
                if(msg[25] == '\x01'):
                    d1=1

                if(msg[27] == '\x00'):
                    lux=0
                else:
                    lux=1
                self._c.execute("""UPDATE sensors SET status = %s WHERE id=1;""", d1)
                self._conn.commit()
                time=str(datetime.now())
                self._c.execute("""INSERT INTO lux_logs (lux,timestamp,room_id) VALUES (%s,%s,%s)""",(lux,time,1))
                self._conn.commit()
            if(msg[18] == '\x15' and msg[22] == '\x34' and msg[25] == '\x04'): #RELAY
                if(msg[26]=='\x64'):
                    self._c.execute("""UPDATE switches SET status = 1 WHERE id = 1""") #CH1
                    self._conn.commit()
                    print('switch status = 1')
                else:
                    self._c.execute("""UPDATE switches SET status = 0 WHERE id = 1""") #CH1
                    self._conn.commit()
                    print('switch status = 0')


                if(msg[27]=='\x64'):
                    self._c.execute("""UPDATE switches SET status = 1 WHERE id = 1""") #CH2
                    self._conn.commit()
                    print('door status = 1')
                else:
                    self._c.execute("""UPDATE switches SET status = 0 WHERE id = 1""") #CH2
                    self._conn.commit()
                    print('door status = 0')
            if(msg[18] == '\x14' and msg[21]=='\xdc' and msg[22]=='\x01'): #TEMP int(msg[26])
                t = 100
                t = (5/9)*(t-32)
                time=str(datetime.now())
                self._c.execute("""INSERT INTO temp_logs (temp,timestamp,room_id) VALUES (%s,%s,%s)""",(t,time,1))
                self._conn.commit()
                #print('temp status = '+str(t))

    def query(self):
        while True:
            self._socket_send.sendto(DOOR_STATUS ,(HOST_SEND_IP,HOST_PORT))
            self._socket_send.sendto(RELAY_STATUS ,(HOST_SEND_IP,HOST_PORT))
            self._socket_send.sendto(TEMP_STATUS ,(HOST_SEND_IP,HOST_PORT))
            sleep(5)
        return 0

    def start(self):
        self._socket_listen.bind((HOST_LISTEN_IP,HOST_PORT))
        self._socket_listen.setblocking(0)
        print("Binding")

        #self._socket_send.bind(('',HOST_PORT))
        #self._socket_send.setblocking(0)

        listen_thread=Thread(target=self.listener, args=())
        listen_thread.start()

        #query_thread=Thread(target=self.query, args=())
        #query_thread.start()
        return 0


x=App()
x.start()
        