#! usr/bin/python
# -*- coding: ISO-8859-1 -*-
from models import *
import time

longueurPlan = 7
hauteurPlan = 7



surface = Plan(longueurPlan, hauteurPlan)

lot = LogicalTest.genererLot(4,longueurMax = longueurPlan, hauteurMax = hauteurPlan)
#lot = Lot()
#lot.dialogueUtilisateur()

s = Solvers(lot , surface, False, False)
