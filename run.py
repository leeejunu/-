import subprocess

# ComfyUI 실행 (백그라운드)
process = subprocess.Popen(["python", "main.py"], cwd="./ComfyUI")

# 필요하면 나중에 종료
# process.terminate()
