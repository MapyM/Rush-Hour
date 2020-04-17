import Vehicule
import random

# --------------------------------------------- Niveaux du jeu --------------------------------------------------------#
NIVEAU1 = ".........AA...P..Q..R.P..QXXR.P..Q..R....B...CC..B.SSS.........."
NIVEAU2 = ".........A..PPP..A..B.Q..XX.BCQ..RRR.CQ....D.EE..FFDGG.........."
NIVEAU6 = ".........AA.B....CC.BPQ...XXRPQ..DDERPQ..F.ER....F..SSS........."
NIVEAU10 = ".........AAB.CC..DDB..P..QXX..P..QRRR.P..Q..EFF..GG.EHH........."
NIVEAU12 = ".........ABB..P..A.Q..P..XXQ..P....QRRR......C...SSS.C.........."
NIVEAU15 = "..........AABB...CCDDPQ..RSXXPQ..RSEFPQ..RSEFGG...HHII.........."
NIVEAU19 = "...........ABB.....A.C....DXXC....DEEF....PPPF.................."
NIVEAU21 = ".........AABP....Q.BP....QXXP....QRRR...............SSS........."
NIVEAU25 = ".........AAB.CC..DDB..P..QXX.EP..QRRREP..QF.GHH...F.GII........."
NIVEAU30 = ".........P.AQQQ..P.AB....PXXA....CCDD.R.......R..EEFF.R........."
NIVEAU33 = "..........AP.BB...AP.....XXP.....CDDEEQ..CFFGHQ..RRRGHQ........."
NIVEAU36 = ".........PQQQAA..PBCC.R..PBXX.R..SSSD.R....EDFF..GGE............"
NIVEAU40 = ".........PAA.B...PCD.BQ..PCDXXQ..RRRE.Q....FEGG..HHFII.........."

list_niv = [NIVEAU1, NIVEAU2, NIVEAU6, NIVEAU10, NIVEAU12, NIVEAU15, NIVEAU19, NIVEAU21, NIVEAU25, NIVEAU30, NIVEAU33,
            NIVEAU36, NIVEAU40]


# ------------------------------------------ Choix des niveaux --------------------------------------------------------#

# fonction appelée dans changer_map() de main.py
def choisir_map():
    num_map = random.randint(0, len(list_niv) - 1)
    return list_niv[num_map]


# fonction appelée dans niv(nb) de main.py
def choix_niveau(i):
    return list_niv[i]


# ---------------------------------------- Manipulations de la matrice ------------------------------------------------#

def init_matrice(matr, L, vr_image, v_lh, v_lv, c_lh, c_lv):
    courant = ""
    o = ""
    im = None
    P = []
    for i in range(len(matr) - 1):
        if matr[i] != ('.'):
            L[i // 8][i % 8] = matr[i]
            if courant != matr[i]:
                if matr[i] not in courant:
                    if matr[i] == "X":
                        nv = Vehicule.Vehicule(i % 8, i // 8, "h", vr_image, "X")
                        P.append(nv)
                    else:
                        if matr[i] == matr[i + 1]:
                            o = "h"
                            if matr[i] >= 'A' and matr[i] < 'P':
                                im = random.choice(v_lh)
                            else:
                                im = random.choice(c_lh)
                        else:
                            o = "v"
                            if matr[i] >= 'A' and matr[i] < 'P':
                                im = random.choice(v_lv)
                            else:
                                im = random.choice(c_lv)
                        nv = Vehicule.Vehicule(i % 8, i // 8, o, im, matr[i])
                        P.append(nv)
                    courant = courant + matr[i]
    # print(courant)
    # for j in range(0, 8):
    #     print(L[j])
    # print(len(P))
    # for g in range(len(P)):
    #     print(P[g].posX, P[g].posY, P[g].orientation, P[g].image, P[g].ident)
    return P


def create_matrice(L, P):
    for i in range(0, len(L)):
        for j in range(0, len(L[i])):
            L[i][j] = 0
    for g in range(0, len(P)):
        L[P[g].posY][P[g].posX] = P[g].ident
        if P[g].orientation == "h":
            L[P[g].posY][P[g].posX + 1] = P[g].ident
            if P[g].type == "camion":
                L[P[g].posY][P[g].posX + 2] = P[g].ident
        else:
            L[P[g].posY + 1][P[g].posX] = P[g].ident
            if P[g].type == "camion":
                L[P[g].posY + 2][P[g].posX] = P[g].ident
    # for i in range(0, 8):
    #    print(L[i])


# --------------------------------------------------- Utilitaires -----------------------------------------------------#

def trouver_tuple(board, obj):  # on calcule sur quel véhicule on clique
    for z in range(0, len(board)):
        if obj == board[z].ident:
            return z


def bsup(board, L, val, o, xx, yy):  # on récupère la valeur de la case jusqu'à laquelle notre véhicule peut se déplacer
    if o == "h":
        for i in range(board[val].posX + board[val].taille, len(L)):
            if L[yy][i] != 0:
                return i
        return 7  # dans le cas où aucune pièce ne bloque le mouvement de val, la pièce peut se déplacer jusqu'au bout
    else:
        for j in range(board[val].posY + board[val].taille, len(L)):
            if L[j][xx] != 0:
                return j
        return 7


def binf(board, L, val, o, xx, yy):  # idem pour la case la plus petite
    if o == "h":
        for i in range(0, board[val].posX):
            j = board[val].posX - 1 - i
            if L[yy][j] != 0:
                return j + 1
        return 1
    else:
        for g in range(0, board[val].posY):
            k = board[val].posY - 1 - g
            if L[k][xx] != 0:
                return k + 1
        return 1


# --------------------------------------------- Résolution de la matrice ----------------------------------------------#

def init(file_matrice, deplac):
    for p in range(len(deplac)):
        f = []
        f.append(deplac[p])
        file_matrice.append(f)
    return file_matrice


def pieces_deplacables(P, L, val):  # permet de calculer les pièces déplaçables dans la matrice L
    deplac = []
    for piece in range(len(P)):
        if piece != val:
            b_inf = binf(P, L, piece, P[piece].orientation, P[piece].posX, P[piece].posY)
            b_sup = bsup(P, L, piece, P[piece].orientation, P[piece].posX, P[piece].posY)
            if P[piece].orientation == "h":
                if b_inf < P[piece].posX:
                    deplac.append(piece * 10 + b_inf)
                if b_sup > P[piece].posX + P[piece].taille:
                    deplac.append(piece * 10 + (b_sup - P[piece].taille))
            else:
                if b_inf < P[piece].posY:
                    deplac.append(piece * 10 + b_inf)
                if b_sup > P[piece].posY + P[piece].taille:
                    deplac.append(piece * 10 + (b_sup - P[piece].taille))
    return deplac


# Un mouvement est caractérisé par le numéro de la pièce suivi de la nouvelle position de la pièce
# ex : 45 signifie qu'on va placer la pièce 4 en position 5


def modif(P, f):  # met à jour la liste de véhicules
    for i in range(len(f)):
        a = f[i] % 10
        b = f[i] // 10
        if P[b].orientation == 'h':
            P[b].posX = a
        else:
            P[b].posY = a


def ajout_possible(z, F):
    i = len(F) - 1
    while i > 0 and len(F[i]) == len(z):
        if sorted(z) == sorted(F[i]):  # on regarde si les deux listes triées par ordre croissant sont égales
            return False
        else:
            i -= 1
    return True
