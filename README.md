# aws-sd-api
invoke stable diffusion api with python.

# install stable diffusion webui on EC2

## 1. Create EC2 instance
Instance type: g4dn.2xlarge  
AMI: Deep Learning AMI GPU PyTorch 2.0.1 (Ubuntu 20.04) 

## 2. Install SD-webui
https://github.com/AUTOMATIC1111/stable-diffusion-webui

## 3. Run webui with API mode
```
webui.sh --listen --share --api
```

## 4. Call API with python script
