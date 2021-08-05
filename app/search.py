from flask import current_app


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(
    index,
    page,
    per_page,
    query,
    filter_by,
    from_num,
    to_num,
    order,
):
    if not current_app.elasticsearch:
        return [], 0

    body = {
        'query': {
            'bool': {
                'filter': {
                    'range': {
                        filter_by: {
                            'gte': from_num,
                            'lte': to_num,
                        }}},
            }},
        'from': (page - 1) * per_page,
        'size': per_page,
        'sort': {order[0]: {
            'order': order[1],
        }},
    }
    if query:
        body['query']['bool']['must'] = {
            'multi_match': {
                'query': query,
                'fields': ['*'],
            }}

    search = current_app.elasticsearch.search(
        index=index,
        body=body,
    )
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
