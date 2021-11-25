DB_HOST = "127.0.0.1"
DB_NAME = "userinfo"
DB_USER = "admin1"
DB_PASS = "a11b23@1#$4567"

import psycopg2
import psycopg2.extras
import uuid
import datetime
import secrets
psycopg2.extras.register_uuid()

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def addUser(f_name, l_name, dob, cob, ballots):
    birth_date = datetime.date(dob[0], dob[1], dob[2])
    voter_uuid = uuid.uuid4()
    cur.execute("INSERT INTO voterinfo (voter_id, first_name, last_name, date_of_birth, country_of_birth) VALUES(%s, %s, %s, %s, %s)", (voter_uuid, f_name, l_name, birth_date, cob))
    conn.commit()
    for ballot in ballots:
        cur.execute("INSERT INTO voterballot (voter_id, ballot_id) VALUES(%s, %s)", (voter_uuid, ballot))
        conn.commit()
    return voter_uuid

def getBallots(voter_id):
    ballots = []
    cur.execute("SELECT * FROM voterballot WHERE voter_id = %s;", [voter_id])
    b_list = cur.fetchall()
    for i in b_list:
        ballots.append(i[2])
    return ballots

def generateUserCredentials(voter_id):
    paswd = secrets.token_hex(16)
    cur.execute("INSERT INTO registeredvoter (voter_id, user_password) VALUES(%s, %s)", (voter_id, paswd)) 
    conn.commit()
    return paswd

def updateOnlineBallotRegulator(voter_id):
    ballots = getBallots(voter_id)
    for i in ballots:
         cur.execute("INSERT INTO registeredvoterballots (voter_id, ballot_id) VALUES(%s, %s)", (voter_id, i))
         conn.commit()



n = int(input("Enter number of voter(s) to be registered : "))
for i in range(0, n):
    dob = [0, 0, 0]
    ballots = []
    print("\n")
    f_name = input("Enter first name : ")
    l_name = input("Enter last name : ")
    dob[0] = int(input("Enter birth year : "))
    dob[1] = int(input("Enter birth month : "))
    dob[2] = int(input("Enter birth day : "))
    cob = input("Enter country of birth : ")
    bn = int(input("Enter number of ballots to register user to : "))
    for i in range(0, bn):
        x = int(input())
        ballots.append(x)
    user_id = addUser(f_name, l_name, dob, cob, ballots)
    updateOnlineBallotRegulator(user_id)
    passwd = generateUserCredentials(user_id)
    print("\n")
    print(f"Hello {f_name} {l_name}, your user_id is {user_id} and password is {passwd}")
    print("\n")
cur.close()









#cur.execute("CREATE TABLE voterinfo (voter_id UUID, first_name VARCHAR NOT NULL, last_name VARCHAR NOT NULL, date_of_birth DATE NOT NULL, country_of_birth VARCHAR NOT NULL, PRIMARY KEY (voter_id));")
#cur.execute("CREATE TABLE voterballot (serial_no SERIAL, voter_id UUID NOT NULL, ballot_id INT NOT NULL, PRIMARY KEY (serial_no));")
#cur.execute("INSERT INTO voterinfo (voter_id, first_name, last_name, date_of_birth, country_of_birth) VALUES(%s, %s, %s, %s, %s)", (uuid.uuid4(), "asd", "bgf", datetime.date(2000, 9, 9), "india"))
#cur.execute("SELECT * FROM voterballot;")
#print(cur.fetchall())
# cur.close()
#addUser("Mary", "Kom", (2012, 11, 11), "india", (1123, 5671, 3213, 4721))
#cur.execute("CREATE TABLE registeredvoter(voter_id UUID, user_password VARCHAR NOT NULL, PRIMARY KEY (voter_id));")
#cur.execute("CREATE TABLE registeredvoterballots(serial_no SERIAL, voter_id UUID NOT NULL, ballot_id INT NOT NULL, PRIMARY KEY (serial_no));")
#conn.commit()
conn.close()