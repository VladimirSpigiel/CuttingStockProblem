#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

list = []
list.append(3)
list.append(5)
list.append(1)

min = 999999

for element in list:
	print("On compare " + str(element) + " avec " + str(min))
	if element < min:
		print("Min trouve ! Nouveau min = " + str(element))
		min = element


print("Minimum a la fin = " + str(min))