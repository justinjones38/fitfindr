# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->
A user types what clothes that they are looking for. Then FitFindr searches for a set of 2nd hand listing for the best match at the price and size of the user. It then suggests outfits that already fits with the user's wardrobe or gives general styling advice if the wardrobe is empty. If nothing matches, then it stops and recommends changes to the user, such as increasing the price limit or dropping the size


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** - Search the listings data for items that match the description, size and max price
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
  - description (str)
  - size (str)
  - max_prize (float)
- **Returns:** - it returns a list of dictionaries, with the best match first. At most it returns 10, with the limit set by SEARCH_RESULT_LIMIT in config.py
- **When it has nothing:** - it returns an empty list

### `suggest_outfit`

- **What it does:** - Given an item and wadrobe, it suggest couple of outfits
- **Inputs:** 
  - new_item (dict)
  - wardrobe (dict)
- **Returns:** - returns a non-empty string with outfit suggestions
- **When it has nothing:** 
returns general styling advice

### `create_fit_card`

- **What it does:** - write a short caption that someone what post about their find
- **Inputs:**
  - outfit suggestion (string)
  - new_item (listing dict) 
- **Returns:** - 2 to 4 sentence caption
- **When it has nothing:** - return a descriptive message 

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**
If search_listings returns an empty list, put a message in session["error"] that says what was searched and what to loosen (raise the price limit, drop the size, or use broader keywords), then stop, without calling suggest_outfit or create_fit_card. Otherwise, take the first result as selected_item and go on to suggest_outfit, then create_fit_card.


**Where it lives:** `agent.py::run_agent`

**How the query is parsed:**
Regex, in agent.py::parse_query. One pattern finds the price ("under $30", "below 60", "$25") and becomes max_price. Another finds "size X" ("size M", "size US 9", and "size medium" → M) and becomes size. Filler words like "looking for a" are removed, and what's left is the description. Anything not found is None, so the search skips that filter.


**What moves through the session:** <!-- which fields, in what order -->
query → parsed (description, size, max_price) → search_results → branch: empty sets error and stops, otherwise it continues → selected_item (the first result) → outfit_suggestion → fit_card.



---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask new green tea under $30

[1] parse_query
      in:  new green  tee under 30$
      out: {'description': 'new green tee', 'size': None, 'max_price': 30.0}
[2] search_listings
      in:  {'description': 'new green tee', 'size': None, 'max_price': 30.0}
      out: 9 items: Y2K Baby Tee — Butterfly Print, Vintage Polo Shirt — Forest Green, Vintage Band Tee — Faded Grey … +6 more
      →    branch: results found, continuing
[3] select_item
      in:  first of search_results
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  {'new_item': 'Y2K Baby Tee — Butterfly Print', 'wardrobe_items': 10}
      out: Hey babe! Oh, you *totally* need to grab that butterfly baby tee—it's such a gorgeous Y2K dream and looks to b…
[5] create_fit_card
      in:  {'outfit': 'Hey babe! Oh, you *totally* need to grab…', 'new_item': 'Y2K Baby Tee — Butterfly Print'}
      out: Scored this dreamy butterfly baby tee on Depop for just $18 and I am obsessed. I threw it on with my baggy dar…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Hey babe! Oh, you *totally* need to grab that butterfly baby tee—it's such a gorgeous Y2K dream and looks to be in amazing shape! Here are two super cute ways to style it using pieces you already own:

**Look 1: Streetwear Sweetheart**
Pair the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans, dark wash, and finish the fit with chunky white sneakers. Add your black crossbody bag for an effortless, everyday look that balances the fitted top with baggy denim!

**Look 2: Effortless Contrast**
Tuck the Y2K Baby Tee — Butterfly Print into your wide-leg khaki trousers, and lace up your black combat boots to add a little edge to the sweet butterfly print. So chic!

  Fit card: Scored this dreamy butterfly baby tee on Depop for just $18 and I am obsessed. I threw it on with my baggy dark wash jeans and chunky white sneakers for the ultimate effortless streetwear vibe. It fits like a glove and brings all the best Y2K energy to my everyday wardrobe.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```
[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Fadedgrey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on thechest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand':None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under agraphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M','condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a longtee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]
```
$ python -c "from tools import suggest_outfit; ..."

