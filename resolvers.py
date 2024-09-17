def resolve_retrieve_recent_history(_, info, limit=None):
    limit = limit or 10
    db = info.context['db']
    recent_history = list(db.queries.find().sort("_id", -1).limit(limit))
    return recent_history


def resolve_retrieve_query(_, info, name):
    query = {"name": {"$regex": name, "$options": "i"}}

    result = info.context['db'].queries.find_one(query)

    return result


def resolve_save_query(_, info, input):
    # Insert the new data into MongoDB
    insert_result = info.context['db'].queries.insert_one(input)

    # Return the inserted object's ID
    return str(insert_result.inserted_id)
