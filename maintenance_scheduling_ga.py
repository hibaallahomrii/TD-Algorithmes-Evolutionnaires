# ============================================================
#  Cédule de maintenance - Algorithme Génétique (corrigé)
#  Sélection : loterie (roulette)  |  Mutation : inversion
#  Croisement : 1 point (sur des blocs de 4 bits)
# ============================================================
import random

# ---------- 1) DONNÉES DU PROBLÈME ----------
# Cas possibles de maintenance pour les unités 1 et 2 (2 intervalles de suite)
groupe1 = ['1100', '0110', '0011']
# Cas possibles pour les unités 3 à 7 (1 seul intervalle)
groupe2 = ['1000', '0100', '0010', '0001']

capacite = [20, 15, 35, 40, 15, 15, 10]   # capacité (MW) de chaque unité
intervalle = [80, 90, 65, 70]             # demande (MW) dans les 4 intervalles
capacite_maximum = 150                    # capacité totale (somme des unités)

# ---------- 2) PARAMÈTRES DE L'AG ----------
NOMBRE_INDIVIDU = 42     # 6 x 7 gènes (règle du cours)
MAX_GENERATION = 50      # nombre de générations
P_CROISEMENT = 0.8       # probabilité de croisement
P_MUTATION = 0.3         # probabilité de mutation


# ---------- 3) CRÉATION DE LA POPULATION ----------
def creation_individu():
    # un individu = 7 gènes (1 gène par unité)
    indi = []
    for i in range(7):
        if i < 2:                                  # unités 1 et 2
            indi.append(random.choice(groupe1))
        else:                                      # unités 3 à 7
            indi.append(random.choice(groupe2))
    return indi


def creation_generation():
    # une génération = plusieurs individus différents
    generation = []
    while len(generation) < NOMBRE_INDIVIDU:
        individu = creation_individu()
        if individu not in generation:             # pas de doublon
            generation.append(individu)
    return generation


# ---------- 4) ÉVALUATION (fonction objectif) ----------
def puissance(individu):
    # puissance perdue (unités en maintenance) dans chacun des 4 intervalles
    somme = []
    for i in range(4):                             # i = numéro de l'intervalle
        x = 0
        for j in range(7):                         # j = numéro de l'unité
            x += int(individu[j][i]) * capacite[j] # '1' = en maintenance
        somme.append(x)
    return somme


def reserves(individu):
    # réserve = capacité totale - puissance perdue - demande
    perdue = puissance(individu)
    return [capacite_maximum - perdue[i] - intervalle[i] for i in range(4)]


def fitness(individu):
    # performance = la plus petite réserve ; si négative -> 0
    return max(0, min(reserves(individu)))


# ---------- 5) SÉLECTION PAR LOTERIE (roulette) ----------
def selection_loterie(generation):
    # plus la fitness est grande, plus l'individu a de chances d'être choisi
    poids = [fitness(ind) for ind in generation]
    if sum(poids) == 0:                            # cas où tout le monde vaut 0
        return random.choice(generation)
    return random.choices(generation, weights=poids)[0]


# ---------- 6) CROISEMENT (1 point, sur des blocs de 4 bits) ----------
def croisement_point(parent1, parent2):
    point = random.randint(1, 6)                   # point de coupure entre 2 gènes
    enfant1 = parent1[:point] + parent2[point:]    # début de P1 + fin de P2
    enfant2 = parent2[:point] + parent1[point:]    # début de P2 + fin de P1
    return enfant1, enfant2


# ---------- 7) MUTATION PAR INVERSION ----------
def mutation_inversion(individu):
    # on inverse l'ordre des gènes entre 2 positions.
    # On reste dans le même groupe (unités 1-2 ou unités 3-7) pour que
    # la cédule reste valide.
    ind = individu[:]
    if random.random() < 0.2:
        debut, fin = 0, 1                          # groupe unités 1 et 2
    else:
        debut, fin = sorted(random.sample(range(2, 7), 2))   # groupe unités 3 à 7
    ind[debut:fin + 1] = reversed(ind[debut:fin + 1])
    return ind


# ---------- 8) DÉVELOPPER UNE GÉNÉRATION ----------
def developpement_generation(generation):
    # élitisme : on garde toujours le meilleur individu
    nouvelle = [max(generation, key=fitness)]
    while len(nouvelle) < NOMBRE_INDIVIDU:
        p1 = selection_loterie(generation)         # choix des 2 parents
        p2 = selection_loterie(generation)
        if random.random() < P_CROISEMENT:
            e1, e2 = croisement_point(p1, p2)
        else:
            e1, e2 = p1[:], p2[:]                  # pas de croisement : copies
        if random.random() < P_MUTATION:
            e1 = mutation_inversion(e1)
        if random.random() < P_MUTATION:
            e2 = mutation_inversion(e2)
        nouvelle.append(e1)
        if len(nouvelle) < NOMBRE_INDIVIDU:
            nouvelle.append(e2)
    return nouvelle


# ---------- 9) AFFICHAGE ----------
def affiche_generation(generation, numero):
    meilleur = max(generation, key=fitness)
    print(f"Génération {numero:2d} | meilleur = {meilleur} | réserve min = {fitness(meilleur)}")


# ---------- 10) PROGRAMME PRINCIPAL ----------
random.seed(2)                                     # même résultat à chaque exécution
generation = creation_generation()                 # génération initiale
affiche_generation(generation, 1)

for numero in range(2, MAX_GENERATION + 1):
    generation = developpement_generation(generation)
    affiche_generation(generation, numero)

meilleur = max(generation, key=fitness)
print("\nLe meilleur individu est :", meilleur)
print("Réserves par intervalle  :", reserves(meilleur))
print("Le meilleur score est    :", fitness(meilleur))