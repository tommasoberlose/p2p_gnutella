import Function as func
import Constant as const
import Package as pack
import Daemon as daemon

# Crea il pacchetto "NEAR.PKTID.IP4|IP6.PORTA.", inserisco manualmente un elemento della rete, se va bene invio il pacchetto, else ne provo un altro.
def updateNeighbor(myHost, listNeighbor):
	del listNeighbor[:]
	pk = pack.neighbor(myHost)
	while True:
		print (">>> SCELTA PEER VICINO")
		nGroup = input("Numero del gruppo: ")
		if nGroup is 0:
			break
		nElement = input("Numero dell'elemento del gruppo: ")
		if nElement is 0:
			break
		nPort = input("Inserire la porta su cui il vicino è in ascolto: ")
		if nPort is 0:
			break
		hostN = func.roll_the_dice("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
																"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
																"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
																":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))
		s = func.create_socket_client(hostN, nPort);
		if s is None:
			func.error("Errore nella scelta del primo peer vicino, scegline un altro.")
			break
		else:
			s.sendall(pk)
			s.close()
			break

def search(myHost, query, listNeighbor, listPkt):
	pk = pack.query(myHost, query)
	if len(listNeighbor) is 0:
		func.error("Nessun vicino presente, crea prima una rete virtuale")
	else:
		func.add_pktid(pk[4:20], listPkt)
		i = 0
		for x in listNeighbor:
			s = func.create_socket_client(func.roll_the_dice(x[0]), x[1]);
			if s is None:
				func.error("\nPeer vicino non attivo:" + str(x[0], "ascii"))
			else:
				s.sendall(pk)
				s.close()
				i = i + 1
		if i is 0:
			func.error("Nessun peer vicino attivo")
		else:
			print("\n\nScegli file da quelli disponibili (0 per uscire): \n")
			choose = int(input("ID\tFILE\t\tIP\n"))
			if choose != 0:
				func.remove_pktid(pk, listPkt)
				download(listResultQuery[choose - 1])
				del listResultQuery[:]
	

# Funzione di download
def download(selectFile):	
	print (">>> DOWNLOAD")
	#print ("Il file selezionato ha questi parametri: ", selectFile)

	md5 = selectFile[1]
	nomeFile = selectFile[2].decode("ascii").strip()
	ip = selectFile[3]
	port = selectFile[4]

	# Con probabilità 0.5 invio su IPv4, else IPv6
	ip = func.roll_the_dice(ip.decode("ascii"))
	print("Connessione con:", ip)

	# Mi connetto al peer

	sP = func.create_socket_client(ip, port)
	if sP is None:
	    print ('Error: could not open socket in download')
	else:
		pk = pack.dl(md5)
		print("Send:", pk)
		sP.sendall(pk)

		nChunk = int(sP.recv(const.LENGTH_HEADER)[4:10])
					
		ricevutoByte = b''

		i = 0
		
		while i != nChunk:
			ricevutoLen = sP.recv(const.LENGTH_NCHUNK)
			print(ricevutoLen)
			while (len(ricevutoLen) < const.LENGTH_NCHUNK):
				ricevutoLen = ricevutoLen + sP.recv(const.LENGTH_NCHUNK - int(ricevutoLen))
			buff = sP.recv(int(ricevutoLen))
			while(len(buff) < int(ricevutoLen)):
				buff = buff + sP.recv(int(ricevutoLen) - len(buff))
			ricevutoByte = ricevutoByte + buff
			print(len(buff), buff)
			i = i + 1

		sP.close()

		#print ("Il numero di chunk è: ", nChunk)
		
		# Salvare il file data
		open((const.FILE_COND + nomeFile),'wb').write(ricevutoByte)
		print("File scaricato correttamente, apertura in corso...")
		try:
			os.system("open " + const.FILE_COND + nomeFile)
		except:
			try:
				os.system("start " + const.FILE_COND + nomeFile)
			except:
				print("Apertura non riuscita")
def logout(ip):
	print (">>> LOGOUT")
	i = 0
	pk = pack.logout()
	s = func.create_socket_client(func.get_ipv4(ip), const.PORT);
	if s is None:
		func.error("Errore nella chiusura del demone:" + func.get_ipv4(ip))
	else:
		s.sendall(pk)
		s.close()
		i = i + 1
	s = func.create_socket_client(func.get_ipv6(ip), const.PORT);
	if s is None:
		func.error("Errore nella chiusura del demone:" + func.get_ipv6(ip))
	else:
		s.sendall(pk)
		s.close()
		i = i + 1
	if i is 2:
		print ("Logout eseguito con successo.")

####### VARIABILI 

listNeighbor = []	
listPkt = []
listResultQuery = []

####### INIZIO CLIENT #######
nGroup = input("Inserire il numero del gruppo: ")
nElement = input("Inserire il numero dell'elemento del gruppo: ")
host = ("172.030." + func.format_string(nGroup, const.LENGTH_SECTION_IPV4, "0") + 
				"." + func.format_string(nElement, const.LENGTH_SECTION_IPV4, "0") + 
				"|fc00:0000:0000:0000:0000:0000:" + func.format_string(nGroup, const.LENGTH_SECTION_IPV6, "0") + 
				":" + func.format_string(nElement, const.LENGTH_SECTION_IPV6, "0"))

print ("IP:", host)

####### DEMONI

daemonThreadv4 = daemon.Daemon("THREAD IPV4 <<<", func.get_ipv4(host), listNeighbor, listPkt, listResultQuery, host)
daemonThreadv6 = daemon.Daemon("THREAD IPV6 <<<", func.get_ipv6(host), listNeighbor, listPkt, listResultQuery, host)
daemonThreadv4.setName("Thread ipv4")
daemonThreadv6.setName("Thread ipv6")
daemonThreadv4.start()	
daemonThreadv6.start()

# Menù di interazione
while True:
	choice = input("\n\nScegli azione:\nupdate\t - Update Neighborhood\nview\t - View Neighborhood\nsearch\t - Search File\nquit\t - Quit\n\nScelta: ")

	if (choice == "update" or choice == "u"):
		updateNeighbor(host, listNeighbor)

	if (choice == "view" or choice == "view"):
		print (">>> VIEW NEIGHBORHOOD")
		if len(listNeighbor) != 0:
			for n in listNeighbor:
				print(n[0] + "\t" + n[1])
		else:
			print("Nessun vicino salvato")

	elif (choice == "search" or choice == "s"):
		print (">>> RICERCA")
		query = input("\n\nInserisci il nome del file da cercare: ")
		while(len(query) > const.LENGTH_QUERY):
			func.error("Siamo spiacenti ma accettiamo massimo 20 caratteri.")
			query = input("\n\nInserisci il nome del file da cercare: ")
		search(host, query, listNeighbor, listPkt)

	elif (choice == "quit" or choice == "q"):
		logout(host)
		daemonThreadv4.join()
		daemonThreadv6.join()
		break

	else:
		func.error("Wrong Choice!")