# Vedecký benchmark – návod na použitie

Dva nové skripty (bežia bez GUI, oddelene od `TSPCT_main.py`):

- **`TSPCT_experiment_runner.py`** – automaticky spustí 20 nezávislých behov
  pre každú kombináciu (3 prostredia × 3 nastavenia × 4 algoritmy = 36
  kombinácií × 20 behov = **720 behov**), paralelne na všetkých CPU jadrách.
  Výsledky uloží do jedného Excel zošita `results/TSPCT_results.xlsx`.
- **`TSPCT_analyze_results.py`** – doplní do toho istého zošita ďalšie
  hárky: Friedmanov test, post-hoc Wilcoxon (Holm korekcia) a priemerné
  konvergenčné krivky s 95 % intervalom spoľahlivosti (vložené priamo ako
  obrázky do hárku).

## Pred spustením

Súbory `TSPCT_ACO.py`, `TSPCT_GA.py`, `TSPCT_ABC.py`, `TSPCT_PSO.py`
(a `TSPCT_FFA.py`, `TSPCT_CSA.py` ak ich chceš pridať) musia byť v tom
istom priečinku ako oba nové skripty.

**Dôležité:** v `TSPCT_experiment_runner.py`, v slovníku `PARAM_SETS`,
sú momentálne len orientačné (placeholder) hodnoty pre `basic` /
`fast_convergence` / `diversity`. Uprav ich na presné hodnoty, ktoré
chceš mať v článku (buď rovnaké ako v pôvodných 9 experimentoch, alebo
nové – v takom prípade to v článku jasne napíš ako novú metodiku).

## Spustenie

```bash
pip install openpyxl scipy matplotlib --break-system-packages
python TSPCT_experiment_runner.py
python TSPCT_analyze_results.py
```

## Výstup: `results/TSPCT_results.xlsx`

Jeden Excel zošit so 6 hárkami:

| Hárok | Obsah |
|---|---|
| **About** | metodika a popis ostatných hárkov |
| **Raw Results** | 1 riadok = 1 beh (algoritmus, prostredie, nastavenie, run, seed, výsledná dĺžka trasy, generácia najlepšieho riešenia, čas) |
| **Aggregate Stats** | mean/std/min/max/počet behov na kombináciu — počítané **živými Excel formulami** (`AVERAGEIFS`, `SUMPRODUCT`, `MINIFS`, `MAXIFS`) priamo z Raw Results, takže sa prepočítajú automaticky, ak dáta zmeníš |
| **Friedman Test** | test signifikancie rozdielov medzi algoritmami pre každú kombináciu prostredie × nastavenie |
| **Wilcoxon Posthoc** | párové porovnania algoritmov s Holm korekciou (len tam, kde bol Friedman test signifikantný) |
| **Convergence Charts** | graf priemernej konvergencie + 95 % CI pre každú kombináciu, vložený priamo do hárku |

Otvor súbor v Exceli alebo LibreOffice Calc – formuly v hárku **Aggregate
Stats** sa pri otvorení automaticky prepočítajú (je to bežné správanie
pri súboroch generovaných cez openpyxl). Ak by náhodou zostali bunky
prázdne, stačí `Ctrl+Shift+F9` (force recalculate all).

## Odhad času behu

Podľa tvojich pôvodných (jednorazových) meraní trvá jedno kolo všetkých
9 konfigurácií × 4 algoritmy cca **36 minút**. Pri 20 behoch sekvenčne
by to bolo cca **12 hodín** – so `ProcessPoolExecutor` (automaticky
využije všetky jadrá CPU) to na bežnom 8-jadrovom stroji klesne
približne na **1,5–2 hodiny**. Odporúčam spustiť cez noc / na pozadí
(napr. `nohup python TSPCT_experiment_runner.py &` na Linuxe/macOS).

## Poznámka k výberu FFA a CSA

Skript momentálne beží len so 4 algoritmami (ACO, GA, ABC, PSO), aby
sedel s pôvodným experimentom v článku. Ak chceš zahrnúť aj FFA a CSA,
odkomentuj príslušné riadky v `ALGORITHMS` na začiatku
`TSPCT_experiment_runner.py` – funguje to bez ďalších úprav.