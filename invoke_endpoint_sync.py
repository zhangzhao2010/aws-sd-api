import boto3
import json
import uuid
import base64
import logging
from botocore.exceptions import ClientError

# Create a low-level client representing Amazon SageMaker Runtime
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name='<YOUR_REGION>')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
s3_bucket_name = '<YOUR_BUCKET_NAME>'

endpoint_name = '<YOUR_ENDPOINT>'

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def get_prediction(input):
    response = sagemaker_runtime.invoke_endpoint(
                            EndpointName=endpoint_name,
                            Body=bytes(json.dumps(input), 'utf-8'),
                            ContentType='application/json',
                            Accept='application/json'
                        )
    return response

# save json to file
def create_input_file_on_s3(input):
    tmpFileName = str(uuid.uuid1())
    f = open(f'tmp/{tmpFileName}.json', 'w')
    f.write(json.dumps(input))
    f.close()

    s3.meta.client.upload_file(f'tmp/{tmpFileName}.json', s3_bucket_name, f'async-endpoint-inputs/{tmpFileName}/{tmpFileName}.json')
    return f's3://{s3_bucket_name}/async-endpoint-inputs/{tmpFileName}/{tmpFileName}.json'

def generate_img_base64_str(img):
    ext = img.split(".")[-1]
    with open(img, 'rb') as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    return "data:image/{ext};base64,{data}".format(ext=ext, data=image_base64)

def parse_s3_url(s3_url):
    s3_url = s3_url.replace("s3://", "")
    bucket_name, object_key = s3_url.split("/", 1)
    return bucket_name, object_key

def main():
    input = {
        "task": "text-to-image",
        "model": "majicmixRealistic_v6.safetensors",
        "txt2img_payload": {
            "enable_hr": False,
            "denoising_strength": 0,
            "hr_scale": 2,
            "hr_upscaler": "",
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "prompt": "1girl,sitting on a cozy couch,crossing legs,soft light",
            "styles": [""],
            "seed": 2363669683,
            "subseed": 3178589920,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "sampler_name": "Euler a",
            "batch_size": 1,
            "n_iter": 1,
            "steps": 30,
            "cfg_scale": 7,
            "width": 512,
            "height": 768,
            "restore_faces": False,
            "tiling": False,
            "do_not_save_samples": False,
            "do_not_save_grid": False,
            "negative_prompt": "(worst quality:2),(low quality:2),(normal quality:2),lowres,watermark,badhandv4,ng_deepnegative_v1_75t,",
            "eta": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "script_args": [],
            "sampler_index": "Euler a",
            "script_name": "",
            "send_images": True,
            "save_images": False,
            "alwayson_scripts": {},
        },
    }

    response = get_prediction(input=input)
    response_body = json.load(response['Body'])
    # print(response)
    # print(response_body['images'])
    result_url = []
    for img in response_body['images']:
        bucket_name, object_key = parse_s3_url(img)
        presigned_url = create_presigned_url(bucket_name=bucket_name,object_name=object_key)
        result_url.append(presigned_url)

    print(result_url)

if __name__ == '__main__':
    main()