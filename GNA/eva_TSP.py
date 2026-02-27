import math, random, copy

class Jedinec :
    def __init__(self, data = []) :
        self.data = copy.deepcopy(data)
        self.delka = 25
        if self.data == [] :
            for i in range(self.delka) :
                self.data.append(random.randint(0,1))

    def __repr__(self) :
        s = ""
        for misto, hodnota in enumerate(self.data) :
            if misto % 5 == 0 :
                s += "\n"
            if hodnota == 1 :
                s += "X"
            else :
                s = s + "0"
        return s

    def fitness(self, cil) :
        f = self.delka
        for misto in range(self.delka) :
            if self.data[misto] != cil[misto] :
                f -= 1
        return f

    def mutuj(self, p_mut) :
        for misto, hodnota in enumerate(self.data) :
            if random.random() < p_mut :
                self.data[misto] = not hodnota

    def skriz_s(self, jedinec) :
        bod_krizeni = random.randint(0, self.delka-1)
        data_syn = self.data[:bod_krizeni] + jedinec.data[bod_krizeni:]
        data_dcera = jedinec.data[:bod_krizeni] + self.data[bod_krizeni:]
        return Jedinec(data_syn), Jedinec(data_dcera)

class Evoluce :
    def __init__(self) :
        self.cil = [0, 0, 1, 0, 0,
           0, 0, 1, 0, 0,
           1, 1, 1, 1, 1,
           0, 0, 1, 0, 0,
           0, 0, 1, 0, 0]
        self.pocet_generaci = 100
        self.p_mut = 0.05
        self.velikost_populace = 20
        self.populace = []
        for i in range(self.velikost_populace) :
            novy_jedinec = Jedinec()
            self.populace.append(novy_jedinec)

    def vyres(self):
        for generace in range(self.pocet_generaci) :
            # jeden krok (jedna generace)
            # selekce
            self.populace.sort( key = (lambda x : Jedinec.fitness(x,self.cil)), reverse=True)
            nova_populace = self.populace[:self.velikost_populace//2]
        
            # krizeni
            for i in range(0, len(nova_populace) -1, 2) :
                syn, dcera = nova_populace[i].skriz_s(nova_populace[i+1])
                nova_populace.append(syn)
                nova_populace.append(dcera)
            # mutace
            for i in range(len(nova_populace)) :
                mutant = copy.deepcopy(nova_populace[i])
                mutant.mutuj(self.p_mut)
                nova_populace.append(mutant)
            # mladi vpred
            self.populace = nova_populace
            # vypis vysledku
            print("vitez generace c. ", generace)
            print(self.populace[0])
        
E = Evoluce()
E.vyres()
