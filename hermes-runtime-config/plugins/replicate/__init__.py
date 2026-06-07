"""Replicate generation plugin for Hermes — best image & video models.

Tools:
  replicate_image — FLUX 1.1 Pro Ultra (default), photorealistic up to 4MP
  replicate_video — Google Veo 3 (default), text-to-video with native audio

Each tool creates a Replicate prediction, polls until it finishes, downloads
the output file to ~/.hermes/replicate_output/ and returns both the URL and the
local path (so the agent can send the media into chat).
"""
from __future__ import annotations
import json, logging, os, time, urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import requests

logger = logging.getLogger(__name__)
API = "https://api.replicate.com/v1"
BEST_IMAGE = "black-forest-labs/flux-1.1-pro-ultra"
BEST_VIDEO = "google/veo-3"
IMG_TIMEOUT = 180
VID_TIMEOUT = 900
POLL = 3

def _err(msg, **x):
    o={"success":False,"provider":"replicate","error":str(msg)}; o.update(x)
    return json.dumps(o, ensure_ascii=False)

def _token() -> str:
    k=str(os.getenv("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_KEY") or "").strip()
    if k: return k
    try:
        envp=(Path(os.getenv("HERMES_HOME")) if os.getenv("HERMES_HOME") else Path.home()/".hermes")/".env"
        for line in envp.read_text(encoding="utf-8").splitlines():
            if line.startswith("REPLICATE_API_TOKEN="):
                return line.split("=",1)[1].strip().strip('"').strip("'")
    except Exception: pass
    return ""

def _check():
    return bool(_token())

def _out_dir() -> Path:
    d=(Path(os.getenv("HERMES_HOME")) if os.getenv("HERMES_HOME") else Path.home()/".hermes")/"replicate_output"
    d.mkdir(parents=True, exist_ok=True); return d

def _download(url: str, kind: str) -> Optional[str]:
    try:
        ext=os.path.splitext(urllib.parse.urlparse(url).path)[1] or (".mp4" if kind=="video" else ".png")
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        fp=_out_dir()/f"replicate_{kind}_{ts}{ext}"
        r=requests.get(url, timeout=120); r.raise_for_status()
        fp.write_bytes(r.content)
        return str(fp)
    except Exception as exc:
        logger.warning("replicate download failed: %s", exc)
        return None

def _run(model: str, inp: Dict[str, Any], timeout: int, kind: str) -> str:
    tok=_token()
    if not tok: return _err("REPLICATE_API_TOKEN not set in ~/.hermes/.env")
    try:
        # create prediction on an official model
        r=requests.post(f"{API}/models/{model}/predictions",
            headers={"Authorization":f"Bearer {tok}","Content-Type":"application/json","Prefer":"wait=60"},
            json={"input":inp}, timeout=90)
        if r.status_code not in (200,201):
            try: detail=r.json().get("detail") or r.text[:300]
            except Exception: detail=r.text[:300]
            return _err(f"create failed (HTTP {r.status_code}): {detail}", model=model)
        pred=r.json()
        get_url=(pred.get("urls") or {}).get("get")
        status=pred.get("status")
        # poll until terminal
        deadline=time.time()+timeout
        while status not in ("succeeded","failed","canceled"):
            if time.time()>deadline:
                return _err(f"timeout after {timeout}s (status={status})", model=model)
            time.sleep(POLL)
            pr=requests.get(get_url, headers={"Authorization":f"Bearer {tok}"}, timeout=30)
            pred=pr.json(); status=pred.get("status")
        if status!="succeeded":
            return _err(f"generation {status}: {str(pred.get('error') or '')[:200]}", model=model)
        out=pred.get("output")
        url = out[0] if isinstance(out,list) and out else (out if isinstance(out,str) else None)
        if not url: return _err("no output returned", model=model)
        local=_download(url, kind)
        metrics=pred.get("metrics") or {}
        return json.dumps({
            "success":True,"provider":"replicate","model":model,"kind":kind,
            "output_url":url,"local_path":local,
            "predict_time_s":round(float(metrics.get("predict_time") or 0),1),
            "_note":f"Generated {kind}. Send the local_path file to the user. Note: Replicate bills per run — check spend at replicate.com/account/billing.",
        }, ensure_ascii=False)
    except requests.ReadTimeout:
        return _err(f"request timed out", model=model)
    except Exception as exc:
        logger.error("replicate run failed: %s", exc, exc_info=True)
        return _err(str(exc), model=model)

