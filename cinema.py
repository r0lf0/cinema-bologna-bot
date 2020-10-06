#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import logging
import os
import re
import time
from datetime import datetime
from datetime import timedelta
import emoji
import requests
import telegram
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler

import handleDB
from Film import Film, render_film
from Genere import Genere
from Spettacolo import Spettacolo, ordina_spettacoli_film_data, get_spettacoli_per_data

# token that can be generated talking with BotFather on telegram
my_token = os.environ.get('TOKEN_HEROKU')
my_id = os.environ.get('MY_ID_HEROKU')

commands_aiuto = ["aiuto", "help", "start"]
commands_programmazione_giornaliera = ["showperdata", "showPerData"]
commands_programmazione_giornaliera_completa = ["showperdataall", "showPerDataAll"]
commands_dettagli_film = ["film", "flims"]
commands_che_ore_sono = ["ora"]

msg_benvenuto = 'Ciao, sono il bot non ufficiale del The Space di Bologna. ' \
                'Ecco le cose che puoi chiedermi:' \
                '\n/aiuto per ricevere questo messaggio' \
                '\n/showPerData per ricevere la programmazione per data' \
                '\n/showPerFilm per ricevere la programmazione per film'


def handler_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg_benvenuto)


def handler_programmazione_giornaliera(update, context):
    data_limite = datetime.now() + timedelta(days=7)
    msg = ("--PROGRAMMAZIONE PER DATA--\n\n"
           + emoji.emojize(get_spettacoli_per_data(logging, data_limite=data_limite), use_aliases=True)
           + "\n\nSono mostrati gli spettacoli dei prossimi 7 giorni, per vederli tutti digita /showPerDataAll.")
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def handler_programmazione_giornaliera_completa(update, context):
    msg = ("--PROGRAMMAZIONE PER DATA--\n\n"
           + emoji.emojize(get_spettacoli_per_data(logging), use_aliases=True))
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def handler_che_ore_sono(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))


def handler_dettagli_film(update, context):
    if context.args:
        regex = ""
        for parola in context.args:
            regex += parola + '.*'
        regex = regex[:-2]
        db_conn_local = handleDB.create_db(r"cinema.db", logging)
        films = handleDB.select_film(db_conn_local)
        film_match = []
        for film in films:
            if re.search(regex, film.titolo, re.IGNORECASE):
                film_match.append(film)

        if not film_match:
            context.bot.send_message(chat_id=update.effective_chat.id, text=emoji.emojize("Nessun film trovato :sob:",
                                                                                          use_aliases=True))
        elif len(film_match) > 1:
            lista_films_match = ""
            for film in film_match:
                lista_films_match += film.titolo + "\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=("Sii più specifico, quale tra questi?\n"
                                                                             + lista_films_match))
        else:
            film = film_match[0]
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=film.locandina_link)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=render_film(film), parse_mode=telegram.ParseMode.MARKDOWN_V2)

    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Non te la so ancora dare la lista dei film in"
                                                                        "programmazione, abbi pazienza... 👍")


def sconosciuto(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=emoji.emojize("Non ho capito... :sob:",
                                                                                  use_aliases=True))


