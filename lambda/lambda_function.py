import boto3
import json

# Create a low-level client representing Amazon SageMaker Runtime
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name='<YOUR_REGION>')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
s3_bucket_name = '<YOUR_BUCKET_NAME>'

endpoint_name = '<YOUR_SAGEMAKER_INFERENCE_ENDPOINT_NAME>'

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,'Key': object_name},
                                                ExpiresIn=expiration)

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

def parse_s3_url(s3_url):
    s3_url = s3_url.replace("s3://", "")
    bucket_name, object_key = s3_url.split("/", 1)
    return bucket_name, object_key

def main(prompt='',negative_prompt=''):
    if prompt=='' and negative_prompt=='':
        prompt = '1girl,sitting on a cozy couch,crossing legs,soft light'
        negative_prompt = '(worst quality:2),(low quality:2),(normal quality:2),lowres,watermark,badhandv4,ng_deepnegative_v1_75t,'

    input = {
        "task": "text-to-image",
        "model": "<YOUR_MODEL_NAME>",
        "txt2img_payload": {
            "enable_hr": False,
            "denoising_strength": 0,
            "hr_scale": 2,
            "hr_upscaler": "",
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "prompt": prompt,
            "styles": [""],
            "seed": -1,
            "subseed": -1,
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
            "negative_prompt": negative_prompt,
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

    return result_url

def lambda_handler(event, context):
    result = {
            'statusCode': 200,
            'headers':{
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({}),
        }
    if 'httpMethod' in event:
        if event['httpMethod'] == 'GET':
            return {
                'statusCode': 200,
                'body': json.dumps({'msg': 'this is a GET request.'}),
            }
        elif event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'body': json.dumps({'msg': 'this is a OPTIONS request.'}),
            }
    
    if 'body' in event:
        try:
            data = json.loads(event['body'])
            prompt = data.get('prompt', '')
            negative_prompt = data.get('negative_prompt', '')
        except json.JSONDecodeError:
            result['statusCode'] = 400
            result['body'] =  json.dumps({'error': 'Invalid JSON payload', 'body': event['event']})
            return result
    else:
        result['statusCode'] = 400
        result['body'] =  json.dumps({'error': 'Missing POST body', 'event': event})
        return result

    result_url = main(prompt=prompt,negative_prompt=negative_prompt)
    result['statusCode'] = 200
    result['body'] =  json.dumps({'images': result_url})
    return result

if __name__ == '__main__':
    main()