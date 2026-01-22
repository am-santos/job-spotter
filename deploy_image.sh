#!/bin/bash
set -e

# Configuration
PROJECT_ID="job-spotter-485100"
REGION="europe-west1"
REPO_NAME="prod-repo"
IMAGE_NAME="job-spotter"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$IMAGE_TAG"

echo "======================================================"
echo "1. Creating Artifact Registry Repo (if not exists)"
echo "======================================================"
cd terraform
terraform apply -target=google_artifact_registry_repository.repo -auto-approve
cd ..

echo "======================================================"
echo "2. Configuring Docker Auth for GCP"
echo "======================================================"
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

echo "======================================================"
echo "3. Building Docker Image"
echo "======================================================"
# Build for linux/amd64 as Cloud Run requires it
docker build --platform linux/amd64 -t $FULL_IMAGE_NAME .

echo "======================================================"
echo "4. Pushing Docker Image to Artifact Registry"
echo "======================================================"
docker push $FULL_IMAGE_NAME

echo "======================================================"
echo "5. Applying Full Terraform Configuration"
echo "======================================================"
cd terraform
terraform apply -auto-approve
cd ..

echo "======================================================"
echo "Deployment Complete!"
echo "======================================================"
