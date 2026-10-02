"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    trace.start_trace()

    # Each pass round the loop runs one step, and the step decides what runs
    # next by looking at what it just produced.
    next_step = "parse"
    count = 0

    while next_step != "done":
        count += 1
        trace.check_iterations(count)

        if next_step == "parse":
            session["parsed"] = parse_query(query)
            trace.step("parse_query", inputs=query, returned=str(session["parsed"]))
            next_step = "search"

        elif next_step == "search":
            parsed = session["parsed"]
            session["search_results"] = search_listings(
                parsed["description"],
                size=parsed["size"],
                max_price=parsed["max_price"],
            )

            # THE BRANCH: nothing matched, so stop here with advice rather
            # than handing suggest_outfit an item that doesn't exist.
            if not session["search_results"]:
                session["error"] = _no_results_message(parsed, query)
                trace.step("search_listings", inputs=str(parsed),
                           returned=session["search_results"],
                           note="branch: empty, stopping before suggest_outfit")
                next_step = "done"
            else:
                trace.step("search_listings", inputs=str(parsed),
                           returned=session["search_results"],
                           note="branch: results found, continuing")
                next_step = "select"

        elif next_step == "select":
            session["selected_item"] = session["search_results"][0]
            trace.step("select_item", inputs="first of search_results",
                       returned=session["selected_item"])
            next_step = "suggest"

        elif next_step == "suggest":
            session["outfit_suggestion"] = suggest_outfit(
                session["selected_item"], session["wardrobe"]
            )
            trace.step("suggest_outfit",
                       inputs=str({"new_item": session["selected_item"]["title"],
                                   "wardrobe_items": len(session["wardrobe"].get("items") or [])}),
                       returned=session["outfit_suggestion"])
            next_step = "fit_card"

        elif next_step == "fit_card":
            session["fit_card"] = create_fit_card(
                session["outfit_suggestion"], session["selected_item"]
            )
            trace.step("create_fit_card",
                       inputs=str({"outfit": session["outfit_suggestion"][:40] + "…",
                                   "new_item": session["selected_item"]["title"]}),
                       returned=session["fit_card"])
            next_step = "done"

    return session


# ── query parsing ─────────────────────────────────────────────────────────────

# "under $30", "below 30", "less than $29.99", "max $40", "up to $25", "$30"
_PRICE_RE = re.compile(
    r"(?:\b(?:under|below|less than|max(?:imum)?|up to|at most)\s*\$?\s*|\$\s*)"
    r"(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# "size M", "size XXS", "size S/M", "size US 9", "size W30"
_SIZE_RE = re.compile(
    r"\bsize\s+((?:us\s+)?[a-z0-9/.]+)",
    re.IGNORECASE,
)

_SIZE_WORDS = {
    "small": "S",
    "medium": "M",
    "large": "L",
    "xs": "XS",
    "extra small": "XS",
    "extra large": "XL",
}

_FILLER_RE = re.compile(
    r"\b(?:i'?m|i am|looking for|searching for|i want|i need|find me|"
    r"show me|can you find|please|something|some|a|an|in)\b",
    re.IGNORECASE,
)


def parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a max_price out of a plain-language query,
    using regex. Anything not found comes back as None, so search_listings
    skips that filter.

        "vintage graphic tee under $30, size M"
        → {"description": "vintage graphic tee", "size": "M", "max_price": 30.0}
    """
    text = query

    max_price = None
    price_match = _PRICE_RE.search(text)
    if price_match:
        max_price = float(price_match.group(1))
        text = text[:price_match.start()] + " " + text[price_match.end():]

    size = None
    size_match = _SIZE_RE.search(text)
    if size_match:
        raw = size_match.group(1).strip()
        size = _SIZE_WORDS.get(raw.lower(), raw.upper())
        text = text[:size_match.start()] + " " + text[size_match.end():]

    text = _FILLER_RE.sub(" ", text)
    description = re.sub(r"[^\w\s'-]", " ", text)
    description = re.sub(r"\s+", " ", description).strip()

    return {"description": description, "size": size, "max_price": max_price}


def _no_results_message(parsed: dict, query: str) -> str:
    """Tell the user what they searched for and which knob to loosen."""
    # Every word of the query was a price, a size, or filler, so the search
    # had no item to look for. Loosening anything wouldn't help — the user
    # needs to say what kind of item they want.
    if not parsed["description"]:
        return (
            f"I couldn't tell what kind of item you want from '{query.strip()}'. "
            "Name the item, like 'denim jacket', 'graphic tee', 'jeans', or "
            "'sneakers' — this shop carries tops, bottoms, outerwear, shoes, "
            "and accessories. You can add a size and a price too, e.g. "
            "'graphic tee size M under $30'."
        )

    searched = f"'{parsed['description']}'"
    if parsed["size"]:
        searched += f" in size {parsed['size']}"
    if parsed["max_price"] is not None:
        searched += f" under ${parsed['max_price']:g}"

    suggestions = []
    if parsed["max_price"] is not None:
        suggestions.append("raise your price limit")
    if parsed["size"]:
        suggestions.append("drop the size filter")
    suggestions.append("try broader keywords (e.g. 'tee' instead of 'vintage band tee')")

    return (
        f"Nothing matched {searched}. To find something, "
        + ", or ".join(suggestions) + "."
    )


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
