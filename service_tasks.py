import azure.functions as func
import json
from service_models import Task
from function_app_context import context

bpTasks = func.Blueprint()

@bpTasks.route(route="chores", methods=['GET', 'POST', 'PUT', 'DELETE'])
def chore_service(req: func.HttpRequest) -> func.HttpResponse:
    context.logging.info('get_chores called')
    return func.HttpResponse("Hello, chores!", status_code=200)
    chores = session.query(Chore).all()
    return func.HttpResponse(json.dumps([chore.__dict__ for chore in chores]), mimetype="application/json")
