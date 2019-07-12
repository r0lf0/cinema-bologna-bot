import requests, json, time, datetime, telepot, sys, emoji, logging, os
from pytz import timezone
import pytz
from telepot.loop import MessageLoop
from DB import DB
from Film import Film
from Giorno import Giorno
from Spettacolo import Spettacolo

# token that can be generated talking with @BotFather on telegram
my_token = os.environ.get('TOKEN_HEROKU')
my_id = os.environ.get('MY_ID_HEROKU')

aiuto = ["aiuto", "/aiuto", "help", "/help", "/start"]
programmazioneGiornaliera = ["/showperdata"]
programmazionePerFilm = ["/showperfilm"]
aggiornamento = ["/update", "/aggiornamenti", "/aggiornamento"]

msg_benvenuto = "Ciao, sono il bot non ufficiale del The Space di Bologna. Ecco le cose che puoi chiedermi:\n/aiuto per ricevere questo messaggio\n/showPerData per ricevere la programmazione per data\n/showPerFilm per ricevere la programmazione per film\n/aggiornamenti per sapere cosa è cambiato nell'ultimo aggiornamento della programmazione"

 
def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	if content_type == 'text':
		logging.info(msg)
		input = msg.get("text").strip().lower()
		if (input in aiuto):
			bot.sendMessage(chat_id, msg_benvenuto)
		elif input in programmazioneGiornaliera:
			bot.sendMessage(chat_id, "--PROGRAMMAZIONE PER DATA--\n\n" + emoji.emojize(currentDB.getSpettacoliPerData(), use_aliases=True) + "\n\n\n")
		elif input in programmazionePerFilm:	
			bot.sendMessage(chat_id, "--PROGRAMMAZIONE PER FILM--\n\n" + emoji.emojize(str(currentDB), use_aliases=True) + "\n\n\n")
		elif input in aggiornamento:
			bot.sendMessage(chat_id, emoji.emojize(differenze, use_aliases=True) + "\n\n:white_check_mark: SPETTACOLI AGGIUNTI :white_check_mark:\n" + emoji.emojize(currentDB.getDifferenze(oldDB).getSpettacoliPerData(), use_aliases=True) + "\n\npenultimo aggiornamento:\n" + oldDB.dataUltimaModifica[0:16] + "\nultimo aggiornamento:\n" + currentDB.dataUltimaModifica[0:16])
		else:
			logging.warning("Messaggio sconosciuto ricevuto - " + msg)
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


logging.basicConfig(filename='bot.log', format='[%(asctime)s]%(levelname)s:%(message)s', level=logging.DEBUG)
bot = telepot.Bot(my_token)
bot.sendMessage(my_id, msg_benvenuto)
MessageLoop(bot, handle).run_as_thread()
oldDB = DB()
currentDB = DB()
differenze = ""
while (1 == 1):
	try:
		currentTime = str(datetime.datetime.now(pytz.timezone('Europe/Rome')))
		tempDB = DB()
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
			tempDB.add(filmDB)
		
		if currentDB == tempDB:
			currentDB = tempDB
			print(":(")
		else:
			print(":)")
			oldDB = currentDB
			currentDB = tempDB
			differenze = (":no_entry: SPETTACOLI RIMOSSI :no_entry:\n" + emoji.emojize(oldDB.getDifferenze(currentDB).getSpettacoliPerData(), use_aliases=True))
			bot.sendMessage(my_id, "Programmazione aggiornata!")
	except Exception as e:
		print("ERRORE")
		logging.error(e)
		bot.sendMessage(my_id, "\nErrore nel recupero o nell'elaborazione delle informazioni")
		
	time.sleep(300)
