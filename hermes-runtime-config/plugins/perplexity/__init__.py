"""Perplexity Sonar research plugin for Hermes — self-contained user plugin.

Tool `perplexity_research`: synthesized, CITATION-BACKED answer (sources embedded
into the answer text) + per-call token & USD cost accounting (local ledger).
Slash `/pplx-usage`: spend totals (today / month / all, per model).
"""
from __future__ import annotations
import json, logging, os, time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)
BASE_URL = "https://api.perplexity.ai"
DEFAULT_MODEL = "sonar"
TIMEOUT_SECONDS = 90
RETRIES = 2
DEFAULT_MAX_TOKENS = 1024
SUPPORTED_MODELS = ("sonar","sonar-pro","sonar-reasoning","sonar-reasoning-pro","sonar-deep-research")
RECENCY_FILTERS = ("day","week","month","year")
PRICE_TABLE = {
    "sonar":{"in":1.0,"out":1.0,"request":0.005},
    "sonar-pro":{"in":3.0,"out":15.0,"request":0.006},
    "sonar-reasoning":{"in":1.0,"out":5.0,"request":0.005},
    "sonar-reasoning-pro":{"in":2.0,"out":8.0,"request":0.006},
    "sonar-deep-research":{"in":2.0,"out":8.0,"request":0.005},
}

def _err(message, **extra):
    out = {"success":False,"provider":"perplexity","tool":"perplexity_research","error":str(message)}
    out.update(extra); return json.dumps(out, ensure_ascii=False)

def _ledger_path():
    home = os.getenv("HERMES_HOME")
    return (Path(home) if home else Path.home()/".hermes")/"perplexity_usage.jsonl"

def _ledger_record(model, pt, ct, tt, cost, src):
    try:
        now = datetime.now()
        row = {"ts":now.timestamp(),"date":now.strftime("%Y-%m-%d"),"month":now.strftime("%Y-%m"),
               "model":model,"prompt_tokens":int(pt or 0),"completion_tokens":int(ct or 0),
               "total_tokens":int(tt or 0),"cost_usd":round(float(cost or 0.0),6),"cost_source":src or "estimated"}
        p = _ledger_path(); p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a",encoding="utf-8") as fh: fh.write(json.dumps(row,ensure_ascii=False)+"\n")
    except Exception as exc:
        logger.warning("perplexity ledger write failed: %s", exc)

def _ledger_summarize():
    p = _ledger_path(); rows = []
    if p.exists():
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                line=line.strip()
                if line:
                    try: rows.append(json.loads(line))
                    except Exception: pass
        except Exception: pass
    today=datetime.now().strftime("%Y-%m-%d"); month=datetime.now().strftime("%Y-%m")
    agg={"calls":0,"tokens":0,"cost":0.0,"today_calls":0,"today_cost":0.0,"month_calls":0,"month_cost":0.0,"per_model":{},"any_estimated":False}
    for r in rows:
        c=float(r.get("cost_usd") or 0.0); tk=int(r.get("total_tokens") or 0)
        agg["calls"]+=1; agg["tokens"]+=tk; agg["cost"]+=c
        if r.get("cost_source")!="api": agg["any_estimated"]=True
        if r.get("date")==today: agg["today_calls"]+=1; agg["today_cost"]+=c
        if r.get("month")==month: agg["month_calls"]+=1; agg["month_cost"]+=c
        m=r.get("model") or "?"; pm=agg["per_model"].setdefault(m,{"calls":0,"cost":0.0,"tokens":0})
        pm["calls"]+=1; pm["cost"]+=c; pm["tokens"]+=tk
    return agg

def _ledger_render():
    s=_ledger_summarize()
    if not s["calls"]: return "🔮 Perplexity: трат пока нет (журнал пуст)."
    lines=["🔮 Perplexity — траты (локальный журнал):",
           f"  Сегодня:  ${s['today_cost']:.4f}  ({s['today_calls']} запр.)",
           f"  Месяц:    ${s['month_cost']:.4f}  ({s['month_calls']} запр.)",
           f"  Всего:    ${s['cost']:.4f}  ({s['calls']} запр., {s['tokens']:,} токенов)"]
    for model,pm in sorted(s["per_model"].items(),key=lambda kv:-kv[1]["cost"]):
        lines.append(f"    • {model}: ${pm['cost']:.4f} ({pm['calls']} запр., {pm['tokens']:,} ток.)")
    if s["any_estimated"]: lines.append("  (часть сумм оценочная; точные — где API вернул cost)")
    return "\n".join(lines)

