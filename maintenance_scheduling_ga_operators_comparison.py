# ============================================================
#  Cédule de maintenance - AG : TOUS les types
#  Sélection : loterie, rang, tournoi, aléatoire
#  Croisement : 1 point, 2 points, uniforme
#  Mutation : inversion, échange, remplacement
# ============================================================
import random

# ---------- DONNÉES ----------
groupe1 = ['1100', '0110', '0011']            # unités 1 et 2
groupe2 = ['1000', '0100', '0010', '0001']    # unités 3 à 7
capacite = [20, 15, 35, 40, 15, 15, 10]
intervalle = [80, 90, 65, 70]
capacite_maximum = 150

# ---------- PARAMÈTRES ----------
NOMBRE_INDIVIDU = 20
MAX_GENERATION = 30
P_CROISEMENT = 0.8
P_MUTATION = 0.2


# ---------- POPULATION ----------
def creation_individu():
    return [random.choice(groupe1 if i < 2 else groupe2) for i in range(7)]

def creation_generation():
    generation = []
    while len(generation) < NOMBRE_INDIVIDU:
        ind = creation_individu()
        if ind not in generation:
            generation.append(ind)
    return generation


# ---------- ÉVALUATION ----------
def reserves(individu):
    # réserve = capacité totale - puissance en maintenance - demande
    res = []
    for i in range(4):
        perdue = sum(int(individu[j][i]) * capacite[j] for j in range(7))
        res.append(capacite_maximum - perdue - intervalle[i])
    return res

def fitness(individu):
    # la plus petite réserve (0 si négative)
    return max(0, min(reserves(individu)))


# ---------- SÉLECTIONS (choisir 1 parent) ----------
def selection_loterie(gen):
    # chance proportionnelle à la fitness
    poids = [fitness(i) for i in gen]
    if sum(poids) == 0:
        return random.choice(gen)
    return random.choices(gen, weights=poids)[0]

def selection_rang(gen):
    # on trie du pire au meilleur ; chance proportionnelle au rang (1,2,3...)
    tri = sorted(gen, key=fitness)
    return random.choices(tri, weights=range(1, len(tri) + 1))[0]

def selection_tournoi(gen, k=3):
    # on tire k individus au hasard, le meilleur gagne
    return max(random.sample(gen, k), key=fitness)

def selection_aleatoire(gen):
    # choix totalement au hasard
    return random.choice(gen)


# ---------- CROISEMENTS (sur des blocs de 4 bits = gènes entiers) ----------
def croisement_1point(p1, p2):
    pt = random.randint(1, 6)
    return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]

def croisement_2points(p1, p2):
    a, b = sorted(random.sample(range(1, 7), 2))
    return p1[:a] + p2[a:b] + p1[b:], p2[:a] + p1[a:b] + p2[b:]

def croisement_uniforme(p1, p2):
    # pour chaque gène, on tire au sort de quel parent il vient
    e1, e2 = [], []
    for g1, g2 in zip(p1, p2):
        if random.random() < 0.5:
            e1.append(g1); e2.append(g2)
        else:
            e1.append(g2); e2.append(g1)
    return e1, e2


# ---------- MUTATIONS (on reste dans le bon groupe pour garder une cédule valide) ----------
def mutation_inversion(ind):
    # on inverse l'ordre d'un morceau de gènes (dans le même groupe)
    ind = ind[:]
    if random.random() < 0.2:
        a, b = 0, 1
    else:
        a, b = sorted(random.sample(range(2, 7), 2))
    ind[a:b + 1] = reversed(ind[a:b + 1])
    return ind

def mutation_echange(ind):
    # on échange 2 gènes du même groupe
    ind = ind[:]
    if random.random() < 0.2:
        a, b = 0, 1
    else:
        a, b = random.sample(range(2, 7), 2)
    ind[a], ind[b] = ind[b], ind[a]
    return ind

def mutation_remplacement(ind):
    # on remplace un gène par un autre cas possible (mutation de Madame)
    ind = ind[:]
    pos = random.randint(0, 6)
    ind[pos] = random.choice(groupe1 if pos < 2 else groupe2)
    return ind


# ---------- ALGORITHME GÉNÉTIQUE ----------
def algo_genetique(selection, croisement, mutation):
    gen = creation_generation()
    for _ in range(MAX_GENERATION):
        nouvelle = [max(gen, key=fitness)]         # élitisme
        while len(nouvelle) < NOMBRE_INDIVIDU:
            p1, p2 = selection(gen), selection(gen)
            if random.random() < P_CROISEMENT:
                e1, e2 = croisement(p1, p2)
            else:
                e1, e2 = p1[:], p2[:]
            if random.random() < P_MUTATION:
                e1 = mutation(e1)
            if random.random() < P_MUTATION:
                e2 = mutation(e2)
            nouvelle += [e1, e2]
        gen = nouvelle[:NOMBRE_INDIVIDU]
    return max(gen, key=fitness)


# ---------- TEST DE TOUTES LES COMBINAISONS ----------
selections = {"loterie": selection_loterie, "rang": selection_rang,
              "tournoi": selection_tournoi, "aléatoire": selection_aleatoire}
croisements = {"1 point": croisement_1point, "2 points": croisement_2points,
               "uniforme": croisement_uniforme}
mutations = {"inversion": mutation_inversion, "échange": mutation_echange,
             "remplacement": mutation_remplacement}

random.seed(1)
NB_ESSAIS = 5                                      # on répète 5 fois (moyenne)
meilleur_global = None
print(f"{'Sélection':10s} {'Croisement':10s} {'Mutation':13s} score moyen")
for ns, s in selections.items():
    for nc, c in croisements.items():
        for nm, m in mutations.items():
            resultats = [algo_genetique(s, c, m) for _ in range(NB_ESSAIS)]
            moyenne = sum(fitness(r) for r in resultats) / NB_ESSAIS
            print(f"{ns:10s} {nc:10s} {nm:13s} {moyenne:.1f}")
            for r in resultats:
                if meilleur_global is None or fitness(r) > fitness(meilleur_global):
                    meilleur_global = r

print("\nMeilleur individu :", meilleur_global)
print("Réserves          :", reserves(meilleur_global))
print("Meilleur score    :", fitness(meilleur_global))