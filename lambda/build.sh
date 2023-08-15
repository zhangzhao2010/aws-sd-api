#!/bin/bash
rm -rf ./my_function

mkdir my_function
cp ./lambda_function.py ./my_function/lambda_function.py

cd my_function
mkdir package

pip install --target ./package boto3
pip install --target ./package json

cd package
zip -r ../my_deployment_package.zip .

cd ..
zip my_deployment_package.zip lambda_function.py