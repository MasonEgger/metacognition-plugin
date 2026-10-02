# The Five Stages

The pipeline has five stages.
Each is a skill with its own page here.
Each page says what the stage asks of you, what it produces, how long it takes, and what done looks like.

```text
/metacognition:design      ->  <root>/<slug>/interview-spec.md
/metacognition:interview   ->  <root>/<slug>/archive.md
/metacognition:compile     ->  <root>/<slug>/profile.md
/metacognition:calibrate   ->  <root>/<slug>/calibration/round-NN.md
/metacognition:skillify    ->  a new or augmented skill
```

`<root>` is the extraction root, which is `./extractions` unless you configure another one.
`<slug>` is the lowercase, hyphenated name of the domain.
See [Configuration](../configuration.md) to change the root.

## Rules That Hold for Every Stage

- Every stage begins by resolving your settings and stating the extraction root it will use in one line.
- Every stage ends by naming the files it wrote and the next stage's command, and then stops.
  No stage starts the next one.
- `interview`, `compile`, and `calibrate` default to the only extraction under the root.
  When there are several, they name the candidates and ask you to pick one.
  `design` derives the slug from your domain statement and prints it.
  `skillify` always needs the slug.
- Every stage can be re-run from its own inputs.
  You can recalibrate without re-interviewing, or recompile after the archive changes.

## About Timing

The stages run for as long as the work takes, and the plugin states no fixed durations.
Each page describes the size of the work in terms the plugin itself defines, such as question counts and token sizes.
The interview is the long one.
It can be resumed across sittings.

## The Pages

- [Design](design.md)
- [Interview](interview.md)
- [Compile](compile.md)
- [Calibrate](calibrate.md)
- [Skillify](skillify.md)
