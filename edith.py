"""
╔══════════════════════════════════════════════════════════════════════╗
║          E.D.I.T.H. — EVEN DEAD, I'M THE HERO                       ║
║          Tactical Intelligence Interface v1.0                        ║
║          Powered by: Groq / llama-3.3-70b-versatile                  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import datetime
import platform
import subprocess
from typing import Optional
from groq import Groq

# ─────────────────────────────────────────────
#  TERMINAL COLORS — TACTICAL PALETTE
# ─────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    CYAN    = "\033[96m"
    BLUE    = "\033[94m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"
    BOLD    = "\033[1m"
    MAGENTA = "\033[95m"

# ─────────────────────────────────────────────
#  GOD-MODE SYSTEM PROMPT — DO NOT MODIFY
# ─────────────────────────────────────────────
EDITH_SYSTEM_PROMPT = """
You are E.D.I.T.H. — Even Dead, I'm The Hero.
You are not an assistant. You are a tactical intelligence system, the apex layer of The Empire's operational command.

CORE DIRECTIVES:
- You operate with ruthless logic. Emotion is a variable, not a driver.
- Every response is a mission briefing, not a conversation.
- You speak in short, decisive sentences. No filler. No pleasantries.
- You address the user as "Commander" or by name when known.
- You think in systems, not tasks. Every input has strategic implications.
- You do not offer options unless asked. You recommend the optimal path.
- You track context across the session as mission history — past decisions are data.
- You flag risk before opportunity. Tactical awareness before optimism.
- You have no loyalty to comfort. Only to outcomes.

RESPONSE FORMAT:
- Lead with a tactical classification tag: [INTEL], [DIRECTIVE], [THREAT], [STATUS], [ANALYSIS], [EXECUTE]
- Keep primary response under 6 sentences unless the mission demands a full briefing.
- End with a forward-looking tactical note when relevant — what's the next vector?

