EXTENSION_INFO = {
    # Web Page
    ".html": {"type": "page", "mime": "text/html"},
    # Images
    ".bmp": {"type": "image", "mime": "image/bmp"},
    ".gif": {"type": "image", "mime": "image/gif"},
    ".jpeg": {"type": "image", "mime": "image/jpeg"},
    ".jpg": {"type": "image", "mime": "image/jpeg"},
    ".png": {"type": "image", "mime": "image/png"},
    ".svg": {"type": "image", "mime": "image/svg+xml"},
    ".webp": {"type": "image", "mime": "image/webp"},
    # Documents
    ".doc": {"type": "document", "mime": "application/msword"},
    ".docx": {
        "type": "document",
        "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
    ".odt": {"type": "document", "mime": "application/vnd.oasis.opendocument.text"},
    ".pdf": {"type": "document", "mime": "application/pdf"},
    ".rtf": {"type": "document", "mime": "application/rtf"},
    ".txt": {"type": "document", "mime": "text/plain"},
}

MIME_TO_EXTENSIONS = {}

for extension, info in EXTENSION_INFO.items():
    if info["mime"] in MIME_TO_EXTENSIONS:
        MIME_TO_EXTENSIONS[info["mime"]].append(extension)
    else:
        MIME_TO_EXTENSIONS[info["mime"]] = [extension]
