#!/bin/bash

echo "This is a file modifier"


echo
echo "The username is: $USERNAME"
echo "The path to the secret file is: $SECRET_FILE_PATH"

--- -- -- --- --- -- 
if id "$USERNAME" &> /dev/null; then
    echo "User exists "
else
    echo "User '$USERNAME' does not exist "
    exit 1
fi

if [ -f "$SECRET_FILE_PATH" ]; then
    echo "Secret file exists ✅"
else
    echo "Secret file not found at '$SECRET_FILE_PATH' "
    exit 1
fi

sed -i "s|username:.*|username: $USERNAME|" data.yaml
sed -i "s|secret_file:.*|secret_file: $SECRET_FILE_PATH|" data.yaml

echo
echo " Configuration file 'data.yaml' updated successfully!"