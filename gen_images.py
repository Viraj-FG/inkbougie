import jwt, time, requests, sys

AK = 'AnFHPatd4tLAANQrMmefE3KmdM3NLpBt'
SK = 'kbdaMAPNGkLdAYmdkQ9NaBLgd9EBhEpN'

def token():
    now = int(time.time())
    return jwt.encode({"iss": AK, "exp": now+1800, "nbf": now-5, "iat": now}, SK, algorithm="HS256", headers={"typ": "JWT"})

def gen_image(prompt, ratio="16:9"):
    r = requests.post("https://api.klingai.com/v1/images/generations",
        json={"model_name": "kling-v1", "prompt": prompt, "n": 1, "aspect_ratio": ratio},
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}, timeout=15)
    data = r.json()
    if data.get("code") != 0:
        print(f"ERROR: {data}")
        return None
    task_id = data["data"]["task_id"]
    print(f"Task {task_id} submitted...")
    for i in range(20):
        time.sleep(8)
        r = requests.get(f"https://api.klingai.com/v1/images/generations/{task_id}",
            headers={"Authorization": f"Bearer {token()}"}, timeout=15)
        result = r.json()
        status = result.get("data", {}).get("task_status", "?")
        if status == "succeed":
            url = result["data"]["task_result"]["images"][0]["url"]
            print(f"Done!")
            return url
        elif status == "failed":
            print(f"FAILED: {result}")
            return None
        print(f"  {status}... ({i+1})")
    return None

images = [
    ("hero", "Cinematic portrait silhouette of a rapper in a recording studio, dark moody lighting with golden backlight, smoke effects, microphone visible, luxury hip hop aesthetic, 8k photography", "16:9"),
    ("artist", "Portrait of a confident young Black male rapper artist, wearing stylish designer clothes, gold chain, moody dramatic studio lighting with warm golden tones, dark background, editorial fashion photography, 8k", "3:4"),
]

for name, prompt, ratio in images:
    print(f"\nGenerating {name}...")
    url = gen_image(prompt, ratio)
    if url:
        data = requests.get(url, timeout=30).content
        path = f"C:/Users/12066/.openclaw/workspace/inkbougie/{name}.png"
        with open(path, "wb") as f:
            f.write(data)
        print(f"Saved: {path} ({len(data)//1024}KB)")
