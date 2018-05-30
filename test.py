from threading import Thread
import socket 
import sys
from time import sleep
import MySQLdb
import select
import pymysql.cursors

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
            #self._socket_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self._socket_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as e:
            print('Failed to init')
            print(e)
            sys.exit()

    # def listener(self):

    #     while True:
    #         result = select.select([self._socket_listen], [], [])
    #         print(result)
    #         msg = result[0][0].recv(BUFFER_SIZE)
    #         print(msg)
    #         if (msg[18]==21 and msg[22]==50 and msg[25]==1 and msg[26]==248): #SWITCH
    #             self._c.execute("""UPDATE switches (status) VALUES (0);""")
    #             self._conn.commit()
    #             print('switch status')
    #         if (msg[18]==21 and msg[22]==50 and msg[25]==2 and msg[26]==248): #DOOR
    #             self._c.execute("""UPDATE doors (status) VALUES (0);""")
    #             self._conn.commit()
    #         if (msg[18]==20 and msg[21]==219 and msg[22]==1): #DIGITAL SENSOR
    #             d1=msg[25]
    #             d2=msg[26]
    #             lux=msg[27]
    #             motion=msg[28]
    #             self._c.execute("""UPDATE sensors (status) VALUES (%d);""",d1)
    #             self._conn.commit()
    #             print('sensor status')
    #         if(msg[18] == 21 and msg[22] == 52 and msg[25] == 4): #RELAY
    #             if(msg[26]==100):
    #                 self._c.execute("""UPDATE switches (status) VALUES (1);""") #CH1
    #                 self._conn.commit()
    #                 print('switch status')
    #             if(msg[27]==100):
    #                 self._c.execute("""UPDATE doors (status) VALUES (1);""") #CH2
    #                 self._conn.commit()
    #                 print('door status')
    #         if(msg[18] == 20 and msg[21]==220 and msg[22]==1): #TEMP
    #             t = msg[26]
    #             t = (5/9)*(t-32)
    #             self._c.execute("""INSERT INTO temp_log (temp) VALUES (%d);""",t)
    #             self._conn.commit()
    #             print('temp status')


    def query(self):
        while True:
            print("Sending")
            #self._socket_send.sendto(DOOR_STATUS ,(HOST_SEND_IP,HOST_PORT))
            self._socket_send.sendto(RELAY_STATUS ,(HOST_SEND_IP,HOST_PORT))
            #self._socket_send.sendto(TEMP_STATUS ,(HOST_SEND_IP,HOST_PORT))
            sleep(5)

    def start(self):
        # self._socket_listen.bind((HOST_LISTEN_IP,HOST_PORT))
        # self._socket_listen.setblocking(0)
        # print("Binding")

        self._socket_send.bind(('',HOST_PORT))
        self._socket_send.setblocking(0)
        print("Binding")

        #listen_thread=Thread(target=self.listener, args=())
        #listen_thread.start()

        query_thread=Thread(target=self.query, args=())
        query_thread.start()
        return 0


x=App()
x.start()
        