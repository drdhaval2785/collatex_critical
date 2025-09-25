from collatex import *
from collatex.core_classes import AlignmentTable, create_table_visualization

collation = Collation()
collation.add_plain_witness("A"," BUpAla iti . BUpAlapramuKAH . BUmAn iti paryantA pati zaw rAjYo nAmavAcakAH . itiSabdaH prakArArTastena BUpAdayo'pi .. ..")
collation.add_plain_witness("B", "BUpAla iti . BUpAlapramuKAH BUmAn iti paryantA ete zaw rAjYo nAmavAcakAH . itiSabdaH prakArArTastena BUpAdayo'pi .. ")
collation.add_plain_witness("C","BUpAla iti BUpAlapramuKAH BUmAn iti paryantA gati zaw rAjYo nAmavAcakAH . itiSabdaprakArTastena BUpAdayo'pi .. 4 ..")
#table = collate(collation, segmentation=False, near_match=True)
#tei = collate(collation, output="tei", segmentation=False, near_match=True)
#json = collate(collation, output="json", segmentation=False, near_match=True)
#print(json)
#print(tei)
xml = collate(collation, output="xml")
print(xml)

table = collate(collation, )
print(table)
