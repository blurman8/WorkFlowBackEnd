from flask import Flask,request, jsonify
from flask_cors import CORS
import json

 
import mysql.connector
import time
from key_generator.key_generator import generate
#set FLASK_APP=hello
#set FLASK_RUN_PORT=8000
#set 
#   FLASK_ENV=development
app = Flask(__name__)
CORS(app)

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8800)

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
        mycursor.execute("CREATE TABLE IF NOT EXISTS flowstepinfo (sid INT AUTO_INCREMENT PRIMARY KEY, fid INT,stepname varchar(255),stepid varchar(255), rid INT, created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS stepdetail (did INT AUTO_INCREMENT PRIMARY KEY, fid INT,sid1 INT,stepid1 varchar(255), sid2 INT,stepid2 varchar(255), created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS jobinfo (jid INT AUTO_INCREMENT PRIMARY KEY, jobname VARCHAR(255), fid INT, currentstep INT ,created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS jobhistory (jhid INT AUTO_INCREMENT PRIMARY KEY, jid INT, fid INT, currentstep INT ,comments text(5000),created_at timestamp )")
        mycursor.execute("CREATE TABLE IF NOT EXISTS rolefunction (rfnid INT AUTO_INCREMENT PRIMARY KEY, fname Varchar(255), rid INT,created_at timestamp )")
        mycursor.execute("INSERT INTO roleinfo (rolename,created_at) VALUES (\"admin\",now()), (\"boss\",now()), (\"head\",now()), (\"user\",now() ) ")
        mydb.commit();
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

    design = '[ ]'

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
        fid = mycursor.lastrowid
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
        return {"result":  "done", "fid" : fid }
    else :
        return {"result": "error", "fid" : 0 }

 
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
    #print ("json data = "+ str2)
    #print ("json data size =",len(str)," ", len(str2))
    str = str2

 


    print ("update flowinfo set design = '",str,"' where fid=" , id)
    try:

        mycursor = mydb.cursor()

        sql = ("update flowinfo set design = '"+str+"' where fid=" + id) 
        mycursor.execute(sql)
        mydb.commit()

        sql = ("delete from  flowstepinfo where  fid=" + id) 
        mycursor.execute(sql)
        mydb.commit()

        sql = ("delete from  stepdetail where  fid=" + id) 
        mycursor.execute(sql)
        mydb.commit()
 

        analyse  = json.loads(str)
        for item in analyse:
            print ( item['type'] )
            print ( item['id'] )
            if item['type'] == 'NStart' or item['type'] == 'NBetween' or item['type'] == 'NEnd' :
                print ( item['labels'][0]['text'] )
                sql = "INSERT INTO flowstepinfo ( fid, stepid, stepname, rid, created_at) VALUES (%s,%s,%s,%s,now() )"
                val = (int(id), item['id'], item['labels'][0]['text'], int(0))
                mycursor.execute(sql, val)
                mydb.commit()
            if item['type'] == 'draw2d.Connection':
                print(item['source']['node'], item['target']['node'])
                sql = "Select sid from flowstepinfo where stepid= '"+item['source']['node']+"'"
                mycursor.execute(sql)
                for x in mycursor:
                    source_id = x[0]
                sql = "Select sid from flowstepinfo where stepid= '"+ item['target']['node'] +"'"
                mycursor.execute(sql)
                for x in mycursor:
                    target_id = x[0]

                sql = "INSERT INTO stepdetail (fid, sid1, stepid1, sid2, stepid2, created_at ) VALUES (%s,%s,%s,%s,%s,now())"
                val = ( int(id), int(source_id), item['source']['node'], int(target_id), item['target']['node'] )

                mycursor.execute(sql, val)
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
@app.route('/publish/flow/<id>',methods=['GET', 'POST'])
def publish_flow(id=None):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
    )
      
    str = "OK"
    
    try:

        mycursor = mydb.cursor()

        sql = ("update flowinfo set used = 1 where fid=" + id) 
        mycursor.execute(sql)
        mydb.commit()

 

    except mysql.connector.Error as error:
        print("Failed to update into MySQL table {}".format(error))
        str ="Error"
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")

    return str
@app.route('/view/flowstep/<id>/<stepid>')
def view_flowstep(id=None, stepid=None):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
    )
    try:
        mycursor = mydb.cursor()
        sql = "SELECT  sid,fid,stepname,rid,created_at FROM flowstepinfo where fid = "+id+" and stepid = '"+stepid+"' "
        mycursor.execute(sql)

        for x in mycursor:
            payload = { 'sid' : x[0],  'fid':x[1] , 'stepname':x[2],'rid':x[3] }
    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        str ="Error"
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")
    return jsonify(payload)


@app.route('/update/flowstep/<id>/<stepid>',methods=['GET', 'POST'])
def update_flowstep(id=None, stepid=None):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
    )
    myJSON = request.get_json(silent=True)
    str = json.dumps(myJSON)
    role = myJSON['rid']


    try:
        mycursor = mydb.cursor()
        sql = "update flowstepinfo SET rid = " + role + " where fid = "+id+" and stepid = '"+stepid+"' "
        print (sql)
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

