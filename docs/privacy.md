# Privacy

The plugin is a framework.
The files you produce with it are yours, and three facts about them are worth knowing before you store or share anything.

## Archives Hold Your Answers Verbatim

`archive.md` records every question and every answer in your own words.
Hedges, false starts, and mid-answer corrections stay in.
The only change is that dash and curly-quote characters are straightened to a hyphen and straight quotes.

An archive can therefore hold anything you said in the interview, including opinions about named people, employers, and clients.
Treat it as a transcript of you.

## Keep the Extraction Root Out of Public Repositories

Extraction files live under the extraction root, which is `./extractions` in the working directory unless you configure another path.
That directory holds the interview spec, the archive, the profile, the compile log, and the calibration rounds.

If your working directory is a Git repository that will ever be public, keep the extraction root out of it.
Add a line to `.gitignore`:

```text
extractions/
```

If you set `extractions_root` to another path inside the repository, ignore that path instead.
See [Configuration](configuration.md).

## A Skillify Package Includes the Archive

A skill produced by [skillify](stages/skillify.md) carries `references/archive.md`, the verbatim interview archive, alongside the profile.
The zip that skillify packages by default contains it too.
Skillify says so before it creates the package.

If you upload or share that skill, you share the interview with it.
Read the archive first, and decide whether the person receiving the skill should see everything in it.
