import mysql.connector
def SQLExecute(list_of_executes, connection_dict):
    try:
        mydb = mysql.connector.connect(host = connection_dict["host"],
                                       user = connection_dict["user"],
                                       password = connection_dict["password"],
                                       database = connection_dict["database"])
        mycursor = mydb.cursor()
        for s in list_of_executes:
            mycursor.execute(s)
        mydb.commit()
    except Exception as e:
        return e
