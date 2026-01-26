#!/bin/bash

# SSL Setup Script for Honeypot API
# Uses Let's Encrypt for free SSL certificates

DOMAIN="your-domain.com"
EMAIL="your-email@example.com"

echo "==================================="
echo "SSL Certificate Setup"
echo "==================================="

# Create directories
mkdir -p certbot/conf certbot/www

# Step 1: Get initial certificate
echo "Step 1: Obtaining SSL certificate..."
docker-compose -f docker-compose.ssl.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# Step 2: Start services
echo "Step 2: Starting services..."
docker-compose -f docker-compose.ssl.yml up -d

echo "==================================="
echo "SSL Setup Complete!"
echo "Your API is now available at: https://$DOMAIN"
echo "==================================="
