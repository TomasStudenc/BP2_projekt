# ==========================================================
#  PARTICLE SWARM OPTIMIZATION (PSO)
# ==========================================================
import random#knižnica na náhodné hodnoty
import math#knižnica na matematické funkcie ako je odmocnina

def PSO(cords, params):
    global particle_count, best_tour_gen_pso
    best_tour_gen_pso = 0#definovanie najlepšej generácie na 0
    iterations = int(params.get("PSO generations", 1000))#definovanie počtu iterácií kotré algoritmus podstúpi
    particle_count = int(params.get("Particle count", 10))#velkosť populácie
    c1 = float(params.get("c1", 1.5))#koeficient na lokálne zlepšovanie
    c2 = float(params.get("c2", 1.5))#koeficinet na globálne zlepšovanie
    w = float(params.get("weight", 0.9))# váha častíc
    seed = int(params.get("PSO_seed", 173))#random seed aby sme mali vždy rovanké random hodnoty
    random.seed(seed)#pridelenie seedu

    num_city = len(cords)#počet vrcholov v grafe
    #funkcia na výpočet vzdialenosti medzi dvoma bodmi
    def dist(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    #funkcia na výpočet celkovej cesty
    def route_length(position, coords):
        total = 0
        for i in range(len(position)):
            a = coords[position[i]]
            b = coords[position[(i + 1) % len(position)]]
            total += dist(a, b)
        return total
    #funkcia na prehodnenie hodnôt
    def apply_swaps(source, target, intensity):
        new = source[:] #kópia sorce aby sme nezmenili originál
        num_swaps = max(1, int(intensity * len(source)))#vyber počtu zmien, čim viac zmien tým sa viac blížime k target pozicií
        for _ in range(num_swaps):
            diff_positions = [i for i in range(len(source)) if new[i] != target[i]]#najde pozície kde sa sorce a taget líššia
            if not diff_positions:#ak už neexistuje možná zmena tak sa ciklus ukončí
                break
            idx = random.choice(diff_positions)#vyberia hodnotu kde sa sorce a taget líšia
            target_val = target[idx]#pridelý hodnotu z taget do temp premennej

            current_pos = new.index(target_val)#získanie indexu
            new[idx], new[current_pos] = new[current_pos], new[idx]#prehodenie týchto hodnôt

        return new
    #class na definovanie jednotlivca v populácií
    class Particle:
        #prvotné nastavenie populácie
        def __init__(self):
            self.position = random.sample(range(num_city), num_city)#nastavenie priebehu riešenia
            self.best_position = self.position[:]#hodnota najlepšieho riešenia
            self.b_fitness = route_length(self.position, cords)#hodnota fitness
        #funkcia na aktualizovanie
        def update(self, g_best, coords, w, c1, c2, iteration, max_iterations):
            current_w = w - (w - 0.2) * (iteration / max_iterations)#výpočet váhy pohybu
            r1, r2 = random.random(), random.random()#generovanie random hodnôt na rohodovanie o zlepšovaní smerom ku globanemu a lokálnemu maximu
            new_pos = self.position[:]#nakopírovanie pozície
            cognitive_intensity = c1 * r1#hodnota na lokálne vylepšovanie
            new_pos = apply_swaps(new_pos, self.best_position, cognitive_intensity)#vylepšenie v lokálnom smere

            social_intensity = c2 * r2#hodnota na globálne vylepšovanie
            new_pos = apply_swaps(new_pos, g_best, social_intensity)#vylepšenie v globalnom smere

            if random.random() < current_w * 0.2:  #náhodný pohyb v priestore na predídenie lokálnemu minimu
                num_mutations = random.randint(1, max(2, num_city // 20))#počet mutovaných dvojíc
                for _ in range(num_mutations):
                    i, j = random.sample(range(num_city), 2)#výber náhodných hodnôt
                    new_pos[i], new_pos[j] = new_pos[j], new_pos[i]#výmena hodnôt

            self.position = new_pos#nastavenie pozicie na novú poziciu
            cost = route_length(self.position, coords)#vypočítanei hodnoty

            if cost < self.b_fitness:#definovanie best fitness
                self.b_fitness = cost#nastavenei na best fitness
                self.best_position = new_pos[:]#kopírovanie aktualnej pozície do lokálneho best

    particles = [Particle() for _ in range(particle_count)]#generovanie populácie
    g_best = min(particles, key=lambda p: p.b_fitness).best_position[:]#nájdenie globálnej pozície
    g_cost = route_length(g_best, cords)#najednie globálneho fitness
    best_distance = [g_cost]#uloženie na finálnu vizualizáciu
    #hlavný ciklus
    for g in range(iterations):
        for p in particles:#prejde celú populáciu a upravý jej hodnoty
            p.update(g_best, cords,w, c1, c2,g,iterations)
        best_particle = min(particles, key=lambda p: p.b_fitness)#nájdenie najlepšej častice
        if best_particle.b_fitness < g_cost:#hladanie globálneho fitness
            g_cost = best_particle.b_fitness#pridelenie globálneho fitness
            g_best = best_particle.best_position[:]#najelšia nájdená cesta
            best_tour_gen_pso = g#generácia kde bolo najdené globálne best fitness
        best_distance.append(g_cost)

    return g_best, best_distance, best_tour_gen_pso