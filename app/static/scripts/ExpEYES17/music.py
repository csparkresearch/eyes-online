# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
C_6 = 1046
#D_6 = 1174
#D_6s = 1244
E_6 = 1318
F_6 = 1396
G_6 = 1567
G_6s = 1661
A_6 = 1760
B_6 = 1975

C_7 = 2093
D_7 = 2349
D_7s = 2489
E_7 = 2637
F_7 = 2793
#G_7 = 3135
#A_7 = 3520
#B_7 = 3951

Notes = [E_7, D_7s, E_7, D_7s, E_7, B_6, D_7, C_7, A_6, 0, C_6, E_6, A_6, B_6, 0, E_6, G_6s, B_6, C_7, 0, E_6, E_7, D_7s, E_7, D_7s, E_7, B_6, D_7, C_7, A_6, 0, C_6, E_6, A_6, B_6, 0, E_6, C_7, B_6, A_6, 0, A_6, B_6, C_7, D_7, E_7, 0, G_6, F_7, E_7, D_7, 0, F_6, E_7, D_7, C_7, 0, E_6, D_7, C_7, B_6, 0, E_6]
Duration = [1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1]


if __name__ == "__main__":
	import expeyes.eyes17 as eyes
	import time
	I=eyes.open()
	I.set_sine_amp(0)
	print ('fur elise')
	for N,D in zip(Notes,Duration):
		print (N,D)
		I.set_sine(N)
		time.sleep(D*0.2)
	I.set_state(SQR1=0)
	I.set_sine(0)