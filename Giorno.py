import datetime


class Giorno():

    def __init__(self, data, dataFormattata, spettacoli):
        self.data = data
        self.spettacoli = spettacoli
        format_str = '%Y-%m-%d'  # The format
        self.dataFormattata = datetime.datetime.strptime(dataFormattata, format_str)

    def __init__(self, data, dataFormattata):
        self.data = data
        self.spettacoli = []
        format_str = '%Y-%m-%d'  # The format
        self.dataFormattata = datetime.datetime.strptime(dataFormattata, format_str)

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
    
    def getSpettacolo(self, orario):
        for spettacolo in self.spettacoli:
            if spettacolo.orario == orario:
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
