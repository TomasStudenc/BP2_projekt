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

    def solution_distance(genome1, genome2):
        diff = sum(1 for i in range(len(genome1)) if genome1[i] != genome2[i])
        return diff / len(genome1)

    def move_tovard(source, target, beta, cords):
        new_genome = source[:]
        swap_count = max(1,int(beta * len(source)))
        for _ in range(swap_count):
            diff= [i for i in range(len(source)) if new_genome[i] != target[i]]
            if not diff:
                break
            choice = rnd_ffa.choice(diff)
            current_index = new_genome.index(target[choice])
            new_genome[choice], new_genome[current_index] = new_genome[current_index], new_genome[choice]

        random_count = max(1,int(alpha * len(source)))
        for _ in range(random_count):
            x1, x2 = rnd_ffa.sample(range(len(source)), 2)
            new_genome[x1], new_genome[x2] = new_genome[x2], new_genome[x1]
        return new_genome

    class Firefly():
        def __init__(self):
            self.genome = rnd_ffa.sample(range(len(cords)), len(cords))
            self.fitness = route_length(self.genome, cords)
            self.brightness = 1.0/self.fitness

        def evaluate(self, cords):
            self.fitness = route_length(self.genome, cords)
            self.brightness = 1.0/self.fitness



    population = [Firefly() for _ in range(firefly_count)]
    best_ff = min(population, key=lambda x: x.fitness)
    global_best_ff = best_ff.fitness
    best_genome = best_ff.genome[:]
    best_distance = []

    for g in range(generations):
        for firefly1 in population:
            for firefly2 in population:
                if firefly2.brightness > firefly1.brightness:
                    r = solution_distance(firefly1.genome, firefly2.genome)
                    beta = beta0 * math.exp(-gamma * (r**2))
                    new_genome = move_tovard(firefly1.genome, firefly2.genome, beta, cords)
                    new_fitness = route_length(new_genome, cords)
                    if new_fitness < firefly1.fitness:
                        firefly1.genome = new_genome
                        firefly1.evaluate(cords)
        current_best = min(population, key=lambda x: x.fitness)
        if current_best.fitness < global_best_ff:
            global_best_ff = current_best.fitness
            best_genome = current_best.genome[:]
            best_tour_gen_ffa = g

        best_distance.append(current_best.fitness)
    best_route = best_genome + [best_genome[0]]
    return best_route, best_distance, best_tour_gen_ffa