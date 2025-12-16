# Release Process

## Pre-release Checklist

- Evaluator not forced
- Policy limits set correctly
- CI passing
- runs/ directory empty or ignored

## Tagging

git tag -a v0.1 -m "Agentix v0.1"
git push --tags

## After Release

- No schema changes without version bump
- Evolution policy changes require review
