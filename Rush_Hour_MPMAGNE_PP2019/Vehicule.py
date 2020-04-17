class Vehicule:

    def __init__(self, posX, posY, orient, img, let):
        self.image = img
        self.posX = posX
        self.posY = posY
        self.orientation = orient
        self.ident = let
        if self.ident >= 'A' and self.ident < 'P' :
            self.type = "voiture"
        if self.ident >= 'P' and self.ident < 'X' :
            self.type = "camion"
        if self.ident == 'X' :
            self.type = "vr"
        if self.type == "camion":
            self.taille = 3
        else:
            self.taille = 2

    def setPosition(self, posx, posy):
        self.posX = posx
        self.posY = posy







