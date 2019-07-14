import datetime
from Spettacolo import Spettacolo


class Giorno():

    def __init__(self, data, dataFormattata, spettacoli=None):
        self.data = data
        format_str = '%Y-%m-%d'  # The format
        self.dataFormattata = datetime.datetime.strptime(dataFormattata[0:10], format_str)
        if isinstance(spettacoli, list):
            self.spettacoli = spettacoli
        elif isinstance(spettacoli, Spettacolo):
            self.spettacoli = [spettacoli]
        else:
            self.spettacoli = []

    def __str__(self):
        output = self.data + "\n"
        for spettacolo in self.spettacoli:
            output += "-" + str(spettacolo) + "\n"
        return output

    def __eq__(self, other): 
        if not isinstance(other, Giorno):
            return False
        return str(self) == str(other)
    
    def __hash__(self):
        return hash(str(self))

    def add(self, spettacolo):
        self.spettacoli.append(spettacolo)

    def toStringSenzaData(self):
        output = ""
        for spettacolo in self.spettacoli:
                output += " -" + str(spettacolo) + "\n"
        return output
    
    def getSpettacolo(self, orario, sala):
        for spettacolo in self.spettacoli:
            if spettacolo.orario == orario and spettacolo.sala == sala:
                return orario
        return None

    def getDifferenze(self, other):
        if str(self) == str(other) or self is None:
            return None
        if other is None:
            return self
        
        outGiorno = Giorno(self.data, self.dataFormattata)
        for spettacolo in set(self.spettacoli) - set(other.spettacoli):
            outGiorno.add(spettacolo)
        for spettacoloSelf in self.spettacoli:
            spettacoloOther = other.getSpettacolo(spettacoloSelf.orario)
            if spettacoloOther is not None and (spettacoloSelf.sala != spettacoloOther.sala):
                outGiorno.add(spettacoloSelf)
        return outFilm   

    def toCsv(self, titolo):
        output = ""
        if self is None:
            return output
        if self.spettacoli == []:
            return output
        
        for spettacolo in self.spettacoli:
            output += spettacolo.toCsv(titolo + self.data + ";" + str(self.dataFormattata) + ";")
        return output
