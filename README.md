# storageMSEntra

![image](https://github.com/user-attachments/assets/c51fbb0b-84d3-486d-bad8-fe16ac17b59b)

 ## Auditing in Azure Blob Storage

This section outlines the auditing implications when using Account Keys versus User Delegation Keys and Shared Access Signature (SAS) tokens for accessing Azure Blob Storage.

### Auditing with Account Keys:

* **Limited User Attribution:**
    When requests are made to Azure Blob Storage using an Account Key, the logs primarily indicate that the authentication was performed using one of the storage account's keys. It is **difficult to directly identify the specific user or application** that initiated the action.

* **Storage Account Level Focus:**
    The Azure Storage logs are primarily centered around the storage account level. While they record the operations performed, the context of **who** carried out these operations is often missing.

* **No Built-in User Identity:**
    Account Keys themselves do not contain any inherent information about the user or application making the request.

### Auditing with User Delegation Keys and SAS Tokens:

* **Improved User Attribution (Indirect):**
    Utilizing User Delegation Keys, which rely on Azure Active Directory (Azure AD) for initial authentication, allows for an indirect linkage of actions to specific users or applications. The typical process involves:
    1.  A user or application authenticates with Azure AD.
    2.  The application uses the obtained Azure AD token to request a User Delegation Key.
    3.  This User Delegation Key is then used by the application to sign SAS tokens, granting specific access to blobs.
    4.  When Azure Storage receives a request authenticated with a SAS token signed by a User Delegation Key, the logs record that a SAS was used for authentication.

* **Combining Logs for Comprehensive Auditing:**
    To gain a more complete understanding of who accessed what resources, it's necessary to correlate Azure Storage logs with:
    * **Azure AD Sign-in Logs:** These logs provide information about user and application authentication events.
    * **Application-Level Logs:** Your application's logs can provide further context about the actions leading to storage access.
    By analyzing these logs together, you can trace the sequence of events from user authentication to the eventual data access.

* **SAS Token Information as a Key Indicator:**
    While Azure Storage logs might not directly contain the originating user's identity from Azure AD, the record of a "User Delegation SAS" being used is a significant piece of information. It confirms that the access was granted based on Azure AD credentials, providing a higher level of accountability compared to Account Key usage.

* **Enhanced Auditing through the Principle of Least Privilege:**
    By employing SAS tokens with specific and limited permissions (a core principle when using User Delegation Keys), you significantly narrow down the scope of actions that a particular user or application could have performed. This focused access control inherently makes auditing more effective and targeted.
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
