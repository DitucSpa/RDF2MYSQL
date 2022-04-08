import rdflib
from rdflib import URIRef, Graph
import json
import re
import networkx as nx
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

def open_rdf_as_xml(path):
    with open(path, "r") as _f:
        _xml = _f.read()
    return str(BeautifulSoup(_xml, 'xml'))

def object_delimited(_str_file, delimiter):
    _list = []
    delimiter_creation = ["<" + delimiter + " ", "</" + delimiter + ">"]
    for _spliter in range(0, len(_str_file.split(delimiter_creation[0]))):
        if _spliter == 0:
            continue
        _tmp = _str_file.split(delimiter_creation[0])[_spliter].split(delimiter_creation[1])[0]
        if "/>" in _tmp.split(">")[0] + ">":
            _list.append(delimiter_creation[0] + _tmp.split("/>")[0] + "/>")
        else:
            _list.append(delimiter_creation[0] + _tmp + delimiter_creation[1])
    return _list
