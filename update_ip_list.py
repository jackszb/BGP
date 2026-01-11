import requests
import json
import os
import subprocess

# 使用 GitHub Actions 提供的默认工作目录
repo_dir = os.getenv('GITHUB_WORKSPACE', '/home/runner/work/BGP/BGP')  # 如果没有环境变量则使用默认值
output_dir = os.path.join(repo_dir, 'ip-set')

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 定义下载的URLs
urls = {
    "ipv4": "https://raw.githubusercontent.com/gaoyifan/china-operator-ip/ip-lists/china.txt",
    "ipv6": "https://raw.githubusercontent.com/gaoyifan/china-operator-ip/ip-lists/china6.txt",
    "ipv4+ipv6": "https://raw.githubusercontent.com/gaoyifan/china-operator-ip/ip-lists/china46.txt"
}

# 下载并生成json文件
def download_and_generate_json(ip_version, url):
    response = requests.get(url)
    ip_list = response.text.splitlines()
    
    # 生成json格式
    json_data = {
        "version": 3,
        "rules": [{"ip_cidr": ip_list}]
    }

    # 保存文件
    json_filename = f"cn-ipv4.json" if ip_version == 'ipv4' else f"cn-ipv6.json" if ip_version == 'ipv6' else "cn-ip.json"
    json_path = os.path.join(output_dir, json_filename)

    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    return json_path

# 编译成 .srs 文件
def compile_to_srs(json_path):
    # 调用 sing-box 命令
    compile_command = f"sing-box rule-set compile --output {json_path.replace('.json', '.srs')} {json_path}"
    subprocess.run(compile_command, shell=True)

# 更新IP列表并推送到GitHub
def update_repository():
    # 下载并生成json文件
    for version, url in urls.items():
        json_path = download_and_generate_json(version, url)
        compile_to_srs(json_path)  # 编译成 .srs 文件
    
    # 添加并推送文件到 GitHub
    os.chdir(repo_dir)
    subprocess.run("git add ip-set/*", shell=True)
    subprocess.run("git commit -m 'Update IP list and .srs files'", shell=True)
    subprocess.run("git push origin main", shell=True)

if __name__ == "__main__":
    update_repository()
