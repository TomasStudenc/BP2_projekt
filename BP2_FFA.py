import random
import math

def FFA (cords, params):
    global firefly_count , best_tour_gen_ffa
    best_tour_gen_ffa = 0  # definovanie najlepšej generácie na 0
    generations    = int(params.get("FFA generations", 1000))   # počet generácií
    firefly_count  = int(params.get("Firefly count", 30))       # veľkosť populácie
    alpha          = float(params.get("FFA_Alpha", 0.2))            # koeficient náhodnosti pohybu
    beta0          = float(params.get("Beta0", 1.0))            # maximálna príťažlivosť (pri nulovej vzdialenosti)
    gamma          = float(params.get("Gamma", 1.0))            # koeficient absorpcie svetla (ako rýchlo klesá príťažlivosť)
    seed           = int(params.get("FFA_seed", 173))           # seed pre rovnaké náhodné hodnoty
    rnd_ffa        = random.Random(seed)

    #funckia na euklidovský výpočet vzdialenosti
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

    #porovnanie dvoch riešení a zistenie vzidalenosti týchto riešení
    def solution_distance(genome1, genome2):
        diff = sum(1 for i in range(len(genome1)) if genome1[i] != genome2[i]) # ak sú riešenia rovanké výde 0 ak úplne odlišné výde 1
        return diff / len(genome1)
    #posun riešení smerom od source do target
    def move_toward(source, target, beta, cords):
        new_genome = source[:] # kopírovanie genotypu
        swap_count = max(1,int(beta * len(source)))#výpočet počtu výmen 
        for _ in range(swap_count):#ciklus na výmeny
            diff= [i for i in range(len(source)) if new_genome[i] != target[i]]#hladá ktoré sa nezhedujú
            if not diff:
                break
            choice = rnd_ffa.choice(diff)#vvberie hednotu z tých ktoré sa nezhodujú
            current_index = new_genome.index(target[choice]) # získanie indexu
            new_genome[choice], new_genome[current_index] = new_genome[current_index], new_genome[choice] # prehodnenie hodnôt
        #náhodný pohyb v priestore
        #vyber počtu výmen
        random_count = max(1,int(alpha * len(source)))
        #cyklus kde sa v rámci jedného genotypu vymienajú hodntoy
        for _ in range(random_count):
            x1, x2 = rnd_ffa.sample(range(len(source)), 2)
            new_genome[x1], new_genome[x2] = new_genome[x2], new_genome[x1]
        return new_genome
    #objekt svetluška
    class Firefly():
        def __init__(self):
            self.genome = rnd_ffa.sample(range(len(cords)), len(cords)) #definovanie možného riešenia
            self.fitness = route_length(self.genome, cords)#ocenenie svojho riešenia
            self.brightness = 1.0/self.fitness#výpočet svietivosti
        #funkcia na reevaluáciu
        def evaluate(self, cords):
            self.fitness = route_length(self.genome, cords)
            self.brightness = 1.0/self.fitness

    population = [Firefly() for _ in range(firefly_count)] #inicializovanie populácie
    best_ff = min(population, key=lambda x: x.fitness)#najlepšia svetluška
    global_best_ff = best_ff.fitness#najelpšie fitness
    best_genome = best_ff.genome[:]#najlepšie riešenie
    best_distance = []#pole kde sa uchovávajú hodnoty najlepších riešení
    #halvný generačný ciklus
    for g in range(generations):
        #iterovanie cez celú populáciu, operácia sa uskotočnuje na každú s každým
        for firefly1 in population:
            for firefly2 in population:
                #porovnanie svietivosti
                if firefly2.brightness > firefly1.brightness:
                    #zistenie rozdielu riešení
                    r = solution_distance(firefly1.genome, firefly2.genome)
                    #výpočet príťažlivosti
                    beta = beta0 * math.exp(-gamma * (r**2))
                    #pohyb svetlušky k druhej svetluške
                    new_genome = move_toward(firefly1.genome, firefly2.genome, beta, cords)
                    #výpočet nvého fitness
                    new_fitness = route_length(new_genome, cords)
                    #ak je fitness lepší tak si ho svetluška zachová
                    if new_fitness < firefly1.fitness:
                        firefly1.genome = new_genome
                        firefly1.evaluate(cords)
        #porovnávanie s globálne najlepším riešením aby sa zistil vývoj riešenie v danej generácií
        current_best = min(population, key=lambda x: x.fitness)
        if current_best.fitness < global_best_ff:
            global_best_ff = current_best.fitness
            best_genome = current_best.genome[:]
            best_tour_gen_ffa = g
        best_distance.append(current_best.fitness)
    best_route = best_genome + [best_genome[0]]
    return best_route, best_distance, best_tour_gen_ffa