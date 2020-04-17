# on importe des librairies graphiques, des classes, etc.
from tkinter import *
from collections import deque
import random
import Vehicule
import Controler
from time import *
from copy import copy
import winsound

# ---------------------------------------- Son ------------------------------------------------------------------------#

winsound.PlaySound('Colorama.wav', winsound.SND_ASYNC | winsound.SND_NOSTOP)
# musique libre de droit trouvé sur https://www.musicscreen.be/
son_actif = True

# ----------------------------------------- Mise en place du canvas ---------------------------------------------------#

fenetre = Tk()  # on crée une nouvelle fenêtre

# --------------------------------------------- Chargement des images -------------------------------------------------#

rendu = PhotoImage(file="rendu.png")  # fond du men jouer
instructions = PhotoImage(file="instructions_jouerv2.png")  # image d'explications du principe du jeu

fond = PhotoImage(file="fondtest.png")  # on charge l'image de fond des niveaux
vr_image = PhotoImage(file="voit_rouge.png")  # on charge l'image de la voiture rouge

# on charge les images des autres voitures
vb_v = PhotoImage(file="v_bleu_v.png")  # voiture bleue verticale
vb_h = PhotoImage(file="v_bleu_h.png")  # voiture bleue horizontale
vv_v = PhotoImage(file="v_vert_v.png")  # voiture verte verticale
vv_h = PhotoImage(file="v_vert_h.png")  # voiture verte horizontale
vvi_v = PhotoImage(file="v_violet_v.png")  # voiture violette verticale
vvi_h = PhotoImage(file="v_violet_h.png")  # voiture violette horizontale
vj_v = PhotoImage(file="v_jaune_v.png")  # voiture jaune verticale
vj_h = PhotoImage(file="v_jaune_h.png")  # voiture jaune horizontale

# on charge les images des camions
bus_v = PhotoImage(file="bus_v.png")  # bus vertical
bus_h = PhotoImage(file="bus_h.png")  # bus horizontal
cam_v = PhotoImage(file="camion_v.png")  # camion vertical
cam_h = PhotoImage(file="camion_h.png")  # camion horizontal
lim_v = PhotoImage(file="limousine_v.png")  # limousine verticale
lim_h = PhotoImage(file="limousine_h.png")  # limousine horizontale

NoSon = PhotoImage(file="NosoundV2.png")
AvecSon = PhotoImage(file="WithSound.png")

# ---------------------------------------------- Variables globales ---------------------------------------------------#

matr = None  # initialisation de la matrice
board = None  # initialisation de la liste de véhicule
val_rouge = -1  # initialisation du rang de la voiture rouge dans board
position_v = [None, None]  # position véhicule au clic
bornes = [None, None]  # bornes entre lesquelles un véhicule peut évoluer
val, image = -2, 0  # initialisation du numero de la voiture sur laquelle on clique et de son image
compteur = 0  # on initialise un compteur de mouvements à 0
affich_compt = 0
old = [None, None]  # on récupère la position antérieure

h = vr_image.height()  # récupère la hauteur de la voiture rouge comme repère
# (j'aurais aimé faire un jeu qui puisse s'adapter à des images de véhicule de toutes les tailles)

# tableaux pour récupérer les différents véhicules par catégorie (ex:voiture vertical)
v_lh = [vb_h, vv_h, vvi_h, vj_h]
v_lv = [vb_v, vv_v, vvi_v, vj_v]
c_lh = [bus_h, cam_h, lim_h]
c_lv = [bus_v, cam_v, lim_v]

# tableau permettant de récupérer les images des véhicules pour garder les mêmes quand on recommence un niveau
save_couleurs_v = []

image_son = AvecSon  # permet de conserver l'image du bouton son en fonction de si le joueur a activé ou non le son
bt_son = None  # initialisation du bouton son

# ------------------------------------------- Création d'un nouveau canvas --------------------------------------------#

