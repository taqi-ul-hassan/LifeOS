

class Multimodal:
    def validate(self, data):
        content = data.get("content", "")
        if len(content) > 5_000_000:
            raise ValueError("Media payload exceeds limit")
        return content

    def transcribe(self, data):
        return {
            "text": self.validate(data),
            "language": data.get("language", "en"),
            "speaker_segments": [],
        }

    def speak(self, data):
        return {
            "text": data["text"],
            "voice": data.get("voice", "default"),
            "format": "audio-interface",
        }

    def image(self, data):
        return {
            "description": data.get("prompt", "Image received for provider analysis."),
            "objects": [],
            "ocr_text": data.get("content", ""),
        }

    def document(self, data):
        text = self.validate(data)
        return {
            "text": text,
            "headings": [line for line in text.splitlines() if line.startswith("#")],
            "tables": [],
            "metadata": {"type": data.get("type", "txt")},
        }

    def video(self, data):
        return {"summary": data.get("content", ""), "frames": [], "subtitles": ""}
