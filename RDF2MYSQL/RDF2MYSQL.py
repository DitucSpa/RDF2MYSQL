# commentare tutto
# aggiustare il passaggio dei nomi "owl:Class", "owl:..." e del "definition.txt"
# pip install -r requirements.txt
# sistemare codice per accettare anche json e convertirli
# convertire ttl in rdf



import tkinter as tk
from tkinter import ttk
from tkinter import *
import mysql.connector
from tkinter import messagebox, filedialog
import os
import rdflib
import time
from rdflib import URIRef, Graph
import networkx as nx


from SQL_object_dataType_property import SQLDomainRangeObjectProperty, SQLDomainRangeDataType
from SQL_class import getPK_FKSubclass
import sys
import rdf_analyzer
import definition_file_creation
import create_random_string


definition_path = "/definition.txt"
rdf_keyWord = {"class":"owl:Class",
               "objectProperty":"owl:ObjectProperty",
               "dataTypeProperty":"owl:DatatypeProperty"}
user_work_path = os.getcwd()
dataTypeMapping_path = user_work_path + "/types_mapping.txt"
connection_params = {}


class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        self.frames = {}
        for F in (CheckConnectionPage, RDF2MYSQLPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")
        self.show_frame(CheckConnectionPage)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class CheckConnectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def my_show():
            if checkbutton.var.get()==0:
                passwordEntry.config(show='') # display the chars
            else:
                passwordEntry.config(show='*')# hide the chars using mask
        def checkConnection():
            global connection_params
            connection_params = {"host":hostEntry.get(),
                                 "user":userEntry.get(),
                                 "password":passwordEntry.get(),
                                 "database":databaseEntry.get()}
            try:
                cnx = mysql.connector.connect(host=connection_params["host"],
                                              user=connection_params["user"],
                                              password=connection_params["password"],
                                              database=connection_params["database"])
                if (cnx.is_connected()):
                    controller.show_frame(RDF2MYSQLPage)
            except Exception as ex: messagebox.showerror('Connection Error', 'ERROR: {0}'.format(str(ex)))

        hostLabel = Label(self, text="Host").grid(row=0, column=0)
        host = StringVar()
        hostEntry = Entry(self, textvariable=hostLabel)
        hostEntry.grid(row=0, column=1)
        hostEntry.insert(END,"localhost")

        userLabel = Label(self, text="Username").grid(row=1, column=0)
        user = StringVar()
        userEntry = Entry(self, textvariable=user)
        userEntry.grid(row=1, column=1)
        userEntry.insert(END,"root")

        databaseLabel = Label(self, text="Database").grid(row=2, column=0)
        database = StringVar()
        databaseEntry = Entry(self, textvariable=database)
        databaseEntry.grid(row=2, column=1)
        databaseEntry.insert(END,"superset")

        passwordLabel = Label(self,text="Password").grid(row=3, column=0)
        password = StringVar()
        passwordEntry = Entry(self, textvariable=password, show='*')
        passwordEntry.grid(row=3, column=1)

        checkbutton = Checkbutton(self, text="Show password", onvalue=False, offvalue=True, command=my_show)
        checkbutton.var = BooleanVar(value=True)
        checkbutton['variable'] = checkbutton.var
        checkbutton.grid(row=3, column=2)

        checkConnection = Button(self, text="Check Connection", command = checkConnection).grid(row=4, column=0)






# second window frame page1
class RDF2MYSQLPage(tk.Frame):
    def __init__(self, parent, controller):


        def updateProgressBar(progressBar, update_value, start=None):
            self.update_idletasks()
            if start:
                progressBar['value'] = 0
            progressBar['value'] += update_value

        """clean the text inside the txt passed.
        The function accepts the value elimination and the txt to be clean"""
        def cleanTxt(value, txt):
            txt.config(state=NORMAL)
            txt.delete(value, END)
            txt.config(state=DISABLED)

        """update the txt with the message passed.
        The function accepts the name of the txt to be update, the text position
        and the message"""
        def updateTxt(txt, position, message):
            txt.config(state=NORMAL)
            txt.insert(position, message)
            txt.config(state=DISABLED)

        """upload of the RDF/XML file (through the window)"""
        def uploadFile():
            cleanTxt('1.0', txtprogression) # clean the txt progression in the window
            cleanTxt(0, txtpath) # clean the txt path in the window
            updateTxt(txtprogression, END, "selecting file...") # the user is selecting a file

            try:
                global user_work_path, dataTypeMapping_path


                tf = filedialog.askopenfilename(initialdir=user_work_path, title="Open RDF/XML file",
                                                filetypes=(("RDF/XML file", "*.owl *.txt"),))
                updateTxt(txtpath, END, tf) # update the txt path with the path of the file
                tf_open = open(tf)
                data = tf_open.read()
                if str(os.path.split(tf)[-1]) == 'types_mapping.txt':
                    with open(dataTypeMapping_path, 'w') as f:
                        f.write(data)
                    tf_open.close()
                    updateTxt(txtprogression, END, "\n***{0}***".format("'types_mapping.txt' imported successfully"))
                    updateProgressBar(pb1, 100, start=True)
                    return
                tf_open.close()
                if os.path.exists(user_work_path + definition_path):
                    os.remove(user_work_path + definition_path)
                if not os.path.exists(dataTypeMapping_path):
                    raise TypeError("ERROR: the 'types_mapping.txt' file is missing in the '{0}' directory. Please upload 'types_mapping.txt' first".format(user_work_path))
                ElaborateFile(data) # start to elaborate the file, passing the data of the file uploaded

            except TypeError as ex: updateTxt(txtprogression, END, "\n***{0}***".format(ex)) # the user is selecting a file
            except Exception as ex: # the user doesn't select any file
                cleanTxt('1.0', txtprogression)
                cleanTxt(0, txtpath)
            finally: return

        """elaboration of the RDF/XML. The function accepts the data of file
        selected by the user"""
        def ElaborateFile(file_data):
            updateTxt(txtprogression, END, "\nanalyzing the file...")
            try:
                """create a random string of 4 chars for change the ":" inside the file.
                ":" isn't recognized by the XML parser"""
                random_string = create_random_string.createRandomChanger(file_data)

                """try to parse the data of the file through rdf main words.
                For example parse respect to Classes, ObjectProperties and so on.
                The function accepts the data and a vector composed by all the rdf main words"""
                key_word = [rdf_keyWord["class"],rdf_keyWord["objectProperty"],rdf_keyWord["dataTypeProperty"]]
                dict_of_objects = rdf_analyzer.analyzeFile(file_data, key_word)
                updateProgressBar(pb1, 10, start=True) # update of the progress bar in the window

                updateTxt(txtprogression, END, "\ncreation of the definition file...")
                """now try to analyze each object parsed and save the result inside a default file
                called "definition.txt". Here are saved the infromation about each class, dataType, etc.
                The function accepts a dictionary of parsed object (Classes, DataType, Object),
                a vector of rdf words (for example 'owl:Class') and the random string"""
                global user_work_path
                message = definition_file_creation.analyzeEachObject(dict_of_objects, key_word, random_string, user_work_path)
                if not "successfully" in str(message).lower():
                    raise TypeError("***ERROR: There's something wrong in the {0} file***".format(txtpath.get()))
                updateTxt(txtprogression, END, "\n***{0}***".format(message))
                updateProgressBar(pb1, 20) # add 20% to the previous value of progress bar
                writeSQLQuery()
            except TypeError as ex:
                updateTxt(txtprogression, END, "\n{0}".format(ex))
            except Exception as ex:
                updateTxt(txtprogression, END, "\n***ERROR: Impossible to analyze the file***")
            finally: return





        def writeSQLQuery():
            try:
                global user_work_path, definition_path, connection_params
                definition_file = user_work_path + definition_path
                dataTypeMapping_path

                """--------------------------CLASS--------------------------"""
                # sistemare questione se creare un nuovo DB oppure no
                updateTxt(txtprogression, END, "\ncreation of the SQL tables...")
                message = getPK_FKSubclass(definition_file, connection_params)
                if not "successfully" in str(message).lower():
                    raise Exception(message)
                updateTxt(txtprogression, END, "\n***{0}***".format(message))
                updateTxt(txtprogression, END, "\ncreation of the connections between tables...")
                updateProgressBar(pb1, 20) # add 20% to the previous value of progress bar


                """--------------------------OBJECT PROPERTIES--------------------------"""
                # default con 1-N cardinalità
                # sistemare codice inverse_of in combination
                # sistemare codice per creare chiavi esterne con lo steso nome
                objectProperties = {"domain":"domain", "range":"range", "inverse":"inverse"}
                message = SQLDomainRangeObjectProperty(definition_file, objectProperties, connection_params)
                if not "successfully" in str(message).lower():
                    raise Exception(message)
                updateTxt(txtprogression, END, "\n***{0}***".format(message))
                updateProgressBar(pb1, 40) # add 20% to the previous value of progress bar


                """--------------------------DATATYPE PROPERTIES--------------------------"""
                # ontologia qudt
                updateTxt(txtprogression, END, "\ncreation of the SQL data columns...")
                dataTypeProperties = {"domain":"domain", "range":"range", "inverse":"inverse"}
                message = SQLDomainRangeDataType(definition_file, dataTypeProperties, connection_params, file_mapping_name=dataTypeMapping_path)
                if not "successfully" in str(message).lower():
                    raise Exception(message)
                updateTxt(txtprogression, END, "\n***{0}***".format(message))
                updateProgressBar(pb1, 10) # add 20% to the previous value of progress bar
                updateTxt(txtprogression, END, "\n\n***************DATABASE CREATED SUCCESSFULLY***************")
            except Exception as ex: updateTxt(txtprogression, END, "\n***{0}***".format(ex))
            finally: return



        tk.Frame.__init__(self, parent)
        txtprogression = Text(self, width=80, height=20)
        txtprogression.pack(pady=20)
        txtprogression.config(state=DISABLED)
        txtpath = Entry(self)
        txtpath.pack(side=LEFT, expand=True, fill=X, padx=20)
        txtpath.config(state=DISABLED)
        Button(self, text="Upload File", command=uploadFile).pack(side=RIGHT, expand=True, fill=X, padx=20)
        pb1 = ttk.Progressbar(self, orient=HORIZONTAL, length=50, mode='determinate')
        pb1.pack(side=RIGHT, expand=True, fill=X, padx=40)






app = tkinterApp()
app.title("RDF2MYSQL")
app.geometry("700x400")
app.mainloop()
