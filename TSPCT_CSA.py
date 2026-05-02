import random
import math

def CSA(cords, params):
    global nest_count, best_tour_gen_csa, beta_csa
    best_tour_gen_csa = 0           # definovanie najlepšej generácie na 0
    generations  = int(params.get("CSA generations", 1000))    # počet generácií
    nest_count   = int(params.get("Nest count", 30))            # veľkosť populácie (počet hniezd)
    pa           = float(params.get("CSA_pa", 0.25))           # pravdepodobnosť objavenia cudzieho vajíčka
    step_size    = float(params.get("CSA_step", 0.3))          # veľkosť kroku Lévyho letu
    beta_csa     = float(params.get("CSA_beta", 1.5))          # konštanta leviho skoku
    seed         = int(params.get("CSA_seed", 173))            # seed pre rovnaké náhodné hodnoty
    rnd_csa      = random.Random(seed)

    def dist(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    # funkcia na výpočet vzdialenosti celej trasy
    def route_length(genome, coords):
        total = 0
        for i in range(len(genome)):
            a = coords[genome[i]]
            b = coords[genome[(i + 1) % len(genome)]]
            total += dist(a, b)
        return total
    #objek definujúci záchytné body
    class Nest():
        def __init__(self):
            self.genome = rnd_csa.sample(range(len(cords)),len(cords))#generovanie riešenia
            self.fitness = route_length(self.genome, cords)#pridelenie fitness podla riešenia
        #funckia na reevaluaciu
        def evaluate(self, cords):
            self.fitness = route_length(self.genome, cords)
    #funkcia simulujúca Levyho let
    def flight(genome, step_size):
        new_genome = genome[:]#kopírovanie genómu
        beta = beta_csa # priradenie beta podla hyperparametru
        #výpočet sigma hodnoty podla štandardu
        sigma = (math.gamma(1+beta)*math.sin(math.pi*beta/2))/(math.gamma((1+beta)/2)*beta*2**(((beta-1)/2)))*(1/beta)
        u = rnd_csa.gauss(0, sigma) #normálne rozdelenie čisel
        v = rnd_csa.gauss(0, 1) #normálne rozdelenie čísel
        step = abs(u/(abs(v)**(1/beta))) # výpočet levyho kroku
        swap_count = max(1,int(step_size*step*len(genome)*0.1)) #výpočet počtu swapov ktoré sa budú aplikovať
        swap_count = min(swap_count, len(genome)//2)# obmedzenei velkosti
        #mutácia genotypu, funguje na princípe prehadzovania dvoch náhodných hodnôt
        for _ in range(swap_count):
            x1, x2 = rnd_csa.sample(range(len(genome)),2)
            new_genome[x1], new_genome[x2] = new_genome[x2] , new_genome[x1]
        return new_genome

    population = [Nest() for _ in range(nest_count)] # inicializácia populácie
    best_nest = min(population, key= lambda x: x.fitness)#definovanie najlepšieho riešenia
    global_best = best_nest.fitness#najelpšie fitness
    best_genome = best_nest.genome[:]#najelpšie riešenie TSP
    best_distance = []#pole najlepšej vzdialenosti
    #hlavný generačný ciklus
    for g in range(generations):
        for cuckoo in population:#iterovanie cez populáciu
            new_genome = flight(cuckoo.genome, step_size)#definovanie nového riešenia
            new_fitness = route_length(new_genome, cords)#výpočet fitness nového riešenia
            random_nest = random.choice(population)#výber náhodného člena populácie
            if new_fitness < random_nest.fitness:#porovnanie oproti zmutovanému riešeniu
                random_nest.genome = new_genome#nahradeneie riešenia
                random_nest.evaluate(cords)#reevaluacia jedinca
            abandon_count = max(1 , int(pa*nest_count))#opustenie hniezd
            population.sort(key=lambda x: x.fitness, reverse=True)#usporiadanie populácie
            for i in range(abandon_count):#opustené hniezda sú nahradené
                population[i].genome = rnd_csa.sample(range(len(cords)),len(cords))
                population[i].evaluate(cords)
        #porovnaie s global best a zapísanie výsledkov
        current_best = min(population, key=lambda x: x.fitness)
        if current_best.fitness < global_best:
            global_best = current_best.fitness
            best_genome = current_best.genome[:]
            best_tour_gen_csa = g
        best_distance.append(current_best.fitness)
    best_route = best_genome + [best_genome[0]]
    return best_route, best_distance, best_tour_gen_csa