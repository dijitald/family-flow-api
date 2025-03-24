import azure.functions as func
import json
from service_models import Activity
from function_app_context import context

bpActivities = func.Blueprint()

@bpActivities.route(route="activities", methods=['GET', 'POST', 'PUT', 'DELETE'])
def activity_service(req: func.HttpRequest) -> func.HttpResponse:
    context.logging.info('get_activities called')
    return func.HttpResponse("Hello, activities!", status_code=200)
    activities = session.query(Activity).all()
    return func.HttpResponse(json.dumps([activity.__dict__ for activity in activities]), mimetype="application/json")
