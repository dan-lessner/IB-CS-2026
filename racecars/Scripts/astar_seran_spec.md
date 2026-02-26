**Shrnutí (1–2 řádky):** A* nad stavovým prostorem **(x, y, vx, vy)**, přechod = „zrychlení“ **ax, ay ∈ {-1,0,1}**, nová poloha = poloha + nová rychlost; heuristika z předzpracování trati (vlna/BFS od cíle) tak, aby šla snadno přepínat i pro „styl jízdy“ (rychlost/úhel) bez rozbití optimality.

Ty heuristiky se mi asi rozbijou, protože někdy je lepší být dál, když za to můžu být rozjetější? Umíme odhadovat o kolik? Nějaké posčítání vzdálenosti v prostoru x/y a zohlednění rychlosti? Něco jako počet kol, kdybych mohl vzdušnou čarou?

---

## 1) Kontext a cíle algoritmu

1. **Úloha**

   * najít sekvenci tahů (zrychlení) pro autíčko v mřížce s překážkami (track maska: `True=na trati`, `False=mimo`)
   * respektovat fyziku: rychlost je 2D vektor, mění se omezeným zrychlením, poloha se posouvá rychlostí

2. **Optimalita**

   * primární optimalizační kritérium: **minimální počet kroků (tahů / ticků simulace)** do cíle
   * sekundárně (jen volitelně): „styl jízdy“ (preferovat/odmítat vysokou rychlost, ostré zatáčky, cik-cak), ale **nesmí to zhoršit minimální počet kroků**, pokud je požadována striktní optimalita

---

## 2) Vstupy / výstupy

1. **Vstupy**

   * `track[y][x] -> bool` (2D maska trati)
   * `start_pos = (x0,y0)`
   * `start_vel = (vx0,vy0)` (typicky (0,0))
   * `finish_cells = množina buněk cílové rovinky` (může být více buněk)
   * limity rychlosti (pokud existují v engine): `vx_min..vx_max`, `vy_min..vy_max`
   * pravidla kolize/platnosti pohybu (API světa):

     * `is_on_track(x,y)` nebo ekvivalent
     * případně `is_segment_clear((x,y)->(x',y'))` pokud řešíš průjezd přes více buněk při velké rychlosti

2. **Výstupy**

   * plán jako seznam akcí `[(ax1,ay1), (ax2,ay2), ...]`, kde `axi,ayi ∈ {-1,0,1}`
   * volitelně i seznam stavů `[(x,y,vx,vy), ...]` pro debug / vizualizaci

---

## 3) Stavový prostor a přechody

1. **Stav (uzel v A*)**

   * `S = (x, y, vx, vy)`
   * interpretace: auto je v buňce `(x,y)` a má aktuální rychlost `(vx,vy)`

2. **Akce**

   * `A = (ax, ay)` kde `ax, ay ∈ {-1, 0, 1}` (9 možností)

3. **Přechodová funkce**

   * `vx2 = vx + ax`
   * `vy2 = vy + ay`
   * `x2 = x + vx2`
   * `y2 = y + vy2`

4. **Validace přechodu (nutno přesně navázat na API světa)**

   * minimální varianta: cílová buňka musí být na trati: `track[y2][x2] == True`
   * robustnější varianta (doporučená pro vyšší rychlosti):

     * zkontrolovat všechny buňky/segmenty na úsečce `(x,y)->(x2,y2)` (line rasterization / Bresenham) nebo volání enginu `is_segment_clear`
   * případné „out of bounds“ = neplatný přechod

5. **Cena hrany**

   * `cost(S->S2) = 1` (jeden tick)
   * tím pádem A* hledá minimum počtu kroků

---

## 4) Cíl a ukončení

1. **Cílový test**

   * `is_goal(S): (x,y) ∈ finish_cells`
   * můžeš ignorovat rychlost, nebo naopak vyžadovat `vx,vy` v nějakém rozsahu (pokud chceš „dojet“ kontrolovaně) – ale to už mění zadání

2. **Rekonstrukce cesty**

   * klasicky přes `came_from[state] = (prev_state, action_used)`
   * po nalezení cíle vrátit akce v obráceném pořadí

---

## 5) Předzpracování heuristiky „vlna od cíle“

### 5.1 Doporučená (jednodušší a dobře definovaná): BFS v 8-směrech (king moves)

