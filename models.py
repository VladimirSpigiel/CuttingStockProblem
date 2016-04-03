#! usr/bin/python
# -*- coding: ISO-8859-1 -*-
from Tkinter import *
from PIL import Image, ImageFont, ImageDraw, ImageTk
from abc import ABCMeta
import random
import platform
from colors import Color
import uuid
import copy

SCALE = 100


class Rectangle:
	""" Rectangle est une classe abstraite, donc non instanciable de l'extérieur """
	__metaclass__ = ABCMeta

	""" Constructeur qui a besoin de coords, et dimensions """
	def __init__(self, x = 0, y = 0, longueur = 0, hauteur = 0):
		self.setLongueur(longueur)
		self.setHauteur(hauteur)
		self.setPoint(x, y)

	""" Destructeur qui supprime le point associé à ce rectangle """
	def __del__(self):
		del self.__point

	"""Getters et Setters qui permettent l'enrichissement d'un code """
	def getLongueur(self):
		return self.__longueur

	def setLongueur(self, l):
		self.__longueur = l

	def getHauteur(self):
		return self.__hauteur

	def setHauteur(self, h):
		self.__hauteur = h

	def getPoint(self):
		return self.__point

	def setPoint(self, x, y):
		self.__point = Point(x, y)

	""" Méthode de calcul d'aire. Utile dans les classes dérivées """
	def getAire(self):
		return self.getHauteur() * self.getLongueur()

#----------------------------------------------------------------------------------
class Point:
	def __init__(self, x, y):
		self.setX(x)
		self.setY(y)

	def getX(self):
		return self.__x

	def setX(self, x):
		self.__x = x

	def getY(self):
		return self.__y

	def setY(self, y):
		self.__y = y

	""" Surcharge de la sortie vers l'ecran via la méthode str. 
		Ici lorsqu'on veut afficher un Point, on voudra toujours afficher ses coords """
	def __str__(self):
		return "[" + str(self.getX()) + ", "+ str(self.getY()) + "]"

	def affiche(self):
		print(self)

#----------------------------------------------------------------------------------
class BreakOutException(Exception):
	""" Une exception qui va permettre de sortir des boucles imbriquées """
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


#----------------------------------------------------------------------------------

class Plan(Rectangle):
	""" Ce plan permet de recevoir les pièces et les positionner.
		Plan est un type de Rectangle dans notre cas, car dispose d'une hauteur et longueur.
		Rectangle est donc le parent, plan l'enfant. """

	""" Constructeur qui utilise le constructeur de son parent 'Rectangle' en lui passant
		les paramètres nécessaires (x,y,longueur,hauteur) """
	def __init__(self, longueur = 0, hauteur = 0):
		Rectangle.__init__(self, 0, 0, longueur, hauteur)
		self.setPieces()
		self.setMatrice()

	""" Un plan comporte des pièces. Utilisation ici d'un tableau, initialement vide """
	def setPieces(self):
		self.__pieces = []

	def getPieces(self):
		return self.__pieces

	def setMatrice(self):
		self.__matrice = [[0 for x in range(self.getLongueur())] for y in range(self.getHauteur())] 

	def getMatrice(self):
		return self.__matrice


	""" Lors d'un ajout d'une pièce dans le plan on vérifie qu'il y'a assez de place dans le plan
		afin d'y ajouter la pièce concernée. Si c'est le cas, ajout de la pièce dans la tableau. 
		Ensuite choix de l'emplacement de la pièce dans le plan, et mise à jour de ses coords X, Y """
	def ajoutePiece(self, piece):
		if(isinstance(piece, Piece)):
			if(self.getAireRestante() - piece.getAire() >= 0):
				if(not self.__cherchePlace(piece)):
					piece.rotateBy90()
					return self.__cherchePlace(piece)
		return False

	def __str__(self):
		for piece in self.__pieces:
			print piece
		return "Il y'a " + str(len(self.getPieces())) + " pieces sur le plan"


	def getAireRestante(self):
		aire = self.getAire()
		for piece in self.getPieces():
			aire -= piece.getAire()

		return aire


	def __cherchePlace(self, piece):
		Y = -1   		#On initialise les positions de placement à -1, -1
		X = -1

		try:
			for y in range(0, self.getHauteur()):
				for x in range(0, self.getLongueur()):

					verifieAire = 0				#variable qui sert à savoir si l'aire en y,x peut être celle de la pièce

					if(self.getMatrice()[y][x] == 0):		#0 détecté alors possibilité de placer la pièce autour de ce point

						for y_possible in range(y, y + piece.getHauteur()):			# On parcours une sous matrice en [y:y+getHauteur(), x:x+getLongueur()]
							for x_possible in range(x, x + piece.getLongueur()):

								if( y_possible < self.getHauteur()):			# On s'assure de ne pas déborder de la matrice.
									if( x_possible < self.getLongueur()):
										
										if(self.getMatrice()[y_possible][x_possible] == 0):
											verifieAire = verifieAire + 1

										if(verifieAire == piece.getAire()):
											Y = y
											X = x
											raise BreakOutException("place disponible")

		except BreakOutException:
			return self.__placePiece(piece, Y, X)

		return False


	def __placePiece(self, piece, y, x):
		piece.getPoint().setX(x)			# Mettre à jour les coords de la Pièce
		piece.getPoint().setY(y)
		self.__pieces.append(piece)			# Ajoute la piece au plan.
		for y in range(piece.getPoint().getY(), piece.getPoint().getY() + piece.getHauteur()):
			for x in range(piece.getPoint().getX(), piece.getPoint().getX() + piece.getLongueur()):
				self.getMatrice()[y][x] = 1 		# Mettre à jour la matrice en remplissant là ou la pièce existe, avec des 1
		return True

	