canvas = Canvas(fenetre, width=h * 8, height=h * 8)
fond_menu = canvas.create_image(0, 0, anchor="nw", image=rendu)
canvas.create_text(4 * h, 2.5 * h, text="RUSH HOUR", font="Ravie 50", fill="#262626")
canvas.create_text(4 * h, 2.5 * h, text="RUSH HOUR", font="Ravie 48", fill="#FCE729")
canvas.pack()

# -------------------- Création de la matrice qui se met à jour selon le déplacement des pièces -----------------------#

L = []

for i in range(0, 8):
    lt = []
    L.append(lt)

# on initialise notre matrice avec des 0
for i in range(0, len(L)):
    for j in range(0, 8):
        L[i].append(0)


# ---------------------------------------------- Initialisation -------------------------------------------------------#


def initial():
    global board, val_rouge, compteur, position_v, bornes, val, image, old
    canvas.delete("all")
    position_v = [None, None]
    bornes = [None, None]
    old = [None, None]
    val, image = -2, 0
    board = None
    compteur = 0
    for i in range(len(L)):
        for j in range(len(L)):
            L[i][j] = 0
    board = Controler.init_matrice(matr, L, vr_image, v_lh, v_lv, c_lh, c_lv)
    for i in range(len(board)):
        if board[i].type == "vr":
            val_rouge = i
    jouer()


# ----------------------------------- Gestion de l'interface graphique et du son --------------------------------------#


