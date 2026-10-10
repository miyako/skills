# Converting Synchronous AI Kit Code to Streaming Callbacks

Steps 1 and 2 (finding the synchronous calls, opening the form with the
non-blocking launcher) are in `../SKILL.md`. Class and form names below
(`ConversationManager`, `chatMessages`, `extractedDataArea`, ...) are
examples -- use the project's own.

## Step 3: Convert Chat Completions to Async

### 3.1 Add Properties to the Class

```4d
property stream : Boolean
property _chatResult : Text
```

In the constructor:
```4d
This.stream:=True
This._chatResult:=""
```

### 3.2 Replace the Synchronous Call

**Before:**
```4d
Function _callAI($history : Collection)->$result : Object
    var $params : Object
    $params:=New object("model"; This.config.defaultModel; "max_tokens"; 1000; "temperature"; 0.5)
    $result:=This.client.chat.completions.create($history; $params)
    return $result
```

**After:**
```4d
Function _callAI($history : Collection)
    var $ChatCompletionsParameters : cs.AIKit.OpenAIChatCompletionsParameters
    $ChatCompletionsParameters:=cs.AIKit.OpenAIChatCompletionsParameters.new(This)
    $ChatCompletionsParameters.model:=This.config.defaultModel
    $ChatCompletionsParameters.max_completion_tokens:=This.MAX_TOKENS
    $ChatCompletionsParameters.temperature:=This.TEMPERATURE
    $ChatCompletionsParameters.stream:=This.stream
    $ChatCompletionsParameters.formula:=This.onEventStreamChat

    This._chatResult:=""

    This.client.chat.completions.create($history; $ChatCompletionsParameters)
```

Key changes:
- No return value — result comes via callback
- Pass `This` to `.new()` so the callback can access class properties
- Use `max_completion_tokens` (NOT `max_tokens`)
- Set `.formula` to a method reference on `This`

### 3.3 Add the Streaming Callback

```4d
Function onEventStreamChat($chatCompletionsResult : cs.AIKit.OpenAIChatCompletionsStreamResult)
    If ($chatCompletionsResult.success)
        If ($chatCompletionsResult.terminated)
            // Stream complete
            If ($chatCompletionsResult.choice#Null)
                If ($chatCompletionsResult.choice.message#Null)
                    // Was NOT streaming (stream=False fallback): use full message
                    If ($chatCompletionsResult.choice.message.content#Null)
                        This._chatResult:=This._chatResult+$chatCompletionsResult.choice.message.content
                        If (Form#Null)
                            WA EXECUTE JAVASCRIPT FUNCTION(*; "chatMessages"; "addAssistantMessage"; *; This._chatResult)
                        End if
                    End if
                End if
            End if
            // Post-completion logic here (save to DB, update form state, etc.)
            If (Form#Null)
                Form.waitingForChat:=False
            End if
        Else
            // Partial result — streaming chunk
            If ($chatCompletionsResult.choice#Null)
                If ($chatCompletionsResult.choice.delta.text#"")
                    If (This._chatResult="")
                        If (Form#Null)
                            // First chunk: create new message bubble
                            WA EXECUTE JAVASCRIPT FUNCTION(*; "chatMessages"; "addAssistantMessage"; *; $chatCompletionsResult.choice.delta.text)
                        End if
                    Else
                        If (Form#Null)
                            // Subsequent chunks: append to existing bubble
                            WA EXECUTE JAVASCRIPT FUNCTION(*; "chatMessages"; "appendAssistantMessage"; *; $chatCompletionsResult.choice.delta.text)
                        End if
                    End if
                    This._chatResult:=This._chatResult+$chatCompletionsResult.choice.delta.text
                End if
            End if
        End if
    Else
        If ($chatCompletionsResult.terminated)
            // Error
            This._chatResult:=$chatCompletionsResult.errors.extract("message").join("\r")
            If (Form#Null)
                WA EXECUTE JAVASCRIPT FUNCTION(*; "chatMessages"; "addAssistantMessage"; *; "❌ Error: "+This._chatResult)
                Form.waitingForChat:=False
            End if
        End if
    End if
```

