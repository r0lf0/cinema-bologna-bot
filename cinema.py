# Install the Python Requests library:
# `pip install requests`

import requests, json, time
import datetime
import telegram

#token that can be generated talking with @BotFather on telegram
my_token = '732570219:AAGhw-q3GDgrNAUO9RhK4MSl4wlyrI6dyG4'
my_id = 49267778

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

output = ""
while (1 == 1):
	print("\n" + str(datetime.datetime.now()))
	raw = send_request()
	jsonData = json.loads(str(raw))
	spiderShows = {}
	oldOutput = output
	output = ""
	for film in jsonData["films"]:
		if film["id"] == "7161":
			for show in film["showings"]:
				if show["date_time"] == "2019-07-10":
					spiderShows = show
	output += "Spettacoli del 10 luglio: \n"
	for show in spiderShows["times"]:
		output += "- Orario: " + show.get("time") + ", sala: " + show.get("screen_number") + "\n"

	if oldOutput != output:
		send(output, my_id)
		print(output)
	else:
		print(":(")
	
	time.sleep(300)
