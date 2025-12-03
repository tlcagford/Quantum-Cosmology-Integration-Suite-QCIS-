# Add dependency injection container
class QCISContainer:
    """Dependency injection container"""
    def __init__(self):
        self._services = {}
        
    def register(self, name, service):
        self._services[name] = service
        
    def get(self, name):
        return self._services[name]

# Add plugin system
class PluginSystem:
    """Allow extending QFT models"""
    def __init__(self):
        self._plugins = {}
        
    def register_plugin(self, name, plugin_class):
        self._plugins[name] = plugin_class
