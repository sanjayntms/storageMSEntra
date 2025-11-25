#cloud-config
package_update: true
package_upgrade: true

packages:
  - git
  - python3
  - python3-venv
  - python3-pip
  - curl

runcmd:
  # --------------------------------------------
  # Clone your GitHub Repo
  # --------------------------------------------
  - mkdir -p /opt/storageMSEntra
  - git clone https://github.com/sanjayntms/storageMSEntra.git /opt/storageMSEntra || true

  # --------------------------------------------
  # Python Virtual Environment Setup
  # --------------------------------------------
  - python3 -m venv /opt/storageMSEntra/venv
  - /opt/storageMSEntra/venv/bin/pip install --upgrade pip
  - /opt/storageMSEntra/venv/bin/pip install -r /opt/storageMSEntra/requirements.txt

  # --------------------------------------------
  # Fetch VM Public IP dynamically
  # --------------------------------------------
  - PUBIP=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/publicIpAddress?api-version=2021-02-01")

  # --------------------------------------------
  # Create systemd Service
  # --------------------------------------------
  - |
    cat <<EOF > /etc/systemd/system/storageMSEntra.service
    [Unit]
    Description=NTMS Secure Media Gallery (Flask)
    After=network.target

    [Service]
    User=vmadmin
    WorkingDirectory=/opt/storageMSEntra

    # ------ Environment Variables injected into Systemd ------
    Environment="AZURE_CLIENT_ID=2740085e-26af-4c5c-b7ea-11bf54867a41"
    Environment="AZURE_CLIENT_SECRET=use-here-Client Id"
    Environment="AZURE_TENANT_ID=d7dc4bf7-c4ff-451d-bddc-a1fbbfc21ea0"
    Environment="AZURE_REDIRECT_URI=https://${PUBIP}:3000/auth/callback"
    Environment="FLASK_SECRET_KEY=your_super_secret_key"
    Environment="STORAGE_ACCOUNT_NAME=ntmssaudk"
    Environment="CONTAINER_NAME=photos"

    ExecStart=/opt/storageMSEntra/venv/bin/python3 /opt/storageMSEntra/app.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    EOF

  # --------------------------------------------
  # Apply service
  # --------------------------------------------
  - systemctl daemon-reload
  - systemctl enable storageMSEntra
  - systemctl start storageMSEntra
