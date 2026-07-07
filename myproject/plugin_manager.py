import os
import importlib
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view

class PluginManager:
    def __init__(self):
        # Inatafuta folda la 'plugins' lililopo nje ya main_project
        self.plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
        self.registry = {}
        self.capabilities = []

    def discover_plugins(self):
        """Inatafuta na kusajili ma-plugin yote yaliyopo kwenye folda la plugins/"""
        if not os.path.exists(self.plugins_dir):
            print("⚠️ Onyo: Folda la 'plugins/' halijapatikana!")
            return

        for folder in os.listdir(self.plugins_dir):
            folder_path = os.path.join(self.plugins_dir, folder)
            
            # Hakikisha ni folda halisi na lina faili la config.py ndani yake
            if os.path.isdir(folder_path) and 'config.py' in os.listdir(folder_path):
                self._register_plugin(folder)

    def _register_plugin(self, plugin_slug):
        """Inasoma faili la config.py la kila plugin na kuliingiza kwenye mfumo"""
        try:
            # Dynamic import ya faili la config la plugin husika
            config_module = importlib.import_module(f"plugins.{plugin_slug}.config")
            
            # Kutafuta Class ya config iliyopo ndani ya faili (Mfano: MediaDownloaderConfig)
            for attr_name in dir(config_module):
                attr = getattr(config_module, attr_name)
                # Tunakagua kama hii class inafuata sheria yetu kuu (Platform Spec)
                if isinstance(attr, type) and hasattr(attr, 'is_plugin') and attr.is_plugin:
                    config = attr()
                    
                    if config.enabled:
                        self.registry[plugin_slug] = config
                        # Kujaza Capability Registry kiotomatiki kwa ajili ya watumiaji wetu
                        self.capabilities.extend(config.capabilities)
                        print(f"🔌 KICHAKA PLATFORM: '{config.name}' v{config.version} imewashwa!")
        except Exception as e:
            print(f"❌ Hitilafu wakati wa kusajili plugin '{plugin_slug}': {e}")

    def get_plugin_urls(self):
        """Inachukua urls.py ya kila plugin na kutengenezea njia kiotomatiki"""
        url_patterns = []
        for slug, config in self.registry.items():
            try:
                # Sasa tunasoma faili la urls.py moja kwa moja kwenye folda la plugin
                urls_module_path = f"plugins.{slug}.urls"
                url_patterns.append(path(f"services/{slug}/", include(urls_module_path)))
            except Exception as e:
                print(f"⚠️ Plugin '{slug}' haina au imefeli kupakia 'urls.py': {e}")
        return url_patterns


# Kuanzisha instance moja kuu ya Plugin Manager (Singleton Pattern)
plugin_manager = PluginManager()
plugin_manager.discover_plugins()
