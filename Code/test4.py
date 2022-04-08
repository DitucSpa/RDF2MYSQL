import xml.etree.ElementTree as ET
# load and parse the file


xmlTree = ET.parse("ciao.xml")

elemList = []
for elem in xmlTree.iter():
    elemList.append(elem.tag)
print(elemList)

# the number of / identifies the level of the tree
#print(xmlTree.find('.//rdfs__domain').attrib['rdf__resource'])


# get the attributes and their values for a certain tag
import xml.dom.minidom as mn
xmldoc = mn.parse("ciao.xml")
itemlist = xmldoc.getElementsByTagName('owl__onClass')
dicts = []
for item in itemlist:
    d = {}
    for a in item.attributes.values():
        d[a.name] = a.value
    dicts.append(d)
print(dicts)
print()
print()

# get the child of the child etc
xmlTree = ET.parse("ciao.xml")
root = xmlTree.getroot()
edges = []
for child in root:
    print(child.tag)
    for x in root.findall(child.tag+"/*"):
        edges.append((child.tag, x.tag))
        print(x.tag)
        for y in child.findall(x.tag+"/*"):
            print(y.tag)
            edges.append((x.tag, y.tag))
print(edges)
# contatore di quante volte una funzione viene chiamata
# serve per dire i livelli che ci sono
def myfunction():
    myfunction.counter += 1
myfunction.counter = 0
myfunction()
myfunction()
print(myfunction.counter)



# get all the element inside ""
import re
text = '''<owl:Class rdf:about="http://ontology.ethereal.cz/ygo#Trap_Card">
        <rdfs:subClassOf rdf:resource="http://ontology.ethereal.cz/ygo#Card"/>
        <rdfs:comment xml:lang="en">Trap cards are cards with purple-colored borders that have various effects. A Trap Card must first be Set and can only be activated after the current turn has finished. After that, it may be activated during either player&apos;s turn. Trap Cards are Spell Speed 2, with the exception of Counter Trap Cards, which are Spell Speed 3.</rdfs:comment>
        <rdfs:label xml:lang="en">Trap Card</rdfs:label>
        <rdfs:seeAlso rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">http://yugioh.wikia.com/wiki/Trap_Card</rdfs:seeAlso>
    </owl:Class>'''
m = re.findall('"(.+?)"', text)
if m:
    print(m)
string = ""
count = 0
for split in range(0, len(text.split('"'))):
    _tmp = text.split('"')[split]
    if split % 2 == 0:
        string = string + _tmp.replace(":","__")
    else:
        string = string + '"' + m[count] + '"'
        count = count + 1
print(string)
print()
print()

# get the value of a tag
import networkx as nx
G = nx.DiGraph()
G.add_nodes_from(elemList)
edges.append(("owl__Class","rdfs__subClassOf"))
G.add_edges_from(edges)
print(edges)
print(elemList)
roots = "owl__Class"
nx.topological_sort(G)
bfs_list = []
for root in roots:
    print(list(nx.bfs_edges(G, source=root)))
