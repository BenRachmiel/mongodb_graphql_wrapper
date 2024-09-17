from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync, load_schema_from_path
from ariadne.explorer import ExplorerPlayground

# Import custom scalars
from scalars import (
    latitude_scalar,
    longitude_scalar,
    angle_scalar,
    nonnegative_float_scalar,
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
host_ip = "localhost"
host_port = 27017
database_name = "test"
app.config["MONGO_URI"] = f"mongodb://{host_ip}:{host_port}/{database_name}"
mongo = PyMongo(app)
db = mongo.db

# Make the executable schema using the loaded schema file
loaded_schema_path = load_schema_from_path("schema.graphql")
query = QueryType()
mutation = MutationType()
query.set_field("retrieveRecentHistory", resolve_retrieve_recent_history)
query.set_field("retrieveQuery", resolve_retrieve_query)
mutation.set_field("saveQuery", resolve_save_query)
loaded_schema = load_schema_from_path("schema.graphql")
schema = make_executable_schema(
    loaded_schema,
    [query, mutation],
    latitude_scalar,
    longitude_scalar,
    angle_scalar,
    nonnegative_float_scalar,
    priority_scalar,
    quality_scalar
)


# GraphQL Playground route for testing the API
@app.route("/")
def graphql_playground():
    return ExplorerPlayground().html("abc"), 200


# GraphQL route for POST requests
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    context = {"db": db, "request": request}
    success, result = graphql_sync(schema, data, context_value=context, debug=app.debug)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
