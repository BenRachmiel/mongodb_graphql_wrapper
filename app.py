from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync, load_schema_from_path
from ariadne.explorer import ExplorerPlayground
from bson.objectid import ObjectId

# Import custom scalars
from scalars import (
    latitude_scalar,
    longitude_scalar,
    angle_scalar,
    positive_float_scalar,
    priority_scalar,
    quality_scalar
)

# Import resolvers
from resolvers import (
    resolve_retrieve_recent_history,
    resolve_retrieve_query,
    resolve_save_query
)

app = Flask(__name__)

# Configure MongoDB connection using Flask-PyMongo
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
mongo = PyMongo(app)
db = mongo.db

# Initialize QueryType and MutationType
query = QueryType()
mutation = MutationType()

# GraphQL resolvers for queries


@query.field("getUser")
def resolve_get_user(_, info, id):
    user = db.users.find_one({"_id": ObjectId(id)})
    if user:
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
    return None


@query.field("getUsers")
def resolve_get_users(_, info):
    users = db.users.find()
    return [
        {"id": str(user["_id"]), "name": user["name"], "email": user["email"]}
        for user in users
    ]


# GraphQL resolvers for mutations
@mutation.field("createUser")
def resolve_create_user(_, info, name, email):
    new_user = {
        "name": name,
        "email": email
    }
    result = db.users.insert_one(new_user)
    return {
        "id": str(result.inserted_id),
        "name": name,
        "email": email
    }


@mutation.field("updateUser")
def resolve_update_user(_, info, id, name=None, email=None):
    updates = {}
    if name:
        updates["name"] = name
    if email:
        updates["email"] = email

    result = db.users.update_one({"_id": ObjectId(id)}, {"$set": updates})
    if result.matched_count:
        user = db.users.find_one({"_id": ObjectId(id)})
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
    return None

@mutation.field("deleteUser")
def resolve_delete_user(_, info, id):
    result = db.users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return "User deleted successfully"
    return "User not found"


# Make the executable schema using the loaded schema file
schema = make_executable_schema(load_schema_from_path("mongoschema.txt"), query, mutation)


# GraphQL Playground route for testing the API
@app.route("/")
def graphql_playground():
    return ExplorerPlayground().html("abc"), 200


# GraphQL route for POST requests
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
