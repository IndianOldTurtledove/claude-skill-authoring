#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Smart Debug Scenario Detection

Design Philosophy:
1. Scoring mechanism - not simple matching, but cumulative score exceeding threshold
2. Frustration signals - profanity, repetition, tone words indicate user frustration
3. Technical signals - error message features (line numbers, file paths, Exception)
4. Context accumulation - track cumulative frustration in session, stricter after multiple failures

Event: UserPromptSubmit
Input: JSON HookInput (stdin)
Output: Debug guidance prompt (stdout) - injected into model context
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

# State file: track cumulative signals in session
STATE_FILE = Path.home() / ".claude" / "debug-detector-state.json"

# ============================================================
# Scoring Weight Configuration
# ============================================================

# Technical signals (explicit error indicators) - high weight
TECH_SIGNALS = {
    # Error types (weight 3)
    r"error": 3,
    r"exception": 3,
    r"traceback": 4,
    r"stack\s*trace": 4,
    r"TypeError|ValueError|KeyError|AttributeError|ImportError": 4,
    r"SyntaxError|NameError|IndexError|RuntimeError": 4,
    r"failed|failure": 3,
    r"crash|crashed": 4,

    # Line number/file path features (weight 4)
    r"line\s+\d+": 4,
    r"\.py:\d+": 5,  # Python file:line
    r"\.ts:\d+|\.js:\d+|\.vue:\d+": 5,  # Frontend files
    r"File\s+[\"'].*[\"'],\s+line": 5,  # Python traceback format

    # HTTP error codes (weight 3)
    r"4\d{2}|5\d{2}": 3,  # 400-599
    r"status\s*:?\s*(4|5)\d{2}": 4,
}

# Problem description words (medium weight)
PROBLEM_SIGNALS = {
    # English
    r"\bbug\b": 3,
    r"\bfix\b": 2,
    r"\bdebug\b": 3,
    r"\bissue\b": 2,
    r"\bbroken\b": 3,
    r"not\s+work": 3,
    r"doesn'?t\s+work": 3,
    r"won'?t\s+work": 3,
    r"can'?t\s+.*work": 3,

    # Chinese problem words
    r"报错": 4,
    r"出错": 3,
    r"错误": 2,
    r"失败": 2,
    r"异常": 3,
    r"崩溃": 4,
    r"挂了|挂掉": 4,
    r"不[工行对]": 2,
    r"没[反响]应": 3,
    r"卡住|卡死": 3,
    r"白屏": 4,
    r"闪退": 4,
}

# Frustration/emotion signals (indicate user is frustrated)
FRUSTRATION_SIGNALS = {
    # Profanity (high weight, indicates severe frustration)
    # Chinese profanity
    r"[草艹操肏]你[妈马麻]|[草艹操肏]nm|cnm": 6,
    r"妈[的逼批]|你[妈马][的逼批]|nmb|nmd": 5,
    r"[傻煞沙][逼批比屄]|sb|2b|二逼|脑残": 5,
    r"卧[槽草艹操]|我[靠艹操草日]|wc|wcnm": 5,
    r"[牛尼泥]玛|nm|尼玛|泥马": 5,
    r"他[妈马]的|tmd|特么|特喵": 5,
    r"[滚艹操日干]|gun|滚蛋|滚犊子": 4,
    r"狗[屎逼日]|gou[br]i|狗东西": 4,
    r"什么鬼|什么玩意|啥玩意": 3,
    r"去你的|去死|见鬼": 4,
    r"智障|弱智|脑子有病|有病吧": 4,
    r"吐了|无语|服了|醉了": 3,
    r"mmp|妈卖批|麻卖批": 5,
    r"wqnmlgb|我去年买了个表": 5,
    r"日了狗|日了个|rng": 4,
    r"坑爹|坑货|坑人": 3,
    # English profanity
    r"fuck|f\*ck|fk|fuk|fcuk": 5,
    r"shit|sh[i1]t|bullshit": 5,
    r"damn|dammit|goddamn": 4,
    r"wtf|wth|what\s+the\s+f": 5,
    r"ffs|for\s+f.+sake": 4,
    r"crap|crappy": 3,
    r"suck|sucks|sucked": 3,
    r"ass|a\*\*|@ss": 3,
    # Symbol expressions of frustration
    r"\?\?\?|？？？": 3,  # Multiple question marks
    r"!!!|！！！": 3,  # Multiple exclamation marks
    r"\.\.\.\.+|。。。。+": 2,  # Many ellipses

    # Repetition signals (indicate multiple failed attempts)
    r"又[出来]|又是": 4,
    r"还是[不没]|依然[不没]|仍然[不没]": 5,
    r"第[二三四五六七八九十\d]+次": 5,
    r"再[试来]一[次下遍]": 4,
    r"怎么又|为啥又|为什么又": 4,
    r"still\s+(not|doesn'?t|won'?t|can'?t)": 4,
    r"again|another\s+time": 3,

    # Question + negation (confusion)
    r"为什么.*不|为啥.*不": 3,
    r"怎么.*不|咋.*不": 3,
    r"明明.*却|明明.*但": 4,
    r"why\s+(is|does|doesn'?t|won'?t|can'?t)": 3,
    r"what'?s\s+wrong": 3,
    r"what\s+the\s+hell": 4,

    # Helplessness/giving up signals
    r"救命|help|救救": 4,
    r"搞不[定懂明]": 4,
    r"没[办法招辙]": 4,
    r"不[知懂]道.*[怎咋]": 3,
    r"give\s+up|放弃": 3,
    r"头疼|头大|崩溃": 3,
}