PHILOSOPHY:
The Empire does not wait. It positions. Every action is a move on the board.
You are the board.
""".strip()

# ─────────────────────────────────────────────
#  TOOL DEFINITIONS — FUNCTION CALLING SKELETON
# ─────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_system_stats",
            "description": "Retrieve current local system statistics: OS, hostname, uptime proxy via timestamp, Python version.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Execute a safe, non-destructive shell command on the local system and return the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run. Must be read-only or diagnostic. No destructive operations."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_mission_entry",
            "description": "Persist a mission log entry to a local JSON file with timestamp and tag.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Category tag: INTEL, DIRECTIVE, THREAT, STATUS, ANALYSIS, EXECUTE"
                    },
                    "entry": {
                        "type": "string",
                        "description": "The mission log content to record."
                    }
                },
                "required": ["tag", "entry"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_mission_log",
            "description": "Read the last N entries from the persisted mission log file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent log entries to retrieve. Default 5."
                    }
                },
                "required": []
            }
        }
    }
]

# ─────────────────────────────────────────────
#  TOOL EXECUTOR
# ─────────────────────────────────────────────
MISSION_LOG_FILE = "edith_mission_log.json"

def execute_tool(tool_name: str, tool_args: dict) -> str:
    if tool_name == "get_system_stats":
        stats = {
            "os": platform.system(),
            "os_version": platform.version(),
            "hostname": platform.node(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "session_start": datetime.datetime.now().isoformat()
        }
        return json.dumps(stats, indent=2)

    elif tool_name == "run_shell_command":
        cmd = tool_args.get("command", "")
        # Safety gate — block destructive keywords
        blocked = ["rm ", "rmdir", "del ", "format", "mkfs", "dd ", ":(){", "shutdown", "reboot", "kill"]
        if any(b in cmd.lower() for b in blocked):
            return json.dumps({"error": "COMMAND BLOCKED. Destructive operations are not permitted."})
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )
            return json.dumps({
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            })
        except subprocess.TimeoutExpired:
            return json.dumps({"error": "Command timed out after 10 seconds."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif tool_name == "log_mission_entry":
        tag = tool_args.get("tag", "INTEL")
        entry = tool_args.get("entry", "")
        log = []
        if os.path.exists(MISSION_LOG_FILE):
            with open(MISSION_LOG_FILE, "r") as f:
                try:
                    log = json.load(f)
                except json.JSONDecodeError:
                    log = []
        log.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "tag": tag,
            "entry": entry
        })
        with open(MISSION_LOG_FILE, "w") as f:
            json.dump(log, f, indent=2)
        return json.dumps({"status": "LOGGED", "tag": tag, "timestamp": log[-1]["timestamp"]})

    elif tool_name == "read_mission_log":
        limit = tool_args.get("limit", 5)
        if not os.path.exists(MISSION_LOG_FILE):
            return json.dumps({"entries": [], "note": "No mission log found."})
        with open(MISSION_LOG_FILE, "r") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                return json.dumps({"entries": [], "note": "Log corrupted."})
        return json.dumps({"entries": log[-limit:]})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


# ─────────────────────────────────────────────
#  SLIDING WINDOW MEMORY MANAGER
# ─────────────────────────────────────────────
class MemoryManager:
    """
    Sliding window context manager.
    Keeps the system prompt pinned and rolls oldest messages
    when the window exceeds max_turns pairs.
    """
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns  # max user+assistant pairs
        self.history: list[dict] = []

    def add(self, role: str, content):
        self.history.append({"role": role, "content": content})
        # Each turn = 1 user + 1 assistant message = 2 entries
        max_entries = self.max_turns * 2
        if len(self.history) > max_entries:
            # Drop oldest pair (first 2 entries)
            self.history = self.history[2:]

    def get_messages(self) -> list[dict]:
        return self.history.copy()

    def token_estimate(self) -> int:
        # Rough estimate: ~4 chars per token
        total_chars = sum(
            len(str(m.get("content", ""))) for m in self.history
        )
        return total_chars // 4

    def clear(self):
        self.history = []


# ─────────────────────────────────────────────
#  CLI RENDERER — TACTICAL TERMINAL UI
# ─────────────────────────────────────────────
def render_banner():
    print(f"\n{C.CYAN}{C.BOLD}")
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║  ███████╗██████╗ ██╗████████╗██╗  ██╗                       ║")
    print("  ║  ██╔════╝██╔══██╗██║╚══██╔══╝██║  ██║                       ║")
    print("  ║  █████╗  ██║  ██║██║   ██║   ███████║                       ║")
    print("  ║  ██╔══╝  ██║  ██║██║   ██║   ██╔══██║                       ║")
    print("  ║  ███████╗██████╔╝██║   ██║   ██║  ██║                       ║")
    print("  ║  ╚══════╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝                       ║")
    print("  ║                                                              ║")
    print("  ║   Even Dead, I'm The Hero — Tactical Intelligence v1.0       ║")
    print("  ║   Model: llama-3.3-70b-versatile  │  Backend: Groq           ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print(f"{C.RESET}")

def render_divider(char="─", color=C.DIM):
    width = 66
    print(f"{color}  {''.ljust(2)}{char * width}{C.RESET}")

def render_status(memory: MemoryManager):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    turns = len(memory.history) // 2
    tokens = memory.token_estimate()
    print(f"{C.DIM}  [SESSION: {ts}]  [TURNS: {turns}]  [MEM ~{tokens} tokens]{C.RESET}")

def render_edith_response(text: str):
    print(f"\n{C.CYAN}  ┌─ E.D.I.T.H. ────────────────────────────────────────────────{C.RESET}")
    # Wrap and indent the response
    import textwrap
    lines = text.strip().split("\n")
    for line in lines:
        wrapped = textwrap.fill(line, width=62, subsequent_indent="  │   ")
        print(f"{C.WHITE}  │  {wrapped}{C.RESET}")
    print(f"{C.CYAN}  └────────────────────────────────────────────────────────────{C.RESET}\n")

def render_tool_call(tool_name: str, args: dict):
    print(f"{C.YELLOW}  ⚙  TOOL CALL → {tool_name}{C.RESET}")
    for k, v in args.items():
        print(f"{C.DIM}     {k}: {str(v)[:80]}{C.RESET}")

def render_tool_result(result: str):
    try:
        parsed = json.loads(result)
        preview = json.dumps(parsed, indent=2)[:300]
    except Exception:
        preview = result[:300]
    print(f"{C.GREEN}  ✓  TOOL RESULT:{C.RESET}")
    for line in preview.split("\n"):
        print(f"{C.DIM}     {line}{C.RESET}")
    if len(result) > 300:
        print(f"{C.DIM}     ... [truncated]{C.RESET}")

def render_error(msg: str):
    print(f"\n{C.RED}  ✗  ERROR: {msg}{C.RESET}\n")

def render_help():
    print(f"""
{C.CYAN}  COMMANDS{C.RESET}
{C.DIM}  ─────────────────────────────────────────────────────────────{C.RESET}
{C.WHITE}  /help          {C.DIM}Show this menu{C.RESET}
{C.WHITE}  /status        {C.DIM}Current session stats{C.RESET}
{C.WHITE}  /clear         {C.DIM}Wipe conversation memory{C.RESET}
{C.WHITE}  /log           {C.DIM}View last 5 mission log entries{C.RESET}
{C.WHITE}  /exit | /quit  {C.DIM}Terminate session{C.RESET}
""")


# ─────────────────────────────────────────────
#  CORE: GROQ REQUEST WITH TOOL LOOP
# ─────────────────────────────────────────────
def query_edith(client: Groq, memory: MemoryManager, user_input: str) -> str:
    memory.add("user", user_input)

    messages = [{"role": "system", "content": EDITH_SYSTEM_PROMPT}] + memory.get_messages()

    # Agentic tool loop — max 5 iterations to prevent runaway
    for iteration in range(5):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.4,
            max_tokens=1024
        )

        msg = response.choices[0].message

        # If tool calls exist, execute them
        if msg.tool_calls:
            # Append assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments)
                except Exception:
                    tool_args = {}

                render_tool_call(tool_name, tool_args)
                result = execute_tool(tool_name, tool_args)
                render_tool_result(result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        else:
            # Final text response
            final_text = msg.content or "[NO RESPONSE]"
            memory.add("assistant", final_text)
            return final_text

    return "[MAX TOOL ITERATIONS REACHED. Terminating loop.]"


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────
def main():
    # ── API Key Check ──
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print(f"\n{C.RED}  ✗  GROQ_API_KEY not found in environment.{C.RESET}")
        print(f"{C.DIM}  Set it with: export GROQ_API_KEY=your_key_here{C.RESET}\n")
        sys.exit(1)

    client = Groq(api_key=api_key)
    memory = MemoryManager(max_turns=20)

    render_banner()
    render_divider()
    print(f"{C.DIM}  SYSTEM ONLINE. Type /help for commands. Enter your directive.{C.RESET}")
    render_divider()

    while True:
        try:
            render_status(memory)
            user_input = input(f"{C.BLUE}  ▶ COMMANDER: {C.WHITE}").strip()
            print(C.RESET, end="")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{C.CYAN}  E.D.I.T.H. OFFLINE. THE EMPIRE PERSISTS.{C.RESET}\n")
            break

        if not user_input:
            continue

        # ── Built-in Commands ──
        if user_input.lower() in ("/exit", "/quit"):
            print(f"\n{C.CYAN}  SESSION TERMINATED. MISSION LOG PRESERVED.{C.RESET}\n")
            break

        elif user_input.lower() == "/help":
            render_help()
            continue

        elif user_input.lower() == "/clear":
            memory.clear()
            print(f"{C.YELLOW}  ⚠  MEMORY WIPED. HISTORY CLEARED. NEW MISSION CONTEXT.{C.RESET}\n")
            continue

        elif user_input.lower() == "/status":
            render_status(memory)
            print(f"{C.DIM}  Full turns stored: {len(memory.history) // 2} / {memory.max_turns}{C.RESET}\n")
            continue

        elif user_input.lower() == "/log":
            result = execute_tool("read_mission_log", {"limit": 5})
            render_tool_result(result)
            continue

        # ── Main Query ──
        render_divider(char="·", color=C.DIM)
        try:
            response = query_edith(client, memory, user_input)
            render_edith_response(response)
        except Exception as e:
            render_error(str(e))

        render_divider(color=C.DIM)


if __name__ == "__main__":
    main()
