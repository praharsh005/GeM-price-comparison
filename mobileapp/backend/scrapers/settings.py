USER_AGENT = "GeM-Price-Comparison-Project/1.0 (academic project; contact: student@example.com)"
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2.0
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 2
RETRY_TIMES = 2
DOWNLOAD_TIMEOUT = 30
LOG_LEVEL = "INFO"
ITEM_PIPELINES = {
    "scrapers.pipelines.GemPipeline": 300,
}
FEEDS = {}