```
Hey friend! Oh, those vintage Levi's 501s are an absolute thrift store holy grail—you *totally* need to grab them! 

Here are two effortless ways to style your new find using pieces you already own:

**Look 1: Effortless & Edgy**
Pair your new Levi's with the **Black cropped zip hoodie** for that cool-girl proportion play. Throw on the **Chunky white sneakers** and finish it all off with your **Black crossbody bag**. 

**Look 2: Cozy Classic**
Tuck the **White ribbed tank top** into the jeans, cinch it with the **Brown leather belt**, and layer the **Oversized grey crewneck sweatshirt** right on top.Step into your **Black combat boots** for the ultimate vintage-meets-streetwearvibe. 

Go snag those jeans!
```
$ python -c "from tools import create_fit_card; ..."

```
Scored these vintage Levi's 501 jeans on depop for just $38 and they fit like an absolute dream. I threw them on with my favorite white sneakers for a classic,effortless streetwear vibe that I'll probably wear three times a week. Nothing beats a good medium wash denim find.
---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* - to help complete the search listing function and the other tool function
- *What came back:* - the corrected functions
- *What I changed:* - I corrected the tool functions

**Moment 2**

- *What I asked for:* - Help with getting the initial project files installed and initial project with Git Bash
- *What came back:* - It gave me the correct commands to set the project with Git Bash
- *What I changed:* - I just used the correct commands with Git Bash to set up the projects

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET | 
| 3. The fit card names the same item as session["selected_item"]: its price and platform match selected_item["price"] and selected_item["platform"]. | 5 of 5  | PASS | PASS | PASS | PASS | PASS | MET |
| 4. The fit card mentions the item's price and platform, and is 2 to 4 sentences long. | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 5. Price ceiling: every item in search_results has price <= max_price. | 5 of 5 | PASS | PASS | PASS | PASS | PASS  | MET |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

File: from run_2026-10-07_1452_before.md
Function: run_eval.py::main
```
**Try 3** 

- stopped early: no
- selected_item: Vintage Band Tee — Faded Grey ($19.0, depop)
- search_results: 10
- search_result prices: [19.0, 24.0, 18.0, 26.0, 20.0, 18.0, 25.0, 12.0, 14.0, 15.0]

Outfit suggestion:

```
Hey friend! That faded vintage band tee is an absolute holy grail find for your wardrobe. It’s got that effortless, broken-in grunge vibe that looks cool with literally everything. 

Here are two ways to style your new treasure:

**Outfit 1: Effortless Streetwear**
Pair the band tee with your *Baggy straight-leg jeans, dark wash*. Add the *Black combat boots* for that edgy, 90s rockstar finish, and sling the *Black crossbody bag* across your chest. 

**Outfit 2: Layered Grunge**
Wear the tee over your *White ribbed tank top* (letting the white peek out the bottom), tucked into the *Wide-leg khaki trousers*. Cinch it with the *Brown leather belt* and finish with *Chunky white sneakers*. 

You're going to wear this piece out!
```

Fit card:

```
Scored this faded grey vintage band tee on Depop for just $19 and it has the absolute best broken-in grunge feel. I threw it on with some baggy dark wash jeans and black combat boots for an effortless 90s rockstar look. It is definitely going to be on heavy rotation in my wardrobe.
```

Trace:

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print … +7 more
      →    branch: results found, continuing
[3] select_item
      in:  first of search_results
      out: Vintage Band Tee — Faded Grey ($19.0, depop)
[4] suggest_outfit
      in:  {'new_item': 'Vintage Band Tee — Faded Grey', 'wardrobe_items': 10}
      out: Hey friend! That faded vintage band tee is an absolute holy grail find for your wardrobe. It’s got that effort…
