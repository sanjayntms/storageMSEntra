# storageMSEntra

![image](https://github.com/user-attachments/assets/c51fbb0b-84d3-486d-bad8-fe16ac17b59b)

Auditing with Account Keys:

Limited User Attribution: When requests are made to Azure Blob Storage using an Account Key, the logs will primarily show that the request was authenticated using one of the account keys. It's difficult to directly identify which specific user or application initiated the action.
Storage Account Level: The logs are primarily focused at the storage account level. While you can see which operations were performed, the context of who performed them is often missing.
No Built-in User Identity: Account Keys don't carry any inherent information about the user or application making the request.
Auditing with User Delegation Keys and SAS Tokens:

Improved User Attribution (Indirect): Because User Delegation Keys rely on Azure AD for the initial authentication, you can indirectly tie actions to specific users or applications. The process involves:
A user or application authenticates with Azure AD.
The application uses the Azure AD token to obtain a User Delegation Key.
The application uses the User Delegation Key to sign SAS tokens for specific blob access.
When Azure Storage receives a request with a SAS token signed by a User Delegation Key, the logs can show that a SAS was used for authentication.
Combining Logs: To get a clearer picture of who accessed what, you would typically need to correlate Azure Storage logs with Azure AD sign-in logs and any application-level logs. This can help trace the sequence of events from user authentication to data access.
SAS Token Information: While the storage logs themselves might not directly contain the user's identity from Azure AD, the fact that a User Delegation SAS was used is a key piece of information. You know that the access was granted based on Azure AD credentials.
Principle of Least Privilege Benefits Auditing: By granting specific, limited permissions through SAS tokens, you narrow down the scope of what actions a particular user or application could have performed. This makes auditing more focused.

# 1) Create Service principal - App registration photo
    Copy Tenant ID, Client ID, Secret
    In photo, Authentication - Add web platform ---Add Web Redirect UIs ---https://98.70.41.142:3000/auth/callback # Change IP
    Add API permission 
# 2) Create storage account and use MS entra id authentication, Create container photos
# 3) Create Azure Linux VM
     mkdir storageMSEntra and Copy app.py 
     mkdir storageMSEntra/templates and copy home.html here
     sudo apt update
     sudo apt install python3 python3-pip
     sudo apt install python3-venv
     python3 -m venv venv
     source venv/bin/activate
     pip install Flask msal azure-identity azure-storage-blob
     # Use above copied values in the following 3 lines: 
     export AZURE_TENANT_ID="b29181dd-e6c6-4cc4-a3eb-deece25ddb54" 
     export AZURE_CLIENT_ID="64a034ae-ac85-4858-a295-26add4b0d24c"
     export AZURE_CLIENT_SECRET="_zP8Q~3v.7NiHtfYV_nLKZHi1Evp8IkfeNFMabes"
     In app.py, Modift storage account name and container name
# 3) Assign Storage Blob Data owner permission to service principal - photo
