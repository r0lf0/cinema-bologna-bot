import requests, json, time, datetime, telepot, sys, emoji
from telepot.loop import MessageLoop
from DB import DB
from Film import Film
from Giorno import Giorno
from Spettacolo import Spettacolo

# token that can be generated talking with @BotFather on telegram
my_token = '732570219:AAGhw-q3GDgrNAUO9RhK4MSl4wlyrI6dyG4'
my_id = 49267778

aiuto = ["aiuto", "/aiuto", "help", "/help", "/start"]
programmazioneGiornaliera = ["/showperdata"]
programmazionePerFilm = ["/showperfilm"]

msg_benvenuto = "Ciao, sono il bot non ufficiale del The Space di Bologna. Ecco le cose che puoi chiedermi:\n/aiuto per ricevere questo messaggio\n/showPerData per ricevere la programmazione per data\n/showPerFilm per ricevere la programmazione per film"

 
def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	print(msg)
	if content_type == 'text':
		input = msg.get("text").strip().lower()
		if (input in aiuto):
			bot.sendMessage(chat_id, msg_benvenuto)
		elif input in programmazioneGiornaliera:
			bot.sendMessage(chat_id, "--PROGRAMMAZIONE PER DATA--\n\n" + emoji.emojize(oldDB.getSpettacoliPerData(), use_aliases=True) + "\n\n\n")
		elif input in programmazionePerFilm:	
			bot.sendMessage(chat_id, "--PROGRAMMAZIONE PER FILM--\n\n" + emoji.emojize(str(oldDB), use_aliases=True) + "\n\n\n")
		else:
			bot.sendMessage(chat_id, emoji.emojize("Non ho capito... :sob:", use_aliases=True))


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


bot = telepot.Bot(my_token)
bot.sendMessage(my_id, msg_benvenuto)
MessageLoop(bot, handle).run_as_thread()
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
			print(":)")
			oldDB = currentDB
			bot.sendMessage(my_id, "Programmazione aggiornata!")
	except:
	 	print("ERRORE")
	 	bot.sendMessage(my_id, "\nErrore nel recupero o nell'elaborazione delle informazioni")
		
	time.sleep(300)
