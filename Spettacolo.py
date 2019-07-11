class Spettacolo():

    def __init__(self, orario, sala):
        self.orario = orario
        self.sala = sala

    def __str__(self):
        return self.orario + " sala " + self.sala

    def __eq__(self, other): 
        if not isinstance(other, Spettacolo):
            return False
        return str(self) == str(other)
    
    def __hash__(self):
        return hash(str(self))
