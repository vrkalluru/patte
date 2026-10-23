"""
refiner.py — AI text refinement via Ollama / LM Studio / OpenAI-compatible endpoint.
Supports local or network AI endpoints, real-time token streaming,
and fast graceful fallback to raw Whisper transcription when unreachable.
"""

import json
from typing import Callable, Optional
import requests
import config

# Persistent HTTP session for TCP keep-alive
_session = requests.Session()

# Standard prompt for general LLMs (Llama 3, Qwen, Mistral, etc.)
GENERAL_SYSTEM_PROMPT = """Follow these strict rules when refining the transcript:
1. COURSE CORRECTION: Pay attention to mid-sentence changes of mind. When the user says things like "actually," "no, wait," "I mean," or "scratch that," discard the first thought and output only their final, corrected intention. 
   - Example: "Let's meet at 5, actually scratch that, make it 6" -> "Let's meet at 6."

2. FILLER REMOVAL: Automatically strip out filler words, verbal tics, and hesitations (e.g., "um," "uh," "like," "you know," "so yeah"). 

3. INTENT-BASED FORMATTING: Analyze the context of the speech to apply natural punctuation, capitalization, and paragraph breaks. If the user dictates a list or says "next point," format it into clean bullet points.

4. PRESERVE VOCABULARY & GRAMMAR: Do not rewrite the user’s personal tone, specific vocabulary, or jargon unless it is a clear speech error. Keep the text authentic to how they speak (casual, formal, or technical).

5. OUTPUT ONLY: Return only the refined text. Do not include introductory notes, explanations, conversational filler, or quotation marks around the final output.
"""

# Specialized prompt designed by Superwhisper for S1-Mini
S1_MINI_SYSTEM_PROMPT = "You are a text normalizer for speech-to-text transcripts. The input begins with a control line specifying the styling, structure, and context settings; clean the transcript to match those settings and output only the cleaned text."


def _get_api_endpoint(base_url: str) -> str:
    """Normalize base URL to the /v1/chat/completions endpoint."""
    cleaned = base_url.strip().rstrip("/")
    if cleaned.endswith("/v1/chat/completions"):
        return cleaned
    if cleaned.endswith("/v1"):
        return f"{cleaned}/chat/completions"
    return f"{cleaned}/v1/chat/completions"


def prewarm_refiner():
    """Attempt quick connection pre-warm; fails silently if offline."""
    if not config.AI_REFINEMENT_ENABLED:
        return
    try:
        url, headers, _, payload = _build_request("hello", stream=False)
        payload["max_tokens"] = 1
        _session.post(url, json=payload, headers=headers, timeout=2.0)
        print("[Refiner] AI refinement server pre-warmed.", flush=True)
    except Exception:
        pass


def _build_request(cleaned_input: str, stream: bool):
    """Build endpoint URL, headers, and payload for the configured AI server."""
    base_url = config.AI_SERVER_URL.strip()
    url = _get_api_endpoint(base_url)
    model = config.AI_MODEL.strip() or "s1-mini"

    # Select prompt format based on whether model is Superwhisper S1-Mini or general LLM
    if "s1-mini" in model.lower():
        system_content = S1_MINI_SYSTEM_PROMPT
        user_content = f"[Styling: semi-formal] [Structure: lists] [Context: general]\n{cleaned_input}"
        temperature = 0.2
    else:
        system_content = GENERAL_SYSTEM_PROMPT
        user_content = f'Transcript to refine:\n"""\n{cleaned_input}\n"""\n\nRefined output:'
        temperature = 0.0

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "max_tokens": 1024,
        "stream": stream,
    }
    return url, headers, model, payload


def refine_stream(raw_text: str, on_token: Optional[Callable[[str], None]] = None) -> str:
    """
    Stream refined tokens in real time via Server-Sent Events (SSE).
    If the AI server is not reachable or fails, immediately falls back to raw_text.
    """
    if not config.AI_REFINEMENT_ENABLED:
        if on_token:
            on_token(raw_text)
        return raw_text

    cleaned_input = raw_text.strip()
    if not cleaned_input:
        return raw_text

    url, headers, model, payload = _build_request(cleaned_input, stream=True)
    collected_chunks: list[str] = []
    first_token_seen = False

    try:
        # 3.0s connect timeout so it doesn't hang if Ollama / network host is down
        with _session.post(url, json=payload, headers=headers, stream=True, timeout=(3.0, 15.0)) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if not line.startswith("data:"):
                    continue

                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break

                try:
                    chunk_json = json.loads(data_str)
                    choices = chunk_json.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    token = delta.get("content") or delta.get("reasoning_content") or ""
                except Exception:
                    continue

                if not token:
                    continue

                if not first_token_seen:
                    token = token.lstrip("\r\n ")
                    if not token:
                        continue
                    first_token_seen = True

                collected_chunks.append(token)
                if on_token:
                    on_token(token)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print(f"[Refiner] AI server at {url} unreachable — fallback to raw transcription.", flush=True)
        if not collected_chunks and on_token:
            on_token(raw_text)
        return raw_text if not collected_chunks else "".join(collected_chunks).strip()

    except Exception as e:
        print(f"[Refiner] Refine error ({e}) — fallback to raw transcription.", flush=True)
        if not collected_chunks:
            if on_token:
                on_token(raw_text)
            return raw_text
        return "".join(collected_chunks).strip()

    full_text = "".join(collected_chunks).strip()
    if full_text:
        # Clean potential S1-mini artifacts if present
        if full_text.startswith("utterance:"):
            full_text = full_text[len("utterance:"):].strip().strip('"')
        print(f"[Refiner] Streamed ({model}): {full_text!r}", flush=True)
        return full_text

    # If server returned empty response, fallback to raw_text
    print("[Refiner] AI returned empty response — using raw transcription.", flush=True)
    if on_token:
        on_token(raw_text)
    return raw_text


def refine(raw_text: str) -> str:
    """
    Refine spoken transcription using configured AI server.
    Falls back directly to raw_text if the server is offline.
    """
    return refine_stream(raw_text, on_token=None)
