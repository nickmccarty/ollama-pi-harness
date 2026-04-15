"""
email_skill.py — /email standalone skill.

Given a CSV of contacts + slide content and a stated goal, generates a
personalized email draft (JSON) per speaker and saves them to an output directory.

CSV expectations:
  Required : name, affiliation
  Preferred: markdown (pre-converted slide text), summary, topic_keywords
  Optional : content_url (fetched via MarkItDown if markdown is empty), emails

Usage (via agent.py):
    python agent.py "/email geo-week-talks.csv reach out about our geospatial AI platform save to outreach/"
"""

import os
import re
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from inference import chat as _llm_chat

_KEEP_ALIVE = int(os.environ.get("OLLAMA_KEEP_ALIVE", -1))

_EMAIL_SYSTEM = """\
You are a professional outreach specialist. Your job is to write a warm, specific, \
personalized email from a sender to a conference speaker.

Rules:
- Address the speaker by first name.
- Open by thanking them sincerely for their talk — reference the specific title or topic.
- In the second paragraph, connect their work to the sender's context naturally and briefly.
- In the third paragraph, mention the sender's platform or resource with a light touch — \
  frame it as potentially useful to the speaker or their community, not a sales pitch.
- Close warmly with a simple sign-off.
- Use plain professional prose. No bullet points, no em dashes, no formal titles.
- Output ONLY the email body text — no Subject line, no From/To headers.
- End with the sender's name exactly as given in the context.
"""

_EMAIL_PROMPT_TMPL = """\
Sender: {sender_name}{sender_company_line}
Goal: {goal}

Speaker profile:
  Name        : {name}
  Affiliation : {affiliation}
  Topic       : {keywords}
  Summary     : {summary}

Slide content excerpt:
{slide_excerpt}

Write the personalized email body from {sender_name} to {first_name}.
"""

_SUBJECT_SYSTEM = """\
You write concise, specific email subject lines. Output ONLY the subject line text — \
no quotes, no prefix like "Subject:". Keep it under 60 characters.
"""

_SUBJECT_PROMPT_TMPL = """\
Sender company: {sender_company}
Goal: {goal}
Speaker: {name} ({affiliation})
Topic keywords: {keywords}

Write a natural, specific subject line for a thank-you / introduction email \
from the sender to this conference speaker. Do not start with "Re:" or use \
the speaker's full name in the subject.
"""

_SLIDE_CHAR_LIMIT = 600   # chars of slide markdown fed to the model


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_url_markdown(url: str) -> str:
    """Fetch a URL and convert to markdown via MarkItDown. Returns empty string on failure."""
    try:
        from markitdown import MarkItDown
        md = MarkItDown(enable_plugins=False)
        result = md.convert_url(url)
        return (result.text_content or "")[:8000]
    except Exception as e:
        print(f"    [email] markitdown fetch failed for {url}: {e}")
        return ""


def _safe_filename(name: str) -> str:
    """Convert a speaker name to a safe filename."""
    clean = re.sub(r"[^\w\s-]", "", name).strip()
    return re.sub(r"\s+", "_", clean).lower()


def _parse_list_field(val: str) -> list[str]:
    """Parse a stringified Python list or comma-separated string."""
    if not val or val.strip() in ("[]", ""):
        return []
    try:
        parsed = json.loads(val.replace("'", '"'))
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except Exception:
        pass
    return [x.strip() for x in val.strip("[]").split(",") if x.strip()]


def _ollama_chat(model: str, messages: list[dict], num_predict: int = 512) -> tuple[str, int, int]:
    """Returns (text, prompt_tokens, completion_tokens)."""
    resp = _llm_chat(
        model=model,
        messages=messages,
        options={"num_predict": num_predict, "temperature": 0.7},
        keep_alive=_KEEP_ALIVE,
    )
    text = resp["message"]["content"].strip()
    # Strip Qwen3 think blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    in_tok  = resp.get("prompt_eval_count", 0) or 0
    out_tok = resp.get("eval_count", 0) or 0
    return text, in_tok, out_tok


# ---------------------------------------------------------------------------
# Per-draft trace logger
# ---------------------------------------------------------------------------

