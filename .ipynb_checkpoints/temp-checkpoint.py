from collatex import *
collation = Collation()
collation.add_plain_witness("A","The big old gray koala:")
collation.add_plain_witness("B", "The big gray fuzzy koala.")
collation.add_plain_witness("C","The grey fuzzy wombat!")
#table = collate(collation, segmentation=False, near_match=True)
tei = collate(collation, output="tei", segmentation=False, near_match=True)
#print(table)
print(tei)