def _extract_cost(usage, model):
    api_cost=usage.get("cost")
    if isinstance(api_cost,dict):
        total=api_cost.get("total_cost")
        if isinstance(total,(int,float)): return {"cost_usd":round(float(total),6),"cost_source":"api"}
    price=PRICE_TABLE.get(model,PRICE_TABLE[DEFAULT_MODEL])
    pt=float(usage.get("prompt_tokens") or 0); ct=float(usage.get("completion_tokens") or 0)
    est=(pt/1e6)*price["in"]+(ct/1e6)*price["out"]+price["request"]
    return {"cost_usd":round(est,6),"cost_source":"estimated"}

def _resolve_key() -> str:
    k = str(os.getenv("PERPLEXITY_API_KEY") or "").strip()
    if k:
        return k
    # Fallback: read ~/.hermes/.env directly (in case the host did not export it).
    try:
        envp = (Path(os.getenv("HERMES_HOME")) if os.getenv("HERMES_HOME") else Path.home()/".hermes")/".env"
        for line in envp.read_text(encoding="utf-8").splitlines():
            if line.startswith("PERPLEXITY_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


def _check_perplexity_available():
    return bool(_resolve_key())

def _perplexity_research(query, model="", recency_filter="", domain_filter=None, max_tokens=DEFAULT_MAX_TOKENS):
    if not query or not query.strip(): return _err("query is required for perplexity_research")
    model=(model or "").strip() or DEFAULT_MODEL
    if model not in SUPPORTED_MODELS: return _err(f"unsupported model {model!r}; choose: {', '.join(SUPPORTED_MODELS)}")
    recency_filter=(recency_filter or "").strip().lower()
    if recency_filter and recency_filter not in RECENCY_FILTERS: return _err(f"recency_filter must be one of {', '.join(RECENCY_FILTERS)}")
    api_key=_resolve_key()
    if not api_key: return _err("PERPLEXITY_API_KEY not set in ~/.hermes/.env")
    payload={"model":model,"messages":[{"role":"user","content":query.strip()}],
             "max_tokens":max(64,int(max_tokens or DEFAULT_MAX_TOKENS)),"temperature":0.2,"return_citations":True}
    if recency_filter: payload["search_recency_filter"]=recency_filter
    domains=[d.strip() for d in (domain_filter or []) if str(d or "").strip()]
    if domains: payload["search_domain_filter"]=domains[:10]
    response=None
    try:
        for attempt in range(RETRIES+1):
            try:
                response=requests.post(f"{BASE_URL}/chat/completions",
                    headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},
                    json=payload, timeout=TIMEOUT_SECONDS)
                response.raise_for_status(); break
            except requests.HTTPError as e:
                status=getattr(getattr(e,"response",None),"status_code",None)
                if status is None or status<500 or attempt>=RETRIES: raise
                time.sleep(min(5.0,1.5*(attempt+1)))
            except (requests.ReadTimeout,requests.ConnectionError):
                if attempt>=RETRIES: raise
                time.sleep(min(5.0,1.5*(attempt+1)))
        if response is None: return _err("perplexity request returned no response")
        data=response.json()
        choices=data.get("choices") or []
        answer=str(((choices[0] or {}).get("message") or {}).get("content") or "").strip() if choices else ""
        citations=[c for c in (data.get("citations") or []) if c]
        search_results=data.get("search_results") or []
        usage=data.get("usage") or {}
        cost=_extract_cost(usage,model)
        usage_out={"prompt_tokens":usage.get("prompt_tokens",0),"completion_tokens":usage.get("completion_tokens",0),
                   "total_tokens":usage.get("total_tokens",0),"search_context_size":usage.get("search_context_size"),
                   "cost_usd":cost["cost_usd"],"cost_source":cost["cost_source"]}
        _ledger_record(model,usage_out["prompt_tokens"],usage_out["completion_tokens"],usage_out["total_tokens"],usage_out["cost_usd"],usage_out["cost_source"])
        ordered=[]; seen=set()
        for r in search_results:
            u=r.get("url")
            if u and u not in seen: seen.add(u); ordered.append((r.get("title") or "",u))
        for u in citations:
            if u and u not in seen: seen.add(u); ordered.append(("",u))
        if ordered:
            src_md="\n".join(f"[{i}] {(t+' — ' if t else '')}{u}" for i,(t,u) in enumerate(ordered,1))
            answer_with_sources=f"{answer}\n\n**Источники:**\n{src_md}"
        else:
            answer_with_sources=f"{answer}\n\n_(источники не вернулись — ответ непроверяемый, перепроверь вручную)_"
        return json.dumps({"success":True,"provider":"perplexity","tool":"perplexity_research","model":model,
            "query":query.strip(),"answer":answer_with_sources,"answer_raw":answer,
            "sources":[{"n":i,"title":t,"url":u} for i,(t,u) in enumerate(ordered,1)],
            "citations":citations,"search_results":search_results,"usage":usage_out,
            "_note":"ALWAYS show: (1) the **Источники** block with links, and (2) a spend line: 🔮 perplexity/<model> · tokens <total_tokens> · $<cost_usd> (<cost_source>)."}, ensure_ascii=False)
    except requests.HTTPError as e:
        resp=getattr(e,"response",None); detail=""
        try: detail=(resp.json() if resp is not None else {}).get("error",{}).get("message","")
        except Exception: detail=str(getattr(resp,"text","") or "")[:300]
        return _err(detail or str(e), error_type=type(e).__name__)
    except requests.ReadTimeout:
        return _err(f"perplexity timed out after {TIMEOUT_SECONDS}s", error_type="ReadTimeout")
    except Exception as e:
        logger.error("perplexity_research failed: %s", e, exc_info=True)
        return _err(str(e), error_type=type(e).__name__)