@app.route('/list/roles')
def list_role():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
    )
    try:
        mycursor = mydb.cursor()
        sql = "SELECT  rid,rolename FROM roleinfo "
        mycursor.execute(sql)
        payload = []
        content = {}

        for x in mycursor:
            content = { 'rid' : x[0],  'rolename':x[1]  }
            payload.append(content)
            print (content)
            content = {}
    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))
        str ="Error"
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")

    return jsonify(payload)


@app.route('/design/list',methods=['GET', 'POST'])
def design_list():

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow"
        
    )
    name="design"
    myJSON = request.get_json(silent=True)
    key = myJSON['key']  
    try:
 
        mycursor = mydb.cursor()
          
        roleid = 0
        result = { "key" : key , "result": "no"} 
        mycursor.execute("select r.rid from roleuserinfo r, userinfo u where  r.uid = u.uid and u.akey ='"+ key +"' ")
        for x in mycursor :
            roleid =   x[0]
        print (roleid)
        mycursor.execute("SELECT rfnid FROM rolefunction  where fname = '"+name+"' and rid="+ str(roleid) )
        mycursor.fetchall()
        rc = mycursor.rowcount

        print (rc)

        json_data=[]
        if rc == 1 :
            mycursor.execute("SELECT fid,flowname FROM flowinfo  where used = 0" )
            row_headers=[x[0] for x in mycursor.description] #this will extract row headers
            rv = mycursor.fetchall()
            print  ( "flowinfo count ", mycursor.rowcount)
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
        mydb.commit();
        mycursor.close()
    except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")
 
    return json.dumps(json_data)

@app.route('/newjob/list',methods=['GET', 'POST'])
def newjob_list():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow" 
    )
    name="newjob"
    myJSON = request.get_json(silent=True)
    key = myJSON['key']  
    try:
 
        mycursor = mydb.cursor()
          
        roleid = 0
        result = { "key" : key , "result": "no"} 
        mycursor.execute("select r.rid from roleuserinfo r, userinfo u where  r.uid = u.uid and u.akey ='"+ key +"' ")
        for x in mycursor :
            roleid =   x[0]
     
        mycursor.execute("SELECT rfnid FROM rolefunction  where fname = '"+name+"' and rid="+ str(roleid) )
        mycursor.fetchall()
        rc = mycursor.rowcount

   

        json_data=[]
        if rc == 1 :
            mycursor.execute("SELECT fid,flowname FROM flowinfo  where used = 1" )
            row_headers=[x[0] for x in mycursor.description] #this will extract row headers
            rv = mycursor.fetchall()
            print  ( "flowinfo count ", mycursor.rowcount)
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
        mydb.commit()
        mycursor.close()
    except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")
 
    return json.dumps(json_data)
@app.route('/newjob/create',methods=['GET', 'POST'])
def newjob_create():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="theblur8",
        database="workflow" 
    )
    print ( "newjob create")
    name="newjob"
    myJSON = request.get_json(silent=True)
    print (myJSON)
    key = myJSON['key']  
    jobname = myJSON['jobname']  
    fid = myJSON['fid']  

    print ( key, jobname, fid )

    json_data = myJSON
    try:
 
        mycursor = mydb.cursor()
          
        roleid = 0
        json_data = { "key" : key , "result": "no"} 
        mycursor.execute("select r.rid from roleuserinfo r, userinfo u where  r.uid = u.uid and u.akey ='"+ key +"' ")
        for x in mycursor :
            roleid =   x[0]
   
        print ( "select r.rid from roleuserinfo r, userinfo u where  r.uid = u.uid and u.akey ='"+ key +"'" )

        mycursor.execute("SELECT rfnid FROM rolefunction  where fname = '"+name+"' and rid="+ str(roleid) + " ")
        mycursor.fetchall()
        rc = mycursor.rowcount
 
         
        if rc == 1 :
            in_sql = ""
            mycursor.execute("select sid2 from stepdetail where fid = " + str(fid))
            for x in mycursor :
                in_sql +=  str(x[0]) + ","
            str1 =  in_sql[:-1]
            print(str1);
            mycursor.execute("select sid1 from stepdetail where not sid1 in ( " + str1 + ") ");
            currentstep = 0
            for x in mycursor :
                currentstep = x[0]
            mycursor.execute("INSERT INTO  jobinfo  (jobname, fid,currentstep, created_at ) VALUES ('"+jobname+"', "+str(fid)+", "+ str(currentstep)+" , now() )") 
            json_data = {
                "key" :  key, "result": "yes"}  


        mydb.commit();
        mycursor.close()
    except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")
 
    return json.dumps(json_data)


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8000')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  response.headers.add('Access-Control-Allow-Credentials', 'true')
  return response