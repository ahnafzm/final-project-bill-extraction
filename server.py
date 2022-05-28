from flask import Flask, Response, request, render_template
import pymongo
import json
from bson.objectid import ObjectId
import ocr
from PIL import Image


app=Flask(__name__)
#######################################
try:
    mongo = pymongo.MongoClient(
        host= "localhost",
        port = 27017,
        serverSelectionTimeoutMS =1000
    )
    db = mongo.final
    mongo.server_info()
except: 
    print("ERROR - Cannot connect to mongodb")
#######################################
@app.route('/')
def home():
   return render_template('temp.html')

@app.route('/users', methods=['POST'])
def create_user():
    try:
        csvfile = request.files["file"]
        img = Image.open(csvfile)
        img = img.save("data/images/zzzz.jpg") 
        konek = ocr.connect()
        semua = ocr.diskon1(konek)
        user = {
            "disc" : semua[0],
            "hargadisc" : semua[1],
            "harga" : semua[2],
            "produk" : semua[3]
        }
        dbResponse = db.users.insert_one(user)
        # print(dbResponse.inserted_id)

        return Response(
            response= json.dumps(
                {
                    "massage": "user created",
                    "id": f"{dbResponse.inserted_id}"
                }
            ), status = 200,
            mimetype = "application/json"
        )

    except:
        return Response(
            response= json.dumps(
                {
                    "massage": "user cant created"
                }
            ), status = 500,
            mimetype = "application/json")
#######################################
@app.route('/users', methods=["GET"])
def read_user():
    try:
        data = list(db.users.find())
        for user in data:
            user["_id"] = str(user['_id'])
        return Response(
            response= json.dumps(data),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        print(e)
        return Response(
            response= json.dumps(
                {"massage": "cannot read users"})
                , status = 500,
                mimetype = "application/json"
        )


#######################################
@app.route("/users/<id>", methods=["PUT"])
def update_user(id):
    try:
        csvfile = request.files["file"]
        img = Image.open(csvfile)
        img = img.save("data/images/zzzz.jpg") 
        konek = ocr.connect()
        semua = ocr.diskon1(konek)
        
        dbRespose = db.users.update_one(
            {"_id":ObjectId(id)},
            {'$push':{"disc" : {'$each' : semua[0]}}})
        dbRespose = db.users.update_one(
            {"_id":ObjectId(id)},
            {'$push':{"hargadisc" : {'$each' : semua[1]}}})
        dbRespose = db.users.update_one(
            {"_id":ObjectId(id)},
            {'$push':{"harga" : {'$each' : semua[2]}}})
        dbRespose = db.users.update_one(
            {"_id":ObjectId(id)},
            {'$push':{"produk" : {'$each' : semua[3]}}})

        return Response(
            response= json.dumps({"massage": "user updated"}),
            status = 200,
            mimetype = "application/json")

    except Exception as e:
        print(e)
        return Response(
            response= json.dumps(
                {"massage": "cannot update users"})
                , status = 500,
                mimetype = "application/json"
        )
#######################################

@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        dbResponse = db.users.delete_one({"_id":ObjectId(id)})
        if dbResponse.deleted_count == 1:
            return Response(
                response= json.dumps({"massage": "user deleted", "id" : f"{id}"}),
                status = 200,
                mimetype = "application/json")
        
        return Response(
                response= json.dumps({"massage": "user not found", "id" : f"{id}"}),
                status = 200,
                mimetype = "application/json")

    except Exception as e:
        print(e)
        return Response(
            response= json.dumps(
                {"massage": "cannot update users"})
                , status = 500,
                mimetype = "application/json"
        )
#######################################

if __name__ == "__main__":
    app.run(port=80, debug=True)