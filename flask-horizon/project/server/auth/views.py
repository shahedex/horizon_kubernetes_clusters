from flask import Blueprint, request, make_response, jsonify
import requests
import json
import pprint
from flask.views import MethodView

auth_blueprint = Blueprint('auth', __name__)


class LoginApi(MethodView):
    """
    Login API to port : 5000
    """
    base_url = 'http://cloud.brilliant.com.bd:5000/identity/v3/'
    global tokens
    tokens = {
        'responseStatus': '',
        'unScopedToken': '',
        'scopedToken': '',
        'projectID': ''
    }

    def post(self):
        email = request.json['email']
        password = request.json['password']
        tokenData = self.fetchUnscopedToken(self.base_url, email, password)
        if tokens['responseStatus'] == 'ok':
            LoginApi.fetchOwnProjects(self.base_url, tokenData, tokens['unScopedToken'])
        responseObject = {
            'status': 'success',
            'projectID': tokens['projectID'],
            'unScopedToken': tokens['unScopedToken'],
            'scopedToken': tokens['scopedToken']
        }
        if tokens['responseStatus'] == 'ok':
            return make_response(jsonify(responseObject)), 200
        return make_response(jsonify({'error': 'There has been a problem. Please try again!'}))

    @staticmethod
    def fetchUnscopedToken(url, email, password):
        auth = {
            'auth': {
                'identity': {
                    'methods': ['password'],
                    'password': {
                        'user': {
                            'name': email,
                            'domain': {
                                'name': 'Default'
                            },
                            'password': password
                        },

                    }
                }
            }
        }
        response = requests.post(url+'auth/tokens', data=json.dumps(auth),
            headers={'Content-type': 'application/json'})
        tokens['responseStatus'] = 'ok' if response.status_code == 201 else 'failed'
        if tokens['responseStatus'] != 'ok':
            return
        tokens['unScopedToken'] = response.headers['X-Subject-Token']
        return response.json()

    @staticmethod
    def fetchOwnProjects(url, data, token):
        userID = data['token']['user']['id']
        header = {
            'X-Auth-Token': token
        }
        response = requests.get(url+'users/'+userID+'/projects', headers=header)
        tokens['responseStatus'] = 'ok' if response.status_code == 200 else 'failed'
        responseData = response.json()
        data = responseData['projects'][0]['id']
        LoginApi.fetchScopedToken(url, data, token)

    @staticmethod
    def fetchScopedToken(url, data, token):
        auth = {
            'auth': {
                'identity': {
                    'methods': ['token'],
                    'token': {
                        'id': token
                    }
                },
                'scope': {
                    'project': {
                        'id': data
                    }
                }
            }
        }
        response = requests.post(url+'auth/tokens', data=json.dumps(auth),
            headers={'Content-type': 'application/json'})
        tokens['projectID'] = data
        tokens['scopedToken'] = response.headers['X-Subject-Token']


LoginApi_view = LoginApi.as_view('login_api')
auth_blueprint.add_url_rule(
    '/api/login',
    view_func=LoginApi_view,
    methods=['POST']
    )
