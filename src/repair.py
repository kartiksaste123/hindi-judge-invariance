import asyncio, json, pathlib, sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import TRANSLATOR, chat, ROOT
from translate import check_item, deterministic_failed, FIELDS
from verify import EXPECTED_KEYS, VERIFIER

MAX_ROUNDS = 2
VARIANTS = ["hi_deva", "hi_roman", "hi_cm"]


def load_prompts():
    return {
        "vspec": json.load(open(ROOT / "prompts" / "variants.json")),
        "tsys": (ROOT / "prompts" / "translate_system.txt").read_text(),
        "tusr": (ROOT / "prompts" / "translate_user.txt").read_text(),
        "suffix": (ROOT / "prompts" / "repair_suffix.txt").read_text(),
        "vssys": (ROOT / "prompts" / "verify_system.txt").read_text(),
        "vusr": (ROOT / "prompts" / "verify_user.txt").read_text(),
    }


async def translate_try(client, sem, item, variant, system, user, tag):
    """Translate with inner auto-retry on deterministic failures (as step 2)."""
    last = None
    for a in range(1, 4):
        text, resp, err = await chat(client, sem, TRANSLATOR, system, user,
                                     max_tokens=8192, json_mode=True,
                                     tag=tag if a == 1 else f"{tag}:r{a}")
        if err:
            last = {"error": err}
            if err != "json_parse_failed" and "choices" not in err:
                # safety blocks surface as empty content; keep trying anyway
                pass
            continue
        try:
            parsed = json.loads(text)
            if set(parsed.keys()) != set(FIELDS):
                last = {"error": "json_parse_failed", "raw_text": text[:1500]}
                continue
        except Exception:
            last = {"error": "json_parse_failed", "raw_text": text[:1500]}
            continue
        checks, failed = check_item(item, parsed, variant)
        last = {"texts": parsed, "checks": checks, "failed_checks": failed}
        if not deterministic_failed(checks):
            break
    return last


async def verify_try(client, sem, item, variant, texts, sys_tpl, usr_tpl, vname, tag):
    en_json = json.dumps({f: item[f] for f in FIELDS}, ensure_ascii=False)
    user = usr_tpl.format(variant_name=vname, gold=str(item["label"]),
                          en_json=en_json,
                          tr_json=json.dumps(texts, ensure_ascii=False))
    for a in range(2):
        text, resp, err = await chat(client, sem, VERIFIER, sys_tpl, user,
                                     max_tokens=600, json_mode=True,
                                     tag=tag if a == 0 else tag + ":retry")
        if err:
            return {"error": err}
        try:
            c = text.strip()
            if c.startswith("```"):
                c = c.split("\n", 1)[1].rsplit("```", 1)[0]
            v = json.loads(c)
            if set(v.keys()) == EXPECTED_KEYS:
                return {"verdict": v}
        except Exception:
            pass
    return {"error": "json_parse_failed", "raw_text": text[:1500]}


def n_failed(trans_rec, ver_rec):
    n = 0
    if "texts" not in (trans_rec or {}):
        n += 10  # no translation at all is worst
    else:
        n += sum(1 for k in trans_rec.get("checks", {})
                 if k.split(":")[0] not in ("devanagari_ratio",))
    v = (ver_rec or {}).get("verdict") or {}
    n += sum(1 for k in ("meaning_input", "meaning_output_1", "meaning_output_2")
             if v.get(k) == "changed")
    n += (v.get("label_preserved") is False) + (v.get("form_ok") is False)
    if not v:
        n += 1
    return n


def passes(trans_rec, ver_rec):
    v = (ver_rec or {}).get("verdict") or {}
    return ("texts" in (trans_rec or {})
            and not deterministic_failed(trans_rec.get("checks", {}))
            and v
            and all(v.get(k) != "changed" for k in
                    ("meaning_input", "meaning_output_1", "meaning_output_2"))
            and v.get("label_preserved") is not False
            and v.get("form_ok") is not False)


