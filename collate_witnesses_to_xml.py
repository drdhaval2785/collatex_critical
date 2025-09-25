from collatex import *
from collatex.core_classes import AlignmentTable, create_table_visualization
import glob
import sys

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python collate_witnesses_to_xml.py input_directory output.md")
		sys.exit(1)

	directory = sys.argv[1]
	outfile = sys.argv[2]
	files = glob.glob(directory + '/' + '*.txt')
	collation = Collation()
	for fil in files:
		bare = fil.rstrip('.txt').lstrip(directory)
		witness_id = bare
		witness_data = open(fil, 'r', encoding='utf-8').read()
		collation.add_plain_witness(witness_id, witness_data)
	xml = collate(collation, output="xml", segmentation=False, near_match=True)
	fout = open(outfile, 'w', encoding='utf-8')
	fout.write(xml)
	fout.close()
	print(xml)

	table = collate(collation, segmentation=False, near_match=True)
	print(table)
