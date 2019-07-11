class Film():

    def __init__(self, titolo, giorni):
        self.titolo = titolo
        self.giorni = giorni

    def __init__(self, titolo):
        self.titolo = titolo
        self.giorni = []

    def __str__(self):
        output = ":clapper: " + self.titolo + " :clapper:" + "\n"
        for giorno in self.giorni:
            output += str(giorno)
        return output

    def __eq__(self, other): 
        if not isinstance(other, Film):
            return False
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def add(self, giorno):
        self.giorni.append(giorno)

    def getGiorno(self, data):
        for giorno in self.giorni:
            if giorno.data == data:
                return giorno
        return None

    def getDifferenze(self, other):
        if str(self) == str(other) or self is None:
            return None
        if other is None:
            return self
        
        outFilm = Film(self.titolo)
        for giorno in set(self.giorni) - set(other.giorni):
            outFilm.add(giorno)
        for giornoSelf in self.giorni:
            giornoOther = other.getGiorno(giornoSelf.data)
            if giornoOther is not None:
                outFilm.add(giornoSelf.getDifferenze(giornoOther))
        return outFilm
