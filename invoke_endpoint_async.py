import boto3
import json
import uuid
import base64

# Create a low-level client representing Amazon SageMaker Runtime
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name='us-west-2')
s3 = boto3.resource('s3')
s3_bucket_name = '<YOUR_BUCKET>'

endpoint_name = '<YOUR_ENDPOINT>'

def get_prediction(input_location):
    response = sagemaker_runtime.invoke_endpoint_async(
                            EndpointName=endpoint_name, 
                            InputLocation=input_location,
                            ContentType='application/json',
                            InvocationTimeoutSeconds=3600)
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
            "prompt": "1 sexy girl, blouse, in the dark",
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
            "negative_prompt": "nsfw, ng_deepnegative_v1_75t,badhandv4, (worst quality:2), (low quality:2), (normal quality:2), lowres,watermark",
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

    image_base64 = generate_img_base64_str('ori_img.png')
    mask_base64 = generate_img_base64_str('mask2.png')

    print(image_base64[0:100])
    print(mask_base64[0:100])
    
    input = {
        "task": "image-to-image",
        "model": "majicmixRealistic_v6.safetensors",
        "img2img_payload":{
            "init_images": [
                image_base64
            ],
            "resize_mode": 0,
            "denoising_strength": 0.75,
            "image_cfg_scale": 0,
            "mask": mask_base64,
            "mask_blur": 4,
            "mask_blur_x": 4,
            "mask_blur_y": 4,
            "inpainting_fill": 1,
            "inpaint_full_res": 0,
            "inpaint_full_res_padding": 32,
            "inpainting_mask_invert": 1,
            "initial_noise_multiplier": 1,
            "prompt": "Dilapidated City, rain, fire, lightning",
            "styles": [],
            "seed": 3929508295,
            "subseed": 2827841109,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "sampler_name": "Euler a",
            "batch_size": 1,
            "n_iter": 1,
            "steps": 30,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
            "restore_faces": False,
            "tiling": False,
            "do_not_save_samples": False,
            "do_not_save_grid": False,
            "negative_prompt": "nsfw, ng_deepnegative_v1_75t,badhandv4, (worst quality:2), (low quality:2), (normal quality:2), lowres,watermark",
            "eta": 0,
            "s_min_uncond": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "script_args": [],
            "sampler_index": "Euler a",
            "include_init_images": False,
            "script_name": "",
            "send_images": True,
            "save_images": False,
            "alwayson_scripts": {}
        },
    }
    input_location = create_input_file_on_s3(input)
    print(f'input location: {input_location}')

    response = get_prediction(input_location)
    print(response)

if __name__ == '__main__':
    main()