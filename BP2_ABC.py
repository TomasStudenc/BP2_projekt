# ==========================================================
#  ARTIFICIAL BEE COLONY (ABC)
# ==========================================================
import random# knižnica na generovanie náhodných hodnôt
import math# knižnica na matematické operácie ako je odmocnina

def ABC(cords, params):
    global bee_count, best_tour_gen_abc
    best_tour_gen_abc = 0 #definovanie najlepšej generácie na 0
    generations = int(params.get("ABC generations", 1000))#počet generácií ktoré musí algoritmus prejst
    bee_count = int(params.get("Bee count", 20))#velkosť populácie
    employ_rate = float(params.get("employ_rate", 0.7))#percento pracovníkov v populácií
    outlooker_rate = 1 - employ_rate#výpočet na zystenie počtu prihliadacích včiel
    scout_rate = float(params.get("scout_rate", 0.01))#percento skautou v populácií
    seed = int(params.get("ABC_seed", 173))#seed aby sme mali rovanké náhodné hodnoty
    random.seed(seed)#nastavenei seedu
    #funkcia na výpočet vzdialenosti medzi dvoma bodmi
    def dist(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    #funkcia na výpočet vzdialenosti celej trasy
    def route_length(genome, coords):
        total = 0
        for i in range(len(genome)):
            a = coords[genome[i]]
            b = coords[genome[(i + 1) % len(genome)]]
            total += dist(a, b)
        return total
    #funkcia na lokálne prehladávanie riešenia
    def local_search(genome):
        new_sol = genome[:]#kopírovanie genómu
        i, j = random.sample(range(len(genome)), 2)#vyberie dva hodnoty
        new_sol[i], new_sol[j] = new_sol[j], new_sol[i]#prehodí hodnoty
        total = route_length(new_sol, cords)#vypočíta celkovú vzdialenosť
        return total, new_sol
    #class pre pracovné včely
    class EmployBee:
        #prvotné nastavenie včiel
        def __init__(self):
            self.genome = random.sample(range(len(cords)), len(cords))#generovanie genómu
            self.fitness = route_length(self.genome, cords)#výpočet fitness
    #class na prihliadajúce včely
    class Outlooker:
        #prvotné nastavenie včiel
        def __init__(self):
            self.genome = []#genóm je na začiatku prázdny
            self.fitness = float("inf")#fitness je na začiatku nekonečno

    e_population = [EmployBee() for _ in range(int(bee_count * employ_rate))]#vytvornie populácie pracovníkov
    out_population = [Outlooker() for _ in range(int(bee_count * outlooker_rate))]#vytvornie populácie prihliadajúcich včiel
    #funkcia práce včely
    def employ_bee(population):
        for bee in population:#prejde všetky včely v populácií
            tick = 0#počet pokusov
            while True:
                new_fit, new_sol = local_search(bee.genome)#hladanie lokálneho riešenia
                if new_fit < bee.fitness:#hladanie či sa riešenie zlepšilo
                    bee.fitness = new_fit#nastavenei nového fitness
                    bee.genome = new_sol#nastavenei nového riešenia
                    tick = 0#resetovaie pokusov na 0
                else:
                    tick += 1#rvýšenie počtu neúspešných pokusov
                if tick == 5:#po 5 nepodarených pokusoch sa ukončí
                    break
        return sorted(population, key=lambda x: x.fitness)#usporiadanie populácie
    #funkcia pre prihliadajúce včely
    def outlooker_bee(e_population, out_population):
        if not out_population:# ak neexistuje outlooker populácia tak pracujeme iba s pracovníkmi
            return e_population
        inv_fit = [1 / bee.fitness for bee in e_population]#prechádza vštky praacovnícke včely a zbiera fitness
        total = sum(inv_fit)#sčíta fitness hodnoty
        probs = [f / total for f in inv_fit]#pravdepodobnosť výberu daného riešenia
        for _ in range(len(out_population)):#prechádzanie populácie outlookerov
            chosen = random.choices(e_population, weights=probs, k=1)[0]#výber riešenia na základe pravdepodobnostiô
            new_fit, new_sol = local_search(chosen.genome)#lokálne prehladávanie riešenia
            if new_fit < chosen.fitness:#zistenie či je fitness lepšie
                chosen.fitness = new_fit#pridelenie fitness
                chosen.genome = new_sol#pridelenie riešenia
        return e_population
    #funkcia pre scout včely
    def scout_bee(e_population):
        for bee in e_population:#prechádzanie populácie
            if random.random() < scout_rate:#pravdepodobnosť scoutingu
                bee.genome = random.sample(range(len(cords)), len(cords))#generovanie nového riešenia
                bee.fitness = route_length(bee.genome, cords)#ohodnotenie riešenia
        return e_population

    best_distances = []#definovnaie pola na najlepšie riešenia
    best_bee = None#definovanie královnej
    global_best = float("inf")#globálne najlepšie riešenie
    #hlavný ciklus ABC
    for g in range(generations):
        e_population = employ_bee(e_population)#definovanie pracovnej skupiny
        e_population = outlooker_bee(e_population, out_population)#definovanie prihliadajucej populácie
        temp_bee = e_population[0]#pridelenie prvej včely
        e_population = scout_bee(e_population[1:])#scouting
        e_population.insert(0, temp_bee)#pridanie prvej včely na začiatok

        current_best = min(e_population, key=lambda x: x.fitness)#najdenie najlepšieho riešenia
        if current_best.fitness < global_best:#najdenie globálneho maxima
            global_best = current_best.fitness#pridelenie najlepšieho fitness
            best_bee = current_best#pridelenie najlepšej včely
            best_tour_gen_abc = g#pridelenie generácie najelepšieho riešenia

        best_distances.append(global_best)#pridanie do pola
        e_population = sorted(e_population, key=lambda x: x.fitness)[:int(bee_count * employ_rate)]#usporiadanie populácie

    best_route = best_bee.genome + [best_bee.genome[0]]#pridelenie prvého miesta na koniec aby bol uzavretý ciklus
    return best_route, best_distances, best_tour_gen_abc
