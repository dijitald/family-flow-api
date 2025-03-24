import uuid
import azure.functions as func
import json
from sqlalchemy.orm import joinedload
from function_app_context import context
from service_models import Household, HouseholdMembership, User

bpMembers = func.Blueprint()

@bpMembers.route(route="memberships", methods=['GET', 'POST', 'PUT', 'DELETE'])
def membership_service(req: func.HttpRequest) -> func.HttpResponse:
    context.logging.info('Membership service called [%s]', req.method)
    
    if req.method == 'GET' or req.method == 'DELETE':
        try:
            uid = req.headers.get('uid')
            hid = req.headers.get('hid')
            if hid:
                hid = uuid.UUID(hid)
            if not hid and not uid:
                return func.HttpResponse("Missing Household ID or User ID", status_code=400)
        except ValueError:
            return func.HttpResponse("Invalid House ID", status_code=400)
    elif req.method == 'POST' or req.method == 'PUT':
        try:
            membership_data = req.get_json()
        except ValueError:
            return func.HttpResponse("Invalid Membership Data", status_code=400)
        else:
            householdid = membership_data.get('hid')
            uid = membership_data.get('uid')
            balance = membership_data.get('balance')
            role = membership_data.get('role')
        context.logging.info('user_data : %s', membership_data)
        try:
            hid = uuid.UUID(householdid)
        except ValueError:
            return func.HttpResponse("Invalid House ID", status_code=400)
        
    if req.method == 'GET':
        return get_membership(hid, uid)
    elif req.method == 'DELETE':
        return delete_membership(hid, uid)
    elif req.method == 'POST':
        return create_membership(hid, uid)
    elif req.method == 'PUT':
        return update_membership(hid, uid, balance, role)
    else:
        return func.HttpResponse("Method Not Allowed", status_code=405)
    
def get_membership(hid: str, uid :str) -> func.HttpResponse:
    context.logging.info('get_membership equal [%s][%s] = %s', hid, context.KEY, str(hid) == str(context.KEY))
    if str(hid) == str(context.KEY):  # get all memberships  
        context.logging.info('getting ALL memberships')
        memberships = context.session.query(HouseholdMembership).options(joinedload(HouseholdMembership.household)).all()
        return func.HttpResponse(json.dumps([membership.to_dict() for membership in memberships], default=str), mimetype="application/json")
    elif not hid:           # get all memberships for a user
        context.logging.info('getting USER memberships')
        memberships = context.session.query(HouseholdMembership).filter(HouseholdMembership.userid == uid).options(joinedload(HouseholdMembership.household)).all()
        # if memberships:
        return func.HttpResponse(json.dumps([membership.to_dict() for membership in memberships], default=str), mimetype="application/json")
        # return func.HttpResponse("{}", mimetype="application/json")
    else :                   # get a membership for a user in a household
        context.logging.info('getting SPECIFIC membership')
        membership = context.session.query(HouseholdMembership).filter(HouseholdMembership.householdid == hid and HouseholdMembership.userid == uid).options(joinedload(HouseholdMembership.household)).first()
        if membership:
            return func.HttpResponse(json.dumps(membership.to_dict(), default=str), mimetype="application/json")   
        return func.HttpResponse("Membership Not Found", status_code=404)

def delete_membership(hid: str, uid :str) -> func.HttpResponse:
    membership = context.session.query(HouseholdMembership).filter(HouseholdMembership.householdid == hid and HouseholdMembership.userid == uid).first()
    if membership:
        context.session.delete(membership)
        context.session.commit()
        return func.HttpResponse(status_code=200)   
    return func.HttpResponse("Membership Not Found", status_code=404)

def create_membership(hid: str, uid: str) -> func.HttpResponse:
    context.logging.info('creating membership for user %s in household %s', uid, hid)

    household = context.session.query(Household).filter(Household.id == hid).first()
    if not household:
        return func.HttpResponse("Household Not Found", status_code=404)
    user = context.session.query(User).filter(User.id == uid).first()
    if not user:
        return func.HttpResponse("User Not Found", status_code=404)
    
    membership = HouseholdMembership(householdid=hid, userid=uid, role='member', balance=0)
    context.session.add(membership)
    context.session.commit()
    context.logging.info('membership created [%s]', json.dumps(membership.to_dict(), default=str))
    return func.HttpResponse(json.dumps(membership.to_dict(), default=str), mimetype="application/json")

def update_membership(hid: str, uid: str, balance: float, role : str) -> func.HttpResponse:
    context.logging.info('updating membership')
    membership = context.session.query(HouseholdMembership).filter(HouseholdMembership.householdid == hid and HouseholdMembership.userid == uid).first()
    if membership:
        membership.balance = balance
        membership.role = role
        context.session.commit()
        context.logging.info('membership updated')
        return func.HttpResponse(json.dumps(membership.to_dict(), default=str), mimetype="application/json")
    return func.HttpResponse("Membership Not Found", status_code=404)
