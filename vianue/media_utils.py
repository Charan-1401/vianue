from pathlib import Path


VIDEO_EXTENSIONS = {
    ".avi",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".webm",
}


def uploaded_file_is_video(uploaded_file):
    content_type = getattr(uploaded_file, "content_type", "") or ""
    if content_type.startswith("video/"):
        return True

    extension = Path(getattr(uploaded_file, "name", "")).suffix.lower()
    return extension in VIDEO_EXTENSIONS
