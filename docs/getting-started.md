# Getting Started

## Install

--8<-- "README.md:install"

The repository is linked from the header of this site.
The Releases page of the repository lists each published zip.

## Invoke a Stage

On Claude Code and Cowork, a stage is a slash command named for the plugin and the stage:

```text
/metacognition:design
/metacognition:interview
/metacognition:compile
/metacognition:calibrate
/metacognition:skillify
```

On claude.ai chat, type "/" and pick the skill.

Each stage ends by naming the files it wrote and the command for the next stage, and then stops.
You decide when to run the next one.

## The Three Surfaces

The stages behave the same way on every surface.
The surroundings differ.

| | Claude Code | Cowork | claude.ai chat |
|---|---|---|---|
| Install | marketplace or `--plugin-dir` | marketplace or zip upload | marketplace or zip upload |
| Invoke | `/metacognition:<stage>` | `/metacognition:<stage>` | "/" plus the skill |
| Plugin agents | load | load | ignored |
| Shipped scripts | run on your machine | run in the session | run in the code execution sandbox, standard library only |
| Extraction files | the working directory | the working folder | the conversation's files |

Two of those rows change what you see.

The research agent is the one plugin agent.
[Design](stages/design.md) dispatches it where the surface loads plugin agents.
On claude.ai chat, design runs the same research itself, in the conversation.
With no web access, design says so and continues from your scoping answers alone.

The shipped scripts resolve your settings and check the structure of the extraction files.
They need code execution and Python 3.11 or newer.
When a stage cannot run them, it applies the same rules by hand and says so in one line.

## Run the Whole Pipeline in One claude.ai Conversation

claude.ai chat has no working directory.
A pipeline can run in one long conversation, with each stage using the files the previous stage wrote.
You can run it in one conversation or in a Project.

1. Start a conversation, or a Project, and run `/metacognition:design` with your domain.
2. Answer the design questions.
   Design writes `interview-spec.md` and the extraction README to the conversation's files.
3. Run `/metacognition:interview` in the same conversation.
   It reads `interview-spec.md` and writes `archive.md`.
4. Run `compile`, then `calibrate`, then `skillify` the same way.
   Each reads what the stage before it wrote.

If you start a stage in a fresh conversation, give it the extraction files it reads, by uploading them.
The inputs and outputs of each stage are listed on its page under [The Five Stages](stages/index.md).

To change a setting, state it in your first message, or put it in the Project instructions.
The skill treats it as a run-time value.
[Configuration](configuration.md) lists the two settings.

!!! warning "Keep the files"

    The extraction files hold your interview answers word for word.
    Read [Privacy](privacy.md) before you store or share them anywhere.