Cíl: pro každou buňku `(x,y)` spočítat dolní odhad minimálního počtu kroků, když by auto mohlo v 1 kroku změnit x i y maximálně o 1 (analogie „max z os“ v otevřeném prostoru).

1. **Definuj sousedy pro BFS**

   * `N8 = {(dx,dy): dx∈{-1,0,1}, dy∈{-1,0,1}, ne (0,0)}`

2. **Multi-source BFS**

   * start fronty = všechny `finish_cells` se vzdáleností 0
   * BFS se šíří jen přes buňky, kde `track[y][x]=True`

3. **Výsledek**

   * `h_grid[y][x] = nejmenší počet kroků (king moves) z (x,y) do cíle při vyhýbání překážkám`
   * pro nedosažitelné buňky `INF`

4. **Heuristika pro A***

   * `h0(S) = h_grid[y][x]`
   * pozn.: je to **dolní odhad** pro tvou fyziku s rychlostí? Často ano jako „relaxace problému“ (auto má reálně omezení, která to můžou jen ztížit), takže h0 typicky nepřestřeluje.

### 5.2 Varianta „dvojí pole X/Y + max“ (bližší tvému popisu, ale hůř definovaná)

Pokud chceš explicitně dvě pole a pak `max`, udělej to takto, aby to mělo přesný význam:

1. **Definice**

   * `hx[y][x]` = minimální počet kroků v relaxovaném pohybu, kde v 1 kroku dovolíš změnu `x` o {-1,0,1} a `y` o {-1,0,1}, ale jako „měřená veličina“ je **počet kroků nutných k dorovnání osy X** v rámci dosažení cíle
   * `hy[y][x]` analogicky pro osu Y
     (prakticky: v BFS neseš i informaci o minimálním „zbývajícím“ |dx_to_goal| a |dy_to_goal|; je to implementačně složitější a často zbytečné, protože `h_grid` už odpovídá zamýšlenému `max`-chování)

2. **Doporučení**

   * pokud nepotřebuješ didakticky ukázat „dvě vlny“, použij 5.1 (jedno pole). Efekt `max(dx,dy)` demonstruješ i tak.

---

## 6) A* – datové struktury a pořadí rozvoje

1. **Open set (prioritní fronta)**

   * klíč `f = g + h`
   * `g[state] = počet kroků od startu`

2. **Closed set / best g**

   * ukládej nejlepší známé `g` pro stav; když přijde horší, zahodit

3. **Generování sousedů**

   * pro každé `(ax,ay)` spočti `S2`
   * pokud neplatné, pokračuj
   * `tentative_g = g[S] + 1`
   * pokud `tentative_g < g_best[S2]`, aktualizuj

4. **Stop podmínka**

   * jakmile vytáhneš z priority queue stav, který splňuje `is_goal`, můžeš skončit (při standardních podmínkách na heuristiku níže)

---

## 7) Heuristika A*: přípustnost vs. monotónnost (konzistence)

1. **Přípustnost (admissible)**

   * `h(n) ≤ skutečná nejmenší cena z n do cíle`
   * důsledek: A* najde optimální řešení (min. kroků), typicky při „tree search“ i „graph search“, ale s různými detaily

2. **Monotónnost / konzistence (consistent)**

   * pro každou hranu `n -> n'` s cenou `c(n,n')` platí:
     `h(n) ≤ c(n,n') + h(n')`
   * důsledek: jakmile je uzel uzavřen (přesunut do closed), už se k němu nemusíš vracet; A* je efektivnější a korektní jako graph search bez reopenů

3. **V tvém nastavení**

   * `c = 1`, takže konzistence je: `h(n) ≤ 1 + h(n')`
   * heuristiky z BFS vzdáleností na gridu (sekce 5.1) bývají konzistentní v tom relaxovaném prostoru; pro 4D stav je konzistence „přeneseně“ často v pohodě, pokud `h` závisí jen na poloze a je to dolní odhad (relaxace)

---

## 8) Parametrická heuristika / preference stylu jízdy (bez rozbití optimality)

Chceš přepínat:

* jen `max`/grid odhad,
* zahrnout velikost rychlosti (Eukleidovsky),
* zahrnout úhel změny rychlosti (min/max).

### 8.1 Bezpečné pravidlo

* Pokud chceš **garanci minimálního počtu kroků**, pak:

  * **heuristiku `h` nech jako dolní odhad** (např. `h0 = h_grid[x,y]`)
  * „styl“ řeš jako **tie-breaker** (sekundární klíč), ne jako přičtení do `h` nebo do `g` (to by měnilo optimalizační kritérium)

