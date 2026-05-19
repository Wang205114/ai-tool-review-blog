"""Agent configuration."""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent

SITE = {
    "name": "AI Tool Guide",
    "domain": "knowaitool.com",
    "canonical_base": "https://knowaitool.com",
}

# Existing posts on the site
EXISTING_POSTS = [
    "best-ai-writing-tools.html",
    "chatgpt-vs-claude.html",
    "free-ai-image-generators.html",
    "best-ai-coding-assistants.html",
    "best-ai-image-generators-2026.html",
    "midjourney-vs-dalle-vs-stable-diffusion.html",
    "github-copilot-review-2026.html",
    "best-ai-tools-for-students-2026.html",
    "notion-ai-vs-chatgpt.html",
    "best-free-ai-writing-tools-2026.html",
    "jasper-ai-review-2026.html",
    "best-ai-video-generators-2026.html",
    "claude-ai-review-2026.html",
    "best-ai-seo-tools-2026.html",
    "grammarly-vs-quillbot-vs-prowritingaid.html",
]

EXISTING_TITLES = [
    "Best AI Writing Tools in 2026",
    "ChatGPT vs Claude",
    "Top 10 Free AI Image Generators",
    "Best AI Coding Assistants in 2026",
    "Best AI Image Generators in 2026",
    "Midjourney vs DALL-E vs Stable Diffusion",
    "GitHub Copilot Review 2026",
    "Best AI Tools for Students 2026",
    "Notion AI vs ChatGPT",
    "Best Free AI Writing Tools 2026",
    "Jasper AI Review 2026",
    "Best AI Video Generators 2026",
    "Claude AI Review 2026",
    "Best AI SEO Tools 2026",
    "Grammarly vs QuillBot vs ProWritingAid",
]

CATEGORY_COLORS = {
    "AI Writing": "#2563EB",
    "AI Image": "#7C3AED",
    "AI Coding": "#059669",
    "AI Video": "#DC2626",
    "AI Productivity": "#D97706",
    "AI SEO": "#0891B2",
    "AI Assistants": "#2563EB",
    "AI Music": "#DC2626",
    "AI Marketing": "#D97706",
}

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
