# EON

The reasoning and planning layer for the Universal AI Mobile Assistant.
This Python backend is the "brain" — it takes natural language commands and returns a structured sequence of tool calls plus a spoken response. Your Android app executes those calls on the actual device.

---

## Project structure

```
ai_brain/
├── tools.py        ← every capability the AI can invoke (tool schema)
├── agent.py        ← core Claude reasoning loop with tool dispatch
├── memory.py       ← per-session conversation history + user profile
├── server.py       ← FastAPI HTTP server (Android app calls this)
├── test_agent.py   ← run and test the brain locally
└── requirements.txt
```

---

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and paste your Anthropic API key
```

---

## Run locally

Test the brain without Android:

```bash
python test_agent.py
```

Start the HTTP server (Android app will call this):

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

API docs available at `http://localhost:8000/docs`

---

## API usage

### Send a command

```
POST /query
{
  "text": "Message John on WhatsApp: Running 10 mins late",
  "session_id": "optional-uuid-for-multi-turn"
}
```

Response:

```json
{
  "response": "Message sent to John on WhatsApp.",
  "tool_calls": [
    {
      "tool": "send_message",
      "input": { "app": "whatsapp", "contact": "John", "message": "Running 10 mins late" },
      "result": { "success": true, "sent_to": "John", "via": "whatsapp" }
    }
  ],
  "session_id": "abc-123"
}
```

---

## Android integration

The brain returns `tool_calls` — your Android app reads this list and executes each action on the device.

### Kotlin call (Retrofit)

```kotlin
data class QueryRequest(val text: String, val session_id: String?)
data class ToolCall(val tool: String, val input: Map<String, Any>, val result: Map<String, Any>)
data class QueryResponse(val response: String, val tool_calls: List<ToolCall>, val session_id: String)

interface BrainApi {
    @POST("query")
    suspend fun query(@Body req: QueryRequest): QueryResponse
}
```

### Tool executor (Android side)

```kotlin
fun executeTool(call: ToolCall) {
    when (call.tool) {
        "send_message" -> {
            val contact = call.input["contact"] as String
            val message = call.input["message"] as String
            val app     = call.input["app"] as String
            WhatsAppBridge.send(contact, message)  // your bridge implementation
        }
        "control_device" -> {
            val setting = call.input["setting"] as String
            val action  = call.input["action"] as String
            DeviceController.apply(setting, action)  // uses Android AccessibilityService
        }
        "navigate" -> {
            val destination = call.input["destination"] as String
            MapsLauncher.navigate(destination)
        }
        // ... one branch per tool
    }
}
```

---

## Replacing stubs with real Android calls

Every `_exec_*` method in `agent.py` is a stub that returns fake data so the AI can reason during development. Replace each with an HTTP callback to your Android app:

```python
def _exec_send_message(self,inp: dict) -> dict:
    r = requests.post("http://android-device/bridge/send_message",json=inp,timeout=5)
    return r.json()
```

Or flip the architecture: let the Android app handle all execution and only call the brain for planning.

---

## Adding a new tool

1. Add the tool schema to `PHONE_TOOLS` in `tools.py`
2. Add an `_exec_toolname` method in `agent.py`
3. Register it in the `_dispatch` handlers dict

The LLM will automatically start using it when appropriate.

---

## Android permissions you will need

| Capability | Android permission |
|---|---|
| Send SMS | SEND_SMS |
| Read contacts | READ_CONTACTS |
| Make calls | CALL_PHONE |
| Read calendar | READ_CALENDAR / WRITE_CALENDAR |
| Location | ACCESS_FINE_LOCATION |
| Device settings | WRITE_SETTINGS |
| App automation | Accessibility Service + BIND_ACCESSIBILITY_SERVICE |
| Notifications | POST_NOTIFICATIONS |
