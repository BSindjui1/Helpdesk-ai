#!/bin/bash
# deploy.sh — redeploy the helpdesk app with latest code

echo "Starting deployment..."

# Pull latest code from git (when you have a remote repo)
# git pull origin main

# Stop the current service
echo "Stopping service..."
sudo systemctl stop helpdesk

# Activate venv and update dependencies
echo "Updating dependencies..."
cd /home/$USER/helpdesk-ai
source venv/bin/activate
pip install -r requirements.txt --quiet

# Restart the service
echo "Starting service..."
sudo systemctl start helpdesk

# Check it came back up
sleep 3
STATUS=$(sudo systemctl is-active helpdesk)
if [ "$STATUS" = "active" ]; then
    echo "Deployment successful. App is running."
else
    echo "Deployment FAILED. Check logs: sudo journalctl -u helpdesk -n 20"
fi
