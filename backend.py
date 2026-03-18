import PyPDF2
import docx
import json
import re
import ast
import os
from textwrap import dedent
import requests


# ──────────────────────────────────────────────
# FILE READERS
# ──────────────────────────────────────────────

def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def read_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def load_file(path):
    if path.endswith(".pdf"):
        return read_pdf(path)
    elif path.endswith(".docx"):
        return read_docx(path)
    else:
        raise ValueError("Unsupported file format")


# ──────────────────────────────────────────────
# TEXT CLEANER
# ──────────────────────────────────────────────

def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


# ──────────────────────────────────────────────
# PROMPT BUILDER
# ──────────────────────────────────────────────

def get_prompt_for_jd_resume_matching(jd_text, resume_text):

    system_prompt = """
You are a strict AI recruitment screener.

Your job is to decide whether a candidate should be shortlisted.

RULES:
- No assumptions. Use only given data.
- Missing skill = not present.
- Be strict. Prefer rejection over weak selection.
- Ignore buzzwords and fluff.

SCORING:
- PASS only if strong match
- FAIL if any major requirement is missing

OUTPUT (STRICT JSON ONLY):
{
  "decision": "PASS or FAIL",
  "match_score": <0-100>,
  "strengths": [],
  "gaps": [],
  "summary": ""
}
"""

    user_prompt = f"""
JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

TASK:
1. Identify core requirements from JD
2. Compare with Resume
3. Check for strong matches and critical gaps
4. Assign score
5. Give final decision

IMPORTANT:
- Be strict
- Do not inflate score
- Highlight only most important points (max 3-5 per list)
"""

    return system_prompt, user_prompt

# ──────────────────────────────────────────────
# AI MODEL CALL
# ──────────────────────────────────────────────

import os
from textwrap import dedent
from fastapi import HTTPException
from fastapi import HTTPException
import streamlit as st
from dotenv import load_dotenv
import requests

load_dotenv()

HF_API_KEY = st.secrets.get("HF_API_KEY") or os.getenv("HF_API_KEY")

MODEL = "Qwen/Qwen2.5-72B-Instruct"
API_URL = f"https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}


def narrate(system_prompt, user_prompt):
    try:
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": dedent(system_prompt).strip()},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 1024
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            raise Exception(response.text)

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI model error: {str(e)}")


# ──────────────────────────────────────────────
# JSON PARSER
# ──────────────────────────────────────────────

def safe_parse(response: str):
    try:
        cleaned = response.strip()
        cleaned = re.sub(r'^```json\s*', '', cleaned)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)

        try:
            return json.loads(cleaned)
        except Exception:
            pass

        try:
            return ast.literal_eval(cleaned)
        except Exception:
            pass

        cleaned_fixed = cleaned.replace('\n', ' ')
        return json.loads(cleaned_fixed)

    except Exception as e:
        raise ValueError(f"Parsing failed: {e}")


def is_valid_json(data):
    if isinstance(data, dict):
        return True
    if isinstance(data, str):
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False
    return False


# ──────────────────────────────────────────────
# MAIN PIPELINE
# ──────────────────────────────────────────────

def run_matching(jd_file_path, resume_file_path):
    jd_text = load_file(jd_file_path)
    resume_text = load_file(resume_file_path)

    jd_text_clean = clean_text(jd_text)
    resume_text_clean = clean_text(resume_text)

    system_prompt, user_prompt = get_prompt_for_jd_resume_matching(
        jd_text_clean, resume_text_clean
    )

    raw_result = narrate(system_prompt, user_prompt)
    parsed = safe_parse(raw_result)

    if not is_valid_json(parsed):
        raise ValueError("Model returned invalid JSON structure.")

    return parsed