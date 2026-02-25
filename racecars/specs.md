* **Shrnutí:** hot-seat “papírové závody” na čtvercové mřížce; pozice jen v průsečících; pohyb přes vektor rychlosti s akcelerací ±1/osa; náhodný generátor tratě s parametry v čtverečcích; náraz = penalizace + reset rychlosti + náhodný nejbližší průsečík; kolize jen shoda cílových bodů; segment musí ležet uvnitř tratě (dotyk okraje validní); ovládání myší přes klik na zvýrazněné možné cíle; UI oddělené od simulace (fyziky).

## 1) Základní pojmy a reprezentace

* **Mřížka (grid):**

  * rozměr: `W x H` v *počtu čtverců* (cells)
  * průsečíky (vertices): souřadnice `x,y` v rozsahu `0..W`, `0..H`
* **Trať:**

  * binární maska buněk `road[cell_x][cell_y] ∈ {0,1}` (1 = „uvnitř trasy“)
  * startovní čára: osa-rovnoběžný úsek (horiz/vert) na hraně tratě, délka ≥ počet hráčů (+ rezerva)
  * cílová čára: osa-rovnoběžný úsek, jasně odlišený

  * cilova cara je **na hranici hriste** (napr. `x = W`), aby byla viditelna

## 2) Datový model – oddělení fyziky a grafiky

### 2.1 Simulace / fyzika (bez UI)

* **GameState (sim):**

  * `track: Track`
  * `cars: list[Car]`
  * `current_player_idx: int`
  * `finished: bool`
  * `winners: list[int]` (id vítězů; remíza je OK)
* **Track (sim):**

  * `W, H: int` (v čtverečcích)
  * `road_mask: 2D bool` (cells)
  * `start_vertices: list[Vertex]` (průsečíky na startovní čáře)
  * `finish_line: FinishLine` (geometrie cílové čáry)
  * metody:

    * `segment_is_valid(p0, p1) -> bool`

      * **požadavek:** celý segment uvnitř trasy (teleport skrz zeď zakázán)
      * **dotyk okraje validní**
    * `nearest_inside_vertex(point) -> Vertex`

      * **především jednoduché**; při více kandidátech **náhodně**
    * `segment_crosses_finish(p0, p1) -> bool`
* **Car (sim):**

  * `id: int`
  * `name: str` (**náhodně volené** při vytvoření)
  * `pos: Vertex` (x,y)
  * `vel: Vector2i` (x,y; celé)
  * `penalty: int`
  * `path: list[Segment]` (pro replay/log; vizualizace si to jen čte)

  * jmena aut jsou **nahodna**, bez kolizi 

### 2.2 Grafika / UI (render + input)

* **Renderer / View:**

  * drží pouze stav zobrazení (zoom/pan) a umí vykreslit `GameState`
  * `camera: {zoom, offset}`
  * `follow_current: bool` (nice to have)
  * `show_grid: bool` (nice to have)
* **Controller / Input:**

  * z `GameState` spočte *klikatelné cíle* a mapuje klik → `apply_move(target_vertex)`
  * žádná pravidla fyziky v renderu

## 3) Pohyb a tah (fyzika)

* **Pořadí:** hráči stále dokola (round-robin)
* **Start:**

  * hráči rozlosováni na různé `start_vertices`
  * `vel=(0,0)`
  * auta se **nahodne rozlosuji** na `start_vertices` (bez poradi)

* **Pravidlo akcelerace:**

  * zvol `ax, ay ∈ {-1,0,+1}`
  * `vel' = (x+ax, y+ay)`
  * `pos' = pos + vel'`
* **UI výběr:**

  * v tahu se zvýrazní **všechny** validní `pos'` dosažitelné přes `ax,ay ∈ {-1,0,+1}`
  * klik na `pos'` → sim provede tah

  * pri penalizaci (cekani) je **jediny mozny cil** soucasna pozice a hrac na ni musi kliknout

## 4) Validita tahu

### 4.1 Segment uvnitř tratě (povinné)

* validní, pokud `track.segment_is_valid(pos, pos') == True`
* implementačně (jednoduše):

  * projít segment mřížkou (např. Bresenham / supercover) → seznam buněk, kterými segment prochází
  * všechny tyto buňky musí mít `road=1`
  * **dotyk hranice tratě je OK**: test „uvnitř“ chápat jako *včetně okraje* (u hranaté masky to typicky znamená, že buňky, které segment „líže“, jsou road)

  * **zakaz tunelovani:** pokud segment opusti trat, auto narazi v **prvnim okamziku** opusteni

### 4.2 Kolize auto–auto (zjednodušení)

* **jen varianta 1:** kolize pouze když `pos'_i == pos'_j` (shoda cílových průsečíků)
* křížení segmentů i „projíždění přes stojící“ se **neřeší**

