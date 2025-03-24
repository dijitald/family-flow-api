import azure.functions as func
import logging, os
from azure.monitor.opentelemetry import configure_azure_monitor
from function_app_context import context

from sqlalchemy.orm import sessionmaker, scoped_session
from service_models import engine
from service_users import bpUsers
# from service_households import bpHouseholds
# from service_tasks import bpTasks
# from service_activities import bpActivities
# from service_memberships import bpMembers

configure_azure_monitor(logger_name="familyflow")
context.logging = logging.getLogger("familyflow")  
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


try:
    app.register_blueprint(bpUsers)
    # app.register_blueprint(bpHouseholds)
    # app.register_blueprint(bpTasks)
    # app.register_blueprint(bpActivities)
    # app.register_blueprint(bpMembers)
except Exception as e:
    context.logging.critical(f"Error initializing application: {e}")
    raise e

try:
    factory = sessionmaker(bind=engine) 
    session = scoped_session(factory)
    context.session = session
    context.KEY = os.getenv("DEBUGKEY")
except Exception as e:
    context.logging.critical(f"Error initializing database: {e}")
    raise e

@app.route(route="ping")
def ping(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )