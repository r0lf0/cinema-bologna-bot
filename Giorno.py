import datetime

class Giorno():
    def __init__(self, data, dataFormattata, spettacoli):
        self.data = data
        self.spettacoli = spettacoli
        format_str = '%Y-%m-%d' # The format
        self.dataFormattata = datetime.datetime.strptime(dataFormattata, format_str)

    def __init__(self, data, dataFormattata):
        self.data = data
        self.spettacoli = []
        format_str = '%Y-%m-%d' # The format
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


    def add(self, spettacolo):
        self.spettacoli.append(spettacolo)

    def toStringSenzaData(self):
        output = ""
        for spettacolo in self.spettacoli:
                output += " -" + str(spettacolo) + "\n"
        return output