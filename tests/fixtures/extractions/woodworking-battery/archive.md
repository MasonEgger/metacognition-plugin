---
domain: woodworking
registers: [shop]
questions_asked: 6
categories:
  joinery: {asked: 5, floor: 2, saturated: true}
  shop-safety: {asked: 2, floor: 2, saturated: true}
  admired-makers: {asked: 1, floor: 1, saturated: true}
  failure-modes: {asked: 0, floor: 1, saturated: false}
  shop-vocabulary: {asked: 0, floor: 1, saturated: false}
  signature-habits: {asked: 0, floor: 1, saturated: false}
  decision-heuristics: {asked: 0, floor: 1, saturated: false}
status: in-progress
---

# Archive: Woodworking Battery Fixture Profile

*Synthetic fixture for the metacognition pipeline tests. Not a real archive.*

Fixture scope note: this archive exercises the probe-counting rule. Joinery holds an open probe, a three-item battery, and a ladder, so its tally is five probes in three entries.
The remaining categories are open on purpose, so `status` stays `in-progress`.

## Contradiction ledger

- L01 (Q01 vs Q03): "A pocket screw never ships on furniture" vs "Painted is the only place I allow it." Resolution: register-dependent (never on visible stock, allowed under paint).

## Open research

- R01 (Q02): Whether the saw maker's manual calls the riving knife mandatory for narrow rips. Status: resolved in Q05

## Exports

- E01 (Q06): Which film finish holds up on a dining table -> unassigned

## Questions

### Q01 [joinery] [shop] [probe: forced-choice]
**Q:** Here are two identical toolboxes, one mitered and glued, one butt-jointed and pinned. Which one ships to a client, and why?
**A:** The butt-jointed one ships. A miter looks sharp until it sees a shop floor, and a pin holds under racking in a way glue alone will not.

### Q02 [shop-safety] [shop] [probe: critical-incident]
**Q:** Tell me about a specific time a safety shortcut on the table saw nearly cost you something.
**A:** I ripped a narrow strip without the riving knife in, because swapping it back in felt like two minutes I did not have. The offcut kicked back and put a welt across my forearm. I have not run a cut without the riving knife since, full stop. I would want to check what the saw maker says about that before I tell anyone it is mandatory.

### Q03 [joinery] [shop] [probe: battery] [items: 3]
**Q:** For each of these shop-built joints, would you ship it to a client as it is?
1. A half-blind dovetail with a visible gap under 1/32 inch.
2. A pocket-screwed face frame on a painted cabinet.
3. A butt joint reinforced with a dowel on a drawer back.
**A:**
1. Yes. Under a thirty-second I will not touch it.
2. Yes, painted is the only place I allow it.
3. No. A drawer back gets a rabbet or I redo it.

### Q04 [admired-makers] [shop] [probe: artifact]
**Q:** Name a maker whose work you hold up as the standard, and point to one specific piece.
**A:** James Krenov. There is a wall cabinet of his with a door that appears to float off the case, no visible hinge line at all.

### Q05 [shop-safety] [shop] [probe: evidence]
**Q:** Two bottom lines from the trade literature. First, most saw makers list the riving knife as required equipment for through cuts (source: a saw manufacturer's manual, https://example.com/saw-manual). Second, kickback reports concentrate on narrow rips (source: a safety bulletin, https://example.com/bulletin). Does that match your rule?
**A:** It matches. Required for every through cut, and I would say it louder than they do.

### Q06 [joinery] [shop] [probe: ladder]
**Q:** Why oil over a film finish on a dining table?
**A:** Oil repairs in place. Why does that matter? Because a table gets scratched, and a film finish makes every scratch a full refinish. Why not accept the refinish? Because I would rather the client fix a ring with a rag than call me. Which film finish holds up best is a finishing question, so I will leave it to whoever owns that territory.
