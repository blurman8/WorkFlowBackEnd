from flask import Flask,request, jsonify
import json

 
import mysql.connector
import time
from key_generator.key_generator import generate
#set FLASK_APP=hello
#set FLASK_RUN_PORT=8000
#set 
#   FLASK_ENV=development
app = Flask(__name__)


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8880)

@app.route('/')
def hello():

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        
    )
    mycursor = mydb.cursor()

    mycursor.execute("SHOW DATABASES")
    
    str = ""
    for x in mycursor:
        str = str + x[0]



    return str

@app.route('/initial_mysql')
def initial_mysql():

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
    )
    try:

        mycursor = mydb.cursor()

        mycursor.execute("SHOW DATABASES")
        
        str = ""
        founddb = "0"
        ans = "0";
        for x in mycursor:
            print (x[0]) 
            if  x[0] == "workflow":
                founddb = "1"
                ans = "1"  
        mycursor = mydb.cursor()        
        if founddb == "0" :
            mycursor.execute("CREATE DATABASE workflow")
        mycursor.execute("use workflow") 

        mycursor.execute("CREATE TABLE IF NOT EXISTS userinfo (uid INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), apassword VARCHAR(255), akey VARCHAR(255), created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS roleinfo (rid INT AUTO_INCREMENT PRIMARY KEY, rolename VARCHAR(255), created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS roleuserinfo (id INT AUTO_INCREMENT PRIMARY KEY, rid INT,uid INT, created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS flowinfo (fid INT AUTO_INCREMENT PRIMARY KEY, flowname VARCHAR(255),design TEXT(10000), created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS flowstepinfo (sid INT AUTO_INCREMENT PRIMARY KEY, fid INT,stepname varchar(255), rid INT, created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS jobinfo (jid INT AUTO_INCREMENT PRIMARY KEY, jobname VARCHAR(255), fid INT, currentstep INT ,created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS jobhistory (jhid INT AUTO_INCREMENT PRIMARY KEY, jid INT, fid INT, currentstep INT ,comments text(5000),created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS rolefunction (rfnid INT AUTO_INCREMENT PRIMARY KEY, fname Varchar(255), rid INT,created_at timestamp )")
        mycursor.close()
            

    except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    return "done"
@app.route('/key_gen')
def key_gen():
    ts = time.time() 

    key = generate(seed = ts)
    key_custom = generate(1, '-', 32, 32 , type_of_value = 'char', capital = 'mix',   seed = ts).get_key()
 
    return key_custom

@app.route('/id_gen')
def id_gen():
    ts = time.time() 
 
    key_custom = generate(4, '-', 4, 8 , type_of_value = 'hex', capital = 'mix',   seed = ts).get_key()
 
    return key_custom

 

@app.route('/create_flow/<name>/<key>')
def create_flow(name=None, key=None):
    error = ""
    ts = time.time() 
 
    key_custom = generate(4, '-', 4, 8 , type_of_value = 'hex', capital = 'mix',   seed = ts).get_key()
    design = '[{ "type": "draw2d.shape.node.Start","id": "'+ key_custom +'","x": 40,"y": 140,"width": 40,"height": 40,"radius": 2 }]'

    #mycursor.execute("CREATE TABLE IF NOT EXISTS flowinfo (fid INT AUTO_INCREMENT PRIMARY KEY, flowname VARCHAR(255),design TEXT(10000), created_at timestamp )")
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
    )
    try:
        mycursor = mydb.cursor()
        sql = "INSERT INTO flowinfo (flowname, design, created_at) VALUES (%s, %s, now())"
        val = (name, design)
        mycursor.execute(sql, val)
        mydb.commit()


    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        error = "Failed to insert into MySQL table"
    finally:
        if mydb.is_connected():
            mycursor.close()            
            mydb.close()
            print("MySQL connection is closed")

    if error == "" :
        return "{result:  done}";
    else :
        return "{result: \""+ error + "\"}"\

 
@app.route('/view/flow/<id>')
def view_flow(id=None):
 

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
    )
    str = ""
    try:

        mycursor = mydb.cursor()

        sql = ("Select * from flowinfo where fid=" + id) 
        mycursor.execute(sql)
        
        
        for x in mycursor:
            print (x[2]) 
            str = x[2]

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    return str
@app.route('/update/flow/<id>',methods=['GET', 'POST'])
def update_flow(id=None):
     
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
    )
    myJSON = request.get_json(silent=True)

    str = json.dumps(myJSON)
    str3 = str[1:]
    str =  str3[:-1]


    str2 = str.replace("\\n", "")
    str = str2.replace("\\\"", "\"")
    str2 = str.replace("  ", "")
    print ("json data = "+ str2)
    print ("json data size =",len(str)," ", len(str2))
    str = str2
    print ("update flowinfo set design = '",str,"' where fid=" , id)
    try:

        mycursor = mydb.cursor()

        sql = ("update flowinfo set design = '"+str+"' where fid=" + id) 
        mycursor.execute(sql)
        mydb.commit()

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        str ="Error"
    finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    return str

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8000')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  response.headers.add('Access-Control-Allow-Credentials', 'true')
  return response