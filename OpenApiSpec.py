api_spec = {
    'openapi': '3.0.2',
    "info": {
        'title': 'Swagger GET-USER-LOGS',
        'description': 'This is a api spec of the GET-USER-LOGS endpoint.',
        'termsOfService': '/tos',
        'contact': {
            'email': 'asafshuster99@gmail.com'},
        'license': {
            'name': 'Apache 2.0',
            'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'},
        'version': '1.0.0'},
    'servers': [
        {'url': 'http://127.0.0.1:5000/'},
        {'url': 'https://127.0.0.1:5000/'}],
    'tags': {
        'name': 'log',
        'description': 'Everything about getting a user logs.'},
    'paths': {
        '/show-logs/': {
            'get': {
                'tags': [
                    'log'],
                'summary': 'Return logs by user id and timestamp.',
                'description': 'Return logs  of specific user by the timestamp they absorbed.\n Control'
                               'the amount of logs retrieve, determine the center of the returns logs by timestamp'
                               'and scroll between them from request to request.',
                'operationId': 'findLogsByTimestamp',
                'parameters': [{
                    'name': 'anchor_timestamp',
                    'in': 'query',
                    'description': 'A timestamp in a format of %Y-%m-%d %H:%M:%S.%f',
                    'required': 'true',
                    'schema': {
                        'type': 'string'}},
                    {'name': 'user_id',
                     'in': 'query',
                     'description': 'A user_id of specific user from the log dataset',
                     'required': 'true',
                     'schema': {
                         'type': 'string'}},
                    {'name': 'log_appearance_limit',
                     'in': 'query',
                     'description': 'An integer that represents and configure how much logs will return '
                                    'equally across the anchor log. log_appearance_limit >= 0'
                                    ' Note - A request with log_appearance_limit which greater '
                                    'then the number of user_logs AND Scrolling = 0 '
                                    'retrieve you all the logs of the user',
                     'required': 'true',
                     'schema': {
                         'minimum': 0,
                         'type': 'integer'}},
                    {'name': 'scrolling',
                     'in': 'query',
                     'description': 'An integer that represent the scrolling operation over the logs list.\n'
                                    'scrolling = 0 return logs that the anchor is at the center.\n'
                                    'scrolling > 0 return anchor log from earlier timestamp.\n'
                                    'scrolling < 0 return anchor log from later timestamp.'
                                    ' Note - You can not scroll to a log whose distance from the end / beginning is '
                                    'less than the number of logs you set to be displayed around the anchor log',
                     'required': 'true',
                     'schema': {
                         'type': 'integer'}}],
                'responses': {
                    200: {
                        'description': 'successful operation',
                        'content': {}},
                    400: {
                        'description': 'BAD REQUEST - One parameter or the combination of to are invalid',
                        'content': {}}}}}},
    'components': {}}

if __name__ == '__main__':
    pass