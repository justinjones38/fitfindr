# Run log — before-failure

- Produced by: `run_eval.py::main`
- Loop: `agent.py::run_agent` · tools: `tools.py`
- Tries per scenario: 5, caching off
- Temperature: 0.9
- When: 2026-10-07 19:22

Paste the table below into your README. Fill in the Criterion and
Target columns from `criteria.md`, then mark each try PASS or FAIL
from the output underneath and count them for the Verdict.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes |  |   |   |   |   |   |  |
| 2. impossible query stops early |  |   |   |   |   |   |  |
| empty wardrobe _(diagnostic — not one of your five)_ |  |   |   |   |   |   |  |
| 3. selected item reaches the fit card |  |   |   |   |   |   |  |
| 4. fit card has price, platform, 2-4 sentences |  |   |   |   |   |   |  |
| 5. search respects price ceiling |  |   |   |   |   |   |  |
| 5. price ceiling boundary |  |   |   |   |   |   |  |

> The Try and Verdict columns are blank on purpose. Whether a try
> passed depends on the criterion you wrote, so it's yours to decide.
> Count the passes, then read that count against your target: a row
> targeting 4 of 5 with three PASS cells is MISSED (3/5).

---

## What actually happened

Real output, as text. Paste the relevant parts into your README —
the rubric asks for output, not a description of it.

### matching query completes

- Query: `vintage graphic tee under $30`
- Wardrobe: example

**Try 1**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 2**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 3**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 4**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 5**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

### impossible query stops early

- Query: `designer ballgown size XXS under $5`
- Wardrobe: example

**Try 1**

- stopped early: yes — Nothing matched 'designer ballgown' in size XXS under $5. To find something, raise your price limit, or drop the size filter, or try broader keywords (e.g. 'tee' instead of 'vintage band tee').
- selected_item: (none)
- search_results: 0
- search_result prices: []

Trace:

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit
```

**Try 2**

- stopped early: yes — Nothing matched 'designer ballgown' in size XXS under $5. To find something, raise your price limit, or drop the size filter, or try broader keywords (e.g. 'tee' instead of 'vintage band tee').
- selected_item: (none)
- search_results: 0
- search_result prices: []

Trace:

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit
```

**Try 3**

- stopped early: yes — Nothing matched 'designer ballgown' in size XXS under $5. To find something, raise your price limit, or drop the size filter, or try broader keywords (e.g. 'tee' instead of 'vintage band tee').
- selected_item: (none)
- search_results: 0
- search_result prices: []

Trace:

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit
```

**Try 4**

- stopped early: yes — Nothing matched 'designer ballgown' in size XXS under $5. To find something, raise your price limit, or drop the size filter, or try broader keywords (e.g. 'tee' instead of 'vintage band tee').
- selected_item: (none)
- search_results: 0
- search_result prices: []

Trace:

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit
```

**Try 5**

- stopped early: yes — Nothing matched 'designer ballgown' in size XXS under $5. To find something, raise your price limit, or drop the size filter, or try broader keywords (e.g. 'tee' instead of 'vintage band tee').
- selected_item: (none)
- search_results: 0
- search_result prices: []

Trace:

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit
```

### empty wardrobe

- Query: `denim jacket under $50`
- Wardrobe: empty

**Try 1**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 2**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 3**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 4**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 5**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

### selected item reaches the fit card

- Query: `vintage graphic tee under $30`
- Wardrobe: example

**Try 1**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 2**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 3**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 4**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 5**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

### fit card has price, platform, 2-4 sentences

- Query: `denim jacket under $50`
- Wardrobe: example

**Try 1**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 2**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 3**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 4**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 5**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

### search respects price ceiling

- Query: `denim jacket under $50`
- Wardrobe: example

**Try 1**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 2**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 3**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 4**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 5**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

### price ceiling boundary

- Query: `denim jacket under $45`
- Wardrobe: example

**Try 1**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 2**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 3**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 4**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Try 5**

Crashed:

```
ModelUnavailable: The model name 'not-a-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```
