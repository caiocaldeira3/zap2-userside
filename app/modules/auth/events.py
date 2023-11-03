from app import api, job_queue, sio
from app.services import user as ussr
from app.util.jobs import RefreshJob

ResponseData = dict[str, str | dict[str, str]]

@sio.on("connect")
def handle_connect () -> None:
    print(f"connection established")

@sio.on("auth_response")
def handle_auth_response (resp: dict):
    print(resp["msg"])
    if resp["status"] == "created":
        job_queue.add_job(api.user_id, 0, RefreshJob)

    elif resp["status"] == "ok":
        pass

    else:
        api.logout()

        if resp.get("data", None) is not None:
            telephone = resp["data"]["telephone"]

            ussr.delete_user(telephone)

@sio.event
def disconnect ():
    api.logout()
    print("disconnected from server")