[5] create_fit_card
      in:  {'outfit': 'Hey friend! That faded vintage band tee …', 'new_item': 'Vintage Band Tee — Faded Grey'}
      out: Scored this faded grey vintage band tee on Depop for just $19 and it has the absolute best broken-in grunge fe…
```
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

No criterion missed in this run.

Criterion 2 and 5 were deterministic. So 5/5 was expected for both. A miss would have been a bug in the code.

Criterion 1 did pass 5/5, but it missed on an earlier run. Try 5 crashed with a 503 error code from the model. There was no model call in generate.py due to the rate limit being exceeded. For this run, there was no 503 error, but I did not fix the problem.

Criterion 3 passed but all 5 tries used the same search queury and selected the same first result. Therefore, it never could have caught the wrong item being passed along. For future tests, I would like to use several different criterion.

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask "vintage under 60" --trace
[1] parse_query
      in:  vintage under 60
      out: {'description': 'vintage', 'size': None, 'max_price': 60.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage', 'size': None, 'max_price': 60.0}
      out: 10 items: Vintage Polo Shirt — Forest Green, Vintage Band Tee — Faded Grey, Oversized Crewneck Sweatshirt — Vintage Navy … +7 more
      →    branch: results found, continuing
[3] select_item
      in:  first of search_results
      out: Vintage Polo Shirt — Forest Green ($18.0, thredUp)
[4] suggest_outfit
      in:  {'new_item': 'Vintage Polo Shirt — Forest Green', 'wardrobe_items': 10}
      out: Hey friend! Oh, you *totally* need to grab that forest green Ralph Lauren polo—it is such a timeless staple an…
[5] create_fit_card
      in:  {'outfit': 'Hey friend! Oh, you *totally* need to gr…', 'new_item': 'Vintage Polo Shirt — Forest Green'}
      out: Scored this vintage Ralph Lauren forest green polo on thredUp for just $18, and I am obsessed with the color. …

  Found:    Vintage Polo Shirt — Forest Green — $18.0 on thredUp

  Outfit:   Hey friend! Oh, you *totally* need to grab that forest green Ralph Lauren polo—it is such a timeless staple and the color is gorgeous. 

Here are two fun ways to style it using pieces you already own:

**Outfit 1: Casual Streetwear Vibe**
Pair the vintage polo shirt with your baggy straight-leg jeans, and cinch them together using the brown leather belt. Slip on your chunky white sneakers, and toss the black crossbody bag over your shoulder for an easy, cool-girl everyday look.

**Outfit 2: Earthy & Relaxed**
Tuck the vintage polo shirt into your wide-leg khaki trousers, accented by the brown leather belt. Finish this classic, preppy outfit with your black combat boots to add a little bit of edge!

  Fit card: Scored this vintage Ralph Lauren forest green polo on thredUp for just $18, and I am obsessed with the color. I tucked it into wide-leg khaki trousers with a leather belt and added black combat boots for a preppy look with a little bit of edge. Such a timeless staple that I'm going to wear on repeat this season!

2 model calls this session, 701 prompt + 236 output tokens
```

**Empty search**

```
$ python app.py ask "..." --trace
[1] parse_query
      in:  ...
      out: {'description': '', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': '', 'size': None, 'max_price': None}
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

  I couldn't tell what kind of item you want from '...'. Name the item, like 'denim jacket', 'graphic tee', 'jeans', or 'sneakers' — this shop carries tops, bottoms, outerwear, shoes, and accessories. You can add a size and a price too, e.g. 'graphic tee size M under $30'.

0 model calls this session
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [X] criteria.md has five numbered criteria, each with a target
       [X] Each criterion has a reason underneath it
       [X] All five unit 3 sections above have real content
       [X] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [X] Planning Loop names the branch rule and agent.py::run_agent
       [X] Sample Run: one full query plus the three per-tool tests, as text
       [X] At least four new commits
       [X] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [X] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [X] Loop Trace, with the MCP call visible in it
       [X] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
