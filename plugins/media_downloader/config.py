# plugins/media_downloader/config.py

class MediaDownloaderConfig:
    """
    Hii ndio Specification (Sheria) ya plugin ya Media Downloader.
    Kila plugin mpya utakayoiweka mbeleni lazima ifuate muundo huu.
    """
    
    # 1. Kitambulisho Kikuu cha Plugin kwa ajili ya Plugin Manager
    is_plugin = True
    enabled = True
    
    # 2. Metadata za Huduma
    name = "Kichaka Media Downloader"
    slug = "media_downloader"
    version = "1.0.0"
    description = "Service maalum ya kupakua video na audio kutoka mitandao mbalimbali ya kijamii."
    
    # 3. Sheria za Ulinzi na Malipo (Core Gateway Rules)
    requires_auth = True  # Mlinzi wa mlangoni atahakikisha mtu ana API Key halali na Pro Plan
    queue = "heavy_queue"  # Inaiambia Celery irun hii kazi kwenye foleni ya kazi nzito
    
    # 4. Capability Registry (GPT Feature)
    # Hizi ndio data zitakazorudishwa kiotomatiki kule kwenye GET /api/v1/capabilities/
    capabilities = [
        "media.download.video",
        "media.download.audio",
        "media.extract.metadata"
    ]
