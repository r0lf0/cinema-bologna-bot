import datetime
from pytz import timezone
import pytz
from Film import Film
from Giorno import Giorno
from Spettacolo import Spettacolo


class DB():
    
    def __init__(self, inputCsv="NienteCsv"):
        if inputCsv == "NienteCsv":
            self.films = []
            self.dataUltimaModifica = str(datetime.datetime.now(pytz.timezone('Europe/Rome')))
        else:        
            self.films = []
            for line in inputCsv.split('\n'):
                campi = line.split(';')
                if campi[0] == "DataUltimaModifica":
                    self.dataUltimaModifica = campi[1]
                elif len(campi) == 5:
                    spettacoloCsv = Spettacolo(campi[3], campi[4])
                    giornoCsv = Giorno(campi[1], campi[2], [spettacoloCsv])
                    filmCsv = Film(campi[0], [giornoCsv])       
                    film = self.getFilm(filmCsv.titolo)
                    if film is not None:
                        giorno = film.getGiorno(giornoCsv.data)
                        if giorno is not None:
                            spettacolo = giorno.getSpettacolo(spettacoloCsv.orario, spettacoloCsv.sala)
                            if spettacolo is None:
                                giorno.add(spettacoloCsv)
                            # else: due entry uguali
                        else:
                                film.add(giornoCsv)
                    else:
                        self.add(filmCsv)

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
        
        outCsv = ""
        selfCsv = self.toCsv()
        otherCsv = other.toCsv()
              
        for lineSelf in selfCsv.split("\n"):
            if lineSelf.split(';')[0] != "DataUltimaModifica":
                trovato = False
                for lineOther in otherCsv.split("\n"):
                    if lineSelf == lineOther:
                        trovato = True
                if trovato == False:
                    outCsv += lineSelf + "\n"
                
        outDB = DB(outCsv)      
        return outDB
        
    def toCsv(self):
        output = ""
        if self is None:
            return output
        output += "DataUltimaModifica;" + self.dataUltimaModifica + "\n"
        if self.films == []:
            return output
        for film in self.films:
            output += film.toCsv()
        return output