### 3.4 Update the Calling Function

The function that previously received a return value must now be fire-and-forget:

**Before:**
```4d
Function sendMessage($docID : Text; $userMessage : Text)->$response : Object
    ...
    $result:=This._callAI($history)
    If ($result.success)
        $response.message:=$result.choice.message.content
    End if
    return $response
```

**After:**
```4d
Function sendMessage($docID : Text; $userMessage : Text)
    ...
    // Add user message to history and save
    $history.push(New object("role"; "user"; "content"; $userMessage))
    This._updateConversation($conv; $history)
    // Fire async call (callback handles response)
    This._callAI($history)
```

## Step 4: Convert Vision API to Async

```4d
Function _analyzeWithVision($file : 4D.File; $prompt : Text; $docID : Text)
    var $ChatCompletionsParameters : cs.AIKit.OpenAIChatCompletionsParameters
    $ChatCompletionsParameters:=cs.AIKit.OpenAIChatCompletionsParameters.new(This)
    $ChatCompletionsParameters.model:=This.config.visionModel
    $ChatCompletionsParameters.max_completion_tokens:=This.MAX_TOKENS
    $ChatCompletionsParameters.temperature:=This.TEMPERATURE
    $ChatCompletionsParameters.stream:=This.stream
    $ChatCompletionsParameters.formula:=This.onEventStreamVision
    $ChatCompletionsParameters.extraHeaders:={docID: $docID}

    This._visionResult:=""

    var $visionHelper : Object
    $visionHelper:=This.client.chat.vision.fromFile($file)
    $visionHelper.prompt($prompt; $ChatCompletionsParameters)
```

**Critical**: `fromFile()` takes ONLY the file. Parameters go to `prompt()`.

Use `extraHeaders` to pass context (like document ID) that the callback can retrieve via `$result.request.headers.docID`.

## Step 5: Update Button/Form Object Methods

Remove `CALL WORKER` + `SET TIMER` polling patterns. Call methods directly:

**Before:**
```4d
CALL WORKER("Worker-"+$docID; "_asyncMethod"; $docID)
SET TIMER(120)  // poll every 2 seconds
Form.processingDocID:=$docID
```

**After:**
```4d
_asyncMethod($docID)
```

The callback handles all UI updates directly — no polling needed.

## Step 6: Create HTML Files for Web Areas with Streaming

For web areas that display AI-generated HTML (summaries), create a persistent HTML file with **two divs**: one for streaming (shows raw text) and one for rendered output (shows final HTML). During streaming, show the raw text as-is using `textContent` — this avoids broken partial HTML rendering. When streaming completes, switch to the rendered div and display the final HTML.

