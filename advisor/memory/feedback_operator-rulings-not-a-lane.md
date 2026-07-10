---
name: operator-rulings-not-a-lane
description: An operator ruling that spans the collapse is general/shared scope, NOT slut-lane or hag-lane — don't attribute Georges's cross-cutting decisions to whichever lane the session is in
metadata:
  type: feedback
---

When Georges rules a question that spans the radical collapse (membership, DB-collapse sequencing, artist axis, cross-lane forks like #150 --mix/--listen), that decision is **operator/general scope**, NOT a lane authoring its own call.

**Why:** On 2026-07-10 I filed his B-in-order ruling on #150 as `--from slut` and he corrected me twice — "it's not slut lane, it's general." slut = identity/music_v4.db writer; hag = MIR/brain; **shared = the spine + operator rulings.** A cross-cutting operator decision belongs to shared/general, not to whichever repo the Cowork/Code session happens to be sitting in.

**Tooling trap:** `handoff-append` only accepts `--from {hag,slut}` — there is NO operator/general value, so the tool structurally forces operator rulings to be misattributed to a lane. When it happens: file the ruling, then immediately file a provenance-correction note (`--re <n>`, kind note) stating it's operator/general and that from=<lane> is a tooling limitation. Better fix: add an `operator`/`general` value to `--from` in `shared/bin/handoff-append` (Code-session change). Filed as spine #163 (2026-07-10).

**How to apply:** Before stamping `--from`, ask whether the decision is the *lane's* call or the *operator's* call across lanes. Lane call → that lane. Operator ruling spanning the collapse → general; note the tooling gap explicitly so provenance stays honest. See [[move-dont-menu]], [[radical-collapse-and-hazards]].
