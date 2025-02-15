SAMPLE_CASES = [
    {"id": 101, "url": "https://prod-images-static.radiopaedia.org/images/1371188/0a1f5edc85aa58d5780928cb39b08659c1fc4d6d7c7dce2f8db1d63c7c737234_big_gallery.jpeg"},
    {"id": 102, "url": "https://prod-images-static.radiopaedia.org/images/1420387/6f63736ff837ff7c5a736b35aba6ab_big_gallery.jpeg"},
    {"id": 103, "url": "https://prod-images-static.radiopaedia.org/images/8686421/17baee9bfb9018e3d109ec63cb380e_big_gallery.jpeg"}
]

# MODEL CONFIG
LLM_MODEL_WORKFLOW_AGENT = "gemini-2.0-flash"
LLM_MODEL_REPORT_AGENT = "gemini-2.0-flash"


# List of LLMs to test
# gemini-2.0-flash                    Input $0.10   Output $0.40
# gemini-2.0-flash-lite-preview-02-05 Input $0.075  Output $0.30