def _handle_perplexity_research(args, **kw):
    return _perplexity_research(query=args.get("query",""),model=args.get("model",""),
        recency_filter=args.get("recency_filter",""),domain_filter=args.get("domain_filter"),
        max_tokens=int(args.get("max_tokens",DEFAULT_MAX_TOKENS) or DEFAULT_MAX_TOKENS))

PERPLEXITY_RESEARCH_SCHEMA={"name":"perplexity_research",
    "description":("Research a question with Perplexity Sonar and get a synthesized, citation-backed "
        "answer WITH source links. Best for current facts, market/competitor research, trends, "
        "statistics, fact-checking, OSINT. ALWAYS present the returned Источники block. Each call "
        "reports tokens spent and USD cost."),
    "parameters":{"type":"object","properties":{
        "query":{"type":"string","description":"The research question or topic."},
        "model":{"type":"string","enum":list(SUPPORTED_MODELS),
                 "description":"'sonar' (cheap/fast, default), 'sonar-pro' (deeper), 'sonar-reasoning(-pro)', 'sonar-deep-research' (costly)."},
        "recency_filter":{"type":"string","enum":list(RECENCY_FILTERS),"description":"Restrict sources to last day/week/month/year."},
        "domain_filter":{"type":"array","items":{"type":"string"},"description":"Limit search to these domains (max 10)."},
        "max_tokens":{"type":"integer","minimum":64,"maximum":8192,"default":DEFAULT_MAX_TOKENS,"description":"Max answer length."}},
        "required":["query"]}}

def _cmd_pplx_usage(*a, **k): return _ledger_render()

def register(ctx):
    ctx.register_tool(name="perplexity_research", toolset="perplexity", schema=PERPLEXITY_RESEARCH_SCHEMA,
        handler=_handle_perplexity_research, check_fn=_check_perplexity_available,
        requires_env=["PERPLEXITY_API_KEY"], emoji="🔮",
        description="Perplexity Sonar research with citations + token/cost accounting")
    try:
        ctx.register_command("pplx-usage", _cmd_pplx_usage, description="Show Perplexity spend (today / month / all, per model)")
    except Exception as exc:
        logger.warning("could not register /pplx-usage command: %s", exc)