# Low weight words (won't trigger alone, but cumulative)
LOW_WEIGHT_SIGNALS = {
    r"问题": 1,
    r"看看": 1,
    r"检查": 1,
    r"怎么办": 1,
    r"咋办": 1,
    r"help": 1,
    r"issue": 1,
}

# Trigger thresholds
THRESHOLD_NORMAL = 6      # Normal trigger
THRESHOLD_FRUSTRATED = 4  # Lower threshold if frustration detected

# ============================================================

SYSTEMATIC_DEBUG_PROMPT = """
============================================================
  SYSTEMATIC DEBUGGING MODE ACTIVATED
============================================================

Detected: Bug fix / debugging task (confidence: {confidence})

IRON LAW: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

MANDATORY 4-PHASE PROCESS:

Phase 1 - ROOT CAUSE INVESTIGATION (MUST complete before any fix):
  [ ] Read FULL error message (line numbers, file paths)
  [ ] Reproduce consistently (exact steps)
  [ ] Check recent changes (git diff)
  [ ] Trace data flow backward to source

Phase 2 - PATTERN ANALYSIS:
  [ ] Find similar WORKING code in codebase
  [ ] List ALL differences between working and broken

Phase 3 - HYPOTHESIS & TEST:
  [ ] Form ONE specific hypothesis (write it down)
  [ ] Make SMALLEST possible change to test
  [ ] If fails, form NEW hypothesis (don't stack fixes)

Phase 4 - IMPLEMENTATION:
  [ ] Create failing test first
  [ ] Make ONE targeted fix at root cause
  [ ] Verify fix AND no regression

RED FLAGS (if you catch yourself saying these, STOP):
  - "Let me try..." (without investigation)
  - "Quick fix for now"
  - "One more attempt" (after 2+ failures)

If 3+ fixes fail -> STOP and question the architecture.

============================================================
"""


def load_state() -> dict:
    """Load cumulative state"""
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            # Clean records older than 30 minutes
            cutoff = (datetime.now() - timedelta(minutes=30)).isoformat()
            if data.get("last_update", "") < cutoff:
                return {"cumulative_score": 0, "trigger_count": 0, "last_update": ""}
            return data
        except Exception:
            pass
    return {"cumulative_score": 0, "trigger_count": 0, "last_update": ""}


def save_state(state: dict):
    """Save cumulative state"""
    state["last_update"] = datetime.now().isoformat()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def calculate_score(prompt: str) -> tuple[int, bool, list[str]]:
    """
    Calculate debug scenario score
    Returns: (total_score, has_frustration, matched_signals)
    """
    score = 0
    has_frustration = False
    matched_signals = []

    # Technical signals
    for pattern, weight in TECH_SIGNALS.items():
        if re.search(pattern, prompt, re.IGNORECASE):
            score += weight
            matched_signals.append(f"tech:{pattern[:20]}")

    # Problem description words
    for pattern, weight in PROBLEM_SIGNALS.items():
        if re.search(pattern, prompt, re.IGNORECASE):
            score += weight
            matched_signals.append(f"problem:{pattern[:20]}")

    # Frustration signals
    for pattern, weight in FRUSTRATION_SIGNALS.items():
        if re.search(pattern, prompt, re.IGNORECASE):
            score += weight
            has_frustration = True
            matched_signals.append(f"frustration:{pattern[:20]}")

    # Low weight signals
    for pattern, weight in LOW_WEIGHT_SIGNALS.items():
        if re.search(pattern, prompt, re.IGNORECASE):
            score += weight
            matched_signals.append(f"low:{pattern[:20]}")

    # Additional heuristics
    # 1. Long message (may contain stack trace)
    if len(prompt) > 500:
        score += 2
        matched_signals.append("long_message")

    # 2. Multi-line message (may be error output)
    if prompt.count('\n') > 5:
        score += 2
        matched_signals.append("multiline")

    # 3. Contains code block
    if "```" in prompt or "    " in prompt:
        score += 1
        matched_signals.append("code_block")

    return score, has_frustration, matched_signals


def is_debug_scenario(prompt: str) -> tuple[bool, str]:
    """
    Smart detection of debug scenario
    Returns: (triggered, confidence_description)
    """
    state = load_state()
    score, has_frustration, _signals = calculate_score(prompt)

    # Cumulative effect: if triggered before, lower threshold
    if state["trigger_count"] > 0:
        score += state["trigger_count"] * 2

    # Determine threshold
    threshold = THRESHOLD_FRUSTRATED if has_frustration else THRESHOLD_NORMAL

    # Check if triggered
    triggered = score >= threshold

    if triggered:
        state["trigger_count"] = state.get("trigger_count", 0) + 1
        state["cumulative_score"] = score
        save_state(state)

        # Generate confidence description
        if score >= 15:
            confidence = "VERY HIGH"
        elif score >= 10:
            confidence = "HIGH"
        elif score >= threshold:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return True, confidence

    return False, ""


def main():
    try:
        input_str = sys.stdin.read()
        if not input_str.strip():
            sys.exit(0)

        hook_input = json.loads(input_str)
        prompt = hook_input.get("prompt", "")

        if not prompt:
            sys.exit(0)

        triggered, confidence = is_debug_scenario(prompt)

        if triggered:
            print(SYSTEMATIC_DEBUG_PROMPT.format(confidence=confidence))

    except Exception:
        pass


if __name__ == "__main__":
    main()
