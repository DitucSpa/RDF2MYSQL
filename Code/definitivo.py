from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import re
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import xml.dom.minidom as mn
import string
import random
import json
import rdflib
from rdflib import URIRef, Graph
import mysql.connector
import networkx as nx

path = r"C:\Users\Ovettino\Desktop\Superset"
objectProperties = {"domain":["rdfs:domain", "schema:domainIncludes"], "range":["rdfs:range", "schema:rangeIncludes"], "inverse":["owl:inverseOf"]}
key_word = ["owl:Class", "owl:ObjectProperty", "owl:DatatypeProperty"]


# update the main text box
def updateMainTxt(position, string):
    txtarea.insert(position, string)
def cleanMainTxt():
    txtarea.delete('1.0', END)
def updateProgressBar(update_value, start=None):
    ws.update_idletasks()
    if start:
        pb1['value'] = 0
    for i in range(0, update_value):
        pb1['value'] += 1

# python and xml tree don't recognize the char ":" inside the tag
# change ":" with an upper string of 4 chars that doens't exist in the file
def createRandomChanger(file):
    running = True
    while running:
        random_choice = ""
        for i in [1,2,3,4]:
            random_choice = random_choice + random.choice(string.ascii_letters).upper()
            if i == 4 and not random_choice in file:
                running = False
    return random_choice


# the function changes the ":" with the random string
def changeElement(element, string_generated):
    m = re.findall('"(.+?)"', element)
    string = ""
    count = 0
    for split in range(0, len(element.split('"'))):
        tmp = element.split('"')[split]
        if split % 2 == 0:
            string = string + tmp.replace(":",string_generated)
        else:
            string = string + '"' + m[count] + '"'
            count = count + 1
    return string

def cleanUri(uri):
    uri = uri.split("/")[-1]
    if "#" in uri:
        uri = uri.split("#")[-1]
    return uri

def PK(dictionary):
    if dictionary["type"] == key_word[0]:
        dictionary["PK"] = cleanUri(dictionary["uri"]) + "_id"
    return dictionary


def uploadFile():
    cleanMainTxt()
    updateMainTxt(END, "selecting file...")
    with open(path + "/definition.txt", "w") as f:
        f.close()
    tf = filedialog.askopenfilename(initialdir=path, title="Open RDF/XML file",
                                    filetypes=(("RDF/XML file", "*.owl"),))
    updateProgressBar(20, start=True)
    pathh.insert(END, tf)
    tf = open(tf)
    data = tf.read()
    tf.close()
    updateMainTxt(END, "\nanalyzing the file...")
    random_string = createRandomChanger(data)
    dict_of_objects = analyzeFile(data)
    updateProgressBar(20)
    updateMainTxt(END, "\nanalyzing the objects...")
    updateMainTxt(END, "\ncreation of the file definition.txt...")
    analyzeEachObject(dict_of_objects, key_word, random_string)
    updateProgressBar(20)
    updateMainTxt(END, "\ncreation of the SQL tables...")
    definition = openDefinition()
    getPK_FKSubclass(definition)
    updateProgressBar(20)
    updateMainTxt(END, "\ncreation of the connection between tables...")
    createConnectionObjectProperty(definition)
    updateProgressBar(20)
    updateMainTxt(END, "\n***************DATABASE CREATED SUCCESSFULLY***************")

def createConnectionObjectProperty(file):
    file.pop()
    try:
        domain_uri = ""
        range_uri = ""
        name = ""
        for x in file:
            element = eval(x)
            if element["type"] == key_word[1]:
                for inverse in objectProperties["inverse"]:
                    if not inverse in list(element.keys()):
                        for type in objectProperties["range"]:
                            if type in element.keys():
                                range_uri = element[type]["rdf:resource"]
                        for type in objectProperties["domain"]:
                            if type in element.keys():
                                domain_uri = element[type]["rdf:resource"]
                        if domain_uri and range_uri:
                            name = cleanUri(element["uri"])
                            getDomainRange(file, name, domain_uri, range_uri)
    except Exception as ex: print(ex)
    finally: return

