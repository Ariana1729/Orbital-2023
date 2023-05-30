import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["vuln"]
users = db["users"]
notes = db["notes"]

# users.drop()
# notes.drop()

users.insert_one({"name":"admin", "password":"3x7R3m3ly53CUR34|)|\/|1|\|"})
notes.insert_one({"id":1, "author":"admin", "public": True, "desc": "First!"})
notes.insert_one({"id":2, "author":"admin", "public": False, "desc": "Password: 3x7R3m3ly53CUR34|)|\/|1|\| (in case i forget)"})
