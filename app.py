from concurrent.futures import ThreadPoolExecutor
import os
from flask import Flask, render_template, request, redirect, url_for, session
import msal
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta, timezone
import uuid  # For generating unique filenames

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_super_secret_key")
app.permanent_session_lifetime = timedelta(minutes=3)

# Azure AD Configuration (Read from environment variables)
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
TENANT_ID = os.environ.get("AZURE_TENANT_ID")
REDIRECT_URI = os.environ.get("AZURE_REDIRECT_URI", "https://98.70.41.142:3000/auth/callback")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read"]

msal_client = None

# Azure Storage Configuration
STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME", "ntmssaudk")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "photos")
credential = DefaultAzureCredential()

blob_service_client = None
container_client = None
try:
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=credential
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
except Exception as e:
    print(f"Error connecting to Azure Storage: {e}")

executor = ThreadPoolExecutor(max_workers=5)

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

@app.route('/login')
def login():
    session.permanent = True
    client = get_msal_client()
    flow = client.initiate_auth_code_flow(
        scopes=SCOPES,
        redirect_uri=url_for("auth_callback", _external=True, _scheme='https')
    )
    session["flow"] = flow
    return redirect(flow["auth_uri"])

@app.route('/auth/callback')
def auth_callback():
    client = get_msal_client()
    flow = session.get("flow", {})
    result = client.acquire_token_by_auth_code_flow(
        flow,
        request.args
    )

    if "id_token_claims" in result:
        session["user"] = result["id_token_claims"]
        return redirect(url_for('index'))
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        return "Authentication failed"

@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("flow", None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@requires_auth
def index():
    upload_error = None
    user_id = session["user"]["oid"]  # Get the user's Entra ID

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                try:
                    # Include user ID in the blob name
                    blob_name = f"{user_id}/{uuid.uuid4()}-{file.filename}"
                    blob_client = container_client.get_blob_client(blob_name)
                    future = executor.submit(blob_client.upload_blob, file.read(), overwrite=True)
                    future.result()
                except Exception as e:
                    upload_error = f'Error uploading: {e}'

    image_urls_with_sas = []
    try:
        user_delegation_key = blob_service_client.get_user_delegation_key(
            datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(minutes=2)
        )
        # List only blobs for the current user
        blob_list = container_client.list_blobs(name_starts_with=user_id + "/")
        for blob in blob_list:
            sas_token = generate_blob_sas(
                account_name=STORAGE_ACCOUNT_NAME,
                container_name=CONTAINER_NAME,
                blob_name=blob.name,
                user_delegation_key=user_delegation_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(minutes=2)
            )
            blob_url_with_sas = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob.name}?{sas_token}"
            image_urls_with_sas.append(blob_url_with_sas)
    except Exception as e:
        print(f"Error listing blobs or generating SAS: {e}")

    return render_template('home.html', images=image_urls_with_sas, upload_error=upload_error)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000, ssl_context='adhoc')

