# https://protegewiki.stanford.edu/wiki/ConvertToDBScript
# https://www.youtube.com/watch?v=kiAK4gFi9WU
# https://protegewiki.stanford.edu/wiki/ConfiguringAntBuildFiles
# https://raw.githubusercontent.com/protegeproject/autoupdate/master/update-info/5.0.0/plugins.repository
# port:3306
# user: Dituc oppure root
# psw: solita
# java -jar owl2vowl.jar -file tesi.owl
import rdflib
from rdflib import URIRef, Graph
import json
import re
import networkx as nx
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

_visualize_URI = True
path = r"C:\Users\Ovettino\Desktop\Tesi_Laurea\GitHub\MyThesis_BiomedicalEngineering\OWL\Gianluca_DiTuccio_tesi.owl"
path = r"C:\Users\Ovettino\Desktop\yugioh.owl"


with open(path, "r") as f:
    xml = f.read()
list_owl = str(BeautifulSoup(xml, 'xml')).split("\n")

def search_and_return(list_name, object_to_find):
    for _element in range(0, len(list_name)):
        if object_to_find in list_name[_element]:
            try:
                _tmp = list_name[_element + 4]
                return _element + 4
            except:
                return _element
    # if the object isn't in the list
    return -1

def from_list_to_splitting_string(list_name, separator, index):
    _str = ""
    for i in range(index, len(list_name)):
        _str = _str + list_name[i]
    return _str.split(separator)

def manipulation_subclasses(list_name, bool):
    dict_subclasses = {}
    for _element in list_name:
        key = ""
        value = ""
        if "subClassOf" in _element and "Class" in _element:
            for split in range(0, len(_element.split('<'))):
                _tmp = _element.split('<')[split].split('>')[0]
                for _object in _tmp.split("\n"):
                    if "subClassOf" in _object:
                        value = re.search('"(.*)"', _object)
                        if value:
                            value = _object[value.start():value.end()]
                    elif "Class" in _object:
                        key = re.search('"(.*)"', _object)
                        if key:
                            key = _object[key.start():key.end()]
            if key and value:
                if not bool:
                    dict_subclasses[key.replace('"', "")] = value.replace('"', "")
                else:
                    if "#" in key and "#" in value:
                        dict_subclasses[key.replace('"', "").split("#")[-1]] = value.replace('"', "").split("#")[-1]
                    elif "#" in key and "/" in value:
                        dict_subclasses[key.replace('"', "").split("#")[-1]] = value.replace('"', "").split("/")[-1]
                    elif "/" in key and "#" in value:
                        dict_subclasses[key.replace('"', "").split("/")[-1]] = value.replace('"', "").split("#")[-1]
                    else:
                        dict_subclasses[key.replace('"', "").split("/")[-1]] = value.replace('"', "").split("/")[-1]
    return dict_subclasses

def manipulation_classes(list_name, bool):
    classes = []
    for _element in list_name:
        if "Class" in _element:
            for split in range(0, len(_element.split('<'))):
                _tmp = _element.split('<')[split].split('>')[0]
                for _object in _tmp.split("\n"):
                    if "owl:Class" in _object:
                        match = re.search('"(.*)"', _object)
                        if not bool:
                            classes.append(_object[match.start():match.end()].replace('"', ""))
                        else:
                            if "#" in _object[match.start():match.end()].replace('"', ""):
                                _tmp_classes = _object[match.start():match.end()].replace('"', "").split("#")
                                classes.append(_tmp_classes[-1])
                            else:
                                _tmp_classes = _object[match.start():match.end()].replace('"', "").split("/")
                                classes.append(_tmp_classes[-1])
    return classes


def manipulation_dataproperty(list_name, type_passed):
    dict_dataproperty = {}
    for _element in list_name:
        key = ""
        value = ""
        _label = ""
        _comment = ""
        for split in range(0, len(_element.split('<'))):
            _tmp = _element.split('<')[split].split('>')[0]
            _tmp2 = _element.split('<')[split].split('>')
            if "Classes" in _element:
                return dict_dataproperty
            if len(_tmp2) == 2:
                if not _tmp2[1] == "":
                    _tmp2 = _element.split('<')[split].split('>')[1]
            if _tmp.startswith('/') or _tmp.startswith('!--'):
                continue
            if type_passed["name"] in _tmp:
                name = re.search('"(.*)"', _tmp)
                if name:
                    name = _tmp[name.start():name.end()].replace('"',"")
            if type_passed["domain"] in _tmp and type_passed["domain_exception"] in _tmp:
                domain = re.search('"(.*)"', _tmp)
                if domain:
                    domain = _tmp[domain.start():domain.end()].replace('"',"")
            if type_passed["range"] in _tmp:
                _range = re.search('"(.*)"', _tmp)
                if _range:
                    _range = _tmp[_range.start():_range.end()].replace('"',"")
            if type_passed["comment"] in _tmp:
                _comment = _tmp2
            if type_passed["label"] in _tmp:
                _label = _tmp2

        if name and domain and _range:
            if _label and _comment:
                print(_label, _comment)
                dict_dataproperty[domain.replace("/","#").replace('"', "").split("#")[-1]] = [name.replace("/","#").replace('"', "").split("#")[-1],
                                  _range.replace("/","#").replace('"', "").split("#")[-1], _label, _comment]
            else:
                dict_dataproperty[domain.replace("/","#").replace('"', "").split("#")[-1]] = [name.replace("/","#").replace('"', "").split("#")[-1],
                                  _range.replace("/","#").replace('"', "").split("#")[-1]]
    return dict_dataproperty

