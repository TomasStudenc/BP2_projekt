# ==========================================================
#  GENETIC ALGORITHM
# ==========================================================
import random #knižnica na náhodné rohodovanie
#knižnica na výpočet distance matrix
#vtupne parametre sú coordináty bodov
#vypočítava sa vzdialenost medzi bodmi 1,1 až n,n kde vzniká matica obsahujúca vzdialenosti medzi všetkými bodmi
import math

def GA(cords, params):
    #globálne premenne
    global pop_size, best_tour_gen_ga
    best_tour_gen_ga = 0#inicializovanie best_tour generácie na 0
    generations = int(params.get("GA generations", 1000))#počet generácií ktoré bude algoritmus bežať
    pop_size = int(params.get("Population size", 100))#velkosť populácie
    elit_rate = float(params.get("Elit rate", 0.25))#percento populácie ktorá prechádza do ďalšej generácie bez zmeny
    mutation_rate = float(params.get("Mutation rate", 0.1))#pravdepodobnosť mutácie
    seed = int(params.get("GA_seed", 173))#seed na ktorom beží random aby pri testovaní sme sledovali rovnakú náhodnosť pri menení parametrov
    random.seed(seed)#nastavenie seedu do randomu
    num_c = len(cords)#celkový počet vrcholov v grafe
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
    #class definujúca jedinca v populácií
    class Person:
        #povodné nastavenie jedinca
        def __init__(self):
            # vytvorenie genomu jedinca
            #genome reprezentuje poradie vrcholov ktoré jednotlivec prejde
            self.genome = random.sample(range(num_c), num_c)
            #ohodnotenie jednotlivca
            self.fitness = 0.0
        #funkcia na hodnotene cesty
        def evaluate(self):
            self.fitness = route_length(self.genome,cords) #nastavenie fittness na celkovú hodnotu cesty
            return self.fitness
    #funkcia na výber člonov populácie na kríženie
    def tournament_selection(pop):
        pick = random.sample(pop, 3)#vyberie 3 náhodných člonov populácie
        pick.sort(key=lambda x: x.fitness)#usporiada ich od najlepšého po najhoršieho
        return pick[0]#vyberie najlepšieho
    #funkcia na kríženie
    def crossover(p1, p2):#vstupujú dvaja členovia populácie
        cut = random.randint(1, num_c - 2)#vyberie miesto kde sa genome rozdelí
        child1_genome = p1.genome[:cut] + [g for g in p2.genome if g not in p1.genome[:cut]]#poskladá nový genom tak aby bola prvá časť z p1 a druhá z p2
        child2_genome = p2.genome[:cut] + [g for g in p1.genome if g not in p2.genome[:cut]]#poskladá nový genom tak aby bola prvá časť z p2 a druhá z p1
        c1, c2 = Person(), Person() # vytvorý nových človoc populácie ako child1 a child2
        c1.genome, c2.genome = child1_genome, child2_genome#priradí týmto deťom genomi
        return c1, c2#vráti deti
    #funkcia na mutáciu
    def mutation(person):
        if random.random() < mutation_rate:#vyberie sa náhodná hodnota a zistí či sa bude mutovať alebo nie
            a, b = random.sample(range(num_c), 2)#vyberie 2 náhodné gény
            person.genome[a], person.genome[b] = person.genome[b], person.genome[a]#vymení poradie týchto génov

    population = [Person() for _ in range(pop_size)]#vytvorenie novej populácie
    #prvotné ohodnotenie populácie
    for p in population:
        p.evaluate()
    best_person = min(population, key=lambda p: p.fitness)#vybranie najlepšieho člena populácie
    best_fitness = best_person.fitness#nastavenie best fitnes
    best_distances = [best_fitness]#pridanie best fitness do pola na zobrazenie
    #hlavný cyklus genetyckého algoritmu
    for g in range(generations):
        population.sort(key=lambda p: p.fitness)#zoradenie populácie od najlepšieho po najhoršiehu
        elites = population[:int(elit_rate * pop_size)]#vyberie elitu
        new_population = elites.copy()#nakopíruje elitu do novej populácie
        while len(new_population) < pop_size:#vytváranie zvyšku populácie
            p1, p2 = tournament_selection(population), tournament_selection(population)#výber dvoch rodičov pre kríženie
            c1, c2 = crossover(p1, p2)#križenie
            mutation(c1)#mutácia child1
            mutation(c2)#mutácia child2
            c1.evaluate()#ohodnotenei child1
            c2.evaluate()#ohodnotenie child2
            new_population.extend([c1, c2])#pridánie detíd do populácie
        population = new_population[:pop_size]#prehodenie populácie
        current_best = min(population, key=lambda p: p.fitness)#nájednie najlepšieho lokálneho riešenia v danej generácií
        if current_best.fitness < best_fitness:#zitíme či je to aj globálne najlepšie riešenie
            best_person = current_best#nastavenie best person
            best_fitness = current_best.fitness#nastavenei best fitness
            best_tour_gen_ga = g#nastavenie generácie v ktorej bola táto hodnota nájdená
        best_distances.append(best_fitness)#pridanie hodnoty do pola

    return best_person.genome, best_distances, best_tour_gen_ga#návra hodnôt na vyzualizáciu