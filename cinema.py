# Install the Python Requests library:
# `pip install requests`

import requests, json, time
import datetime
import telegram
import datetime

#token that can be generated talking with @BotFather on telegram
my_token = '732570219:AAGhw-q3GDgrNAUO9RhK4MSl4wlyrI6dyG4'
my_id = 49267778

class DB():
	def __init__(self):
		self.films = []

	def __str__(self):
		output = ""
		for film in self.films:
			if (film.giorni != []):
				output += str(film) + "\n"
		return output

	def __eq__(self, other): 
		if not isinstance(other, DB):
			return False
		return str(self) == str(other)

	def getSpettacoloPerData(self, data):
		trovato = False
		output = "Film di " + data + "\n"
		for film in self.films:
			for giorno in film.giorni:
				if data == giorno.data:
					output += film.titolo + "\n" + giorno.toStringSenzaData()
					trovato = True
		if (trovato):
			return output
		return ""

	def getSpettacoliPerDataFormattata(self, dataFormattata):
		trovato = False
		trovatoFilm = False
		temp = ""
		output = ""
		tempData = ""
		for film in self.films:
			for giorno in film.giorni:
				if dataFormattata == giorno.dataFormattata:
					output += film.titolo + "\n" + giorno.toStringSenzaData()
					tempData = giorno.data
					trovato = True

		if (trovato):
			return "Film di " + tempData + "\n" + output
		return ""

	def add(self, film):
		self.films.append(film)

	def getSpettacoliPerData(self):
		dateFormattate = []
		for film in self.films:
			for giorno in film.giorni:
				if giorno.spettacoli != []:
					if giorno.dataFormattata not in dateFormattate:
						dateFormattate.append(giorno.dataFormattata)

		output = ""
		dateFormattate.sort()
		for dataFormattata in dateFormattate:
			output += self.getSpettacoliPerDataFormattata(dataFormattata) + "\n"
		return output



class Film():
	def __init__(self, titolo, giorni):
		self.titolo = titolo
		self.giorni = giorni

	def __init__(self, titolo):
		self.titolo = titolo
		self.giorni = []

	def __str__(self):
		output = self.titolo + "\n"
		for giorno in self.giorni:
			output += str(giorno)
		return output

	def __eq__(self, other): 
		if not isinstance(other, Film):
			return False
		return str(self) == str(other)

	def add(self, giorno):
		self.giorni.append(giorno)

class Giorno():
	def __init__(self, data, dataFormattata, spettacoli):
		self.data = data
		self.spettacoli = spettacoli
		format_str = '%Y-%m-%d' # The format
		self.dataFormattata = datetime.datetime.strptime(dataFormattata, format_str)

	def __init__(self, data, dataFormattata):
		self.data = data
		self.spettacoli = []
		format_str = '%Y-%m-%d' # The format
		self.dataFormattata = datetime.datetime.strptime(dataFormattata, format_str)

	def __str__(self):
		output = self.data + "\n"
		for spettacolo in self.spettacoli:
			output += "-" + str(spettacolo) + "\n"
		return output

	def __eq__(self, other): 
		if not isinstance(other, Giorno):
			return False
		return str(self) == str(other)


	def add(self, spettacolo):
		self.spettacoli.append(spettacolo)

	def toStringSenzaData(self):
		output = ""
		for spettacolo in self.spettacoli:
				output += " -" + str(spettacolo) + "\n"
		return output

class Spettacolo():
	def __init__(self, orario, sala):
		self.orario = orario
		self.sala = sala

	def __str__(self):
		return self.orario + " sala " + self.sala

	def __eq__(self, other): 
		if not isinstance(other, Spettacolo):
			return False
		return str(self) == str(other)










def send(msg, chat_id, token=my_token):
	"""
	Send a mensage to a telegram user specified on chatId
	chat_id must be a number!
	"""
	bot = telegram.Bot(token=token)
	bot.sendMessage(chat_id=chat_id, text=msg)

def send_request():
	try:
		response = requests.get(
			url="https://www.thespacecinema.it/data/filmswithshowings/3",
		)
		print('Response HTTP Status Code: {status_code}'.format(
			status_code=response.status_code))
		return response.text
	except requests.exceptions.RequestException:
		print('HTTP Request failed')

oldDB = DB()
while (1 == 1):
	try:
		currentTime = str(datetime.datetime.now())
		currentDB = DB()
		print("\n" + currentTime)
		raw = send_request()
		jsonData = json.loads(str(raw))
		for filmTS in jsonData["films"]:
			filmDB = Film(filmTS.get("title"))
			for showingTS in filmTS["showings"]:
				giornoDB = Giorno(showingTS.get("date_short"), showingTS.get("date_time"))
				for timeTS in showingTS["times"]:
					spettacoloDB = Spettacolo(timeTS.get("time"), timeTS.get("screen_number"))
					giornoDB.add(spettacoloDB)
				filmDB.add(giornoDB)
			currentDB.add(filmDB)

		if oldDB == currentDB:
			print(":(")
		else:
			print(":) -> sending...")
			send("--PROGRAMMAZIONE PER FILM--\n\n" + str(currentDB) + "\n\n\n", my_id)
			send("--PROGRAMMAZIONE PER DATA--\n\n" + currentDB.getSpettacoliPerData() + "\n\n\n", my_id)
			oldDB = currentDB
	except:
		print("ERRORE")
		send(currentTime + "\nErrore nel recupero o nell'elaborazione delle informazioni", my_id)
		
	time.sleep(300)
