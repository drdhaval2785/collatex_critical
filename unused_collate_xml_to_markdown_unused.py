from collatex import *
from collatex.core_classes import AlignmentTable, create_table_visualization
import glob
import sys
import os
from datetime import datetime

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python collate_witnesses_to_xml.py project_id")
		sys.exit(1)
	project_id = sys.argv[1]
	directory = 'input/' + project_id + '/slp1'
	outfile = 'output/' + project_id + '/slp1/' + project_id + '.xml'
	files = glob.glob(directory + '/' + '*.txt')
	files = sorted(files)
	collation = Collation()
	print(files)
	print('Witness addition started')
	print(datetime.now())
	for fil in files:
		print(fil)
		witness_id = os.path.splitext(os.path.basename(fil))[0]  # '1', '2', '3'
		witness_data = open(fil, 'r', encoding='utf-8').read()
		collation.add_plain_witness(witness_id, witness_data)
		print(f"Added witness: {witness_id}")
	print('Witness addition completed')
	print(datetime.now())
	print('Collation started')
	xml = collate(collation, output="xml", segmentation=False, near_match=True)
	fout = open(outfile, 'w', encoding='utf-8')
	fout.write(xml)
	#print(xml)
	print(f"Collated witnesses and wrote to {outfile}")
	print(datetime.now())
	fout.close()