def getDomainRange(file, name, domain, range):
    try:
        domain_table = ""
        range_table = ""
        domain_PK = ""
        for x in file:
            element = eval(x)
            if element["uri"] == domain:
                domain_table = element["tableName"]
                domain_PK = element["PK"]
            elif element["uri"] == range:
                range_table = element["tableName"]

        if domain_table and range_table:
            mydb = mysql.connector.connect(
              host="localhost",
              user="root",
              password="Avm46ferces99!",
              database = "superset"
            )
            mycursor = mydb.cursor()
            print("ALTER TABLE " + range_table.lower() + " ADD FOREIGN KEY (" + name + ") REFERENCES " + domain_table.lower() + " (" + domain_PK + ")")
            mycursor.execute("ALTER TABLE " + range_table.lower() + " ADD " + name + " INT NOT NULL")
            mycursor.execute("ALTER TABLE " + range_table.lower() + " ADD FOREIGN KEY (" + name + ") REFERENCES " + domain_table.lower() + " (" + domain_PK + ")")
    except Exception as ex: print(ex)
    finally: return

def analyzeFile(file):
    # create a dict where each element in the file is splitted
    # this dict will contain lists for each object in the file
    # for example the first list could be contained all the "owl:Class" and as key "owl:Class"
    dict_of_elements = {}
    for key in key_word:
        # object_delimited function returns a list with all the objects found in the file
        # key is the delimeter used for search inside the file
        # for example if you want all the Class of the Ontology, you can use
        # "owl:Class" as key
        dict_of_elements[key] = object_delimited(file, key)
    return dict_of_elements



# this function takes the file and search all the elements that contain the delimiter
# it returns a list of all the objects found inside the file
# for example for "owl:Class" you could have ['<owl:Class Mario/>', '<owl:Class Luigi', ...]
def object_delimited(file, delimiter):
    list_of_objects = []
    # the object starts with <delimiter ... > and ends with </delimiter>, or it can be <delimiter ... />
    delimiter_creation = ["<" + delimiter + " ", "</" + delimiter + ">"]
    for spliter in range(0, len(file.split(delimiter_creation[0]))):
        if spliter == 0:
            continue
        tmp = file.split(delimiter_creation[0])[spliter].split(delimiter_creation[1])[0]
        if "/>" in tmp.split(">")[0] + ">":
            list_of_objects.append(delimiter_creation[0] + tmp.split("/>")[0] + "/>")
        else:
            list_of_objects.append(delimiter_creation[0] + tmp + delimiter_creation[1])
    return list_of_objects


def analyzeEachObject(dict_of_objects, object_word, random_string_generated):
    for key in dict_of_objects.keys():
        for element in dict_of_objects[key]:
            new_element = changeElement(element, random_string_generated)
            createTemporanyXml(new_element, random_string_generated)
    return

def createTemporanyXml(file, random_string_generated):
    path_of_temporany_xml = path + "/temporany.xml"
    with open(path_of_temporany_xml, "w") as f:
        f.write(file)
        f.close()
    list_of_tags, root = getXmlTagRoot(path_of_temporany_xml)


    dict_of_attributes = getXmlAttributeValue(path_of_temporany_xml, root.tag, random_string_generated, root=True)
    #dict_of_attributes["path"] = getChildren(root, random_string_generated)

    for t in list_of_tags:
        dict_of_attributes.update(getXmlAttributeValue(path_of_temporany_xml, t, random_string_generated))

    dict_of_elements = PK(dict_of_attributes)
    os.remove(path_of_temporany_xml)
    with open(path + "/definition.txt", "a") as f:
        f.write(json.dumps(dict_of_attributes))
        f.write(";")
        f.close()
    return

