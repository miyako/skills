---
name: 4daikit
description: >
  Use 4D AI Kit (cs.AIKit.OpenAI) from 4D code: chat completions and vision
  with OpenAIChatCompletionsParameters, asynchronous callbacks and streaming
  (formula / onData / onTerminate, stream, extraHeaders), exact parameter
  names (max_completion_tokens, not max_tokens), vision fromFile() + prompt(),
  showing streamed tokens in web areas (WA EXECUTE JAVASCRIPT FUNCTION, never
  WA SET PAGE CONTENT after WA OPEN URL) and text inputs (HIGHLIGHT TEXT).
  Use when adding AI features or converting blocking AI Kit calls to
  streaming.
---

# 4D AI Kit

## Scope

Calling an LLM through the 4D AI Kit component without blocking the UI:

* rules that are easy to get wrong (parameter names, call signatures, web
  area updates)
* the asynchronous / streaming callback model
* converting a project from synchronous calls to streaming --
  `references/async-streaming.md`

### Not in this skill

| Topic | Skill |
|---|---|
| Opening the form window non-blockingly (launcher method) | `4dstartup` |
| Class syntax, `Formula`, `cs.` lookups | `4dlang` |
| Form JSON for web areas and inputs | `4dform` |
| Validating `.4dm` | `4dlsp` |

## Route Table

| Task involves | Open |
|---|---|
| Converting `create()` / `prompt()` calls to callbacks, streaming into web areas or inputs, HTML/JS helpers | `references/async-streaming.md` |
| Rules, launcher, callback model | this file |

References:
- AI Kit overview: https://developer.4d.com/docs/aikit/overview
- Asynchronous calls: https://developer.4d.com/docs/aikit/asynchronous-call
- `OpenAIChatCompletionsParameters`: https://developer.4d.com/docs/aikit/Classes/openaichatcompletionsparameters
- `OpenAIChatCompletionsStreamResult`: https://developer.4d.com/docs/aikit/Classes/openaichatcompletionsstreamresult
- `OpenAIVision`: https://developer.4d.com/docs/aikit/Classes/openaivision
- `OpenAIParameters` (callbacks, `extraHeaders`, `throw`): https://developer.4d.com/docs/aikit/Classes/openaiparameters
- Files API: https://developer.4d.com/docs/aikit/Classes/openaifilesapi
- Source: https://github.com/4d/4D-AIKit

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## Rules

1. **Exact parameter names.** Check the class page before writing a
   property. The token limit is `max_completion_tokens`, **not**
   `max_tokens`.
2. **Vision:** `client.chat.vision.fromFile($file)` takes **only** the file.
   Parameters go to `.prompt($text; $params)`.
3. **Web areas loaded with `WA OPEN URL`:** never call `WA SET PAGE CONTENT`
   on them -- it destroys the page's JavaScript context. Update them with
   `WA EXECUTE JAVASCRIPT FUNCTION`.
4. **Callbacks may run after the form closed:** test `Form#Null` before
   touching `Form` or form objects.
5. **Reset accumulators** (`This._chatResult:=""`, ...) before each call.
6. **Results are objects.** `$result.choice` is an object: the text is
   `$result.choice.message.content` (streamed chunks:
   `$result.choice.delta.text`). Check `$result.success`; errors are in
   `$result.errors`.
7. **The models resource is plural:** `$client.models.list()` returns
   `.models`. Some documentation examples write `$client.model`, which is
   Undefined.
8. **Compatible and local providers** (Ollama, LM Studio, Mistral...): pass
   `baseURL` **and** an `apiKey` -- a dummy one for local servers that need
   none (observed: without `apiKey` the client can be Null). Configured
   provider names and model aliases are an alternative.
9. Call providers through AI Kit, not raw `4D.HTTPRequest`.
10. Write commands without token suffixes unless the exact token already
    exists in the project (token rules in `skills/4dproject/SKILL.md`).

## Callback Model

