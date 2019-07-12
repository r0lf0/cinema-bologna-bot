import datetime
from pytz import timezone
import pytz


class DB():

    def __init__(self):
        self.films = []
        self.dataUltimaModifica = str(datetime.datetime.now(pytz.timezone('Europe/Rome')))

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
    
    def __hash__(self):
        return hash(str(self))

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
        self.dataUltimaModifica = str(datetime.datetime.now(pytz.timezone('Europe/Rome')))

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
    
    def getFilm(self, titolo):
        for film in self.films:
            if film.titolo == titolo:
                return film
        return None

    def getDifferenze(self, other):
        if str(self) == str(other) or self is None:
            return None
        if other is None:
            return self
 
        outDB = DB()       
        for film in set(self.films) - set(other.films):
            outDB.add(film)
        for filmSelf in self.films:
            filmOther = other.getFilm(filmSelf.titolo)
            if filmOther is not None:
                outDB.add(filmSelf.getDifferenze(filmOther))
        return outDB
        
