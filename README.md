# storageMSEntra

![image](https://github.com/user-attachments/assets/c51fbb0b-84d3-486d-bad8-fe16ac17b59b)


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
