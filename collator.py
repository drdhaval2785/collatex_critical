import os
from collatex import *
import glob


if __name__=="__main__":
	collation = Collation()
	files = glob.glob('witnesses/*')
	files = sorted(files)
	for filein in files:
		number = filein.rstrip('.txt').lstrip('witnesses/')
		fin = open(filein, 'r')
		datain = fin.read()
		collation.add_plain_witness(number, datain)
	alignment_table = collate(collation, output='tsv')
	print(alignment_table)

	
