import json
import os
import shutil

class ProjectManager:
    def __init__(self, base_dir="projects", config_path="config.json"):
        self.base_dir = base_dir
        self.config_path = config_path
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def save_config(self, api_data):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=4)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_project_path(self, project_name):
        path = os.path.join(self.base_dir, project_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def list_projects(self):
        if not os.path.exists(self.base_dir):
            return []
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]
        
    def read_file(self, project_name, filename):
        """读取项目目录下的指定文件"""
        path = os.path.join(self.base_dir, project_name, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
        
    def delete_project(self, project_name):
        """删除整个项目文件夹及其中所有内容"""
        path = os.path.join(self.base_dir, project_name)
        if os.path.exists(path):
            shutil.rmtree(path)  # 递归删除目录树
            return True
        return False

    def delete_chapter(self, project_name, chapter_num):
        """单独删除某一个章节的剧本和逻辑文件，保留世界观大纲"""
        script_path = os.path.join(self.base_dir, project_name, f"chapter_{chapter_num}_script.md")
        logic_path = os.path.join(self.base_dir, project_name, f"chapter_{chapter_num}_logic.json")
        
        deleted = False
        if os.path.exists(script_path):
            os.remove(script_path)
            deleted = True
        if os.path.exists(logic_path):
            os.remove(logic_path)
            deleted = True
            
        return deleted