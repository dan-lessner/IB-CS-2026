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

# nastaveni evoluce
velikost_populace = 32
pocet_generaci = 20
delka_DNA = pocet_predmetu
pst_mutace = 1.0/delka_DNA ############ jak to bude zrat float? ocisti deleni

import random
random.seed(0)

def novy_seznam( hodnota, pocet ) :
    seznam = []
    for i in range( pocet ) :
        seznam = seznam + [hodnota]				#########šš je to lepsi nez append???
    return seznam

### pomocne funkce
def soucin_po_prvcich( s1, s2 ):	## tzv. "skalarni soucin", ale to budete probirat az pozdeji
    S = 0
    for i in range( len(s1) ):		# predpokladame, ze jsou seznamu stejne dlouhe
        S = S + s1[i] * s2[i]		# postupne vynasobi odpovidajici prvky seznamu a souciny secte, neboli s1[0]*s2[0] + s1[1]*s2[1] + s1[2]*s2[2] + ...
    return S

def fitness( jedinec ):
    if soucin_po_prvcich( jedinec, hmotnosti ) <= nosnost_batohu :
        return soucin_po_prvcich( jedinec, ceny )
    else :
        return 0
   
def mutuj( mutant ):
    for pozice in range( delka_DNA ) :
      if random.random() <= pst_mutace :
        if mutant[pozice] == 0 :
          mutant[pozice] = 1
        else :
          mutant[pozice] = 0

def zkriz( tata, mama ):
    synek = novy_seznam( 0, delka_DNA )
    dcera = novy_seznam( 0, delka_DNA )
    pozice = random.randrange( delka_DNA )
    for i in range( pozice ) :
      synek[i] = tata[i]     
      dcera[i] = mama[i]
    for i in range( pozice, delka_DNA ) :
      synek[i] = mama[i]
      dcera[i] = tata[i]
    return [synek, dcera]

### inicializace populace
populace = []
for i in range( velikost_populace ) :
    miminko = novy_seznam( 0, delka_DNA )
    for cislo_kodonu in range( delka_DNA ) :
        miminko[cislo_kodonu] = random.randrange( 2 )
    populace = populace + [ miminko ]

### evoluce
for plonkova_promenna in range( pocet_generaci ) :
    # selekce - "turnajova"
    random.shuffle(populace)
    prezivsi = []    
    for i in range( 0, len(populace), 2 ) :
        if fitness(populace[i]) >= fitness(populace[i+1]) :
            prezivsi = prezivsi + [ populace[i]   ]
        else :
            prezivsi = prezivsi + [ populace[i+1] ]
    # krizeni
    krizenci = []
    for i in range( 0, len(prezivsi), 2 ) :
        krizenci = krizenci + zkriz(prezivsi[i], prezivsi[i+1])
    # slozeni dalsi generace: vitezove turnaju a jejich deti
    populace = prezivsi + krizenci
    # mutace
    for jedinec in populace :
        mutuj(jedinec)
    
### vypis vysledku
F = 0
nejlepsi_jedinec = None
for j in populace :
    if fitness(j) > F :
        nejlepsi_jedinec = j
print ("vitez: ", nejlepsi_jedinec)
print ("fitness: ", fitness(nejlepsi_jedinec),
", cena: ", soucin_po_prvcich(nejlepsi_jedinec, ceny),
", hmotnost: ", soucin_po_prvcich(nejlepsi_jedinec, hmotnosti))
