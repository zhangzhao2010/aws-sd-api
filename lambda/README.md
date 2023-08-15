# aws-sd-api
invoke stable diffusion api by lambda.

# deploy a sagemaker inference endpoint
https://github.com/xieyongliang/stable-diffusion-webui-api

# reference blog
https://aws.amazon.com/cn/blogs/machine-learning/call-an-amazon-sagemaker-model-endpoint-using-amazon-api-gateway-and-aws-lambda/

# deploy lambda
1. create lambda function with python3
2. run `build.sh`
3. upload zip package to lambda
4. Add sagemaker:invokeEndpoint permission to lambda

# create api gateway(use lambda proxy)
