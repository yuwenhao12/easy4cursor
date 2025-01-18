import os
import json
import uuid
from datetime import datetime
import shutil

"""
    请以管理员身份运行 PowerShell，并执行以下命令：
    python change_machine_id.py
"""

# 配置文件路径，适配 Windows 的路径格式
# storage_file = os.path.expanduser(r"~\AppData\Local\Cursor\User\globalStorage\storage.json")
# win11 专用
storage_file = os.path.expanduser(r"C:\Users\Administrator\AppData\Roaming\Cursor\User\globalStorage\storage.json")

# 生成随机 ID
def generate_random_id():
    return uuid.uuid4().hex

# 获取新的 ID（从命令行参数或自动生成）
def get_new_id():
    import sys
    return sys.argv[1] if len(sys.argv) > 1 else generate_random_id()

# 创建备份
def backup_file(file_path):
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(file_path, backup_path)
        print(f"已创建备份文件: {backup_path}")
    else:
        print("未找到需要备份的文件，跳过备份步骤。")

# 更新或创建 JSON 文件
def update_machine_id(file_path, new_id):
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 如果文件不存在，创建一个空的 JSON 文件
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

    # 读取 JSON 数据
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    # 更新或添加 machineId
    data["telemetry.machineId"] = new_id

    # 写回更新后的 JSON 文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"已成功修改 machineId 为: {new_id}")

# 主函数
def reset_machine_code():
    new_id = get_new_id()
    
    # 创建备份
    backup_file(storage_file)
    
    # 更新 JSON 文件
    update_machine_id(storage_file, new_id)

if __name__ == "__main__":
    reset_machine_code()
