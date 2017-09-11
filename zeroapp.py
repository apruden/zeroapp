from flask import Flask, render_template, session, request, send_from_directory, jsonify, url_for, redirect, Response
import json, flask.json, datetime
import itertools
import pprint as pp

from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import and_, or_
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_continuum import make_versioned
from sqlalchemy.schema import Index, UniqueConstraint
from alchemyjsonschema import SchemaFactory
from alchemyjsonschema import ForeignKeyWalker

from fiql_parser import parse_str_to_expression


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj._json()

        return json.JSONEncoder.default(self, obj)


class JsonMixin:
    def _json(self):
        obj = self
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
            data = obj.__getattribute__(field)
            try:
                json.dumps(data) # this will fail on non-encodable values, like other classes
                fields[field] = data
            except TypeError:
                #if isinstance(data, WKBElement):
                #    fields[field] = 'SRID=4326;%s' % (to_shape(data).wkt,)
                if isinstance(data, datetime.date):
                    fields[field] = data.strftime('%Y-%m-%d')
                else:
                    fields[field] = None
        return fields


def dumps(obj):
    return flask.json.dumps(obj, cls=AlchemyEncoder)


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='@@',
        variable_end_string='@@'
        ))


app = CustomFlask(__name__, static_url_path='/', template_folder='src/webapp/dist')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://chatr:Admin123@localhost/chatr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class CustomColumn(db.Column):

    def __init__(self, *args, pattern=None,  **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern = pattern

    def copy(self, **kwargs):
        c = super().copy(**kwargs)
        c.pattern = self.pattern
        return c


class Authentication:
    def validate(self):
        pass


class User(db.Model, JsonMixin, Authentication):
    id = CustomColumn(db.Integer, primary_key=True)
    email = CustomColumn(db.String(255), unique=True)
    password = CustomColumn(db.String(255))
    confirmed_at = CustomColumn(db.DateTime())

    __table_args__ = (Index('ix_user_email', 'email'),)


class Profile(db.Model, JsonMixin, Authentication):
    id = CustomColumn(db.Integer, primary_key=True)
    username = CustomColumn(db.String(255))
    gender = CustomColumn(db.Integer)
    dob = CustomColumn(db.Date)
    headline = CustomColumn(db.Text)
    about = CustomColumn(db.Text)
    city = CustomColumn(db.String(255))
    latestSeen = CustomColumn(db.DateTime)

    __table_args__ = (Index('ix_profile_search', 'gender', 'dob', 'latestSeen'),)

    def validate(self):
        pass


class Message(db.Model, JsonMixin, Authentication):
    id = CustomColumn(db.Integer, primary_key=True)
    sent = CustomColumn(db.DateTime)
    to = CustomColumn(db.Integer)
    fro = CustomColumn(db.Integer)
    read = CustomColumn(db.DateTime)



_ops = {
        'OR': or_,
        'AND': and_
        }

_comp = {
        '==': '__eq__' ,
        '<': '__lt__',
        '>=': '__ge__',
        '<=': '__le__',
        '>': '__gt__',
        '!=': '__ne__'
        }


_entities = { 'User': User, 'Profile': Profile, 'Message': Message }


def parse_query(e, q):
    expression = parse_str_to_expression(q)
    return build_criteria(e, expression.to_python())


def build_criteria(e, exp):
    if isinstance(exp, list):
        op, *rest = exp
        return _ops[op](*[build_criteria(e, r) for r in rest])
    elif isinstance(exp, tuple):
        l, comp, r = exp
        return getattr(getattr(e, l), _comp[comp])(r)
    else:
        raise Exception('invalid expression')


@app.route('/api/<entity>/_schema', methods=['GET'])
def get_schema(entity):
    factory = SchemaFactory(ForeignKeyWalker)
    return dumps(factory(_entities[entity]))


@app.route('/api/<entity>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def do_entities(entity):
    '''
    GET /api/user?q=name==foo*,(age=lt=55;age=gt=5)&include=name,test,toto&exclude=name&load=messages&offset=0&limit=0&sort_by=name&sort_dir=asc

    POST /api/user

    PUT /api/user?ids=1,2,3

    DELETE /api/user?ids=1,2,3
    '''
    e = _entities[entity]

    if request.method == 'GET':
        criteria = parse_query(e, request.args['q'])
        query = e.query.filter(criteria)
        count = query.count()

        if 'load' in request.args:
            query = query.options(joinedload(getattr(e, request.args['load'])))

        query = query.order_by(
                        getattr(
                            getattr(e, request.args['sort_by']),
                            request.args.get('sort_dir', 'asc')
                            )() if 'sort_by' in request.args else None)\
                .offset(request.args.get('offset', 0))\
                .limit(request.args.get('limit', 20))

        res = Response(dumps(query.all()), mimetype='application/json')
        res.headers['X-Total-Count'] = count

        return res
    elif request.method == 'POST': # POST
        obj = e(**request.json)
        db.session.add(obj)
        db.session.commit()

        return dumps(obj)
    elif request.method == 'PUT':
        updates = {getattr(e, k): v for k, v in request.json.items()}
        e.query.filter(getattr(e, 'id').in_(request.args['ids'])).update(updates)
        db.session.commit()

        return 'OK'
    else: #DELETE
        e.query.filter(getattr(e, 'id').in_(request.args['ids'])).delete()
        db.session.commit()

        return 'OK'


@app.route('/api/<entity>/<id>', methods=['GET', 'PUT', 'DELETE'])
def do_entity(entity, id):
    e = _entities[entity]
    query = e.query
    
    if 'load' in request.args:
        query = query.options(joinedload(getattr(e, request.args['load'])))

    obj = query.get(id)

    if request.method == 'GET':
        return dumps(obj)
    elif request.method == 'PUT':
        for k, v in request.json.items():
            setattr(obj, k, v)

        db.session.commit()    
        return dumps(obj)
    else:
        db.session.delete(obj)
        db.session.commit()
        return 'OK'


make_versioned(plugins=[FlaskPlugin()])


if __name__ == '__main__':
    db.create_all()
    app.run()
