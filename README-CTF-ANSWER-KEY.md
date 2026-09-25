# The Locked Apothecary Cabinet — Answer Key (for you, not your players)

**Flag:** `WICYS{n3v3r_tru5t_4_bl4ckl1st}`
**Category:** File exploitation / Path Traversal
**Difficulty:** Medium

## The vulnerability
`app.py`'s `sanitize_filename()` "defends" against traversal by removing
the literal substring `../` from user input — but it's a single,
non-recursive pass. Python's `str.replace()` scans left to right once
and never re-scans its own output. So an input like `....//` isn't
caught: removing the one `../` match found *inside* `....//` leaves
`../` behind:

```
"....//".replace("../", "")  →  "../"
```

This is a well-known, widely-taught blacklist-bypass technique (it's
one of PortSwigger's Web Security Academy path-traversal labs). Absolute
paths are blocked outright by a separate check, so the intended lesson
is specifically the "the filter only ran once" bug — not just "there's
no filter at all."

## Solve path
1. Visit the site, notice six recipes are loaded via `?name=<filename>`.
2. Try the obvious thing: `?name=../restricted/forbidden_formulae.txt` → blocked (404), because the naive filter strips it clean.
3. Try `?name=/etc/passwd` or similar → blocked (403), absolute paths are rejected outright.
4. Realize the filter only runs once, and craft an input that *becomes* `../` after the filter removes one match: `....//`.
5. Request:
   ```
   /recipe?name=....//restricted/forbidden_formulae.txt
   ```
6. The flag is in the response.

## Files
- `app.py` — the Flask app and the vulnerable sanitizer (fully commented for you; players never see this file)
- `templates/` — index, recipe, and error pages (Jinja2)
- `static/style.css` — the forbidden-magic visual theme (near-black, blood crimson, violet smoke)
- `recipes/` — six flavor-text "recipes," fictional and non-actionable, covering both poisonous flowers and poisonous insects
- `restricted/forbidden_formulae.txt` — the flag file, not served by any legitimate route

## Deploying to Render
This is a real backend, so it needs a **Web Service**, not a Static Site:
1. Push this whole folder to a Git repo (GitHub/GitLab/Bitbucket).
2. Render dashboard → **New → Web Service** → connect the repo.
3. **Runtime**: Python 3.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn app:app`
6. Deploy. Render gives you a URL like `your-app.onrender.com`.
7. Test the full solve path against the *live* URL before handing it to students — confirm step 2 above 404s and step 5 returns the flag.

## If you want to change the flag
Edit the flag line directly in `restricted/forbidden_formulae.txt`.

## If you want to change the difficulty
- **Easier:** add a comment in the HTML (like the herbarium challenge) hinting that the filter "only checks once."
- **Harder:** remove the absolute-path block entirely and require students to find the bypass with no guardrails at all, or add a second, differently-vulnerable endpoint as a red herring.
- **Different bypass entirely:** swap the sanitizer for a different classic mistake — e.g. checking for `../` case-sensitively but the filesystem is case-insensitive, or normalizing the path *before* checking it instead of after (order-of-operations bug).

---

## Challenge story (for your CTF platform)

> **Forbidden Arts: The Locked Apothecary Cabinet**
> *Category: File Exploitation / OSINT · Difficulty: Medium*
>
> Professor Vesper Thorne runs the strictest wing in the Academy. Six
> recipes are cleared for student use — poisons from petal and pincer
> alike, catalogued and locked behind a filename lookup. Everything
> past that is sealed under a notice that reads, in full: *"Filenames
> are checked against a blacklist before they are opened. This has
> never once failed."*
>
> Thorne has said that verbatim to every incoming class for eleven
> years. No one has ever asked her what "checked once" actually means.
>
> Find what's behind the sixth shelf. It'll spell out where to submit.
>
> Flag format: `WICYS{...}`
