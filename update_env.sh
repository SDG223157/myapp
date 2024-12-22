#!/bin/bash

# Parse the MySQL URL
DB_URL="mysql://mysql:FuN5Oe5y0kQfQH1ZzWRo9XUFNAfZsrLvbh7QOS3BUQuB1eRl5QBBOcDdWx3fa75G@b44gc00csgk4c84400k0ook4:3306/default"

# Extract components using string manipulation
DB_USER=$(echo $DB_URL | cut -d':' -f2 | cut -d'/' -f3)
DB_PASS=$(echo $DB_URL | cut -d':' -f3 | cut -d'@' -f1)
DB_HOST=$(echo $DB_URL | cut -d'@' -f2 | cut -d':' -f1)
DB_PORT=$(echo $DB_URL | cut -d':' -f4 | cut -d'/' -f1)
DB_NAME=$(echo $DB_URL | cut -d'/' -f4)

# Create or update .env file
cat << EOF > .env
MYSQL_HOST=$DB_HOST
MYSQL_USER=$DB_USER
MYSQL_PASSWORD=$DB_PASS
MYSQL_PORT=$DB_PORT
MYSQL_DATABASE=$DB_NAME
EOF

# Set proper permissions
chmod 600 .env

echo ".env file has been created with the following settings:"
echo "MYSQL_HOST=$DB_HOST"
echo "MYSQL_USER=$DB_USER"
echo "MYSQL_PORT=$DB_PORT"
echo "MYSQL_DATABASE=$DB_NAME"
echo "Note: Password has been set but not displayed for security"