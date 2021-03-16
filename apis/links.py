# -*- coding: utf-8 -*-
import traceback

from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response, json_serializer

api = Namespace('links', description='Links related operations')


def create_link(user_id, url, description, image_url):
    try:
        db.insert_link(user_id, url, description, image_url)
        return True
    except:
        traceback.print_exc()
        return False


def delete_links(ids):
    try:
        db.delete_links(ids)
        return True
    except:
        traceback.print_exc()
        return False


# https://flask-restplus.readthedocs.io/en/stable/parsing.html
parser_create = reqparse.RequestParser()
parser_create.add_argument('url', type=str, required=True, location='form', help='url')
parser_create.add_argument('description', type=str, required=True, location='form')
parser_create.add_argument('image_url', type=str, location='form')

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('ids', type=str, required=True, action='split')


@api.route('/')
class Links(CustomResource):
    @api.doc('get all links')
    def get(self):
        links = db.get_links()        
        res = response(status=1, result=links)
        return self.send(res)
    
    @api.doc('create a new link')
    @api.expect(parser_create)
    def post(self):
        args = parser_create.parse_args()
        url = args["url"]
        description = args["description"]        
        image_url = args.get("image_url")
        
        result = create_link(1, url, description, image_url)
        status = 1 if result else 0

        res = response(status=status)
        return self.send(res)

    @api.doc('delete links')
    @api.expect(parser_delete)
    def delete(self):
        args = parser_delete.parse_args()
        delete_links(args["ids"])
        res = response(status=1)
        return self.send(res)


@api.route('/<id_>')
@api.param('id_', 'The link identifier')
@api.response(404, 'Link not found')
class Task(CustomResource):
    @api.doc('get_link')
    def get(self, id_):
        '''Fetch an link given its identifier'''
        try:
            link = db.get_links(id_=id_)
            res = response(status=1, result=link)
        except:
            res = response(status=0)
        return self.send(res)
    
    @api.doc('delete a link')
    def delete(self, id_):
        '''delete a link given its identifier'''
        try:
            delete_links([id_])
            res = response(status=1)
        except:
            res = response(status=0)
        
        return self.send(res)