from collatex import *
from collatex.core_classes import AlignmentTable, create_table_visualization
import glob

if __name__ == "__main__":
	collation = Collation()
	directory = 'witnesses/lorem_ipsum/'
	files = glob.glob(directory + '*.txt')
	for fil in files:
		bare = fil.rstrip('.txt').lstrip(directory)
		witness_id = bare
		witness_data = open(fil, 'r', encoding='utf-8').read()
		collation.add_plain_witness(witness_id, witness_data)
	xml = collate(collation, output="xml", segmentation=False, near_match=True)
	print(xml)

	table = collate(collation, segmentation=False, near_match=True)
	print(table)