#----------------------------------------------------------------------------------

class Piece(Rectangle):
	""" Cette classe permet de définir une pièce qui peut s'ajouter à un plan. 
		Elle hérite de Rectangle car nos pièces, selon un cahier des charges, sont rectangulaire """

	""" Par défaut on considère que la pièce est horizontale. """
	def __init__(self, longueur = 0, hauteur = 0):
		Rectangle.__init__(self, 0, 0, longueur, hauteur)
		self.setHorizontal(True)
		self.setColor()
		self.__id = uuid.uuid4()

	def getHorizontal(self):
		return self.__horizontal

	def setHorizontal(self, b):
		self.__horizontal = b
		return self

	def rotateBy90(self):
		self.__horizontal = not self.__horizontal

	def getLongueur(self):
		if(not self.getHorizontal()):
			return Rectangle.getHauteur(self)
		return Rectangle.getLongueur(self)

	def getHauteur(self):
		if(not self.getHorizontal()):
			return Rectangle.getLongueur(self)
		return Rectangle.getHauteur(self)

	def getId(self):
		return self.__id

	def getColor(self):
		return self.__color

	def setColor(self):
		self.__color = random.choice(Color.getColors())

	def __str__(self):
		return "[" + str(self.getLongueur()) + ", " + str(self.getHauteur()) + "]"

	def affiche(self):
		print(self, self.getPoint())


#----------------------------------------------------------------------------------

class Lot:
	"""Va permettre de gérer le lot comportant toutes les pieces à placer sur le plan """
	
	def __init__(self):
		self.setPieces()

	def __del__(self):
		for piece in self.getPieces():
			del piece

	def getPieces(self):
		return self.__pieces

	def setPieces(self):
		self.__pieces = []

	def getPiece(self, piece):
		
		for p in self.__pieces:
			if p.getId() == piece.getId():
				return p

		return None 

	def ajoutePiece(self, piece):
		if(isinstance(piece, Piece)):
			if self.getPiece(piece) is None:
				self.__pieces.append(piece)
				
			

	def supprimePiece(self, piece):
		if(isinstance(piece, Piece)):
			self.__pieces.remove(self.getPiece(piece))

	def dialogueUtilisateur(self):

		nbrPieces = input("Combien de pièces voulez-vous entrer ? : ")
		for i in range(0, nbrPieces):
			print "Valeurs pièce NR " + str(i + 1)
			l = input("Entrez la longueur de la pièce : ")
			h = input("Entrez la hauteur de la pièce : ")
			self.ajoutePiece(Piece(int(l), int(h)))


	def __str__(self):
		return str(len(self.getPieces())) + " pièces dans le lot"

