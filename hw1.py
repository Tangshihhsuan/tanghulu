#請先在local下載paramiko : pip install paramiko

import paramiko
import socket
import os
import json
from datetime import datetime


def get_latest_directory(sftp, remote_base_dir):
    dir_list = sftp.listdir_attr(remote_base_dir)
    latest_dir = max(dir_list, key=lambda attr: attr.st_mtime)
    return latest_dir

def find_file_recursively(sftp, directory, target_file):
    for item in sftp.listdir_attr(directory):
        item_path = f"{directory}/{item.filename}"
        if item.st_mode & 0o040000:  # 檢查是否為目錄
            found_path = find_file_recursively(sftp, item_path, target_file)
            if found_path:
                return found_path
        elif item.filename == target_file:
            return item_path
    return None

def sftp_fetch_latest_file(hostname, port, username, password, remote_base_dir, target_file, local_path, json_path):
    try:
        # 建立 SSH 連接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 設置超時時間
        timeout = 10  # 10秒

        ssh.connect(hostname, port, username, password, timeout=timeout)
        print("成功連接到 SFTP 伺服器")
        
        try:
            # 建立 SFTP 會話
            sftp = ssh.open_sftp()
            
            try:
                # 獲取最新的子目錄
                latest_dir_attr = get_latest_directory(sftp, remote_base_dir)
                latest_dir = latest_dir_attr.filename
                latest_dir_path = f"{remote_base_dir}/{latest_dir}"
                
                # 調試輸出以確認目錄和文件
                print(f"最新的子目錄: {latest_dir_path}")

                # 递归搜索目标文件
                target_file_path = find_file_recursively(sftp, latest_dir_path, target_file)
                if target_file_path is None:
                    raise FileNotFoundError(f"在最新子目錄及其子目錄中找不到文件: {target_file}")

                # 檢查本地目錄是否存在
                local_dir = os.path.dirname(local_path)
                if not os.path.exists(local_dir):
                    print(f"本地目錄 {local_dir} 不存在，嘗試創建...")
                    os.makedirs(local_dir)

                # 下載文件
                sftp.get(target_file_path, local_path)
                print(f"成功下載 {target_file_path} 到 {local_path}")

                # 構建文件信息
                file_info = {
                    "file_name": target_file,
                    "upload_time": datetime.fromtimestamp(latest_dir_attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    "download_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # 保存文件信息到 json
                with open(json_path, 'w') as json_file:
                    json.dump(file_info, json_file, indent=4)
                print(f"文件信息保存到 {json_path}")

            except FileNotFoundError as e:
                print(e)

            except PermissionError:
                print(f"沒有權限寫入本地路徑: {local_path}")

            except Exception as e:
                print(f"文件傳輸過程中發生錯誤: {e}")

            finally:
                # 關閉 SFTP 會話
                sftp.close()

        except Exception as e:
            print(f"建立 SFTP 會話過程中發生錯誤: {e}")

        finally:
            # 關閉 SSH 連接
            ssh.close()

    except paramiko.AuthenticationException:
        print("身份驗證失敗，請檢查用戶名或密碼是否正確")

    except paramiko.SSHException as e:
        print(f"無法建立 SSH 連接: {e}")

    except socket.timeout:
        print("連接超時，請檢查伺服器地址和網絡連接")

    except Exception as e:
        print(f"連接過程中發生錯誤: {e}")

if __name__ == "__main__":
    hostname = input("請輸入 SFTP 伺服器地址: ")
    port = int(input("請輸入 SFTP 伺服器端口號 (預設為22): ") or 22)
    username = input("請輸入用戶名: ")
    password = input("請輸入密碼: ")
    remote_base_dir = input("請輸入遠端目錄: ")
    target_file = input("請輸入文件名稱: ")
    local_path = input("請輸入本地保存文件的路徑 (包括文件名): ")
    json_path = input("請輸入本地保存文件信息的 json 文件路徑: ")

    sftp_fetch_latest_file(hostname, port, username, password, remote_base_dir, target_file, local_path, json_path)

