from datetime import datetime
import uuid
import azure.functions as func
import json
from service_models import User
from function_app_context import context

bpUsers = func.Blueprint()

@bpUsers.route(route="users", methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_service(req: func.HttpRequest) -> func.HttpResponse:
    context.logging.info('User service called')
    if req.method == 'GET' or req.method == 'DELETE':
        try:
            id = req.headers.get('id')
            guid = req.headers.get('guid')
            email = req.headers.get('email')
            name = req.headers.get('name')
            if not guid or not email or not name:
                raise ValueError()
        except ValueError:
            context.logging.error('Invalid User Data')
            return func.HttpResponse("Invalid User Data", status_code=400)
    elif req.method == 'POST' or req.method == 'PUT':
        try:
            user_data = req.get_json()
        except ValueError:
            return func.HttpResponse("Invalid User Data", status_code=400)
        else:
            id = user_data.get('id')        
            name = user_data.get('name')
            email = user_data.get('email')
            sms = user_data.get('sms')
            avatarPath = user_data.get('avatarPath')
            householdid = user_data.get('householdid')
        context.logging.info('user_data : %s', user_data)
        if not id and not name and not email:
            return func.HttpResponse("Invalid User Data", status_code=400)

    if req.method == 'GET' :
        return get_add_user(guid, email, name)
    elif req.method == 'DELETE':
        return delete_user(id)
    # elif req.method == 'POST':
        # return add_user(name)  # not implemented. use Get with guid to add new user
    elif req.method == 'PUT':
        return update_user(id, name, email, avatarPath, sms, householdid)
    else:
        return func.HttpResponse("Method Not Allowed", status_code=405)

def get_add_user(guid: str, email: str, name: str) -> func.HttpResponse:
    context.logging.info('getting user : %s', guid)
    if guid == context.KEY:
        context.logging.info('getting ALL users')
        users = context.session.query(User).all()
        return func.HttpResponse(json.dumps([user.to_dict() for user in users], default=str), mimetype="application/json")
    else:
        user = context.session.query(User).filter(User.guid == guid).first()
        if not user:
            context.logging.info('creating new user : %s', guid)
            user = User(guid=guid, email=email, name=name.split(' ')[0])
            context.session.add(user)
            context.session.commit()
            # logging.info('user created [%s] : %s', user.id, json.dumps(user.to_dict(), default=str))
            return func.HttpResponse(json.dumps(user.to_dict(), default=str), mimetype="application/json")
        else:
            output = json.dumps(user.to_dict(), default=str)
            context.logging.info('user found : %s', output)
            user.lastLogon = datetime.now()
            context.session.commit()
            return func.HttpResponse(output, mimetype="application/json")

def delete_user(id: str) -> func.HttpResponse:
    context.logging.info('deleting user : %s', id)
    user = context.session.query(User).filter(User.id == id).first()
    if not user:
        return func.HttpResponse("User Not Found", status_code=404)
    else:
        context.session.delete(user)
        context.session.commit()
        context.logging.info('user deleted : %s', json.dumps(user.to_dict(), default=str))
        return func.HttpResponse(json.dumps(user.to_dict(), default=str), mimetype="application/json")

def update_user(id: str, name: str, email: str, avatarPath: str, sms : str, houseid: str) -> func.HttpResponse:
    context.logging.info('updating user data : %s', id)
    if not id or not name or not email:
        return func.HttpResponse("Invalid User Data", status_code=400)
    try:
        if houseid:
            hid = uuid.UUID(houseid)
            if not id:
                raise ValueError()
    except ValueError:
        return func.HttpResponse("Invalid House ID", status_code=400)

    user = context.session.query(User).filter(User.id == id).first()
    if not user:
        return func.HttpResponse("User Not Found", status_code=404)
    else:
        user.name = name
        user.email = email
        user.sms = sms if sms else None
        user.avatarPath = avatarPath if avatarPath else None
        user.householdid = houseid if houseid else None
        context.session.commit()
        context.logging.info('user found : %s', json.dumps(user.to_dict(), default=str))
        return func.HttpResponse(json.dumps(user.to_dict(), default=str), mimetype="application/json")
