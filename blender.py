import subprocess
import sys
import os
import requests
from keybert import KeyBERT

# 🔹 1️⃣ 키워드 추출 (KeyBERT)
def extract_keywords(text):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
    return [kw[0] for kw in keywords]

# 🔹 2️⃣ ComfyUI로 이미지 생성
def generate_image(prompt, output_path="generated_texture.png"):
    comfyui_url = "http://127.0.0.1:8188/prompt"

    payload = {
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "steps": 20,
        "cfg_scale": 7.5,
        "sampler_name": "Euler a",
        "seed": -1
    }

    response = requests.post(comfyui_url, json=payload)
    if response.status_code != 200:
        raise Exception("ComfyUI 요청 실패! ComfyUI가 실행 중인지 확인하세요.")

    result = response.json()
    image_path = result.get("image_path")
    
    # 이미지 다운로드
    image_url = f"http://127.0.0.1:8188/get_image/{image_path}"
    img_data = requests.get(image_url).content
    with open(output_path, 'wb') as handler:
        handler.write(img_data)
    
    return os.path.abspath(output_path)

# 🔹 3️⃣ Blender 실행 함수 (Mac/Linux 지원)
def run_blender_script(script_path):
    """ Blender를 백그라운드에서 실행하여 Python 스크립트 실행 """

    # Blender 실행 경로 자동 탐색 (Mac/Linux)
    blender_paths = [
        "/opt/homebrew/bin/blender",
        "/usr/local/bin/blender",
        "/snap/bin/blender"
    ]
    blender_exe = None

    for path in blender_paths:
        if os.path.exists(path):
            blender_exe = path
            break

    if not blender_exe:
        raise FileNotFoundError("Blender 실행 파일을 찾을 수 없습니다! Blender가 설치되어 있는지 확인하세요.")

    command = [blender_exe, "--background", "--python", script_path]
    subprocess.run(command, check=True)

# 🔹 4️⃣ Blender에서 실행할 스크립트 저장
def create_blender_script(image_path, output_script="blender_script.py"):
    script_content = f"""
        import bpy

        # 기존 객체 삭제
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # 큐브 생성
        bpy.ops.mesh.primitive_cube_add(size=2)
        cube = bpy.context.object

        # 머티리얼 생성
        mat = bpy.data.materials.new(name="GeneratedMaterial")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")

        # 이미지 텍스처 노드 추가
        tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex_image.image = bpy.data.images.load(r"{image_path}")

        # BSDF에 연결
        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

        # 큐브에 머티리얼 적용
        cube.data.materials.append(mat)
    """

    with open(output_script, "w", encoding="utf-8") as f:
        f.write(script_content)
    return os.path.abspath(output_script)

# 🔹 5️⃣ 실행 파이프라인
if __name__ == "__main__":
    text_input = "지진 발생, 안전한 곳으로 대피하세요."
    keywords = extract_keywords(text_input)
    prompt_text = " ".join(keywords) + " in a realistic style"

    # ComfyUI로 이미지 생성
    image_path = generate_image(prompt_text)

    # Blender 실행할 스크립트 생성 후 실행
    blender_script = create_blender_script(image_path)
    run_blender_script(blender_script)
