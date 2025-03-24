import azure.functions as func
import uuid
import json
from service_models import Household
from function_app_context import context

bpHouseholds = func.Blueprint()

@bpHouseholds.route(route="households", methods=['GET', 'POST', 'PUT', 'DELETE'])
def household_service(req: func.HttpRequest) -> func.HttpResponse:
    context.logging.info('Household service called [%s]', req.method)

    if req.method == 'GET' or req.method == 'DELETE':
        try:
            hid = req.params.get('hid')
            if hid:
                id = uuid.UUID(hid)
                if not id:
                    raise ValueError()
            else:
                raise ValueError()
        except ValueError:
            return func.HttpResponse("Invalid House ID", status_code=400)
    elif req.method == 'POST' or req.method == 'PUT':
        try:
            household_data = req.get_json()
        except ValueError:
            pass
        else:
            name = household_data.get('name')
            idStr = household_data.get('id')        
        context.logging.info('household_data : %s', household_data)
        if not idStr and not name:
            return func.HttpResponse("Household data must contain id or name", status_code=400)
    
    if req.method == 'GET' :
        return get_household(id)
    elif req.method == 'DELETE':
        return delete_household(id)
    elif req.method == 'POST':
        return add_household(name)
    elif req.method == 'PUT':
        return update_household(idStr, name)
    else:
        return func.HttpResponse("Method Not Allowed", status_code=405)

def get_household(id: str) -> func.HttpResponse:
    #retrieving a household
    context.logging.info('getting household')

    if id == uuid.UUID(context.KEY):
        context.logging.info('getting ALL households')
        households = context.session.query(Household).all()
        return func.HttpResponse(json.dumps([household.to_dict() for household in households], default=str), mimetype="application/json")
    else:
        household = context.session.query(Household).filter(Household.id == id).first()
        if household:
            return func.HttpResponse(json.dumps(household.to_dict(), default=str), mimetype="application/json")
        return func.HttpResponse("Household not found", status_code=404)

def delete_household(id: str) -> func.HttpResponse:
    context.logging.info('deleting household')
    household = context.session.query(Household).filter(Household.id == id).first()
    if household:
        context.session.delete(household)
        context.session.commit()
        return func.HttpResponse(json.dumps(household.to_dict(), default=str), mimetype="application/json")
    else:
        return func.HttpResponse("Household not found", status_code=404)

def add_household(name: str) -> func.HttpResponse:
    context.logging.info('adding household : %s', name)
    if not name:
        return func.HttpResponse("Household Name Missing", status_code=400)
    household = Household(name=name)
    context.session.add(household)
    context.session.commit()
    # context.logging.info(household.id) #why is this required to get the household to contain any data
    return func.HttpResponse(json.dumps(household.to_dict(), default=str), mimetype="application/json")

def update_household(hid: str, name: str) -> func.HttpResponse:
    context.logging.info('updating household')
    if not name:
        return func.HttpResponse("Invalid Household Name", status_code=400)
    try:
        hid = uuid.UUID(hid)
    except ValueError:
        return func.HttpResponse("Invalid House ID", status_code=400)

    household = context.session.query(Household).filter(Household.id == hid).first()
    if household:
        household.name = name
        context.session.commit()
        context.logging.info(json.dumps(household.to_dict(), default=str))
        return func.HttpResponse(json.dumps(household.to_dict(), default=str), mimetype="application/json")
    else:
        return func.HttpResponse("Household not found", status_code=404)
