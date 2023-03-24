import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from marshmallow import Schema, fields, ValidationError, pre_load

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/events.db"
db = SQLAlchemy(app)

### MODELS ###

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.String(200))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    date = db.Column(db.Date)
    url = db.Column(db.String)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", backref=db.backref("events", lazy="dynamic"))

### SCHEMAS ###

class GroupSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()

def must_not_be_blank(data):
    if not data:
        return ValidationError("Data not provided")
    
class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)
    description = fields.Str(required=True, validate=must_not_be_blank)
    date = fields.Date(required=True, validate=must_not_be_blank)
    url = fields.Str(required=True, validate=must_not_be_blank)
    group = fields.Nested(GroupSchema, validate=must_not_be_blank)
    
    @pre_load
    def get_group(self, data, **kwargs):
        gruop_id = data['group']
        group = Group.query.filter(Group.id == gruop_id).one()
        group_dict = dict(id=group.id, name=group.name,description=group.description)
        data['group'] = group_dict
        return data
    
group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)
event_schema = EventSchema()
events_schema = EventSchema(many=True)


### API ###

@app.route("/groups")
def get_groups():
    groups = Group.query.all()
    result = groups_schema.dump(groups)
    return {"groups" : result }

@app.route("/group/<int:pk>")
def get_group(pk):
    try:
        group = Group.query.filter(Group.id == pk).one()
    except NoResultFound:
        return {"message": "Group could not be found."}, 400
    
    group_result = group_schema.dump(group)
    events_result = events_schema.dump(group.events.all())

    return {"group" : group_result, "events" : events_result}

@app.route("/group", methods=['POST'])
def new_group():
    data = request.get_json()
    name = data['name']
    description = data['description']
    group = Group(name=name, description=description)
    db.session.add(group)
    db.session.commit()

    return {"message" : "New Group Created", "Group Id": group.id}

@app.route("/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    result = events_schema.dump(events, many=True)
    return {"events" : result}

@app.route("/event/<int:pk>", methods=['GET'])
def get_event(pk):
    try:
        event = Event.query.filter(Event.id == pk).one()
    except NoResultFound:
        return {"message" : "Event could not be fount"}, 400
    
    result = event_schema.dump(event)

    return {"event" : result}

@app.route("/event",methods=['POST'])
def new_event():
    json_data = request.get_json()

    if not json_data:
        return {"message" : "No input data provided"}, 400
    
    try:
        data = event_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422
    
    event = Event(
        name = data['name'], 
        description = data['description'],
        date = data['date'],
        url = data['url'],
        group_id = data['group']['id']
    )

    db.session.add(event)
    db.session.commit()
    result = event_schema.dump(Event.query.get(event.id))

    return {"message" : "New Evente created" , "event" : result}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
