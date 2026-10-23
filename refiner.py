"""
refiner.py — AI text refinement via LM Studio (local) or Groq / OpenAI (cloud).
Supports real-time Server-Sent Events (SSE) token streaming (~150ms time-to-first-token)
and Superwhisper S1-Mini specialized speech normalization.
"""

import json
import subprocess
from typing import Callable, Optional
import requests
import config

# Persistent HTTP session for TCP keep-alive and zero handshake overhead
_session = requests.Session()

# Standard prompt for general-purpose LLMs (Groq, OpenAI, Llama)
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


def _start_lm_studio_server():
    """Attempt to start the LM Studio server via CLI if connection failed."""
    print("[Refiner] LM Studio server offline, attempting to start via lms CLI...", flush=True)
    try:
        lms_path = r"C:\Users\vrkal\.lmstudio\bin\lms.exe"
        subprocess.run([lms_path, "server", "start"], capture_output=True, timeout=5)
    except Exception as e:
        print(f"[Refiner] Could not auto-start LM Studio: {e}", flush=True)


def prewarm_refiner():
    """Pre-warm TCP keep-alive connection and S1-Mini system prompt KV cache."""
    if not config.AI_REFINEMENT_ENABLED or config.AI_PROVIDER != "lmstudio":
        return
    try:
        url, headers, _, payload = _build_request("hello", stream=False)
        payload["max_tokens"] = 1
        _session.post(url, json=payload, headers=headers, timeout=5)
        print("[Refiner] S1-Mini KV cache & TCP keep-alive pre-warmed.", flush=True)
    except Exception:
        pass


def _build_request(cleaned_input: str, stream: bool):
    """Build URL, headers, model name, and JSON payload for the configured provider."""
    provider = config.AI_PROVIDER
    headers = {"Content-Type": "application/json"}

    if provider == "groq" and config.GROQ_API_KEY:
        url = "https://api.groq.com/openai/v1/chat/completions"
        model = config.GROQ_MODEL
        headers["Authorization"] = f"Bearer {config.GROQ_API_KEY}"
        system_content = GENERAL_SYSTEM_PROMPT
        user_content = f'Transcript to refine:\n"""\n{cleaned_input}\n"""\n\nRefined output:'
    elif provider == "openai" and config.OPENAI_API_KEY:
        url = "https://api.openai.com/v1/chat/completions"
        model = config.OPENAI_MODEL
        headers["Authorization"] = f"Bearer {config.OPENAI_API_KEY}"
        system_content = GENERAL_SYSTEM_PROMPT
        user_content = f'Transcript to refine:\n"""\n{cleaned_input}\n"""\n\nRefined output:'
    else:
        # Force 127.0.0.1 instead of localhost to avoid Windows 2s IPv6 loopback delay
        base_url = config.LM_STUDIO_URL.replace("localhost", "127.0.0.1")
        url = f"{base_url}/v1/chat/completions"
        model = config.LM_STUDIO_MODEL

        if "s1-mini" in model.lower():
            system_content = S1_MINI_SYSTEM_PROMPT
            user_content = f"[Styling: semi-formal] [Structure: lists] [Context: general]\n{cleaned_input}"
        else:
            system_content = GENERAL_SYSTEM_PROMPT
            user_content = f'Transcript to refine:\n"""\n{cleaned_input}\n"""\n\nRefined output:'

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.0,
        "max_tokens": 1024,
        "stream": stream,
    }
    return url, headers, model, payload


def refine_stream(raw_text: str, on_token: Optional[Callable[[str], None]] = None) -> str:
    """
    Stream refined tokens in real time via Server-Sent Events (SSE).
    Calls `on_token(token_str)` as each token chunk arrives (~150ms TTFT).
    Falls back to raw_text if streaming fails before any tokens are emitted.
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

    for attempt in range(2):
        try:
            with _session.post(url, json=payload, headers=headers, stream=True, timeout=15) as response:
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
                        # Strip leading newline/whitespace that S1-Mini emits on the very first token
                        token = token.lstrip("\r\n ")
                        if not token:
                            continue
                        first_token_seen = True

                    collected_chunks.append(token)
                    if on_token:
                        on_token(token)
            break

        except requests.exceptions.ConnectionError:
            if attempt == 0 and config.AI_PROVIDER == "lmstudio":
                _start_lm_studio_server()
                continue
            print("[Refiner] Connection offline — falling back to raw transcription.", flush=True)
            if not collected_chunks and on_token:
                on_token(raw_text)
            return raw_text

        except Exception as e:
            print(f"[Refiner] Stream error ({e}) — falling back.", flush=True)
            if not collected_chunks:
                if on_token:
                    on_token(raw_text)
                return raw_text
            return "".join(collected_chunks).strip()

    full_text = "".join(collected_chunks).strip()
    if full_text:
        print(f"[Refiner] Streamed ({model}): {full_text!r}", flush=True)
        return full_text

    # If model emitted 0 tokens (e.g., short already-formatted phrase), fallback to raw_text
    print("[Refiner] Stream completed with 0 tokens — using raw transcription.", flush=True)
    if on_token:
        on_token(raw_text)
    return raw_text


def refine(raw_text: str) -> str:
    """
    Refine spoken transcription using LM Studio (S1-Mini/local), Groq, or OpenAI.
    Collects the streamed response and returns the complete refined text.
    """
    return refine_stream(raw_text, on_token=None)
