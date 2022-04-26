"""This package tries to create the "definition.txt" file, cointaining the main features of the file passed"""
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import xml.dom.minidom as mn
from clean_uri import cleanUri
import os
import json


"""The function replaces the ':' with the random string for parsing through XML
The function accepts a dictionary of parsed object (for example parsed in 'owl:Class', 'owl:ObjectProperty', etc),
a vector of the main words in rdf ('owl:Class', 'owl:ObjectProperty') and the random string for replacing ':'
and the current work path."""
def analyzeEachObject(dict_of_objects, object_word, random_string_generated, current_path):
    try:
        message = ""
        for key in dict_of_objects.keys():
            for element in dict_of_objects[key]:
                new_element = changeElement(element, random_string_generated) # replace ':' for each element
                message = createTemporanyXml(new_element, random_string_generated, current_path, object_word)
                if "ERROR" in message:
                    raise Exception("ERROR")
        return message
    except Exception as ex: return ex


"""The function replaces the ':' with the random string.
For example an element could be: <owl:Class rdf:about="http://xmlns.com/foaf/0.1/Agent"/>"""
def changeElement(element, string_generated):
    m = re.findall('"(.+?)"', element)
    string = ""
    count = 0
    for split in range(0, len(element.split('"'))):
        tmp = element.split('"')[split]
        if split % 2 == 0:
            string = string + tmp.replace(":",string_generated)
        else: # the ':' inside URIdon't have to be replaced
            string = string + '"' + m[count] + '"'
            count = count + 1
    return string


"""for each element the function creates a temporany XML file for parsing the element through XML parser.
The function accepts an element to be parse, the random string, the user work directory
and the rdf main words."""
def createTemporanyXml(element, random_string_generated, work_path, rdf_word):
    try:
        path_of_temporany_xml = work_path + "/temporany.xml"
        with open(path_of_temporany_xml, "w") as f: # create the file and write the element
            f.write(element)
            f.close()
        """Get the root of the element; for example for <owl:Class rdf:about="http://xmlns.com/foaf/0.1/Agent"/> the root is owl:Class
        Remember that the ':' has been replaced into a random string."""
        list_of_tags, root = getXmlTagRoot(path_of_temporany_xml)

        """Get the attribute and value of the root element"""
        dict_of_attributes = getXmlAttributeValue(path_of_temporany_xml, root.tag, random_string_generated, rdf_word, root=True)
        if dict_of_attributes == "ERROR":
            raise Exception("ERROR")

        for t in list_of_tags:
            current_tmp = getXmlAttributeValue(path_of_temporany_xml, t, random_string_generated, rdf_word)
            if "ERROR" in current_tmp:
                raise Exception("ERROR")
            dict_of_attributes.update(current_tmp)

        """Insert the Primary Key name if the element is a class"""
        dict_of_elements = PK(dict_of_attributes, rdf_word[0]) # rdf_word[0] is the class definition in the rdf (for example "owl:Class")
        if "ERROR" in dict_of_elements:
            raise Exception("ERROR")
        os.remove(path_of_temporany_xml) # remove the temporany xml

        with open(work_path + "/definition.txt", "a") as f: # create definition file saving the dictionary with all the main features
            f.write(json.dumps(dict_of_attributes))
            f.write(";") # the separator between each object
            f.close()
        return "definition.txt file created successfully"
    except Exception as ex: return ex


"""Get the root of the element written in the temporany xml file.
The function returns the root and a list of element tags obtained from the root."""
def getXmlTagRoot(file):
    try:
        xmlTree = ET.parse(file)
        root = xmlTree.getroot()
        elemList = []
        for elem in xmlTree.iter():
            if not elem.tag == root.tag:
                elemList.append(elem.tag)
        return elemList, root
    except: return


"""Get the attribute and value of the root element.
The function accepts the temporany xml file path, the current tag of the node to be evaluate,
the random string generated and if the current node is a Root or not.
The function returns a dict contained attributes, values, etc for the node passed"""
def getXmlAttributeValue(file, node, random_string_generated, rdf_words_used, root=None):
    try:
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
                    dicts[node.replace(node, "URI")] = root_uri
                    dicts["type"] = node.replace(random_string_generated, ":")
                    if node.replace(random_string_generated, ":") == rdf_words_used[0]:
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
    except Exception as ex: return "ERROR"


def PK(dictionary, rdf_class):
    try:
        if dictionary["type"] == rdf_class:
            dictionary["PK"] = cleanUri(dictionary["URI"]) + "_id"
        return dictionary
    except: return "ERROR"
