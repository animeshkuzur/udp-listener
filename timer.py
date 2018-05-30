from threading import Thread
import socket 
import sys
from time import sleep
import select
import pymysql.cursors
import datetime

from config import HOST_SEND_IP, HOST_LISTEN_IP, HOST_PORT,BUFFER_SIZE, CH1ON, CH1OFF, CH2ON, CH2OFF, MYSQL_DB, MYSQL_USER,MYSQL_PASSWORD,MYSQL_HOST

class Timer():
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
            self._thread_dict={}
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


    def lock(self,time):
        if(time>0):
            print("Creating a thread for : "+str(time)+" Seconds")
            sleep(time)
            print("locking")
            self._socket_send.sendto(CH1OFF ,(HOST_SEND_IP,HOST_PORT))
            self._socket_send.sendto(CH2ON ,(HOST_SEND_IP,HOST_PORT))
            self._socket_send.sendto(CH1OFF ,(HOST_SEND_IP,HOST_PORT))
            self._socket_send.sendto(CH2ON ,(HOST_SEND_IP,HOST_PORT))
        print("destroying thread")
        return 0

    def run(self,a,t):
        self._thread_dict[a]=Thread(target=self.lock, args=(t,))
        self._thread_dict[a].start()
        return 0

    def start(self):
        # self._socket_listen.bind((HOST_LISTEN_IP,HOST_PORT))
        # self._socket_listen.setblocking(0)
        # print("Binding")
        self._socket_send.bind(('',HOST_PORT))
        self._socket_send.setblocking(0)
        print("Binding")
        while True:
            _conn = pymysql.connect(host=MYSQL_HOST,
                             user=MYSQL_USER,
                             password=MYSQL_PASSWORD,
                             db=MYSQL_DB,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
            _c = _conn.cursor()
            sleep(3)
            #listen_thread=Thread(target=self.listener, args=())
            #listen_thread.start()
            data = _c.execute("""SELECT * FROM access_logs WHERE active = 1""")
            if(data):
                for row in _c:
                    sdate = row['start_datetime']
                    edate = row['end_datetime']
                    diff=edate-sdate
                    diff=int(diff.total_seconds())
                    print(diff)
                    #int diff=tdiff.total_seconds()
                    #print(diff.Ticks())
                    self.run(data,diff)
                    _u = _conn.cursor()
                    sql = """UPDATE access_logs SET active = 0 WHERE id = %s"""
                    temp = row['id']
                    _u.execute(sql, (int(temp),))
                    _conn.commit()
                    sql2 = """UPDATE switches SET status = 1 WHERE id = 1"""
                    sql3 = """UPDATE doors SET status = 0 WHERE id = 1"""
                    _u.execute(sql2)
                    _conn.commit()
                    _u.execute(sql3)
                    _conn.commit()
                    _u.close()
                    data=data-1
                _c.close()
                _conn.close()
            
        # query_thread=Thread(target=self.query, args=())
        # query_thread.start()
        return 0


x=Timer()
x.start()
        