def getXmlAttributeValue(file, node, random_string_generated, root=None):
    xmldoc = mn.parse(file)
    itemlist = xmldoc.getElementsByTagName(node)
    dicts = {}
    root_uri = ""
    subclass = False
    for item in itemlist:
        d = {}
        if item.attributes.values():
            for a in item.attributes.values():
                if root:
                    root_uri = a.value.replace(random_string_generated, ":")
                elif node.replace(random_string_generated, ":") == "rdfs:subClassOf" and a.name.replace(random_string_generated, ":") == "rdf:resource":
                    subclass = True
                    root_uri = a.value.replace(random_string_generated, ":")
                else:
                    if a.name.replace(random_string_generated, ":"):
                        d[a.name.replace(random_string_generated, ":")] = a.value.replace(random_string_generated, ":")
                        for i in item.childNodes:
                            if i.nodeType == i.TEXT_NODE:
                                if not "    " in i.data:
                                    d["value"] = i.data.replace("\n","")
            if root:
                dicts[node.replace(node, "uri")] = root_uri
                dicts["type"] = node.replace(random_string_generated, ":")
                if node.replace(random_string_generated, ":") == key_word[0]:
                    dicts["tableName"] = cleanUri(root_uri) + "_"
            elif node.replace(random_string_generated, ":") == "rdfs:subClassOf" and subclass:
                dicts["rdfs:subClassOf"] = root_uri
                dicts["FK_subclass"] = cleanUri(root_uri)
            else:
                if node.replace(random_string_generated, ":") in dicts.keys():
                    running = True
                    count = 1
                    while running:
                        if not node.replace(random_string_generated, ":") + "_" + str(count) in dicts.keys():
                            dicts[node.replace(random_string_generated, ":") + "_" + str(count)] = d
                            running = False
                        else:
                            count = count + 1
                else:
                    dicts[node.replace(random_string_generated, ":")] = d
    return dicts

def getXmlTagRoot(file):
    xmlTree = ET.parse(file)
    root = xmlTree.getroot()
    elemList = []
    for elem in xmlTree.iter():
        if not elem.tag == root.tag:
            elemList.append(elem.tag)
    return elemList, root

def openDefinition():
    with open(path + "/definition.txt", "r") as f:
        tmp = f.read()
        f.close()
    return [x + "}" for x in tmp.split("};")]

def getPK_FKSubclass(dictionary):
    dictionary.pop()
    table = {}
    edges = []
    nodes = []
    bfs_list = []
    roots = []
    try:
        for x in dictionary:
            element = eval(x)
            if element["type"] == key_word[0]:
                if "PK" in element.keys():
                    table[element["tableName"]] = element["PK"]
                    nodes.append(element["tableName"])
                if "FK_subclass" in element.keys():
                    edges.append((element["FK_subclass"], element["tableName"]))
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.topological_sort(G)
        for component in nx.weakly_connected_components(G):
            G_sub = G.subgraph(component)
            roots.extend([n for n,d in G_sub.in_degree() if d==0])
        for root in roots:
            bfs_list.append(list(nx.bfs_edges(G, source=root)))
        createSQLTable(bfs_list, table)
    except Exception as ex:
        print(ex)
    finally:
        return
def createSQLTable(bfs_list, table):
    psw = "Avm46ferces99!"
    try:
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

        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password=psw,
          database = "superset"
        )
        mycursor = mydb.cursor()

        for key in table.keys():
            mycursor.execute("CREATE TABLE " + key.lower() + " (" + table[key] + " INT NOT NULL, PRIMARY KEY(" + table[key] + "))")
        for b in bfs_list:
            for ed in b:
                if "thing" in ed[0].lower():
                    continue
                mycursor.execute("ALTER TABLE " + ed[1].lower() + " ADD " + ed[0] + "_fk INT NOT NULL")
                mycursor.execute("ALTER TABLE " + ed[1].lower() + " ADD FOREIGN KEY (" + ed[0] + "_fk) REFERENCES " + ed[0].lower() + "_ (" + ed[0] + "_id)")
                mycursor.execute("ALTER TABLE " + ed[1].lower() + " ADD CONSTRAINT UNQ_ST_S_ID UNIQUE (" + ed[0] + "_fk);")


    except Exception as ex:
        print(ex)

ws = Tk()
ws.title("Test1")
ws.geometry("700x400")
txtarea = Text(ws, width=80, height=20)
txtarea.pack(pady=20)
pathh = Entry(ws)
pathh.pack(side=LEFT, expand=True, fill=X, padx=20)

Button(ws, text="Upload File", command=uploadFile).pack(side=RIGHT, expand=True, fill=X, padx=20)
pb1 = Progressbar(ws, orient=HORIZONTAL, length=100, mode='determinate')
pb1.pack(side=RIGHT, expand=True, fill=X, padx=40)
ws.mainloop()
