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


def query_index(index, page, per_page, query, from_price, to_price,
                order_price, order_date):
    if not current_app.elasticsearch:
        return [], 0
    if query:
        if order_date:
            body={'query':{'bool':{'must':{'multi_match':{'query':query,'fields':['*']}},'filter':{'range':{'price':{'gte':from_price,'lte':to_price}}}}},
             'from':(page - 1) * per_page,'size':per_page,'sort':{'published':{'order':order_date}}}
        elif order_price:
            body={'query':{'bool':{'must':{'multi_match':{'query':query,'fields':['*']}},'filter':{'range':{'price':{'gte':from_price,'lte':to_price}}}}},
             'from':(page - 1) * per_page,'size':per_page,'sort':{'price':{'order':order_price}}}
        else:
            body={'query':{'bool':{'must':{'multi_match':{'query':query,'fields':['*']}},'filter':{'range':{'price':{'gte': from_price, 'lte': to_price}}}}},
              'from':(page - 1) * per_page,'size':per_page}
    else:
        if order_date:
            body={'query':{'bool':{'filter':{'range':{'price':{'gte':from_price,'lte':to_price}}}}},'from':(page - 1) * per_page,'size':per_page,
             'sort':[{'published':{'order':order_date}}]}
        elif order_price:
            body={'query':{'bool':{'filter':{'range':{'price':{'gte':from_price,'lte':to_price}}}}},'from':(page - 1) * per_page,'size':per_page,
             'sort':[{'price':{'order':order_price}}]}
        else:
            body={'query':{'bool':{'filter':{'range':{'price':{'gte':from_price,'lte':to_price}}}}},'from':(page - 1) * per_page,'size':per_page}
            
    search = current_app.elasticsearch.search(
        index=index,
        body=body)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