def _log_draft_trace(
    name, affiliation, to_email, subject, body,
    subject_prompt, body_prompt,
    producer_model, tokens_in, tokens_out, duration_s,
    json_path, goal,
):
    """Append one runs.jsonl entry per email draft so each gets its own dashboard row."""
    from logger import LOG_PATH
    record = {
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "task":           f"Email draft: {name} <{to_email}>",
        "producer_model": producer_model,
        "evaluator_model": None,
        "run_duration_s": duration_s,
        "input_tokens":   tokens_in,
        "output_tokens":  tokens_out,
        "tokens_by_stage": {
            "subject": {"input": 0, "output": 0},
            "body":    {"input": 0, "output": 0},
        },
        "tool_calls": [
            {"name": "subject_prompt", "query": subject_prompt, "result_chars": len(subject)},
            {"name": "body_prompt",    "query": body_prompt,    "result_chars": len(body)},
        ],
        "vision_images": [], "total_search_chars": 0, "quality_floor_hit": False,
        "files_read": [], "code_executions": 0, "injection_stripped": 0, "memory_hits": 0,
        "plan": None, "orchestrated": False, "subtask_count": 0, "synth_forced": False,
        "output_path":  json_path,
        "output_lines": len(body.splitlines()),
        "output_bytes": len(body.encode()),
        "count_check_retry": False,
        "wiggum_rounds": 0, "wiggum_scores": [], "wiggum_dims": [], "wiggum_eval_log": [],
        "final": "PASS",
        "task_type":   "email_draft",
        "email_to":    to_email,
        "email_name":  name,
        "email_affiliation": affiliation,
        "email_subject": subject,
        "email_body":    body,
        "email_goal":    goal,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_email_standalone(
    csv_path: str,
    goal: str,
    output_dir: str,
    producer_model: str,
    sender_name: str = "",
    sender_email: str = "",
    sender_company: str = "",
    platform_url: str = "",
    max_emails: int = 30,
    filter_keyword: str = "",
) -> list[dict]:
    """
    Generate personalized email JSON drafts for speakers in csv_path.

    Returns a list of result dicts:
      {name, affiliation, json_path, subject, body, to_email, generated_at}
    """
    csv_path = Path(csv_path)
    out_dir  = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        print(f"  [email] CSV not found: {csv_path}")
        return []

    # --- Load CSV ---
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"  [email] loaded {len(rows)} rows from {csv_path.name}")

    # Optional keyword filter
    if filter_keyword:
        kw = filter_keyword.lower()
        rows = [r for r in rows if kw in (r.get("topic_keywords", "") + r.get("domain", "") + r.get("summary", "")).lower()]
        print(f"  [email] filtered to {len(rows)} rows matching '{filter_keyword}'")

    rows = rows[:max_emails]
    print(f"  [email] generating {len(rows)} email draft(s) -> {out_dir}/")

    results   = []
    total_in  = 0
    total_out = 0

    for i, row in enumerate(rows, 1):
        name        = row.get("name", "").strip()
        affiliation = row.get("affiliation", "").strip()
        first_name  = name.split()[0] if name else "there"
        keywords    = ", ".join(_parse_list_field(row.get("topic_keywords", ""))) or row.get("domain", "")
        summary     = (row.get("summary", "") or "")[:400]
        emails_raw  = row.get("emails", "") or row.get("emails_regex", "") or ""
        to_email    = ""
        all_emails  = []
        if emails_raw and emails_raw not in ("[]", ""):
            all_emails = [e for e in _parse_list_field(emails_raw) if "@" in e]
        if not all_emails:
            print(f"  [{i}/{len(rows)}] SKIP {name} — no email address found")
            continue
        if len(all_emails) > 1:
            print(f"  [{i}/{len(rows)}] {name} has {len(all_emails)} addresses, using first: {all_emails[0]}")
        to_email = all_emails[0]

        # Slide content — prefer pre-converted markdown, fallback to URL fetch
        slide_md = (row.get("markdown", "") or "").strip()
        if not slide_md and row.get("content_url", "").strip():
            print(f"    [{i}/{len(rows)}] fetching slides for {name}...")
            slide_md = _fetch_url_markdown(row["content_url"])
        slide_excerpt = slide_md[:_SLIDE_CHAR_LIMIT] if slide_md else "(no slide content available)"

        print(f"  [{i}/{len(rows)}] drafting email for {name} ({affiliation})...")
        draft_start = time.monotonic()

        # Build goal string — append platform URL if provided
        goal_full = goal
        if platform_url:
            goal_full = f"{goal} (platform: {platform_url})"

        sender_company_line = f" ({sender_company})" if sender_company else ""

        # --- Generate subject line ---
        subject_prompt = _SUBJECT_PROMPT_TMPL.format(
            goal=goal_full,
            sender_company=sender_company or sender_name,
            name=name,
            affiliation=affiliation,
            keywords=keywords,
        )
        subject, s_in, s_out = _ollama_chat(
            producer_model,
            [
                {"role": "system", "content": _SUBJECT_SYSTEM},
                {"role": "user",   "content": subject_prompt},
            ],
            num_predict=64,
        )
        total_in  += s_in
        total_out += s_out

        # --- Generate email body ---
        body_prompt = _EMAIL_PROMPT_TMPL.format(
            goal=goal_full,
            sender_name=sender_name or "Nick",
            sender_company_line=sender_company_line,
            name=name,
            affiliation=affiliation,
            keywords=keywords,
            summary=summary,
            slide_excerpt=slide_excerpt,
            first_name=first_name,
        )
        body, b_in, b_out = _ollama_chat(
            producer_model,
            [
                {"role": "system", "content": _EMAIL_SYSTEM},
                {"role": "user",   "content": body_prompt},
            ],
            num_predict=512,
        )
        total_in  += b_in
        total_out += b_out

        draft_duration = round(time.monotonic() - draft_start, 1)

        # --- Write per-contact JSON ---
        record = {
            "name":          name,
            "affiliation":   affiliation,
            "to_email":      to_email,
            "sender_name":   sender_name,
            "sender_email":  sender_email,
            "subject":       subject,
            "body":          body,
            "generated_at":  datetime.now(timezone.utc).isoformat(),
        }
        json_filename = f"{_safe_filename(name)}.json"
        json_path     = out_dir / json_filename
        json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        record["json_path"] = str(json_path.resolve())

        # --- Log individual draft trace to runs.jsonl ---
        _log_draft_trace(
            name=name, affiliation=affiliation, to_email=to_email,
            subject=subject, body=body,
            subject_prompt=subject_prompt, body_prompt=body_prompt,
            producer_model=producer_model,
            tokens_in=s_in + b_in, tokens_out=s_out + b_out,
            duration_s=draft_duration,
            json_path=str(json_path.resolve()),
            goal=goal_full,
        )

        results.append(record)
        print(f"    -> {json_path.name}  subject: {subject[:50]}")

    # Write manifest
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  [email] {len(results)} drafts saved to {out_dir}/ (manifest: manifest.json)")
    print(f"  [email] tokens — in: {total_in:,}  out: {total_out:,}  total: {total_in + total_out:,}")
    for r in results:
        r["_tokens_in"]  = total_in
        r["_tokens_out"] = total_out
    return results
