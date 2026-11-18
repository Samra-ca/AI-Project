from fastapi import FastAPI

app = FastAPI(title="Mind2Machine Planning Agent")

# GET  /api/dashboard        - dashboard statistics
# POST /api/messages/upload  - upload message file
# GET  /api/messages         - retrieve messages
# POST /api/messages/add     - add a new message
# POST /api/run               - execute initial planning
# POST /api/update            - process new messages
# GET  /api/plan/current     - retrieve current plan
# GET  /api/plan/history     - retrieve previous plans
# GET  /api/trace            - retrieve AI trace
# GET  /api/validation       - retrieve validation results
# GET  /api/budget           - retrieve budget details
# GET  /api/export           - export final results


@app.get("/api/dashboard")
def get_dashboard():
    raise NotImplementedError
