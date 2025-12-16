#!/usr/bin/env bash
set -e

echo "[agentix] adding recommended placeholders..."

# ---------- knowledge layer ----------
mkdir -p knowledge

if [ ! -f knowledge/README.md ]; then
cat > knowledge/README.md << 'EOF'
# Knowledge Base (Placeholder)

This directory represents system-owned knowledge.

Principles:
- Agents do not own long-term memory
- Knowledge persists across runs
- Knowledge is curated, summarized, and versioned

Possible contents:
- extracted facts
- summaries of sources
- compressed agent learnings
- validated conclusions
EOF
fi

# ---------- fitness definition ----------
if [ ! -f docs/fitness.md ]; then
cat > docs/fitness.md << 'EOF'
# Fitness (Placeholder)

Fitness is defined at the system level.

Agents:
- do not compute their own fitness
- do not see their fitness scores
- cannot optimize themselves directly

Potential fitness dimensions:
- task success
- correctness
- efficiency (time, tokens, disk)
- human feedback
- consistency across runs

Fitness is used exclusively for:
- evaluation
- evolution decisions
- archival or promotion of agents
EOF
fi

# ---------- governance ----------
if [ ! -f docs/governance.md ]; then
cat > docs/governance.md << 'EOF'
# Governance (Placeholder)

This document defines control and authority boundaries.

Core principles:
- no agent has unilateral control
- all irreversible actions require approval
- kernel is immutable by agents

Governance topics (to be defined):
- agent creation rules
- agent activation / deactivation
- evolution approval workflow
- tool permission granting
- human-in-the-loop checkpoints
EOF
fi

# ---------- tool registry ----------
mkdir -p kernel/tools

if [ ! -f kernel/tools/registry.md ]; then
cat > kernel/tools/registry.md << 'EOF'
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
EOF
fi

echo "[agentix] recommended placeholders added."
