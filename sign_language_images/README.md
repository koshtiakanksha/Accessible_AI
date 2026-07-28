# Adding to the sign vocabulary

`manifest.json` maps a phrase to its image file. To add a new entry:

1. Add the image to this folder.
2. Add a line to `manifest.json`:
   ```json
   {"phrase": "Good morning", "image": "Good morning.png"}
   ```
3. Run `python scripts/validate_sign_vocabulary.py` to check the manifest and
   the image files on disk actually match up (catches typos, missing files,
   and orphaned images nobody's manifest entry points to).

That's the whole mechanism — the app reads `manifest.json` at runtime, so no
code changes are needed to add vocabulary.

## Where the images should come from — please read this before adding any

**Don't hand-draw or improvise a sign from a rough mental picture of what you
think it looks like.** An incorrect handshape isn't a cosmetic bug the way a
typo is — someone could genuinely try to communicate with it and be
misunderstood, which is the opposite of what an accessibility tool is for.

Reasonable sources, in order of preference:

- A fluent signer or a Deaf/ASL community member reviews or provides the
  image.
- A recognized ASL reference (e.g. a university ASL program, a Deaf
  educational organization) — check the license before redistributing their
  image in a public repo; many are copyrighted even when freely viewable.
- Your own photo/illustration, verified against a reliable reference and
  ideally checked by someone who actually signs.

If you're not confident a sign is correct, it's better to leave that phrase
out than to include a guess — the vocabulary being small and accurate is more
useful than it being large and sometimes wrong. (This is also why this
project scaled back its "sign language translation" claims to begin with —
see the main README.)
