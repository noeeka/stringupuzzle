import pymysql
from flask_cors import *
from flask import request
from flask import Flask, session
from flask_session import Session
import os
app = Flask(__name__)
app.secret_key = 'guess'
CORS(app, supports_credentials=True)

@app.route("/login", methods=['GET','POST'])
def login():
    data = request.get_json()
    session['username'] = data['username']
    return {"state": 0, "ret": "success"}

@app.route('/guess', methods=['GET', 'POST'])
def guess():
    if(session.get('count')!=0):
        pass
    else:
        session['count']=0
    username=session.get('username')
    conn = pymysql.connect(
        host="*",
        user="root", password="root",
        database="chengyu",
        charset="utf8")
    cursor = conn.cursor()
    if request.method == "GET":
        session['count'] = 0
        cursor.execute("SELECT * FROM cy ORDER BY RAND() LIMIT 1")
        raw_idiom = cursor.fetchone()
        return {"state": 0, "ret": {"idom": raw_idiom[1], "explain": raw_idiom[3], "id": raw_idiom[0],
                                    "username": username}}

    else:
        data = request.get_json()
        input_idiom = data['guess']
        original = data['original']
        cursor.execute("SELECT * FROM cy WHERE `id`=" + original)
        raw_idiom = cursor.fetchone()
        cursor.execute("SELECT * FROM cy WHERE `name`='" + input_idiom.strip() + "'")
        guess_idiom = cursor.fetchone()
        if guess_idiom is None:
            return {"state": 1, "ret": "您猜的不对,本次您答对："+str(session.get('count'))+"次"}
        else:
            pinyin = guess_idiom[2].split("  ")
            if pinyin[0] != raw_idiom[2].split("  ")[3]:
                return {"state": 1, "ret": "您猜的不对,本次您答对："+str(session.get('count'))+"次"}

            else:
                session['count']=int(session.get('count'))+1
                return {"state": 0, "ret": {"idom": guess_idiom[1], "explain": guess_idiom[3], "id": guess_idiom[0],'count':session.get('count')}}
    cursor.close()
    conn.close()


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
