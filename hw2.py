import requests
from requests.auth import HTTPBasicAuth
import subprocess
import os

def connect_to_gerrit(gerrit_url, username, password):
    try:
        response = requests.get(gerrit_url, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            print("Successfully connected to Gerrit")
            return True
        else:
            print(f"Failed to connect to Gerrit. Status code: {response.status_code}")
            response.raise_for_status()
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Gerrit: {e}")
        return False

def execute_git_command(command):
    print(f"Executing command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=os.environ)
    if result.returncode == 0:
        print(f"Command executed successfully:\n{result.stdout}")
    else:
        print(f"Command execution failed with return code {result.returncode}:\n{result.stderr}")

def download_from_gerrit(repo_url, local_dir):
    git_executable = "D:/Git/cmd/git.exe"  # 使用正斜杠
    # 打印 repo_url 和 local_dir 進行調試
    print(f"Repo URL: {repo_url}")
    print(f"Local Directory: {local_dir}")
    # 確保 local_dir 存在
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    # 增加 Git 的內存緩衝區大小
    execute_git_command(f'"{git_executable}" config --global http.postBuffer 524288000')
    # 進行克隆操作
    command = f'"{git_executable}" clone "{repo_url}" "{local_dir}"'
    execute_git_command(command)

def upload_to_gerrit(local_dir, commit_message):
    git_executable = "D:/Git/cmd/git.exe"  # 使用正斜杠
    commands = [
        f'cd "{local_dir}"',
        f'"{git_executable}" add .',
        f'"{git_executable}" commit -m "{commit_message}"',
        f'"{git_executable}" push origin HEAD:refs/for/master'
    ]
    execute_git_command(" && ".join(commands))

def main():
    gerrit_url = "https://mm2sd.rtkbf.com" # input("Enter Gerrit URL: ")
    username = "sam051808" # input("Enter your username: ")
    password = input("Enter your password: ")
    repo_url = "ssh://sam051808@mm2sd.rtkbf.com:29418/SRE_Dev_Kernel"
    # repo_url = "ssh://mm2sd.rtkbf.com:29418/kernel/linux-kdriver2" # input("Enter the repo URL: ")
    local_dir = "D:/gerrit_test" # input("Enter the local directory to clone the repo into: ")

    # 打印和更新 PATH 環境變數
    # print("Initial PATH:", os.environ["PATH"])
    git_path = "D:/Git/cmd"  # 使用正斜杠
    os.environ["PATH"] += os.pathsep + git_path
    # print("Updated PATH:", os.environ["PATH"])

    if connect_to_gerrit(gerrit_url, username, password):
        download_from_gerrit(repo_url, local_dir)
        # 在本地修改代碼後，使用下面的命令上傳更改
        # commit_message = input("Enter your commit message: ")
        # upload_to_gerrit(local_dir, commit_message)

if __name__ == "__main__":
    main()