#----------------------------------------------------------------------------------		

class Solvers:
	def __init__(self,lot, surface, affichePossibilites = False, affichePossibilitesLotsRestant = False):
		self.setLot(copy.deepcopy(lot))
		self.setSurface(copy.deepcopy(surface))
		print "Solving surfaces..."

		self.__solver = Solver(self.getLot(), self.getSurface(), self.getSurface().getAireRestante(), affichePossibilites)
		self.__graphics = []
		self.__graphics.append(GUI(self.getSurface().getLongueur()*SCALE, self.getSurface().getHauteur()*SCALE))
		self.__graphics[-1].getGraphique().afficheRectangle(self.__solver.getSolvedSurface(), background="red")
		if affichePossibilites == True:
			for graphic in self.__solver.getGraphics():
				graphic.getGraphique().render()


		while len(self.__solver.getLotRestant().getPieces()) > 0:
			self.setSurface(Plan(self.getSurface().getHauteur(), self.getSurface().getLongueur()))
			self.setLot(self.__solver.getLotRestant())
			self.__solver = Solver(self.getLot(), self.getSurface(), self.getSurface().getAireRestante(), affichePossibilitesLotsRestant)
			self.__graphics.append(GUI(self.getSurface().getLongueur()*SCALE, self.getSurface().getHauteur()*SCALE))
			self.__graphics[-1].getGraphique().afficheRectangle(self.__solver.getSolvedSurface(), background="red")
			if affichePossibilitesLotsRestant == True:
				for graphic in self.__solver.getGraphics():
					graphic.getGraphique().render()

		print "Solved. Il faut ", len(self.__graphics), " surfaces afin de découper les pieces"

		for graphic in self.__graphics:
			graphic.getGraphique().render()


	def setLot(self, lot):
		self.__lot = lot

	def getLot(self):
		return self.__lot

	def setSurface(self, surface):
		self.__surface = surface

	def getSurface(self):
		return self.__surface


#----------------------------------------------------------------------------------

class Solver:


	def __init__(self, lot, surface, aire, affichePossibilites = False ):
		self.__minAire = 99999999
		self.__minSurface = None
		self.__lotRestant = copy.deepcopy(lot)
		self.__surface = surface
		self.__lot = lot
		self.__aire = aire
		self.__possibilites = 0
		self.__graphics = []
		self.__affichePossibilites = affichePossibilites

		print "Solving a surface"
		self.__solve(copy.deepcopy(lot), copy.deepcopy(surface), aire)
		self.__buildLotRestant()
		print "Il y'a eu ", self.__possibilites, " possibilités de placements de pieces."

		if len(self.__lotRestant.getPieces()) > 0:
			print "Lot non vide. Tentative de résoudre une autre surface."
			


	def getSolvedSurface(self):
		return self.__minSurface

	def getLotRestant(self):
		return self.__lotRestant

	def getGraphics(self):
		return self.__graphics

	def affiche(self, gui):

		gui.getGraphique().afficheRectangle(self.getSolvedSurface(), background="red")
		

	def __solve(self, lot, surface, aire, piece = None):

	
		if piece is not None:
			surface.ajoutePiece(piece)		
			lot.supprimePiece(piece)
			self.__possibilites += 1
			if self.__affichePossibilites:
				self.__graphics.append(GUI(surface.getLongueur()*SCALE,surface.getHauteur()*SCALE))
				self.__graphics[-1].getGraphique().afficheRectangle(surface)			

		if aire <= self.__minAire:
			self.__minAire = aire
			self.__minSurface = copy.deepcopy(surface)

		for piece in lot.getPieces():
			self.__solve(copy.deepcopy(lot), copy.deepcopy(surface), surface.getAireRestante(), piece)
			p = copy.deepcopy(piece)
			p.rotateBy90()
			self.__solve(copy.deepcopy(lot), copy.deepcopy(surface), surface.getAireRestante(), p)


	def __buildLotRestant(self):
		for piece in self.__lot.getPieces():
			LogicalTest.pieceExistsOnSurface(piece, self.__minSurface)
			if LogicalTest.pieceExistsOnSurface(piece, self.__minSurface):
				self.__lotRestant.supprimePiece(piece)

