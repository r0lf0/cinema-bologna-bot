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

    def add(self, giorno):
        self.giorni.append(giorno)
