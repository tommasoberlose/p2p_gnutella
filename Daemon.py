from threading import Thread
import time
import socket
import Constant as const
import Function as func
import Package as pack

class Daemon(Thread):

	# Inizializza il thread, prende in ingresso l'istanza e un valore su cui ciclare
	# Tutti i metodi di una classe prendono l'istanza come prima variabile in ingresso
	# __init__ è un metodo predefinito per creare il costruttore
	def __init__(self, host, listNeighbor, listPkt, listResultQuery, pktID):
		# Costruttore
		Thread.__init__(self)
		self.host = host
		self.port = const.PORT
		self.alive = True
		self.listNeighbor = listNeighbor
		self.listPkt = listPkt
		self.listResultQuery = listResultQuery
		self.pktID = pktId

	# Funzione per stopppare il Thread
	def stop(self):
		self.alive = False

	def run(self):
		# Creazione socket
		s = func.create_socket_server(self.host, self.port)

		if s is None:
			func.write_daemon_text(self.host, 'Error: Daemon could not open socket in upload on ' + self.host)
			sys.exit(1)

		while 1:
			conn, addr = s.accept()
			func.write_daemon_text(myHost, 'Connected by ' + addr[0])
			ricevutoByte = conn.recv(1024)
			if ((not ricevutoByte) || (ricevutoByte[0:4] == const.CODE_LOGO)):
				break
			else:
				if func.add_pktid(ricevutoByte[4:20]) is True:
					if ricevutoByte[0:4] == const.CODE_ANSWER_QUERY:

					elif ricevutoByte[0:4] == const.CODE_QUERY:
						# Inoltro
						pk = pack.forward_query()
						if pk != bytes(const.ERROR_PKT, "ascii"):
							for x in listNeighbor:
								s = func.create_socket_client(x[0], x[1])
								if not(s is None):
									s.sendall(pk)
									s.close()

					elif ricevutoByte[0:4] == const.CODE_NEAR:
						func.write_daemon_text("Response near request:", ricevutoByte[20:75])
						# Inoltro
						pk = pack.forward_neighbor()
						if pk != bytes(const.ERROR_PKT, "ascii"):
							for x in listNeighbor:
								s = func.create_socket_client(x[0], x[1])
								if not(s is None):
									s.sendall(pk)
									s.close()

						# Response neighborhood
						pk = pack.neighbor(self.host)
						s = func.create_socket_client(func.roll_the_dice(ricevutoByte[20:75]), ricevutoByte[75:80])
						if s != None:
							s.sendall(pk)
							s.close()

					elif ricevutoByte[0:4] == const.CODE_ANSWER_NEAR:
						func.write_daemon_text("Add neighbor:", ricevutoByte[20:75])
						listNeighbor.append([ricevutoByte[20:75], ricevutoByte[75:80]])

			conn.close()



