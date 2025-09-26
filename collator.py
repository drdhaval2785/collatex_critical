from collatex import *
from collatex.core_classes import AlignmentTable, create_table_visualization
import glob
import sys
import os


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python collate_witnesses_to_xml.py project_id")
		sys.exit(1)
	project_id = sys.argv[1]
	directory = 'input/' + project_id + '/slp1'
	outfile = 'output/' + project_id + '/slp1/' + project_id + '.xml'
	files = glob.glob(directory + '/' + '*.txt')
	collation = Collation()
	for fil in files:
		witness_id = os.path.splitext(os.path.basename(fil))[0]  # '1', '2', '3'
		witness_data = open(fil, 'r', encoding='utf-8').read()
		collation.add_plain_witness(witness_id, witness_data)
		print(f"Added witness: {witness_id}")
	xml = collate(collation, output="xml", segmentation=False, near_match=True)
	fout = open(outfile, 'w', encoding='utf-8')
	fout.write(xml)
	fout.close()

