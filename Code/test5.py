# get all the element inside ""
import re
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as mn
import mysql.connector
mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="Avm46ferces99!"
        )
mycursor = mydb.cursor()
mycursor.execute("DROP DATABASE IF EXISTS superset")
mycursor.execute("CREATE DATABASE superset")
xmldoc = mn.parse("prova-gianlu4.owl")
itemList = xmldoc.getElementsByTagName("")
print(xmldoc.getElementsByTagName())

text = '''<owl:Class rdf:about="http://ontology.ethereal.cz/ygo#Trap_Card">
        <rdfs:subClassOf rdf:resource="http://ontology.ethereal.cz/ygo#Card"/>
        <rdfs:comment xml:lang="en">Trap cards are cards with purple-colored borders that have various effects. A Trap Card must first be Set and can only be activated after the current turn has finished. After that, it may be activated during either player&apos;s turn. Trap Cards are Spell Speed 2, with the exception of Counter Trap Cards, which are Spell Speed 3.</rdfs:comment>
        <rdfs:label xml:lang="en">Trap Card</rdfs:label>
        <rdfs:seeAlso rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">http://yugioh.wikia.com/wiki/Trap_Card</rdfs:seeAlso>
    </owl:Class>'''

import test3
text1 = test3.open_rdf_as_xml("prova-gianlu4.owl")
lista = test3.object_delimited(text1, "owl:Class")
text = lista[1]
print(text)


m = re.findall('"(.+?)"', text)
"""if m:
    print(m)"""
string = ""
count = 0
for split in range(0, len(text.split('"'))):
    _tmp = text.split('"')[split]
    if split % 2 == 0:
        string = string + _tmp.replace(":","__")
    else:
        string = string + '"' + m[count] + '"'
        count = count + 1


with open("file.xml", 'w') as xfile:
    xfile.write(string)
    xfile.close()
#os.remove("file.xml")


xmlTree = ET.parse("file.xml")
elemList = []
for elem in xmlTree.iter():
    elemList.append(elem.tag)
print(elemList)


# get the child of the child etc
xmlTree = ET.parse("file.xml")
root = xmlTree.getroot()
edges = []
for child in root:
    print(child.tag)
    edges.append((root.tag, child.tag))
    for x in root.findall(child.tag+"/*"):
        edges.append((child.tag, x.tag))
        print(x.tag)
        for y in child.findall(x.tag+"/*"):
            print(y.tag)
            edges.append((x.tag, y.tag))
print(edges)



"""# get the value of a tag
import networkx as nx
G = nx.DiGraph()
G.add_nodes_from(elemList)
G.add_edges_from(edges)
roots = "owl__Class"
nx.topological_sort(G)
bfs_list = []
# se ricerca al contrario: reverse = True
#print("The QUEUE with BFS for each root are:")
#bfs_list.append(list(nx.bfs_edges(G, source="owl__Class")))
#print(list(nx.bfs_edges(G, source="owl__Class")))
lista_nuova = list(nx.shortest_path(G, source='owl__Class', target='owl__minQualifiedCardinality'))

dizionario = ['owl__Class', 'rdfs__subClassOf', 'owl__Restriction']"""
