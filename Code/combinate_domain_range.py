import itertools as it
import clean_uri

def populate(element, type):
    population = []
    for key in element.keys():
        if type in key:
            population.append(element[key]["rdf:resource"])
    if population:
        return population
    return []

def combinate(domain, range):
    dictionary = {}
    dictionary["domain"] = domain
    dictionary["range"] = range
    combinations = it.product(*(dictionary[key] for key in dictionary.keys()))
    return list(combinations)

def combinateDomainRange(file, property_dict, owl_name, inverse_of=False):
    try:
        combinations = []
        name = []
        for x in file:
            element = eval(x)
            range = []
            domain = []
            if element["type"] == owl_name:
                if not [True for s in element.keys() if property_dict["inverse"] in s]:
                    if owl_name == "owl:DatatypeProperty":
                        if [s for s in element.keys() if property_dict["range"] in s]:
                            range = populate(element, property_dict["range"])
                        else:
                            range = ["None"]
                    else:
                        range = populate(element, property_dict["range"])
                    domain = populate(element, property_dict["domain"])
                    if domain and range:
                        combinations.append(appendName(clean_uri.cleanUri(element["URI"]), combinate(domain, range)))
        return combinations
    except Exception as err:
        return err

def appendName(name, combination):
    new_combination = []
    for i in range(0, len(combination)):
        new_combination.append((name,) + combination[i])
    return new_combination
