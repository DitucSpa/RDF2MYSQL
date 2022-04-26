def analyzeFile(file, keyWord):
    # create a dict where each element in the file is splitted
    # this dict will contain lists for each object in the file
    # for example the first list could be contained all the "owl:Class" and as key "owl:Class"
    dict_of_elements = {}
    for key in keyWord:
        # object_delimited function returns a list with all the objects found in the file
        # key is the delimeter used for search inside the file
        # for example if you want all the Classes of the Ontology, you can use
        # "owl:Class" as key
        dict_of_elements[key] = objectDelimited(file, key)
    return dict_of_elements

"""this function takes the file and search all the elements that contain the delimiter.
It returns a list of all the objects found inside the file.
For example for "owl:Class" you could have ['<owl:Class Mario/>', '<owl:Class Luigi', ...]"""
def objectDelimited(file, delimiter):
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