### 8.2 Konkrétní návrh prioritního klíče (lexikograficky)

Použij prioritní klíč jako trojici:

1. `f = g + h0`
2. `tiebreak = style_score(state, action)` (menší je lepší; nebo naopak podle přepínače)
3. volitelně `-g` nebo `+g` podle toho, jestli chceš pro stejné `f` preferovat hlubší/plynulejší

Tím zajistíš:

* primárně minimalizuješ počet kroků,
* sekundárně volíš „hezčí“ trasu mezi stejně krátkými řešeními.

### 8.3 Definice volitelných style metrik

1. **Velikost rychlosti**

   * `speed = sqrt(vx*vx + vy*vy)` (Eukleidovsky)
   * varianty:

     * preferovat vyšší rychlost: `style = -speed`
     * preferovat nižší rychlost: `style = +speed`

2. **Úhel změny rychlosti**

   * máš `v_prev = (vx,vy)` a `v_next = (vx2,vy2)`
   * cos úhlu:
     `cosθ = dot(v_prev, v_next) / (|v_prev|*|v_next|)` (ošetři nulu)
   * varianty:

     * minimalizovat úhel (plynulost): maximalizovat `cosθ` ⇒ `style = -cosθ`
     * maximalizovat úhel („kličkování“): minimalizovat `cosθ` ⇒ `style = +cosθ`

3. **Cik-cak „zadarmo“ (demonstrování metrik)**

   * chceš delší geometrickou stopu bez navýšení kroků:

     * to řeš čistě tie-breakem: pro stejné `f` vybírej kroky, které zvětší „lateral movement“ / změní směr / sníží `cosθ` apod.
   * **nepřidávej penalizaci do `g`**, jinak už neoptimalizuješ „počet kroků“.

### 8.4 Pokud naopak chceš záměrně měnit optimalizační kritérium

* pak je to jiný problém (multi-objective nebo vážená cena)
* můžeš použít:

  * **Weighted A***: `f = g + w*h0`, `w>1` (rychlejší, ale bez garance optima)
  * nebo `g = kroky + λ*penalizace` (už nehledáš minimum kroků)

---

## 9) Implementační detaily, které musí být explicitní (aby to šlo rovnou nakódovat)

1. **Rozsahy rychlostí**

   * definuj hranice, jinak stavový prostor může explodovat
   * pokud engine limity nemá, zaveď je prakticky:

     * např. `|vx|,|vy| ≤ VMAX`, kde `VMAX` odvodíš z rozměru mapy nebo z toho, že vyšší rychlosti už nedávají smysl kvůli zatáčkám
2. **Detekce kolize na segmentu**

   * pokud `vx,vy` mohou být >1, samotný check cílové buňky nestačí
   * vyžaduje buď:

     * rasterizaci segmentu (Bresenham) a kontrolu všech průchozích buněk
     * nebo API světa
3. **Paměť a výkon**

   * `g_best` jako dictionary/hashmap nad 4-ticí intů
   * priority queue může obsahovat zastaralé položky; při popu ověř, že `g` odpovídá `g_best`
4. **Nedosažitelnost**

   * pokud open set dojde, vrať „nenalezeno“

---

## 10) Testovací scénáře (minimální sada)

1. rovná trať, start (0,0), cíl (N,0), bez překážek
2. jedna ostrá zatáčka (L) – ověř, že fyzika rychlosti vyžaduje zpomalení/změnu
3. šikana – ověř segmentovou kolizi (pokud rychlosti >1)
4. více cílových buněk – ověř multi-source BFS a cílový test
5. porovnání tie-break módů:

   * stejný počet kroků, ale různé „stylové“ preference vedou k jiné trase

---

## Závěr: co přesně předat codexu jako „kontrakty“

* API validace přechodu: `is_state_valid(x,y,vx,vy)` nebo minimálně `is_on_track` + `is_segment_clear`
* reprezentace cíle: seznam buněk
* parametry:

  * `HEURISTIC_MODE = {GRID_ONLY}`
  * `TIEBREAK_MODE = {NONE, SPEED_MIN, SPEED_MAX, ANGLE_MIN, ANGLE_MAX}`
  * `VMAX` (pokud není z enginu)
* jednoznačná definice: **primární optimalita = minimální počet kroků**, styl jen tie-break (pokud chceš garanci)