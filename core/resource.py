import json

from flask import Response
from flask_restplus import Resource


class CustomResource(Resource):
    def __init__(self,api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    def send(self,*args, **kwargs):
        headers = {}
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Headers'] = '*'
        headers['Access-Control-Allow-Credentials'] = True

        response_body = {'result' : None , 'message' : None}

        for arg in args:
            if arg is not None:
                for key in arg.keys():
                    response_body[key] = arg[key]

        for param_key in kwargs.keys():
            response_body[param_key] =  kwargs[param_key]
        
        json_encode = json.JSONEncoder().encode
        return Response(json_encode(response_body), headers=headers, mimetype="application/json")


def response(**kwargs):
    params = ['status', 'message', 'result']
    for param in params:
        if param not in kwargs.keys():
            kwargs[param] = None

    return kwargs


from datetime import date, datetime

def json_serializer(obj, ignore_type_error=False):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if not ignore_type_error:
        raise TypeError ("Type %s not serializable" % type(obj))

def json_serializer_all_datetime_keys(data):

    for key, value in data.items():
        data[key] = json_serializer(value, ignore_type_error=True)

    return data