AI Kit's asynchronous calls are built on `4D.HTTPRequest`: the callback runs
**in the process that made the call**, so that process must stay alive. A
form opened with `DIALOG(...; *)` in a worker does; a method that ends (a
`New process` that returns, or running from the method editor) does not.
Open forms that call AI Kit with the pattern in
`skills/4dstartup/SKILL.md` -- `CALL WORKER(1; ...)` + `Open form window` +
`DIALOG(form; data; *)`, no `CLOSE WINDOW`.

Pass the callback in the parameters object:

```4d
var $params : cs.AIKit.OpenAIChatCompletionsParameters
$params:=cs.AIKit.OpenAIChatCompletionsParameters.new(This)  // This becomes the callback's This
$params.model:=This.config.defaultModel
$params.max_completion_tokens:=This.MAX_TOKENS
$params.stream:=True
$params.formula:=This.onEventStreamChat   // called for every chunk and at the end
This._chatResult:=""
This.client.chat.completions.create($messages; $params)
```

* `formula` (alias `onTerminate`) receives every event; test `.success`
  and `.terminated` and read `.choice.delta.text` for partial chunks. The
  documented alternatives are `onData` for chunks, or `onResponse` /
  `onError` for non-streamed calls. The callback receives the same result
  class the synchronous call would return. `throw` and `maxRetries` only
  apply without a callback.
* `extraHeaders` (e.g. `{docID: $docID}`) travels with the request; the
  callback reads it back as `$result.request.headers.docID`.
* The call returns immediately; functions that returned the result must
  become fire-and-forget, and polling with `CALL WORKER` + `SET TIMER` goes
  away. **Everything that used to follow the call** (UI feedback, enabling
  a button, the next step) moves into the callback -- it is the only place
  that knows the request finished.
* State needed by several form objects (e.g. the id of an uploaded file)
  goes on `Form`, not on the class instance that made the call.
* **Subforms:** in a callback, `Form` may designate the parent form, not
  the subform. Capture the instance explicitly --
  `var $self:=This` then `$params.formula:=Formula($self._onResult($1))` --
  and update the subform through `$self`.
* **Batches:** process items one at a time by starting the next request
  from the callback of the previous one (keep a queue on `This`); the UI
  refreshes between items without workers or timers.
* **File uploads** follow the same model:
  `$client.files.create($file; "user_data"; $fileParams)` with
  `$fileParams:=cs.AIKit.OpenAIFileParameters.new(This)`,
  `$fileParams.formula:=...` and optionally
  `$fileParams.expires_after:={anchor: "created_at"; seconds: 3600}`. The
  callback receives an `OpenAIFileResult`: on success, `.file.id` is what
  `OpenAIMessage.addFileId()` needs. `extraHeaders` (e.g.
  `{name: $file.fullName}`) carries context such as the file name.

## Steps

1. Find synchronous calls: `client.chat.completions.create($messages;
   $params)` or `visionHelper.prompt($prompt; $params)` with a plain
   object, followed by code reading `$result.success` /
   `$result.choice.message.content`.
2. Make sure the form is opened with the `4dstartup` pattern.
3. Convert each call, its callback, and the UI updates as described in
   `references/async-streaming.md`.
4. Validate changed `.4dm` with `4dlsp`.

## Checklist

- [ ] Every `create()` / `prompt()` passes an `OpenAIChatCompletionsParameters` with a callback
- [ ] Vision parameters passed to `prompt()`, not `fromFile()`
- [ ] `max_completion_tokens` (not `max_tokens`)
- [ ] No `WA SET PAGE CONTENT` on web areas loaded with `WA OPEN URL`
- [ ] No `CALL WORKER` + `SET TIMER` polling left
- [ ] Form opened non-blockingly (`4dstartup`)
- [ ] Callbacks test `Form#Null`; accumulators reset before each call
- [ ] Final rendering (e.g. `renderFinal()`) runs on every `terminated` event, not only when `choice#Null`
- [ ] No invented token suffixes