## 5) Následek nárazu

* **Náraz do auta nebo mimo trať:**

  * `pos := track.nearest_inside_vertex(collision_point)`

    * collision_point: pro jednoduchost použít `pos'` (zamýšlený cíl) nebo „nejbližší validní“ bod na segmentu; **priorita: přímočarost**
    * při více kandidátech: **náhodně**
  * `vel := (0,0)`
  * `penalty := 2`

  * i pri narazu se do `car.path` prida **usek z predchozi pozice do mista narazu**

## 6) Cíl a konec hry

* `segment_crosses_finish(pos, pos')` → auto „dojelo“
* **remíza OK:** pokud dojede více aut (v různých tazích nebo stejné „kolo“ podle pořadí), evidovat je jako vítěze bez tie-breaku

  * prakticky: jakmile první auto protne cíl, můžeš (A) hru ukončit okamžitě, nebo (B) nechat doběhnout zbytek „kola“ a připsat další dojezdy do remízy
  * vyber jednu implementační variantu (A je nejjednodušší; B je férovější)

  * pouzita varianta **B**: po prvnim dojezdu dojede **zbytek kola**
  * pokud segment protne cil, **cilem se stane bod na cilove care**

## 7) UI/UX a ovládání

### 7.1 Setup okno

* setup okno jako celek je **nice to have**

* vstupy (kde dává smysl **v čtverečcích**):

  * `W,H` (velikost pole v čtverečcích)
  * `players (2..10)`
  * `track_width_mean` (čtverečky)
  * `track_width_var` (čtverečky)
  * `turn_sharpness (0..100)`
  * `turn_density (0..100)`
  * `seed` (volitelně)
* akce:

  * `Generate track`
  * `Start game`
* pozn.: on-the-fly regen při posouvání je volitelné (není nutné)

* parametry lze zadat i **z konzole** (pokud jsou predany, automaticky prepisou defaulty)

### 7.2 Herní okno

* zobrazení:

  * road maska + start/cíl
  * auta jako barevná kolečka
  * zvýraznění hráče na tahu
  * zvýrazněné klikatelné cíle
  * stopy: lomené čáry podle `car.path`
  * pro auto na tahu se kresli **slabe spojnice** do vsech validnich cilu
  * pri moznosti dojezdu se nabizi **cilovy bod primo na cilove care**

* ovládání:

  * klik na cíl
  * zoom in/out (nice to have)
  * pan (nice to have)
  * „follow current car“ (centrovat kameru na auto na tahu) (nice to have)

## 8) Generátor tratě (parametry v čtverečcích)

* cíle:

  * souvislá trať start→cíl
  * start/cíl osa-rovnoběžné a dost dlouhé
  * obtížnost řízená parametry
* postup (koncept):

  1. zvolit startovní čáru u okraje pole
  2. zvolit cílovou čáru na protějším okraji
  3. vygenerovat středovou polyline po buňkách s biasem k cíli

     * `turn_density` = jak často měnit směr
     * `turn_sharpness` = jak „prudce“ (časté 90°/krátké rovinky vs delší rovinky)
  4. „ztlustit“ na road masku

     * šířka v čtverečcích: `track_width_mean ± track_width_var`
     * sirka trate se **meni po trase** (nekolikrat) a je v rozmezi **0.8x az 2x pocet hracu**
     * minimalni sirka je **aspon 2 uzly**
     * sirka trate je zaroven **omezena vyskou** hriste
  5. validace souvislosti a dosažitelnosti; případně regen
     * overit, ze z kazdeho startu vede **spojita cesta** po road mask k cilove care
     * pokud ne, **regenerovat** celou trat

## 9) Defaulty

* `W,H`: např. 60×40 (čtverečky)
* `players`: 2
* `track_width_mean`: 6 (čtverečky)
* `track_width_var`: 2
* `turn_density`: 50
* `turn_sharpness`: 50
* penalizace: 2 tahy

## 10) Upresneni z implementace a z diskuse

* tyto body byly **presunuty do vhodnejsich sekci**:
  * sekce 1 (Trat): cilova cara na hranici hriste
  * sekce 2.1 (Car): nahodna jmena bez kolizi
  * sekce 3 (Start/UI vyber): nahodne rozlosovani + klik pri penalizaci
  * sekce 4.1 (Validita): zakaz tunelovani a naraz v prvnim okamziku opusteni
  * sekce 5 (Nasledek narazu): stopa do mista narazu
  * sekce 6 (Cil a konec): varianta B + cilovy bod na care
  * sekce 7.1 a 7.2 (UI): konzolove parametry + slabe spojnice + cilovy bod na care
  * sekce 8 (Generator): omezeni sirky trate
