# Add versioning
class ResultsVersion:
    VERSION = "1.0.0"
    
    @staticmethod
    def check_compatibility(file_version):
        return file_version == ResultsVersion.VERSION

# Add provenance tracking
class Provenance:
    """Track how results were generated"""
    def __init__(self):
        self.timestamp = datetime.now()
        self.git_hash = self._get_git_hash()
        self.config_hash = None
        self.machine_info = platform.platform()
    
    def _get_git_hash(self):
        try:
            return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
        except:
            return "unknown"
