## dobrovolny domaci ukol:
# 0) Jsou "evolucni algoritmy" vubec algoritmy? Diskutuj o jednotlivych vlastnostech.
# 1) Kolik vyskousi zpusobu zabaleni tento algoritmus,
#    kolik by bylo treba pri zkouseni vsech moznosti?
# 2) Zaved nejake rozumne ukoncovaci kriterium, at se nepocita zbytecne dlouho.
# 3) Vytvor graf, ktery co nejlepe vystihuje, je se v populaci vyviji fitness.
#    Tzn. pripis vypis statistik (promysli jakych), vloz je do Excelu...
# 4) Proc kvalita populace muze klesnout? Uprav kod tak, aby k tomu nedochazelo.
# 5) Najdi pet zasadnich rozdilu tohoto algoritmu a prirozene evoluce.
#    Rozhodni, jestli by jejich implementace vypoctu pomohla, nebo ne, nebo je to jedno.
# 6) Zkus jestli te napadne takova uprava, ktera by v prirode byla "podvod",
#    ale vypoctu to pomuze.
# 7) Implementuj nejakou zmenu (dvoubodove krizeni, ruletova selekce
#    - vyhledej si, co to je) a porovnej puvodni a novy vypocet. Jak rychle
#    dojdeme k vysledku, s jakou mirou jistoty a tak.
# 8) Hledej jina zadani - tezka pro cloveka, lehka pro ev. alg., nebo treba naopak...

# vstupy
nosnost_batohu = 50
pocet_predmetu = 10
hmotnosti = [5, 8, 12, 25, 45, 10, 13, 32, 4, 7]
ceny =      [1, 3, 6,   3,  20, 9, 20, 15, 6, 2]

velikost_populace = 32
pst_mutace = .1

import random, copy
random.seed(0)

### pomocne funkce
def ss( v1, v2 ):
    S = 0
    for i in range(len(v1)):
        S += v1[i] * v2[i]
    return S

def fitness( jedinec ):
    if ss(jedinec, hmotnosti) <= nosnost_batohu :
        return ss(jedinec, ceny)
    else :
        return 0

def krizeni( tata, mama ):
    pozice = random.randint(0, len(tata)-1 )
    syn = tata[:pozice] + mama[pozice:]
    dcera = mama[:pozice] + tata[pozice:]
    return [syn, dcera]
    
def mutace( mutant ):
    pozice = random.randint(0, len(mutant)-1 )
    mutant[pozice] = (mutant[pozice]+1) % 2

### inicializace populace
populace = []
for i in range(velikost_populace) :
    miminko = []
    for j in range(pocet_predmetu) :
        miminko.append(random.randint(0,1))
    populace.append(miminko)

### evoluce
#while ukoncovaci_kriterium
for plonkova_promenna in range(20) :
    # selekce - "turnajova"
    prezivsi = []    
    for i in range(0,len(populace),2) :
        if fitness(populace[i]) >= fitness(populace[i+1]) :
            postupujici = populace[i]
        else :
            postupujici = populace[i+1]
        # mutace
        if random.random() <= pst_mutace :
            mutace(postupujici)
        prezivsi.append(postupujici)
    # krizeni
    krizenci = []
    for i in range(0,len(prezivsi),2) :
        krizenci.extend(krizeni(prezivsi[i], prezivsi[i+1]))
    # slozeni dalsi generace        
    populace = prezivsi + krizenci
    random.shuffle(populace)
    # tady lze pripsat vypis statistik
    F = 0
    vitez = None
    for j in populace :
        if fitness(j) > F :
            vitez = j
    #print ("prozatimni vitez: ", vitez)
    print ("fitness: ", fitness(vitez), ", cena: ", ss(vitez, ceny), ", hmotnost: ", ss(vitez, hmotnosti))
    
### vypis vysledku
F = 0
vitez = None
for j in populace :
    if fitness(j) > F :
        vitez = j
print ("vitez: ", vitez)
print ("fitness: ", fitness(vitez), ", cena: ", ss(vitez, ceny), ", hmotnost: ", ss(vitez, hmotnosti))
