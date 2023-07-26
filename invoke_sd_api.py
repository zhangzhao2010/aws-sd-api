import requests
import base64
import io
import time
from PIL import Image, PngImagePlugin

url = 'your_webui_api_url'

# convert image to base64 string
def generate_img_base64_str(img):
    ext = img.split(".")[-1]
    with open(img, 'rb') as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    return "data:image/{ext};base64,{data}".format(ext=ext, data=image_base64)

image_base64 = generate_img_base64_str('ori_img.png')
mask_base64 = generate_img_base64_str('mask.png')

print(image_base64[0:100])
print(mask_base64[0:100])

payload = {
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
    "inpainting_mask_invert": 0,
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
}

headers = {'content-type': 'application/json'}
r = requests.post(f'{url}/sdapi/v1/img2img', json=payload, headers=headers)
# 查看响应结果
json_r = r.json()
index = 1
for i in json_r['images']:
    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

    png_payload = {
        "image": "data:image/png;base64," + i
    }
    response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

    PI = PngImagePlugin.PngInfo()
    PI.add_text("parameters", response2.json().get("info"))

    output = f'output-{int(time.time())}-{index}.png'
    image.save(output, pnginfo=PI)
    print(f"{output} saved.\n")

    index+=1