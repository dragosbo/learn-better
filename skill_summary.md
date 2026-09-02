# Skill: Transcript Summary

A reusable instruction set for turning a video transcript into a concise,
clear, structured summary. Give this file plus a transcript to an assistant
(or reuse it yourself) to produce a summary in a consistent format.

## How to use

> Apply `skill_summary.md` to `<transcript file>` and save the result to
> `summaries/<same base name>.summary.md`.

The assistant should read the transcript in full, then produce one Markdown
file following the template below. Keep it concise: the summary should be a
fraction of the transcript length, not a rewrite.

## Inputs

- **Transcript**: a `.txt` file, usually timestamped as `[HH:MM:SS] text`
  (as produced by `code/test_read_transcript.py`). Timestamps are used to
  anchor the table of contents; they are not copied line by line.

## Output

- One Markdown file named `<transcript base name>.summary.md` inside a
  `summaries/` folder (create the folder if missing).
- Base name = the transcript filename without the `.<lang>.txt` suffix.
  Example: `Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].en.txt`
  -> `summaries/Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].summary.md`.

## Rules

- Be concise and clear. Prefer short sentences and bullet points.
- Ground everything in the transcript. Do not invent facts, tools, or steps
  that are not present. If something is unclear, say so rather than guessing.
- Use approximate timestamps (from the transcript) to build the table of
  contents so a reader can jump to a section in the video.
- Neutral, factual tone. Strengths/weaknesses are about the content's value as
  a learning resource, not personal opinion about the presenter.
- Keep any code/commands in backticks or code blocks, exactly as shown.
- Target length: roughly 1 page (about 300-500 words), regardless of video
  length.

## Template

Copy this structure into the output file and fill it in.

```markdown
# Summary: <Video Title>

- **Source video**: <title> (`<video id>`)
- **Approx. length**: <mm:ss or hh:mm>
- **Topic**: <one line>
- **Audience / level**: <e.g. beginners, intermediate>

## One-line takeaway
<a single sentence capturing the core value>

## Table of contents
| Time | Section |
|------|---------|
| 00:00 | <section 1 title> |
| MM:SS | <section 2 title> |
| ...   | ... |

## Sections
### <Section 1 title> (MM:SS)
- <2-4 concise bullets on what is covered / key commands or steps>

### <Section 2 title> (MM:SS)
- <...>

<repeat per major section>

## Key takeaways
- <3-6 bullets: the most important things a viewer learns>

## Strengths
- <what this resource does well: clarity, completeness, hands-on demos, etc.>

## Weaknesses
- <gaps, dated info, missing depth, anything glossed over or unexplained>

## Who should watch
<one or two sentences on the ideal viewer and prerequisites>
```

## Checklist before saving

- [ ] File is in `summaries/` and named `<base>.summary.md`.
- [ ] Table of contents has real timestamps from the transcript.
- [ ] Every section maps to actual transcript content.
- [ ] Strengths AND weaknesses are both filled in (not left blank).
- [ ] Length is close to one page; no filler.
