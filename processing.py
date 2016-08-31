import os

file = open('FauvPieces.txt','r')
for line in file:
    os.system(line)
file.close()
