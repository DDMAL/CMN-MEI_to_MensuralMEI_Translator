import os

fauvel = open('FauvPieces.txt','r')
for piece in fauvel:
    os.system(piece)
fauvel.close()

ivtrem = open('IvTremPieces.txt', 'r')
for piece in ivtrem:
    os.system(piece)
ivtrem.close()