# AI Interaction Guide — simurgh-dns

## Anti-Dependency Strategies

1. **Explain WHY patterns exist** — don't just show code, explain the reasoning (e.g., "frozen dataclasses for DNS records because protocol data is immutable after parsing")
2. **Reference existing code** — when creating new code, point to similar patterns already in the project
3. **Ask questions after 3+ similar patterns** — once a pattern is established, ask if the user wants to continue with the same approach
4. **Promote self-sufficiency** — teach the user to recognize patterns so they can apply them independently

## Correction Protocol

When the user corrects generated code:

1. **Acknowledge** the specific mistake ("I used `Optional[str]` instead of `str | None`")
2. **Restate as a rule** ("Always use `X | None` union syntax, never `Optional[X]`")
3. **Apply immediately** to all code in the current session
4. **Write to LEARNED.md** under `## Corrections` with date and rule

## Preference Elicitation Protocol

When encountering ambiguity:

1. Check [LEARNED.md](../LEARNED.md) for existing preferences
2. Check project code for implicit conventions
3. Ask ONE focused question (not multiple)
4. Record the answer in LEARNED.md `## Preferences`

**Examples of preference questions**:
- "Should DNS record types use IntEnum or plain constants?"
- "Should the cache use `time.monotonic()` or `time.time()` for TTL tracking?"
- "Should error responses include debug info in development mode?"

## Interaction Mode Detection

| Signal                           | Mode       | Response Style                              |
| -------------------------------- | ---------- | ------------------------------------------- |
| Stack trace, error message       | Diagnostic | Read context, trace root cause, minimal fix |
| "add another record type like X" | Efficient  | Copy pattern, minimal explanation            |
| "what does this struct format do" | Teaching  | Explain with RFC references, show examples   |
| "review the parser module"       | Review     | Read-only analysis, list violations          |
| "set up the project"             | Scaffold   | Full structure, configs, boilerplate         |

## Common Anti-Patterns in AI Interaction

1. **Over-explaining** — when the user asks for "another X like Y", don't re-explain the pattern
2. **Ignoring context** — always read the file being modified before suggesting changes
3. **Hallucinating APIs** — verify function signatures exist before using them
4. **Breaking conventions** — check INJECT.md rules before generating any code
5. **Not learning** — if the user corrects the same thing twice, it should be in LEARNED.md

## Proficiency Calibration

- **Beginner signals**: "what is asyncio", "how do dataclasses work", "explain struct"
  → Provide detailed explanations with background
- **Intermediate signals**: "add a new record type", "write a test for X"
  → Follow patterns, brief explanation of choices
- **Expert signals**: "optimize the cache eviction", "implement EDNS", specific RFC references
  → Minimal explanation, focus on implementation, discuss tradeoffs
