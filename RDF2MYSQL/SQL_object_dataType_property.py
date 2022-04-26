import combinate_domain_range as cdr
import SQL_execute
import mysql
from read_file import readFile
from clean_uri import cleanUri

def SQLDomainRangeObjectProperty(file, objectProperties, connection_params, class_name="owl:ObjectProperty", inverse=False):
    try:
        definition = readFile(file, split = "};")
        combinations = cdr.combinateDomainRange(definition, objectProperties, class_name, inverse)
        for combination in combinations:
            for pair in combination:
                #print("****")
                #print("Pair:\t" + str(pair))
                domain_table = ""
                range_table = ""
                domain_PK = ""
                for x in definition:
                    element = eval(x)
                    if element["URI"] == pair[1]:
                        domain_table = element["tableName"]
                        domain_PK = element["PK"]
                    elif element["URI"] == pair[2]:
                        range_table = element["tableName"]
                    if pair[1] == pair[2]:
                        range_table = element["tableName"]
                    if domain_table and range_table and domain_PK:
                        s = []
                        s.append("ALTER TABLE " + range_table.lower() + " ADD " + pair[0] + "_" + domain_table.replace("_","") + " INT")
                        s.append("ALTER TABLE " + range_table.lower() + " ADD FOREIGN KEY (" + pair[0] + "_" + domain_table.replace("_","") + ") REFERENCES " + domain_table.lower() + " (" + domain_PK + ")")
                        #print(s)
                        query = SQL_execute.SQLExecute(s, connection_params)
                        if query:
                            raise query
                        break
        return "Object Properties created successfully."
    except TypeError as e: return "ERROR: Impossible to open or read the '{0}' file.".format(file)
    except SyntaxError as e: return "ERROR: There's something wrong in the definition file."
    except mysql.connector.errors.ProgrammingError as e: return "ERROR " + str(e)


def SQLDomainRangeDataType(file, dataTypeProperties, connection_params, file_mapping_name, class_name="owl:DatatypeProperty"):
    try:
        mapping_types_dict = eval(readFile(file_mapping_name, split = "}", token = "#")[0].lower())
    except TypeError as e: return "Impossible to open or read the '{0}' file.".format(file_mapping_name)
    try:
        definition = readFile(file, split = "};")
        combinations = cdr.combinateDomainRange(definition, dataTypeProperties, class_name)
        for combination in combinations:
            for pair in combination:
                #print("****")
                #print("Pair:\t" + str(pair))
                domain_table = ""
                for x in definition:
                    element = eval(x)
                    if element["URI"] == pair[1]:
                        domain_table = element["tableName"]
                    type = cleanUri(pair[2])
                    if domain_table and type != "None":
                        if not type.lower() in mapping_types_dict.keys():
                            raise Exception("ERROR: the owl type '{0}' doesn't exist in the SQL language.".format(type.lower()))
                        SQLtype = mapping_types_dict[type.lower()].upper()
                        s = []
                        s.append("ALTER TABLE " + domain_table.lower() + " ADD COLUMN " + pair[0] + " " + SQLtype)
                        #print(s)
                        query = SQL_execute.SQLExecute(s, connection_params)
                        if query:
                            raise query
                        break
                    elif domain_table and type == "None":
                        SQLtype = mapping_types_dict["string"].upper()
                        s = []
                        s.append("ALTER TABLE {0} ADD COLUMN value {1}, ADD COLUMN unit_qudt {2}".format(domain_table.lower(), SQLtype, SQLtype))
                        #print(s)
                        query = SQL_execute.SQLExecute(s, connection_params)
                        if query:
                            raise query
                        break
        return "DataType Properties created successfully."
    except TypeError as e: return "ERROR: Impossible to open or read the '{0}' file.".format(file)
    except SyntaxError as e: return "ERROR: There's something wrong in the '{0}' file.".format(file)
    except mysql.connector.errors.ProgrammingError as e: return "ERROR " + str(e)