# fonction appelée quand on clique sur le bouton "Jouer" du menu
def menu():
    global save_couleurs_v
    canvas.delete('all')
    canvas.config(cursor="arrow")
    # on enlève l'écouteur d'évènements pour éviter que le jeu reste jouable en fond
    canvas.unbind('<B1-Motion>')
    canvas.unbind('<Button-1>')
    canvas.unbind('<Motion>')
    canvas.unbind('<ButtonRelease>')
    # on réinitialise le tableau de récupération des couleurs des véhicules
    save_couleurs_v = []
    # on crée les éléments du menu (textes, boutons, rectangles, etc.)
    canvas.create_rectangle(0, 0, 8 * h, 8 * h, fill="grey")
    canvas.create_rectangle(h, 0.75 * h, 7.5 * h, 1.9 * h, fill='dark grey')
    canvas.create_text(4.3 * h, h, text="Niveaux débutants", font="Arial 16 italic", fill="black")
    bt_nv1 = Button(fenetre, text="Niveau 1", command=lambda: niv(0), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(2 * h, 1.5 * h, window=bt_nv1)
    bt_nv2 = Button(fenetre, text="Niveau 2", command=lambda: niv(1), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(3.5 * h, 1.5 * h, window=bt_nv2)
    bt_nv3 = Button(fenetre, text="Niveau 3", command=lambda: niv(2), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(5 * h, 1.5 * h, window=bt_nv3)
    bt_nv4 = Button(fenetre, text="Niveau 4", command=lambda: niv(3), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(6.5 * h, 1.5 * h, window=bt_nv4)
    canvas.create_rectangle(h, 2.25 * h, 7.5 * h, 3.4 * h, fill='dark grey')
    canvas.create_text(4.3 * h, 2.5 * h, text="Niveaux intermédiaires", font="Arial 16 italic", fill="black")
    bt_nv5 = Button(fenetre, text="Niveau 5", command=lambda: niv(4), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(2 * h, 3 * h, window=bt_nv5)
    bt_nv6 = Button(fenetre, text="Niveau 6", command=lambda: niv(5), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(4.25 * h, 3 * h, window=bt_nv6)
    bt_nv7 = Button(fenetre, text="Niveau 7", command=lambda: niv(6), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(6.5 * h, 3 * h, window=bt_nv7)
    canvas.create_rectangle(h, 3.75 * h, 7.5 * h, 4.9 * h, fill='dark grey')
    canvas.create_text(4.3 * h, 4 * h, text="Niveaux experts", font="Arial 16 italic", fill="black")
    bt_nv8 = Button(fenetre, text="Niveau 8", command=lambda: niv(7), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(2 * h, 4.5 * h, window=bt_nv8)
    bt_nv9 = Button(fenetre, text="Niveau 9", command=lambda: niv(8), width=10, height=1, bg='grey', relief='raised',
                    overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(4.25 * h, 4.5 * h, window=bt_nv9)
    bt_nv10 = Button(fenetre, text="Niveau 10", command=lambda: niv(9), width=10, height=1, bg='grey', relief='raised',
                     overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(6.5 * h, 4.5 * h, window=bt_nv10)
    canvas.create_rectangle(h, 5.25 * h, 7.5 * h, 6.4 * h, fill='dark grey')
    canvas.create_text(4.3 * h, 5.5 * h, text="Niveaux diaboliques", font="Arial 16 italic", fill="black")
    bt_nv11 = Button(fenetre, text="Niveau 11", command=lambda: niv(10), width=10, height=1, bg='grey', relief='raised',
                     overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(2 * h, 6 * h, window=bt_nv11)
    bt_nv12 = Button(fenetre, text="Niveau 12", command=lambda: niv(11), width=10, height=1, bg='grey', relief='raised',
                     overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(4.25 * h, 6 * h, window=bt_nv12)
    bt_nv13 = Button(fenetre, text="Niveau 13", command=lambda: niv(12), width=10, height=1, bg='grey', relief='raised',
                     overrelief='raised', font=('courier', 10, 'bold'))
    canvas.create_window(6.5 * h, 6 * h, window=bt_nv13)
    bt_hasard = Button(fenetre, text="Map random", command=changer_map, width=60, height=2, bg='grey', relief='raised',
                       font=('courier', 10, 'bold'))
    canvas.create_window(4.25 * h, 7.1 * h, window=bt_hasard)


# fonction appelée quand on clique sur le bouton "Comment jouer ?"
def commentjouer():
    canvas.delete('all')
    canvas.create_image(0, 0, anchor="nw", image=instructions)
    bt_menu = Button(fenetre, text="Jouer", command=menu, width=7, height=1, bg="#64305A", relief='flat',
                     overrelief='raised', font=('courier', 25, 'bold'))
    canvas.create_window(4 * h, 7.3 * h, window=bt_menu)


# fonction appelée après initialisation/réinitialisation du plateau --> lancement du niveau choisi
def jouer():
    global bt_son
    canvas.delete("all")
    canvas.create_image(0, 0, anchor='nw', image=fond)
    defin_canvas()  # on appelle la fonction defin_canvas() pour dessiner le canvas
    canvas.bind('<B1-Motion>', glisser)  # appelée quand on clique et qu'on déplace en maintenant appuyée
    canvas.bind('<Button-1>', clic)  # appelée quand on relâche la souris
    canvas.bind('<Motion>', deplacable)  # appelée quand on se déplace sur le canvas
    canvas.bind('<ButtonRelease>', drop)  # appelée quand on lâche le bouton
    bt_resol = Button(fenetre, text="BFS à venir", command=resoudre_matrice, width=12, height=1, bg='white',
                      relief='flat',
                      overrelief='raised', font=('courier', 10, 'bold'), fg='black')
    canvas.create_window(7.1 * h, 0.4 * h, window=bt_resol)
    bt_rejouer = Button(fenetre, text="Menu", command=menu, width=10, height=1, bg='white', relief='flat',
                        overrelief='raised', font=('courier', 10, 'bold'), fg='black')
    canvas.create_window(1.4 * h, 0.4 * h, window=bt_rejouer)
    bt_reinit = Button(fenetre, text="Recommencer", command=initial, width=14, height=1, bg='white', relief='flat',
                       overrelief='raised', font=('courier', 10, 'bold'), fg='black')
    canvas.create_window(2.9 * h, 0.4 * h, window=bt_reinit)
    bt_son = Button(fenetre, image=image_son, command=modifier_son, bg='light grey', relief='flat',
                    overrelief='raised')
    canvas.create_window(0.5 * h, 0.4 * h, window=bt_son)


# fonction appelée quand on lance un niveau --> dessine les véhicules sur le plateau (selon board et matr)
def defin_canvas():
    global bt_rejouer_w, bt_reinit_w, save_couleurs_v
    canvas.create_rectangle(h, h, 7 * h, 7 * h, fill="grey")

    # on crée les lignes de déplacement

    n = 1
    while n <= 7:
        canvas.create_line(h, h * n, h * 7, h * n, fill='white', width=5, capstyle='round')
        canvas.create_line(h * n, h, h * n, h * 7, fill='white', width=5, capstyle='round')
        n += 1
    if save_couleurs_v == []:
        # on dessine nos voitures et on met à jour la matrice
        for g in range(0, len(board)):
            save_couleurs_v.append(board[g].image)
            board[g].image = canvas.create_image(board[g].posX * h, board[g].posY * h, anchor="nw",
                                                 image=board[g].image)
    else:
        for g in range(0, len(board)):
            board[g].image = canvas.create_image(board[g].posX * h, board[g].posY * h, anchor="nw",
                                                 image=save_couleurs_v[g])


# gestion du son --> fonction appelée quand on appuie sur le bouton son de n'importe quel niveau
def modifier_son():
    global son_actif, bt_son, image_son
    if son_actif:
        winsound.PlaySound(None, winsound.SND_PURGE)
        image_son = NoSon
        son_actif = False
    else:
        winsound.PlaySound('Colorama.wav', winsound.SND_ASYNC | winsound.SND_NOSTOP)
        image_son = AvecSon
        son_actif = True
    bt_son.config(image=image_son)


# ----------------------------------------- Gestion du choix des niveaux ----------------------------------------------#


def niv(nb):
    global matr
    matr = Controler.choix_niveau(nb)
    print(matr)
    initial()


def changer_map():
    global matr
    matr = Controler.choisir_map()
    print(matr)
    initial()


# ------------------------------------------ Gestion d'événements -----------------------------------------------------#


# on récupère la valeur de la voiture sur laquelle on a cliqué et les bornes entre lesquelles elle peut varier
def clic(evt):
    global val, image, compteur
    old[0], old[1] = evt.x, evt.y
    mat_posX = old[0] // h
    mat_posY = old[1] // h
    if L[mat_posY][mat_posX] != 0:
        compteur += 1
        essai = L[mat_posY][mat_posX]
        val = Controler.trouver_tuple(board, essai)
        image = board[val].image
        position_v[0], position_v[1] = canvas.coords(image)
        bornes[0] = Controler.binf(board, L, val, board[val].orientation, mat_posX, mat_posY)
        bornes[1] = Controler.bsup(board, L, val, board[val].orientation, mat_posX, mat_posY)


# on déplace le véhicule et on change les coordonnées de nos véhicules sur le canvas
def glisser(evt):
    if val != -2:  # on n'applique le déplacement que si on a cliqué sur une pièce (et non pas le sol/décor)
        if board[val].orientation == "h":  # si la pièce est horizontale
            # Gestion horizontale
            if bornes[0] * h <= position_v[0] + evt.x - old[0] <= (
                    bornes[1] - board[val].taille) * h:  # dans le cas où on se situe entre les bornes
                if position_v[0] == bornes[0] * h and evt.x - old[0] <= 0:
                    board[val].setPosition(bornes[0], board[val].posY)
                elif position_v[0] + board[val].taille * h == bornes[1] * h and evt.x - old[0] >= 0:
                    board[val].setPosition(bornes[1] - board[val].taille, board[val].posY)
                else:
                    canvas.move(image, evt.x - old[0], 0)
                    dec = (position_v[0] / h) - (position_v[0] // h)
                    if dec >= 0.5:  # on place la pièce suivant la case la plus proche
                        position_v[0] = position_v[0] + h
                    board[val].setPosition(int(position_v[0] / h), board[val].posY)

            else:
                canvas.coords(image, board[val].posX * h, board[val].posY * h)
        else:  # si la pièce est verticale
            # Gestion verticale
            if bornes[0] * h <= position_v[1] + evt.y - old[1] <= (bornes[1] - board[val].taille) * h:
                if position_v[1] == bornes[0] * h and evt.y - old[1] <= 0:
                    board[val].setPosition(board[val].posX, bornes[0])
                elif position_v[1] + board[val].taille * h == bornes[1] * h and evt.y - old[1] >= 0:
                    board[val].setPosition(board[val].posX, bornes[1] - board[val].taille)
                else:
                    canvas.move(image, 0, evt.y - old[1])
                    dec = (position_v[1] / h) - (position_v[1] // h)
                    if dec >= 0.5:
                        position_v[1] = position_v[1] + h
                    board[val].setPosition(board[val].posX, int(position_v[1] / h))
            else:
                canvas.coords(image, board[val].posX * h, board[val].posY * h)
        old[0], old[1] = evt.x, evt.y
        position_v[0], position_v[1] = canvas.coords(image)


# on "dépose" le véhicule
def drop(evt):
    global val, image, affich_compt
    canvas.coords(image, board[val].posX * h, board[val].posY * h)
    position_v[0], position_v[1] = None, None
    bornes[0], bornes[1] = None, None
    val, image = -2, 0  # on réinitialise toutes nos valeurs
    canvas.delete(affich_compt)
    texte = "Nombre de déplacements = " + str(compteur)
    affich_compt = canvas.create_text(4 * h, 7.75 * h, text=texte, font="Arial 16 italic", fill="white")
    Controler.create_matrice(L, board)  # on met à jour la matrice avec les nouvelles coordonnées
    fin_du_jeu()  # on vérifie que la voiture rouge ne puisse pas sortir du parking


# selon la position de la souris sur le canvas et le positionnement des véhicules
def deplacable(evt):
    x = evt.x
    y = evt.y
    try:
        if L[(y // h)][(x // h)] != 0:
            canvas.config(cursor="fleur")
        else:
            canvas.config(cursor="arrow")
    except IndexError:  # dans le cas où la souris sort de la fenêtre, on affiche un message d'erreur
        print("Vous êtes sorti du cadre !")


# ----------------------------------------- Gestion de la condition de victoire ---------------------------------------#

# fonction appelée à chaque fois qu'on lâche un véhicule
def fin_du_jeu():  # on regarde si le joueur a libéré la voir devant la voiture rouge
    global compteur
    borne_vr = Controler.bsup(board, L, val_rouge, board[val_rouge].orientation, board[val_rouge].posX,
                              board[val_rouge].posY)
    if borne_vr == 7:
        # on supprime les événements car le joueur a terminé le jeu
        canvas.unbind('<B1-Motion>')
        canvas.unbind('<Button-1>')
        canvas.unbind('<Motion>')
        canvas.unbind('<ButtonRelease>')
        compteur += 1
        canvas.delete(board[val_rouge].image)
        position_v[0], position_v[1] = board[val_rouge].posX * h, board[val_rouge].posY * h
        mouvement()


# fonction qui définit le mouvement du véhicule
def mouvement():
    global image
    canvas.delete(image)
    image = canvas.create_image(position_v[0], position_v[1], anchor="nw", image=vr_image)
    position_v[0] = position_v[0] + 20
    if position_v[0] <= 8 * h:
        canvas.after(20, mouvement)
    else:
        canvas.delete(image)
        canvas.after(500, congratulations)


def congratulations():
    canvas.delete('all')
    canvas.config(cursor="arrow")
    canvas.create_rectangle(0, 0, 8 * h, 8 * h, fill="black")
    phrase = "Félicitations ! Vous avez terminé le niveau en " + str(compteur) + " coups !"
    canvas.create_text(4 * h, 4 * h, text=phrase, font="Arial 16 italic", fill="white")
    canvas.create_text(2 * h, 7.5 * h, text="Projet réalisé par Marie-Pierre MAGNE L2 DLMI", font="Arial 8 italic",
                       fill="white")
    bt_rejouer = Button(fenetre, text="Menu", command=menu, width=20, height=2, bg='black', relief='flat',
                        overrelief='flat', font=('courier', 20, 'bold'), fg='white')
    canvas.create_window(4 * h, 6 * h, window=bt_rejouer)


# ------------------------------------- Résolution de la matrice ------------------------------------------------------#


file_matrice = []
f = None


# algorithme de résoltuion de la matrice
def resoudre_matrice():
    global f, compteur
    deb = process_time()  # début chrono
    f = []
    deplac = Controler.pieces_deplacables(board, L,
                                          None)  # on calcule les pièces déplaçables à partir de la matrice actuelle
    Controler.init(file_matrice, deplac)  # on initialse notre file_matrice avec tous les mouvements possibles
    save = []
    for b in range(len(board)):
        save.append(str(board[b].posX) + str(
            board[b].posY))  # on fait une sauvegarde de toutes les positions de la matrice de base
    print("Veuillez patienter...")
    bouleen = False
    while bouleen != True:  # tant qu'on a pas trouvé de combinaison gagnante, on continue de parcourir file_matrie
        f = file_matrice[0]  # on récupère le premier élément de file_matrice
        Controler.modif(board,
                        f)  # on change les positions des différents véhicules selon la combinaison de mouvements f
        Controler.create_matrice(L, board)  # on met à jour la matrice
        deplac = Controler.pieces_deplacables(board, L, f[
            len(f) - 1] // 10)  # on calcule les pièces déplaçables à partir de cette nouvelle configuration
        del file_matrice[0]  # on supprime f (car on ne veut pas l'analyser à niveau)
        for p in range(len(deplac)):  # pour chaque pièce déplaçable
            z = f[:]
            z.append(deplac[p])  # on crée ue nouvelle combinaison composée de f et de notre nouveau mouvement
            ajout = Controler.ajout_possible(z,
                                             file_matrice)  # on regarde si cette configuration existe déjà dans file_matrice
            if ajout:  # si ce n'est pas le cas, on l'ajoute
                file_matrice.append(z)
        bouleen = (Controler.bsup(board, L, val_rouge, board[val_rouge].orientation, board[val_rouge].posX,
                                  board[
                                      val_rouge].posY) == 7)  # on regarde si la nouvelle configuration valide la condition de victoire
        for c in range(len(board)):  # on remet les véhicules à leur position initiale
            board[c].setPosition(int(save[c][0]), int(save[c][1]))
        Controler.create_matrice(L, board)  # on met à jour la matrice
        # for i in range(len(L)):
        #     print(L[i])
    fin = process_time()  # fin chrono
    # quand on sort du while et qu'on a trouvé une solution
    print("Exécution en ", fin - deb, " s")
    print("La solution est :", f)
    Controler.modif(board, f)  # on met à jour les positions des véhicules
    Controler.create_matrice(L, board)  # on met à jour la matrice
    for d in range(len(f)):
        s = "on déplace le véhicule " + str(f[d] // 10) + " en position " + str(f[d] % 10)
        print(s)
    for b in range(len(board)):  # on met à jour les placements des vahicules sur le canvas
        canvas.coords(board[b].image, board[b].posX * h, board[b].posY * h)
    compteur = compteur+len(f)
    fin_du_jeu()  # on lance l'animation de victoire
    while len(file_matrice) != 0:  # on réinitialise file_matrice à []
        del file_matrice[0]
    f = None


# ----------------------------------------------- Programme principal -------------------------------------------------#


bt_menu = Button(fenetre, text="Jouer", command=menu, width=7, height=1, bg='grey', relief='flat', overrelief='raised',
                 font=('courier', 30, 'bold'))
canvas.create_window(4 * h, 4 * h, window=bt_menu)
bt_instructions = Button(fenetre, text="Comment jouer ?", command=commentjouer, width=15, height=1, bg='grey',
                         relief='flat', overrelief='raised', font=('courier', 20, 'bold'))
canvas.create_window(4 * h, 5 * h, window=bt_instructions)
fenetre.resizable(width=False, height=False)  # la taille de la fenêtre ne peut pas être modifiée par l'utilisateur
fenetre.title("Rush Hour")
fenetre.mainloop()
