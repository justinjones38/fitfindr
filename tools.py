"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    words = _keywords(description)
    results = []

    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and not _size_matches(size, listing["size"]):
            continue

        score = _score(words, listing)
        if score > 0:
            results.append((score, listing))

    # Highest score first; ties go to the cheaper item.
    results.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return [listing for _, listing in results[:config.SEARCH_RESULT_LIMIT]]


# ── search_listings helpers ───────────────────────────────────────────────────

_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "with", "in", "of", "to", "on",
    "some", "something", "looking", "want", "need", "find", "me", "my", "i",
}


def _normalize(word: str) -> str:
    """Lowercase and drop a plural 's', so "tees" matches "tee"."""
    word = word.lower()
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return word


def _keywords(text: str) -> set[str]:
    """The words in `text` worth matching on — no stopwords, no plurals."""
    return {
        _normalize(w) for w in re.findall(r"[a-z0-9]+", text.lower())
        if w not in _STOPWORDS
    }


def _score(words: set[str], listing: dict) -> int:
    """
    Keyword overlap, weighted by where the word was found. A query word in the
    title counts 3, in the category or style tags 2, and anywhere else
    (description, colors, brand) 1. Each query word counts once, at its best
    weight. `brand` is often None, so it's skipped when missing.
    """
    fields = [
        (3, listing["title"]),
        (2, " ".join([listing["category"], *listing["style_tags"]])),
        (1, " ".join([listing["description"], *listing["colors"],
                      listing["brand"] or ""])),
    ]
    field_words = [(weight, _keywords(text)) for weight, text in fields]

    score = 0
    for word in words:
        score += max((w for w, found in field_words if word in found), default=0)
    return score


def _size_tokens(size: str) -> set[str]:
    """
    Split a size string into the sizes it actually covers.

        "S/M"                 → {"S", "M"}
        "XL (fits oversized)" → {"XL"}
        "W30 L30"             → {"W30", "L30"}
        "US 8.5"              → {"US 8.5"}
        "One Size / Oversized"→ {"ONE SIZE"}
    """
    size = re.sub(r"\(.*?\)", "", size).upper().strip()
    if size.startswith("ONE SIZE"):
        return {"ONE SIZE"}
    if size.startswith("US "):
        return {"US " + size[3:].strip()}
    return {part for part in re.split(r"[/\s]+", size) if part}


def _size_matches(wanted: str, listing_size: str) -> bool:
    """
    A size matches when it is one of the sizes the listing covers — a whole
    token, never a substring, so "S" doesn't match "US 9" and "L" doesn't
    match "XL". "M" matches "S/M" and "M/L". A bare number like "9" matches
    "US 9". One Size listings match any requested size, because they fit
    anyone.
    """
    wanted = wanted.upper().strip()
    if re.fullmatch(r"\d+(\.\d+)?", wanted):
        wanted = "US " + wanted

    tokens = _size_tokens(listing_size)
    return "ONE SIZE" in tokens or bool(_size_tokens(wanted) & tokens)


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []
    item_text = _describe_item(new_item)

    if not items:
        prompt = (
            f"Someone is thinking about buying this thrifted item:\n{item_text}\n\n"
            "They haven't told us what's in their wardrobe yet. Suggest one or "
            "two outfits built around this item, naming the kinds of pieces "
            "that would pair well with it (e.g. 'straight-leg dark jeans', "
            "'chunky white sneakers'). Don't pretend they already own anything. "
            "Keep it under 120 words."
        )
    else:
        wardrobe_text = "\n".join(_describe_wardrobe_item(i) for i in items)
        prompt = (
            f"Someone is thinking about buying this thrifted item:\n{item_text}\n\n"
            f"Here is what they already own:\n{wardrobe_text}\n\n"
            "Suggest one or two outfits that pair the new item with pieces "
            "from their wardrobe. Name the wardrobe pieces exactly as listed, "
            "and only use pieces from that list. Keep it under 120 words."
        )

    response = generate(
        prompt,
        system="You are a friendly personal stylist who specializes in thrifted fashion.",
    ).strip()

    if response:
        return response

    # The model came back blank — still give the user something to go on.
    return (
        f"Try the {new_item.get('title', 'item')} with simple basics in "
        f"neutral colors, and let it be the statement piece of the outfit."
    )


def _describe_item(item: dict) -> str:
    """One listing as a few readable lines for a prompt. Brand is often None."""
    lines = [
        f"- {item.get('title')}",
        f"- category: {item.get('category')}",
        f"- colors: {', '.join(item.get('colors') or [])}",
        f"- style: {', '.join(item.get('style_tags') or [])}",
        f"- condition: {item.get('condition')}",
    ]
    if item.get("brand"):
        lines.append(f"- brand: {item['brand']}")
    return "\n".join(lines)


def _describe_wardrobe_item(item: dict) -> str:
    """One wardrobe piece as a single prompt line. Notes are often None."""
    details = [
        item.get("category"),
        ", ".join(item.get("colors") or []),
        ", ".join(item.get("style_tags") or []),
        item.get("notes"),
    ]
    return f"- {item.get('name')} ({'; '.join(d for d in details if d)})"


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return (
            "Couldn't write a fit card: no outfit suggestion was provided for "
            f"{new_item.get('title', 'this item')}. Run suggest_outfit first "
            "and pass its result in."
        )

    price = new_item.get("price")
    price_text = f"${price:g}" if isinstance(price, (int, float)) else "an unknown price"
    platform = new_item.get("platform") or "a thrift app"

    prompt = (
        f"Write a caption for a social media post about this thrift find:\n"
        f"{_describe_item(new_item)}\n"
        f"- price: {price_text}\n"
        f"- found on: {platform}\n\n"
        f"Here is how it's being styled:\n{outfit.strip()}\n\n"
        "Rules:\n"
        "- 2 to 4 sentences, written in first person like a real post, "
        "not a product description.\n"
        f"- Mention the item, the price ({price_text}) and the platform "
        f"({platform}) once each.\n"
        "- Be specific about the vibe of the outfit — pick one look from the "
        "styling above rather than listing everything.\n"
        "- No hashtags, no bullet points, no quotation marks around the caption.\n"
        "Return only the caption."
    )

    return generate(
        prompt,
        system="You write short, natural captions for people's thrifted outfit posts.",
    ).strip().strip('"')