def send_request():
    try:
        response = requests.get(
            url="https://www.thespacecinema.it/data/filmswithshowings/3",
        )
        print(('Programmazione - Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code)))
        return response.text
    except requests.exceptions.RequestException:
        print('Programmazione - HTTP Request failed')


def get_locandina(url):
    try:
        response = requests.get(url=url, )
        print(('Locandina - Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code)))
        return response.content
    except requests.exceptions.RequestException:
        print('Locandina - HTTP Request failed')
        return None


logging.basicConfig(filename='bot.log', format='[%(asctime)s]%(levelname)s:%(message)s', level=logging.DEBUG)
updater = Updater(token=my_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler(commands_aiuto, handler_start))
dispatcher.add_handler(CommandHandler(commands_programmazione_giornaliera, handler_programmazione_giornaliera))
dispatcher.add_handler(CommandHandler(commands_programmazione_giornaliera_completa,
                                      handler_programmazione_giornaliera_completa))
dispatcher.add_handler(CommandHandler(commands_dettagli_film, handler_dettagli_film))
dispatcher.add_handler(CommandHandler(commands_che_ore_sono, handler_che_ore_sono))
dispatcher.add_handler(MessageHandler(Filters.command | Filters.text, sconosciuto))
updater.start_polling()
updater.bot.send_message(my_id, msg_benvenuto)

while True:
    try:
        db_conn = handleDB.create_db(r"cinema.db", logging)
        if db_conn is None:
            print("ERRORE - Impossibile creare connessione con il DB")
            raise Exception("ERRORE - Impossibile creare connessione con il DB")
        handleDB.create_tables(db_conn, logging)

        handleDB.elimina_spettacoli_passati(db_conn)
        handleDB.azzera_flag_spettacoli_consolidati(db_conn)

        raw = send_request()
        jsonData = json.loads(raw)
        nuoviFilm = []
        nuoviSpettacoli = []
        for filmTS in jsonData["films"]:
            filmDB = Film(
                (filmTS.get("id"), filmTS.get("title"), filmTS.get("ReleaseDate"), filmTS.get("info_director"),
                 filmTS.get("info_cast"), filmTS.get("synopsis_short"), filmTS.get("info_runningtime"),
                 filmTS.get("video"),filmTS.get("image_poster"), None))
            generi = []
            for genereTS in (filmTS.get("genres"))["names"]:
                generi.append(Genere((filmDB.id_film, genereTS.get("name"))))
            if handleDB.insert_film(db_conn, filmDB, generi):
                nuoviFilm.append(filmDB)
                filmDB.locandina = get_locandina(filmTS.get("image_poster"))
                handleDB.update_film_locandina(db_conn, filmDB)
            for spettacoloTS in filmTS["showings"]:
                for orarioTS in spettacoloTS["times"]:
                    spettacoloDB = Spettacolo((orarioTS.get("session_id"), filmDB.id_film, orarioTS.get("date"),
                                               orarioTS.get("screen_number"), spettacoloTS.get("date_short"),
                                               orarioTS.get("time")))
                    if handleDB.insert_spettacolo(db_conn, spettacoloDB):
                        nuoviSpettacoli.append(spettacoloDB)
        spettacoliRimossi = handleDB.select_spettacoli_non_consolidati(db_conn)
        handleDB.elimina_spettacoli_non_consolidati(db_conn)

        aggiornamento = ""
        if nuoviFilm:
            aggiornamento = aggiornamento + "\n:clapper: FILM AGGIUNTI :clapper:\n"
            for film in nuoviFilm:
                aggiornamento += film.titolo + "\n"
        if nuoviSpettacoli:
            ordina_spettacoli_film_data(nuoviSpettacoli)
            aggiornamento = aggiornamento + "\n:movie_camera: SPETTACOLI AGGIUNTI :movie_camera:\n"
            for spettacolo in nuoviSpettacoli:
                aggiornamento += handleDB.select_film(db_conn,
                                                      spettacolo.id_film).titolo + " - " + spettacolo.data + " " \
                                 + spettacolo.ora + "\n"
        if spettacoliRimossi:
            ordina_spettacoli_film_data(spettacoliRimossi)
            aggiornamento = aggiornamento + "\n:no_entry: SPETTACOLI RIMOSSI :no_entry:\n"
            for spettacolo in spettacoliRimossi:
                aggiornamento += handleDB.select_film(db_conn,
                                                      spettacolo.id_film).titolo + " - " + spettacolo.data + " " \
                                 + spettacolo.ora + "\n"
        if aggiornamento != "":
            updater.bot.send_message(my_id, emoji.emojize(aggiornamento, use_aliases=True))

        db_conn.close()

    except Exception as e:
        print("ERRORE\n")
        print(e)
        logging.error(e)
        updater.bot.send_message(my_id, "\nErrore nel recupero o nell'elaborazione delle informazioni")
        if db_conn is not None:
            db_conn.close()

    time.sleep(300)
