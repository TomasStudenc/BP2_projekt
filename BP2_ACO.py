# ==========================================================
#  ANT COLONY OPTIMIZATION
# ==========================================================
import random # knižnica na náhodné hodnoty
import math# knižnica na matematické operácie ako odmocnina

def ACO(cords, params):
    global ant_count, best_tour_gen_aco
    best_tour_gen_aco = 0 #definovanie najlepšej generácie na 0
    generation = int(params.get("ACO generations", 1000))# počet generácie mravcou
    ant_count = int(params.get("Ant count", 5))#velkosť populácie
    alpha = float(params.get("Alpha", 1.0))#dopad feromónovej cesty
    beta = float(params.get("Beta", 2.0))#dopad visibility
    evap_rate = float(params.get("Evaporation rate", 0.1))#množsvo evaporácie feromónov
    Q = float(params.get("Q", 100.0))#množstvo feromónov pri ohodnocovaní
    seed = int(params.get("ACO_seed", 173))#random seed aby sme mali rovanké náhodné hodnoty
    random.seed(seed)#priradenie seedu
    #class na prostredie
    class Environment:
        #prvotné nastavnie prostredia
        def __init__(self):
            self.city_coords = cords#koordináty vrcholov grafu
            self.cities = len(cords)#počet vrcholov v grafe
            #vytvorenie matice vzdialeností kotrá ukladá vzdialenosti medzi všetkými vrcholmi
            self.distance = [[math.dist(cords[i], cords[j]) if i != j else 0 for j in range(self.cities)] for i in range(self.cities)]
            #vytvorenie matice feromónov ktorá ukladá všetky feromónové ohodnotenia medzi vrcholmi
            self.pheromones = [[1 / (self.distance[i][j] * self.cities) if i != j else 0 for j in range(self.cities)] for i in range(self.cities)]
        #funkcia na evaporáciu feromónov na hranách
        def evapor(self):
            #prejde všetky hrany
            for i in range(self.cities):
                for j in range(self.cities):
                    self.pheromones[i][j] *= (1 - evap_rate)#vynásoby evaporáciou
    #funkcia na výpočet pravdepodobnosti
    def probability(env, current, unvisited):
        num = []#pole váh
        for j in unvisited:#pozrie na všetky nenavštívené vrcholy
            tau = env.pheromones[current][j]#pozrie sa na feromóny medzi aktuálnym vrchol a ostatnými vrcholmi
            eta = 1 / env.distance[current][j]#pozrie sa na vzdialenosť medzi aktuálnim vrcholm a ostatnými vrcholmi
            num.append((tau ** alpha) * (eta ** beta))#vypočíta váhu
        total = sum(num)#spočíta pravdepodobnosti
        return [n / total for n in num]#vráti maticu pravdepodobností
    #funkcia na vytvorenie cesty
    def construct_tour(env):
        start = random.randint(0, env.cities - 1)#vyberie náhodný index
        tour = [start]#prily náhodný index ako počiatočný bod
        unvisited = list(set(range(env.cities)) - {start})# vytvorí list nenavštívených miest
        current = start# nastavý current na štart
        while unvisited:#kým existujú nenavštívené vrchli
            probs = probability(env, current, unvisited)#výpočet pravdepodobnostnej matice
            next_city = random.choices(unvisited, weights=probs)[0]#vyberie dalšei vrchol na základe pravdepodobnosti
            tour.append(next_city)#pridá vrchol do cesty
            unvisited.remove(next_city)#vymaže vrchol z nenavštívených
            current = next_city#presunie sa na ďlaši vrchol
        tour.append(start)#na koncie pridá pôvodné mesto aby sa uzavrel ciklus
        return tour
    #funkcia na výpočet dĺžky cesty
    def tour_length(env, tour):
        return sum(env.distance[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))
    #funkcia na aktualizáciu feromónou
    def update_pheromones(env, tours):
        env.evapor()#evaporuje
        for tour in tours:#prejde trasu
            L = tour_length(env, tour)#pridelý dĺžku cesty
            for i in range(len(tour) - 1):#prejde celú cestu
                a, b = tour[i], tour[i + 1]#definuje vrcholy ktoré sa aktualizujú
                env.pheromones[a][b] += Q / L#pridá hodnotu feromónov pre trasu z a do b
                env.pheromones[b][a] += Q / L#pridá hodnotu feromónov pre trasu z b do a

    env = Environment()#vytvorenei prostredia
    best_tour, best_length = None, float("inf")#definovanie globálne najlepšich riešení
    best_lengths, best_tours_over_time = [], []#definovanie polí pre najlepšie riešenia
    #Hlavný ciklus ACO
    for g in range(generation):
        tours = []#definovanie ciest
        for _ in range(ant_count):#prechádza podla vlakosti populácie
            t = construct_tour(env)#vytvorenie cesty
            tours.append(t)#pridanie cesty do pola ciest
            L = tour_length(env, t)#zistenie dĺžky cesty
            if L < best_length:#zistenie či je cesta novým najlepším riešením
                best_tour, best_length = t, L#nastavenie cesty a dĺžky cesty ako nový globálny best
                best_tour_gen_aco = g#nastavenei najlepšej generácie
        update_pheromones(env, tours)#aktualizácia feromónov
        best_lengths.append(best_length)#pridanie dĺžky do pola
        best_tours_over_time.append(best_tour)#pridanie cesty do pola

    return best_tours_over_time, best_lengths, best_tour_gen_aco

