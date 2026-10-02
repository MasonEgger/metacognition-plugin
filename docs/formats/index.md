# File Formats

Each stage reads and writes plain Markdown files with YAML frontmatter.
These pages are the reference for the four formats.
They say the same thing as the plugin's own reference files, which the stages follow.

Every extraction lives in its own directory, `<root>/<slug>/`:

```text
<root>/<slug>/
  README.md              status table, one row
  interview-spec.md      written by design
  archive.md             written by interview
  profile.md             written by compile, edited by calibrate
  compile-log.md         written by compile
  calibration/
    round-01.md          written by calibrate, one file per round
```

| File | Written by | Page |
|---|---|---|
| `interview-spec.md` | design | [interview-spec.md](interview-spec.md) |
| `archive.md` | interview | [archive.md](archive.md) |
| `profile.md` | compile, then calibrate | [profile.md](profile.md) |
| `calibration/round-NN.md` | calibrate | [Calibration Round Files](calibration-round.md) |

The extraction README status table is described at the end of the [interview-spec.md](interview-spec.md#extraction-readme-status-table) page.

A structure check, `python3 scripts/validate_artifacts.py <root>/<slug>`, runs at the end of interview, compile, and calibrate.
It checks structure only: a missing or empty directory, frontmatter that does not parse, archive question numbering and category counts, the profile token ceiling and estimate, missing or misordered profile sections, incomplete golden examples, and gaps in calibration round numbers.

## The Example Extraction

The plugin's repository carries one synthetic woodworking extraction as a test fixture.
It is not a real profile.
Excerpts on these pages marked as the woodworking fixture come from it unchanged.
