# Tool Registry (Placeholder)

This document enumerates all tools available in the system.

Each tool specifies:
- name
- category
- allowed operations
- side effects
- risk level
- required permissions

## Registered Tools

### filesystem.read
Category: filesystem
Risk: low
Side effects: none

### filesystem.write
Category: filesystem
Risk: medium
Side effects: modifies files

### shell.execute
Category: shell
Risk: high
Side effects: executes commands

### web.search
Category: web
Risk: medium
Side effects: external requests

### web.fetch
Category: web
Risk: medium
Side effects: external requests

Tool registry is authoritative.
Agents may only reason about tools listed here.
