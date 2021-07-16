import functools

from Genere import render_generi
from utils.Utils import escape


class Film:
    def __init__(self, id_film, titolo, data_uscita, regista, attori, trama, durata, trailer_link, locandina_link,
                 locandina):
        self.id_film = id_film
        self.titolo = titolo
        self.data_uscita = data_uscita
        self.regista = regista
        self.attori = attori
        self.trama = trama
        self.durata = durata
        self.trailer_link = trailer_link
        self.locandina_link = locandina_link
        self.locandina = locandina


def compare_film_per_titolo(a, b):
    if a.titolo < b.titolo:
        return -1
    elif a.titolo > b.titolo:
        return 1
    else:
        return 0


def compare_film_per_data_di_uscita(a, b):
    if a.data_uscita.date() < b.data_uscita.date():
        return -1
    elif a.data_uscita.date() > b.data_uscita.date():
        return 1
    else:
        return compare_film_per_titolo(a, b)


def ordina_per_data_di_uscita(films):
    if films is []:
        return []
    films.sort(key=functools.cmp_to_key(compare_film_per_data_di_uscita))


def render_film(film, generi=None):
    film_string = "*" + escape(film.titolo) + "*\n"
    if generi:
        generi_string = render_generi(generi)
        if generi_string:
            film_string += escape(generi_string) + "\n"
    if film.data_uscita:
        film_string += "Data di uscita: " + escape(film.data_uscita.strftime("%d/%m/%Y")) + "\n"
    if film.regista:
        film_string += "Regia: " + escape(film.regista) + "\n"
    if film.attori:
        film_string += "Cast: " + escape(film.attori) + "\n"
    if film.durata:
        film_string += "Durata: " + escape(film.durata) + "\n"
    if film.trama:
        film_string += "_" + escape(film.trama) + "_\n"
    if film.trailer_link:
        film_string += "[Visualizza trailer](" + film.trailer_link + ")"
    return film_string