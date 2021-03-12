from flask_restplus import Namespace, Resource, fields

api = Namespace('sessions', description='Sessions related operations')

sessions = [
    {
        "id": 1,
        "name": 'water'
    },
    {
        "id": 2,
        "name": 'coke'
    }
]

def delete_session(key):
    # get from db
    pass

def create_session(user_id):
    pass

@api.route('/')
class Sessions(Resource):
    @api.doc('list_sessions')
    def get(self):
        '''List all sessions'''
        return sessions

@api.route('/<id>')
@api.param('id', 'The session identifier')
@api.response(404, 'Session not found')
class Session(Resource):
    @api.doc('get_sessions')
    def get(self, id):
        '''Fetch a session given its identifier'''
        for session in sessions:
            if sessions['id'] == id:
                return sessions
        api.abort(404)
    
    @api.doc('get_sessions')
    def post(self, id):
        '''Fetch a session given its identifier'''
        for session in sessions:
            if sessions['id'] == id:
                return sessions
        api.abort(404)

    @api.doc('get_sessions')
    def delete(self, id):
        '''Fetch a session given its identifier'''
        for session in sessions:
            if sessions['id'] == id:
                return sessions
        api.abort(404)