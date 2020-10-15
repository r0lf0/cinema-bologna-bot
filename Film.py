from Genere import render_generi


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