# ---- image ----
def _handle_image(args: dict, **kw) -> str:
    prompt=str(args.get("prompt") or "").strip()
    if not prompt: return _err("prompt is required")
    model=str(args.get("model") or "").strip() or BEST_IMAGE
    inp={"prompt":prompt}
    if args.get("aspect_ratio"): inp["aspect_ratio"]=args["aspect_ratio"]
    if args.get("raw"): inp["raw"]=bool(args["raw"])
    inp["output_format"]=args.get("output_format") or "png"
    return _run(model, inp, IMG_TIMEOUT, "image")

IMAGE_SCHEMA={"name":"replicate_image",
    "description":("Generate a top-quality image via Replicate (FLUX 1.1 Pro Ultra by default — "
        "photorealistic, up to 4MP). Returns a downloaded local file path to send to the user. "
        "Use for marketing creatives, banners, visuals."),
    "parameters":{"type":"object","properties":{
        "prompt":{"type":"string","description":"What to generate (English works best)."},
        "aspect_ratio":{"type":"string","description":"e.g. '1:1','16:9','9:16','3:2'. Default 1:1."},
        "output_format":{"type":"string","enum":["png","jpg"],"description":"Default png."},
        "raw":{"type":"boolean","description":"FLUX raw mode — more natural/less processed."},
        "model":{"type":"string","description":"Override model (default black-forest-labs/flux-1.1-pro-ultra)."}},
        "required":["prompt"]}}

# ---- video ----
def _handle_video(args: dict, **kw) -> str:
    prompt=str(args.get("prompt") or "").strip()
    if not prompt: return _err("prompt is required")
    model=str(args.get("model") or "").strip() or BEST_VIDEO
    inp={"prompt":prompt}
    if args.get("negative_prompt"): inp["negative_prompt"]=args["negative_prompt"]
    if args.get("aspect_ratio"): inp["aspect_ratio"]=args["aspect_ratio"]
    return _run(model, inp, VID_TIMEOUT, "video")

VIDEO_SCHEMA={"name":"replicate_video",
    "description":("Generate a top-quality video via Replicate (Google Veo 3 by default — flagship, "
        "WITH native audio). Takes up to several minutes. Returns a downloaded local mp4 path to send "
        "to the user. Use for Reels/Shorts, ads, promo clips."),
    "parameters":{"type":"object","properties":{
        "prompt":{"type":"string","description":"Scene/action description (English works best)."},
        "negative_prompt":{"type":"string","description":"What to avoid."},
        "aspect_ratio":{"type":"string","description":"e.g. '16:9','9:16'."},
        "model":{"type":"string","description":"Override model (default google/veo-3)."}},
        "required":["prompt"]}}

def register(ctx) -> None:
    ctx.register_tool(name="replicate_image", toolset="replicate", schema=IMAGE_SCHEMA,
        handler=_handle_image, check_fn=_check, requires_env=["REPLICATE_API_TOKEN"], emoji="🎨",
        description="Generate best-quality image (FLUX 1.1 Pro Ultra) via Replicate")
    ctx.register_tool(name="replicate_video", toolset="replicate", schema=VIDEO_SCHEMA,
        handler=_handle_video, check_fn=_check, requires_env=["REPLICATE_API_TOKEN"], emoji="🎬",
        description="Generate best-quality video with audio (Google Veo 3) via Replicate")