#----------------------------------------------------------------------------------		

class Graphique:
	""" Surcouche de Tk personnalisée permettant dans nos cas un code plus léger """

	def __init__(self,  l = 0, h = 0):
		self.__frame = Tk()
		self.__zone = Canvas(self.__frame, width = l, height = h)
		self.__zone.pack()
		self.__longueur = l
		self.__hauteur = h

	def __checkEvent(self):
		self.__frame.after(500, self.__checkEvent)

	""" Utilité de l'abstract class 'Rectangle' qui va permettre l'utilisation des méthodes
		getPoint() et getLongueur(), getHauteur() sur des pieces et des plan.
		Lors de l'affichage d'un rectangle, si il s'agit un plan, on affiche tout son contenu.
		Sinon on affiche simplement un rectangle """
	def afficheRectangle(self, rectangle, background="white"):
		global SCALE

		if(isinstance(rectangle, Rectangle)):
			if(isinstance(rectangle, Plan)):
				self.__zone.create_rectangle(
					rectangle.getPoint().getX()*SCALE, 
					rectangle.getPoint().getY()*SCALE, 
					(rectangle.getPoint().getX() + rectangle.getLongueur()) * SCALE, 
					(rectangle.getPoint().getY() + rectangle.getHauteur())*SCALE, 
					fill=background)

				self.__zone.create_text(
						(0)*SCALE + SCALE/2, 
						(rectangle.getHauteur())*SCALE + SCALE/2, 
						text= str(rectangle.getAireRestante()))
				
				for piece in rectangle.getPieces():
					self.__zone.create_rectangle(
						piece.getPoint().getX()*SCALE , 
						piece.getPoint().getY()*SCALE, 
						(piece.getPoint().getX() + piece.getLongueur())*SCALE, 
						(piece.getPoint().getY() + piece.getHauteur())*SCALE, 
						fill= piece.getColor())

					self.__zone.create_text(
						(piece.getPoint().getX())*SCALE + SCALE/2, 
						(piece.getPoint().getY())*SCALE + SCALE/2, 
						text= str(piece))
					
				self.__zone.create_rectangle(
					rectangle.getPoint().getX()*SCALE , 
					rectangle.getPoint().getY()*SCALE, 
					(rectangle.getPoint().getX() + rectangle.getLongueur()) * SCALE, 
					(rectangle.getPoint().getY() + rectangle.getHauteur())*SCALE,
					 width=5)

	""" Méthode permettant d'afficher la fenêtre de Tk """
	def render(self):
		try:
			
			self.__checkEvent()
			self.__frame.mainloop()		
		except KeyboardInterrupt:
			print("Fin de l'affichage")


#----------------------------------------------------------------------------------	

class GUI:
	""" Classe regroupant la gestion graphique"""
	

	def __init__(self, longueur = 0, hauteur = 0):
		self.__graphique = Graphique(longueur, hauteur)
		


	def getGraphique(self):
		return self.__graphique


class LogicalTest:
	""" Classe qui permet de faire les test unitaires """

	@staticmethod
	def genererLot(nombrePieces = None, longueurMax = 7, hauteurMax = 7):
		lot = Lot()
		if(nombrePieces == None):
			nombrePieces = random.randrange(1, 15)

		for i in range(0, nombrePieces):
			longueurGenere = random.randrange(1, longueurMax);
			hauteurGenere = random.randrange(1, hauteurMax);
			piece = Piece(longueurGenere, hauteurGenere)
			print "Pièce générée : " + str(piece)
			lot.ajoutePiece(piece)

		return lot

	@staticmethod
	def pieceExistsOnSurface(piece, surface):
		state = False
		for p in surface.getPieces():
			if p.getId() == piece.getId():
				state = True

		return state