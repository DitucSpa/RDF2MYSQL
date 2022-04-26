from read_file import readFile
import networkx as nx
from SQL_execute import SQLExecute

def getPK_FKSubclass(definition_path, connection_params, class_name = "owl:Class"):
    table = {}
    edges = []
    nodes = []
    bfs_list = []
    roots = []
    try:
        definition = readFile(definition_path, split = "};")
        for x in definition:
            element = eval(x)
            if element["type"] == class_name:
                if "PK" in element.keys() and "tableName" in element.keys() and "URI" in element.keys():
                    table[element["tableName"]] = element["PK"]
                    nodes.append(element["tableName"])
                else:
                    raise Exception("ERROR: some parameters in the '{0}' file are wrong or missing.".format(definition_path))
                if "FK_subclass" in element.keys():
                    edges.append((element["FK_subclass"], element["tableName"]))
        if not edges and not nodes:
            raise Exception("ERROR: There are no classes.")
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.topological_sort(G)
        for component in nx.weakly_connected_components(G):
            G_sub = G.subgraph(component)
            roots.extend([n for n,d in G_sub.in_degree() if d==0])
        for root in roots:
            bfs_list.append(list(nx.bfs_edges(G, source=root)))
        tmp = checkDatabase(connection_params)
        if tmp:
            raise Exception(tmp)
        tmp = createSQLTable(bfs_list, table, connection_params)
        if tmp:
            raise Exception(tmp)
        return "Classes created successfully"
    except TypeError as e: return "ERROR: Impossible to open or read the '{0}' file.".format(definition_path)
    except SyntaxError as e: return "ERROR: There's something wrong in the '{0}' file.".format(definition_path)
    except Exception as ex: return ex



def checkDatabase(sql_params_connection):
    try:
        s = []
        s.append("DROP DATABASE IF EXISTS superset")
        s.append("CREATE DATABASE superset")
        tmp = SQLExecute(s, sql_params_connection)
        if tmp:
            raise Exception(tmp)
    except Exception as ex: return "ERROR " + str(ex)


def createSQLTable(bfs_list, table, sql_params_connection):
    try:
        s = []
        for key in table.keys():
            s.append("CREATE TABLE {0} ({1} INT NOT NULL AUTO_INCREMENT, URI VARCHAR(255), PRIMARY KEY ({2}))".format(key.lower(), table[key], table[key]))
        for bfs in bfs_list:
            for element in bfs:
                if not "thing" in element[0].lower():
                    s.append("ALTER TABLE {0} ADD {1}_fk INT".format(element[1].lower(), element[0]))
                    s.append("ALTER TABLE {0} ADD FOREIGN KEY ({1}_fk) REFERENCES {2}_ ({3}_id)".format(element[1].lower(), element[0], element[0].lower(), element[0]))
                    s.append("ALTER TABLE {0} ADD CONSTRAINT UNQ_ST_S_ID UNIQUE ({1}_fk);".format(element[1].lower(), element[0]))
        query = SQLExecute(s, sql_params_connection)
        if query:
            raise Exception("ERROR " + str(query))
    except Exception as ex: return ex
