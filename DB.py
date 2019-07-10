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
            return ":calendar: Film di " + tempData + "\n" + output
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
