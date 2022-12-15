import os
import re
from flask import Flask, jsonify, redirect
from werkzeug.routing import Rule
from app.common.error import InvalidUsage
from app.models.dynamodb import ShortenUrl
#from app.common.decimal_encoder import DecimalEncoder

app = Flask(
    __name__,
    template_folder='../config')
app.url_map.strict_slashes = False
#app.json_encoder = DecimalEncoder

jinja_options = app.jinja_options.copy()
jinja_options.update({
    'block_start_string': '[%',
    'block_end_string': '%]',
    'variable_start_string': '[[',
    'variable_end_string': ']]',
    'comment_start_string': '[#',
    'comment_end_string': '#]'
})
app.jinja_options = jinja_options

# get prefix from environment variable
APP_ROOT = os.getenv('APP_ROOT')
if not APP_ROOT is None:
    # define custom_rule class
    class Custom_Rule(Rule):
        def __init__(self, string, *args, **kwargs):
            # check endswith '/'
            if APP_ROOT.endswith('/'):
                prefix_without_end_slash = APP_ROOT.rstrip('/')
            else:
                prefix_without_end_slash = APP_ROOT
            # check startswith '/'
            if APP_ROOT.startswith('/'):
                prefix = prefix_without_end_slash
            else:
                prefix = '/' + prefix_without_end_slash
            super().__init__(prefix + string, *args, **kwargs)

    # set url_rule_class
    app.url_rule_class = Custom_Rule


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/<string:url_id>', methods=['GET'])
def main(url_id):
    if not re.match(r'^[0-9a-zA-Z]{10}$', url_id):
        raise InvalidUsage('url_id is invalid', 400)

    shorten_url = ShortenUrl.get_one_by_pkey('urlId', url_id)
    if not shorten_url:
        raise InvalidUsage('Not Found', 404)

    return redirect(shorten_url['locationTo'])
    #return 'location to: ' + shorten_url['url']
