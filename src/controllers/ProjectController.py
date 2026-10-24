from helpers.config import get_settings , Settings
from .BaseController import BaseController
import os 

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def project_path(self, project_id : str): #retrive project id from datarouter upload endpoint (project_dir_path =ProjectController().project_path(project_id = project_id))
        project_dir = os.path.join(self.files_dir,project_id)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