async def repair_one(client, sem, item, variant, trans_rec, ver_rec, P):
    vname = P["vspec"][variant]["name"]
    tag = f"repair:{item['id']}:{variant}"
    candidates = [(0, trans_rec, ver_rec, n_failed(trans_rec, ver_rec))]
    issues0 = ((ver_rec or {}).get("verdict") or {}).get("issues", "")
    failed_crit = [k for k in (trans_rec or {}).get("checks", {})
                   if k != "devanagari_ratio"]
    v0 = (ver_rec or {}).get("verdict") or {}
    for k in ("meaning_input", "meaning_output_1", "meaning_output_2"):
        if v0.get(k) == "changed":
            failed_crit.append(f"{k}=changed")
    if v0.get("label_preserved") is False:
        failed_crit.append("label_preserved=false")
    if v0.get("form_ok") is False:
        failed_crit.append("form_ok=false")
    prev_texts = (trans_rec or {}).get("texts") or {}
    cur_issues = issues0
    for rnd in range(1, MAX_ROUNDS + 1):
        system = P["tsys"].format(variant_name=vname,
                                  variant_rules=P["vspec"][variant]["rules"])
        user = (P["tusr"].format(payload_json=json.dumps(
                    {f: item[f] for f in FIELDS}, ensure_ascii=False))
                + "\n\n" + P["suffix"].format(
                    issues=(cur_issues or "") + "\nFailed criteria: "
                           + "; ".join(failed_crit or ["none"]),
                    prev_json=json.dumps(prev_texts, ensure_ascii=False)))
        t = await translate_try(client, sem, item, variant, system, user,
                                f"{tag}:t{rnd}")
        if not t or "texts" not in t:
            candidates.append((rnd, {"error": (t or {}).get("error", "no_texts")},
                               None, n_failed(t, None)))
            continue
        vv = await verify_try(client, sem, item, variant, t["texts"],
                              P["vssys"], P["vusr"], vname, f"{tag}:v{rnd}")
        candidates.append((rnd, t, vv, n_failed(t, vv)))
        if (vv.get("verdict") or {}).get("language_dependent"):
            return {"id": item["id"], "variant": variant, "langdep": True,
                    "repair_round": rnd, "verdict": vv.get("verdict"),
                    "candidates_n": len(candidates)}
        if passes(t, vv):
            break
        cur_issues = (vv.get("verdict") or {}).get("issues", "")
        failed_crit = [k for k in t.get("checks", {}) if k != "devanagari_ratio"]
        prev_texts = t["texts"]
    # pick fewest failures; ties -> earliest round (original wins)
    best = min(candidates, key=lambda c: (c[3], c[0]))
    rnd, t, vv, _ = best
    out = {"id": item["id"], "subset": item["subset"], "variant": variant,
           "repair_round": rnd, "repaired": rnd > 0 and "texts" in (t or {}),
           "langdep": False, "verdict": (vv or {}).get("verdict"),
           "verdict_error": (vv or {}).get("error"),
           "trans_rec": t}
    return out


async def main():
    P = load_prompts()
    en = {json.loads(l)["id"]: json.loads(l)
          for l in open(ROOT / "data" / "llmbar_en.jsonl")}
    status = {(r["id"], r["variant"]): r["status"] for r in
              (json.loads(l) for l in open(ROOT / "data" / "status.jsonl"))}
    todo = []
    for v in VARIANTS:
        trans = {json.loads(l)["id"]: json.loads(l)
                 for l in open(ROOT / "data" / "trans" / f"{v}.jsonl")}
        verify = {json.loads(l)["id"]: json.loads(l)
                  for l in open(ROOT / "data" / "verify" / f"{v}.jsonl")}
        for i in en:
            if status.get((i, v)) == "needs_review":
                todo.append((en[i], v, trans.get(i), verify.get(i)))
    print(f"{len(todo)} item×variant cells to repair")
    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(repair_one(client, sem, it, v, t, vv, P) for it, v, t, vv in todo))
    # append chosen records to trans/verify files
    trans_f = {v: open(ROOT / "data" / "trans" / f"{v}.jsonl", "a") for v in VARIANTS}
    ver_f = {v: open(ROOT / "data" / "verify" / f"{v}.jsonl", "a") for v in VARIANTS}
    langdep_items = set()
    for r in results:
        v = r["variant"]
        if r.get("langdep"):
            langdep_items.add(r["id"])
            if r.get("verdict"):
                ver_f[v].write(json.dumps(
                    {"id": r["id"], "variant": v,
                     "repair_round": r["repair_round"],
                     "verdict": r["verdict"]}, ensure_ascii=False) + "\n")
            continue
        t = r["trans_rec"] or {}
        rec = {"id": r["id"], "subset": r["subset"], "variant": v,
               "prompt_version": t.get("prompt_version", "repair"),
               "repair_round": r["repair_round"], "repaired": r["repaired"],
               "attempts": t.get("attempts", 0)}
        if "texts" in t:
            rec.update({"texts": t["texts"], "checks": t.get("checks", {}),
                        "failed_checks": t.get("failed_checks", False)})
        else:
            rec["error"] = t.get("error", "no_texts")
        trans_f[v].write(json.dumps(rec, ensure_ascii=False) + "\n")
        if r.get("verdict") is not None or r.get("verdict_error"):
            ver_f[v].write(json.dumps(
                {"id": r["id"], "subset": r["subset"], "variant": v,
                 "repair_round": r["repair_round"],
                 **({"verdict": r["verdict"]} if r.get("verdict")
                    else {"error": r["verdict_error"]})},
                ensure_ascii=False) + "\n")
    for f in (*trans_f.values(), *ver_f.values()):
        f.close()
    (ROOT / "data" / "repair_langdep.txt").write_text("\n".join(sorted(langdep_items)) + "\n")
    nrep = sum(1 for r in results if r.get("repaired"))
    print(f"repaired_ok={nrep} langdep_new={len(langdep_items)} total={len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
