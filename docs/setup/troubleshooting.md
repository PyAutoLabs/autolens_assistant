# Troubleshooting (browser chats)

Failure modes we know about across the conversational-AI options. If you hit something not
listed here, [open a GitHub issue](https://github.com/PyAutoLabs/autolens_assistant/issues)
— these surfaces change fast and user reports are how the guide stays current.

**Claude's GitHub connector attaches the repo but just inserts a `github.com/.../tree/main`
link into the message.**
This is the open connector bug
([claude-code#71542](https://github.com/anthropics/claude-code/issues/71542)), which we
reproduced on our own Free-account test (2026-08-06). Some accounts have recovered by
connecting the repo inside a **brand-new Project**, or by disconnecting the connector fully
(also revoke Claude under GitHub → Settings → Applications) and reconnecting — but don't
sink time into it: the [Project + knowledge pack](claude_chat_free.md) needs no connector
at all and works today.

**"I can't access that repository" / it answers from memory anyway.**
The most common cause is a `blob/` URL — `github.com/.../blob/main/llms.txt` is an HTML page
that many chats receive as an empty JavaScript shell. Always use the
`raw.githubusercontent.com` form; every link in `llms.txt` already is. If it still fails,
[paste the bundle](paste_bundle.md).

**It fetched `llms.txt` but can't follow the links inside it — it keeps asking you to paste
URLs.**
On claude.ai (and some other chats) the fetch tool only retrieves URLs *you* pasted or
literal search hits — links the assistant discovers inside a page it fetched stay blocked.
Pasting the raw URL it asks for works instantly, but costs a message each time. If you're
doing this more than once or twice, switch to the
[Project + knowledge pack](claude_chat_free.md): with the pack in project knowledge, nothing
needs fetching.

**The custom GPT says it can't retrieve its documentation.**
Known issue — the GPT's uploaded knowledge is not reliably retrievable in published chats,
and on free accounts browsing can't fetch raw GitHub pages either (see
[the custom GPT page](chatgpt_custom_gpt.md)). Its honest refusal to write unverified code
is by design; [paste the bundle](paste_bundle.md) to get a verified script.

**It wrote `aplt.FitImagingPlotter(...)` or `aplt.MatPlot2D(...)`.**
That is the stale-API failure — those classes were removed. Reply: *"Plotting is functional
now — re-check against `01_api_surface.md` and the plotting skill, and rewrite using
`aplt.subplot_fit_imaging(...)`."* If it keeps happening, your context was lost — re-paste
the bundle or check the project knowledge actually uploaded.

**It ran out of context / got slow and vague.**
Something large was pulled in — `wiki/literature/` and `llms-full.txt` are big enough to
crowd out the conversation on their own. Start a fresh chat and tell it to fetch single
pages only.

**It stopped mid-task, or switched to a weaker model.**
Free plans have usage limits that are unpublished and vary with load — in the region of a
few dozen messages per 5 hours on Claude, and a smaller number of flagship-model turns on
ChatGPT before it falls back to a lighter model. Long modelling sessions are where a paid
plan or a local [coding agent](gemini_cli.md) genuinely pays for itself.

**A generated script fails on an API error anyway.**
The bundle pins one specific stack version (stated at the top of `01_api_surface.md`). If
your installed PyAutoLens is newer, there may be genuine drift. Report it as an issue with
the error text — and note this is exactly the failure a coding agent's code gate catches
automatically.
