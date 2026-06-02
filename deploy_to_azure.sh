#!/usr/bin/env bash
# deploy_to_azure.sh
# ------------------
# End-to-end Azure deployment script for the MLOps Project API.

set -euo pipefail

RESOURCE_GROUP="rg-mlops-project"
LOCATION="eastus2"
ACR_NAME="mlopsacr$RANDOM"
ACA_ENVIRONMENT="mlops-env"
CONTAINER_APP_NAME="mlops-api"
IMAGE_NAME="mlops-api"
IMAGE_TAG="latest"
API_TOKEN=${API_TOKEN:-"Partner@123"} 

echo "============================================================"
echo " Deployment Variables"
echo "============================================================"
echo "  Resource Group  : $RESOURCE_GROUP"
echo "  Location        : $LOCATION"
echo "  ACR Name        : $ACR_NAME"
echo "  ACA Environment : $ACA_ENVIRONMENT"
echo "  Container App   : $CONTAINER_APP_NAME"
echo "============================================================"

echo ">> Creating Resource Group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

echo ">> Creating Azure Container Registry ($ACR_NAME)..."
az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic --admin-enabled true

echo ">> Building Docker image in ACR (az acr build)..."
# Important: Ensure the context is the project root where Dockerfile is located (or pass it explicitly)
az acr build --registry "$ACR_NAME" --image "${IMAGE_NAME}:${IMAGE_TAG}" --file docker/Dockerfile .

echo ">> Creating Azure Container Apps Environment..."
az containerapp env create --name "$ACA_ENVIRONMENT" --resource-group "$RESOURCE_GROUP" --location "$LOCATION"

ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query "loginServer" --output tsv | tr -d '\r')
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query "username" --output tsv | tr -d '\r')
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query "passwords[0].value" --output tsv | tr -d '\r')

echo ">> Deploying container to Azure Container Apps..."
az containerapp create \
  --name "$CONTAINER_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$ACA_ENVIRONMENT" \
  --image "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}" \
  --registry-server "$ACR_LOGIN_SERVER" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --ingress external \
  --target-port 80 \
  --env-vars "API_TOKEN=$API_TOKEN" \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi

echo "============================================================"
echo " Deployment complete!"
echo "============================================================"
APP_FQDN=$(az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.configuration.ingress.fqdn" --output tsv)
echo "  App URL  : https://$APP_FQDN"
echo "============================================================"
