Synthetic fixtures for the metacognition pipeline tests: never real profiles.

- `woodworking-battery/`: an in-progress archive with open probes, one three-item battery, one evidence entry, an Open research line, and an Exports line. Its frontmatter counts follow the probe rule, so it validates clean.
- `../extractions-bad/battery-item-mismatch/`: a copy of `woodworking-battery/` whose one battery says `[items: 4]` over three items. It yields exactly one `archive-battery-items` finding.
