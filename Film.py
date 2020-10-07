from Genere import render_generi


class Film:
    def __init__(self, xxx_todo_changeme):
        (id_film, titolo, data_uscita, regista, attori, trama, durata, trailer_link, locandina_link,
         locandina) = xxx_todo_changeme
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


def render_film(film, generi=None):
    film_string = "*" + escape(film.titolo) + "*\n"
    if generi is not None:
        generi_string = render_generi(generi)
        if generi_string != "":
            film_string += escape(generi_string) + "\n"
    if film.data_uscita is not None:
        film_string += "Data di uscita: " + escape(film.data_uscita[0:10]) + "\n"
    if film.regista is not None:
        film_string += "Regia: " + escape(film.regista) + "\n"
    if film.attori is not None:
        film_string += "Cast: " + escape(film.attori) + "\n"
    if film.durata is not None:
        film_string += "Durata: " + escape(film.durata) + "\n"
    if film.trama is not None:
        film_string += "_" + escape(film.trama) + "_\n"
    if film.trailer_link is not None:
        film_string += "[Visualizza trailer](" + film.trailer_link + ")"
    return film_string


def escape(input_string):
    return input_string.translate(input_string.maketrans({"(": r"\(",
                                                          ")": r"\)",
                                                          "-": r"\-",
                                                          "]": r"\]",
                                                          "\\": r"\\",
                                                          "^": r"\^",
                                                          "$": r"\$",
                                                          "*": r"\*",
                                                          ".": r"\."}))