types_of_separator = {"class": "</owl:Class>",
                      "dataproperty":"</owl:DatatypeProperty>"}

dataproperty_separator = {"name":"owl:DatatypeProperty",
                          "domain":"rdfs:domain",
                          "range":"rdfs:range",
                          "domain_exception":"rdf:resource",
                          "comment":"rdfs:comment",
                          "label":"rdfs:label",
                          "language":'xml:lang="en"'}




index_classes = search_and_return(list_owl, "Classes")
index_dataproperty = search_and_return(list_owl, "Data properties")
list_classes = from_list_to_splitting_string(list_owl, "</owl:Class>", index_classes)
dict_subclasses = manipulation_subclasses(list_classes, _visualize_URI)


list_dataproperty = from_list_to_splitting_string(list_owl, types_of_separator["dataproperty"], index_dataproperty)
dict_dataproperty = manipulation_dataproperty(list_dataproperty, dataproperty_separator)


G = nx.DiGraph()
nodes = manipulation_classes(list_classes, _visualize_URI)
edges = []
for key, value in dict_subclasses.items():
    edges.append((value, key))


G.add_nodes_from(nodes)
G.add_edges_from(edges)
nx.topological_sort(G)
print("BFS ALGORITHM ==============================================================================================")
print("The NODES are:")
print(nodes)
roots = []
for component in nx.weakly_connected_components(G):
    G_sub = G.subgraph(component)
    roots.extend([n for n,d in G_sub.in_degree() if d==0])
print("The ROOTS are:")
print(roots)
print("The EDGES are:")
print(list(nx.topological_sort((nx.line_graph(G)))))



bfs_list = []
# depth_limit=2
# se ricerca al contrario: reverse = True
print("The QUEUE with BFS for each root are:")
for root in roots:
    bfs_list.append(list(nx.bfs_edges(G, source=root)))
    print(list(nx.bfs_edges(G, source=root)))

psw = "Avm46ferces99!"
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=psw
)
mycursor = mydb.cursor()
mycursor.execute("DROP DATABASE IF EXISTS superset")
mycursor.execute("CREATE DATABASE superset")

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=psw,
  database = "superset"
)
mycursor = mydb.cursor()

for cl in nodes:
    try:
        mycursor.execute("CREATE TABLE " + cl.lower() + "_ (" + cl + "_id INT NOT NULL, PRIMARY KEY(" + cl +"_id))")
    except:
        mycursor.execute("CREATE TABLE " + cl.lower().replace("-","") + "_ (" + cl.replace("-","") + "_id INT NOT NULL, PRIMARY KEY(" + cl.replace("-","") +"_id))")

for b in bfs_list:
    for ed in b:
        if "thing" in ed[0].lower():
            continue
        try:
            mycursor.execute("ALTER TABLE " + ed[1].lower() + "_ ADD " + ed[0] + "_fk INT NOT NULL")
            mycursor.execute("ALTER TABLE " + ed[1].lower() + "_ ADD FOREIGN KEY (" + ed[0] + "_fk) REFERENCES " + ed[0].lower() + "_ (" + ed[0] + "_id)")
            mycursor.execute("ALTER TABLE " + ed[1].lower() + "_ ADD CONSTRAINT UNQ_ST_S_ID UNIQUE (" + ed[0] + "_fk);")
        except:
            mycursor.execute("ALTER TABLE " + ed[1].lower().replace("-","") + "_ ADD " + ed[0].replace("-","") + "_fk INT NOT NULL")
            mycursor.execute("ALTER TABLE " + ed[1].lower().replace("-","") + "_ ADD FOREIGN KEY (" + ed[0].replace("-","") + "_fk) REFERENCES " + ed[0].lower().replace("-","") + "_ (" + ed[0].replace("-","") + "_id)")
            mycursor.execute("ALTER TABLE " + ed[1].lower().replace("-","") + "_ ADD CONSTRAINT UNQ_ST_S_ID UNIQUE (" + ed[0].replace("-","") + "_fk);")

print()
print()
print("DATA PROPERTY ==============================================================================================")
print("Class [DataPropertyName | Type | Label | Comment]")
print()
for key in dict_dataproperty.keys():
    try:
        if dict_dataproperty[key][1].lower() == "anyuri" or dict_dataproperty[key][1].lower() == "literal" or dict_dataproperty[key][1].lower() =="string":
            value = dict_dataproperty[key]
            value[1] = "VARCHAR(255)"
            _dict_tmp = {}
            _dict_tmp[key] = value
            dict_dataproperty.update(_dict_tmp)

        for a in value:
            if a.lower() == "anyuri" or a.lower() == "literal" or a.lower() =="string":
                value
        print(key, dict_dataproperty[key])
        mycursor.execute("ALTER TABLE " + key.lower() + "_ ADD COLUMN " + dict_dataproperty[key][0] + " " + dict_dataproperty[key][1])

    except:
        mycursor.execute("ALTER TABLE " + key.lower().replace("-","") + "_ ADD COLUMN " + dict_dataproperty[key][0].replace("-","") + " " + dict_dataproperty[key][1])

# edge_labels = nx.get_edge_attributes(G,'label')
pos = nx.planar_layout(G)
nx.draw_networkx_nodes(G, pos=pos)
nx.draw_networkx_labels(G, pos=pos)
nx.draw_networkx_edges(G, pos=pos)
# nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
plt.show()
