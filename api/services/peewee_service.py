def query_from_dict(Model, data):
    query = list()
    for key, item in data.iteritems():
        query.append(eval('(Model.' + key + ' == data[\'' + key + '\'])'))
    return query