**Resources/summary.html:**
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body { margin: 0; padding: 0; font-family: -apple-system, sans-serif; font-size: 13px; line-height: 1.6; background: #fff; color: #1f2937; }
#streaming { padding: 20px; white-space: pre-wrap; word-wrap: break-word; }
#rendered { display: none; }
#rendered > * { max-width: 100%; }
</style>
</head>
<body>
<div id="streaming"></div>
<div id="rendered"></div>
<script>
var _raw = '';
var streamingEl = document.getElementById('streaming');
var renderedEl = document.getElementById('rendered');

function setContent(text) {
    _raw = text;
    streamingEl.style.display = 'block';
    renderedEl.style.display = 'none';
    streamingEl.textContent = _raw;
    window.scrollTo(0, document.body.scrollHeight);
}
function appendContent(chunk) {
    _raw += chunk;
    streamingEl.textContent = _raw;
    window.scrollTo(0, document.body.scrollHeight);
}
function renderFinal() {
    streamingEl.style.display = 'none';
    renderedEl.style.display = 'block';
    renderedEl.innerHTML = _raw;
    window.scrollTo(0, document.body.scrollHeight);
}
function setRenderedHTML(html) {
    _raw = html;
    streamingEl.style.display = 'none';
    renderedEl.style.display = 'block';
    renderedEl.innerHTML = html;
    window.scrollTo(0, document.body.scrollHeight);
}
</script>
</body>
</html>
```

**Key design**: 
- `setContent` / `appendContent` → use `textContent` on the streaming div (shows raw text, avoids broken HTML)
- `renderFinal` → switches to the rendered div and uses `innerHTML` (renders final HTML)
- `setRenderedHTML` → for displaying pre-existing cached content as HTML immediately

Load it once in the form's On Load:
```4d
WA OPEN URL(*; "summaryText"; File("/RESOURCES/summary.html").platformPath)
```

## Step 7: Add JS Functions to Chat Web Area

In the method that renders chat HTML (e.g., `_renderChatHTML`), add these JavaScript functions to the output:

```javascript
function addAssistantMessage(content) {
    var row = document.createElement('div');
    row.className = 'message assistant';
    row.innerHTML = '<div class="role">🤖 Assistant</div><div class="content">' + content + '</div>';
    row._raw = content;
    document.body.appendChild(row);
    window.scrollTo(0, document.body.scrollHeight);
}
function appendAssistantMessage(chunk) {
    var msgs = document.querySelectorAll('.message.assistant');
    var last = msgs[msgs.length - 1];
    if (!last) { addAssistantMessage(chunk); return; }
    last._raw = (last._raw || '') + chunk;
    var contentEl = last.querySelector('.content');
    if (contentEl) contentEl.innerHTML = last._raw;
    window.scrollTo(0, document.body.scrollHeight);
}
function addUserMessage(content) {
    var row = document.createElement('div');
    row.className = 'message user';
    row.innerHTML = '<div class="role">👤 You</div><div class="content">' + content + '</div>';
    document.body.appendChild(row);
    window.scrollTo(0, document.body.scrollHeight);
}
```

## Step 8: Update Form Method

- Remove `On Timer` handling for chat and summary polling
- Keep document processing timer only if the vision callback updates DB and you still poll the DB
- Better: have the vision callback update the form directly and remove all timers
- Initialize async manager instances on Form (e.g., `Form.convManager`, `Form.summaryGen`)
- Load web area HTML files via `WA OPEN URL`

## Step 9: Handle Text Area Streaming (extractedDataArea)

For plain text form objects (not web areas), update the variable with accumulated text and use `HIGHLIGHT TEXT` to **position the cursor at the end** (which auto-scrolls):

```4d
// In the vision streaming callback (non-terminated events):
This._visionResult:=This._visionResult+$chatCompletionsResult.choice.delta.text
If (Form#Null)
    Form.extractedDataArea:=This._visionResult
    var $start; $end : Integer
    $start:=Length(Form.extractedDataArea)+1
    $end:=$start
    HIGHLIGHT TEXT(*; "extractedDataArea"; $start; $end)
End if
```

**CRITICAL**: `$start` must be `Length(...)+1` and `$end:=$start`. This places the cursor AFTER the last character, causing the text area to scroll to the bottom. Do NOT use `$start:=1; $end:=Length(...)` — that SELECTS all text instead of scrolling.

## Architecture Diagram

```
┌─────────────┐     ┌───────────────────────────┐     ┌─────────────┐
│  Button     │────▶│  Class Method             │────▶│  AI Kit API │
│  (On Click) │     │  (creates params,         │     │  (HTTP)     │
│             │     │   calls .create/.prompt)  │     │             │
└─────────────┘     └───────────────────────────┘     └──────┬──────┘
                                                             │
                    ┌───────────────────────────┐            │ callbacks
                    │  Callback Function        │◀───────────┘
                    │  (onEventStream...)       │
                    │  - updates web area via   │
                    │    WA EXECUTE JS FUNCTION │
                    │  - saves to DB on done    │
                    │  - updates Form state     │
                    └───────────────────────────┘
```
