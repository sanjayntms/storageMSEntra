from concurrent.futures import ThreadPoolExecutor
import os
from flask import Flask, render_template, request, redirect, url_for, session
import msal
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta, timezone
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_super_secret_key")
app.permanent_session_lifetime = timedelta(minutes=30)

# Azure Entra ID
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
TENANT_ID = os.environ.get("AZURE_TENANT_ID")
REDIRECT_URI = os.environ.get("AZURE_REDIRECT_URI")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read"]

# Azure Storage
STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")
credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=credential
)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

executor = ThreadPoolExecutor(max_workers=5)
msal_client = None


def get_msal_client():
    global msal_client
    if not msal_client:
        msal_client = msal.ConfidentialClientApplication(
            CLIENT_ID,
            authority=AUTHORITY,
            client_credential=CLIENT_SECRET
        )
    return msal_client


def requires_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ========================
#      ROUTES
# ========================

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/login")
def login():
    client = get_msal_client()
    flow = client.initiate_auth_code_flow(
        scopes=SCOPES,
        redirect_uri=url_for("callback", _external=True, _scheme="https")
    )
    session["flow"] = flow
    return redirect(flow["auth_uri"])


@app.route("/auth/callback")
def callback():
    client = get_msal_client()
    flow = session.get("flow")
    result = client.acquire_token_by_auth_code_flow(flow, request.args)

    if "id_token_claims" in result:
        session["user"] = result["id_token_claims"]
        return redirect(url_for("gallery"))

    return "Authentication Error", 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))


@app.route("/gallery", methods=["GET", "POST"])
@requires_auth
def gallery():
    upload_error = None
    user_id = session["user"]["oid"]

    # UPLOAD
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            blob_name = f"{user_id}/{uuid.uuid4()}-{file.filename}"
            try:
                blob_client = container_client.get_blob_client(blob_name)
                executor.submit(blob_client.upload_blob, file.read(), overwrite=True).result()
            except Exception as e:
                upload_error = str(e)

    # GENERATE SAS URLs
    items = []
    try:
        user_delegation_key = blob_service_client.get_user_delegation_key(
            datetime.now(timezone.utc),
            datetime.now(timezone.utc) + timedelta(minutes=10)
        )

        for blob in container_client.list_blobs(name_starts_with=f"{user_id}/"):
            sas = generate_blob_sas(
                account_name=STORAGE_ACCOUNT_NAME,
                container_name=CONTAINER_NAME,
                blob_name=blob.name,
                user_delegation_key=user_delegation_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(minutes=10)
            )
            url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob.name}?{sas}"

            ext = blob.name.lower()
            if ext.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                ftype = "image"
            elif ext.endswith(".mp4"):
                ftype = "video"
            elif ext.endswith((".mp3", ".wav")):
                ftype = "audio"
            elif ext.endswith(".pdf"):
                ftype = "pdf"
            else:
                ftype = "other"

            items.append({"url": url, "type": ftype, "blob_name": blob.name})

    except Exception as e:
        print("SAS error:", e)

    return render_template("home.html", files=items, upload_error=upload_error)


# DELETE FILE
@app.route("/delete/<path:blob_name>", methods=["POST"])
@requires_auth
def delete_file(blob_name):
    user_id = session["user"]["oid"]
    if not blob_name.startswith(f"{user_id}/"):
        return "Unauthorized", 403
    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        return ("", 204)
    except:
        return "Delete failed", 500


# SHARE LINK
@app.route("/share/<path:blob_name>")
@requires_auth
def share_file(blob_name):
    user_id = session["user"]["oid"]
    if not blob_name.startswith(f"{user_id}/"):
        return "Unauthorized", 403
    try:
        key = blob_service_client.get_user_delegation_key(
            datetime.now(timezone.utc),
            datetime.now(timezone.utc) + timedelta(hours=24)
        )
        sas = generate_blob_sas(
            account_name=STORAGE_ACCOUNT_NAME,
            container_name=CONTAINER_NAME,
            blob_name=blob_name,
            user_delegation_key=key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob_name}?{sas}"
        return url
    except:
        return "Share failed", 500


# RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True, ssl_context="adhoc")

