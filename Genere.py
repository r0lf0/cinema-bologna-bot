class Genere:
    def __init__(self, id_film, genere):
        self.id_film = id_film
        self.genere = genere


def render_generi(generi):
    output_string = ""
    if generi:
        output_string += "Genere: "
        for genere in generi:
            output_string += genere + ", "
        output_string = output_string[:-2]
    return output_string
