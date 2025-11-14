# Checkpoint and Commit Workflow Prompt

## Task Description
Create a comprehensive project checkpoint and commit current changes to maintain development continuity for the Omega agentic migration system.

## Execution Steps

### 1. Create Project Checkpoint
Execute the checkpoint creation tool with current work context:

```bash
/workspace/tools/src/create-checkpoint.sh \
  -e "Current Epic/Feature" \
  -t "Current Task/Issue" \
  -s "Task Status (in-progress/blocked/testing/completed)" \
  -n "Next planned tasks" \
  -b "Current blockers or issues" \
  --notes "Additional context or important notes"
```

**Example:**
```bash
/workspace/tools/src/create-checkpoint.sh \
  -e "Tool Development" \
  -t "Modernize checkpoint script" \
  -s "completed" \
  -n "Update documentation and test integration" \
  --notes "Successfully converted to JSON output with CLI args"
```

### 2. Review Generated Checkpoint
- Verify JSON checkpoint was created successfully
- Check file location: `/workspace/checkpoints/checkpoint_YYYYMMDD_HHMMSS.json`
- Validate JSON structure is correct

### 3. Stage and Commit Changes
Follow this sequence to properly stage and commit all changes:

```bash
# 1. Check current Git status
git status

# 2. Stage all changes (including new files)
git add .

# 3. Commit with descriptive message
git commit -m "📊 Checkpoint: [Epic] - [Task Status]

- [Brief description of main changes]
- [Key accomplishments or progress]
- [Next steps or blockers noted]

Checkpoint: checkpoint_YYYYMMDD_HHMMSS.json"
```

### 4. Push to Remote Repository
```bash
git push
```

## Success Criteria
- ✅ JSON checkpoint created successfully
- ✅ All project changes staged and committed
- ✅ Descriptive commit message includes checkpoint reference
- ✅ Changes pushed to remote repository
- ✅ No uncommitted files remain (`git status` shows clean working tree)

## Template Values to Replace
When using this prompt, replace these placeholders:
- `[Epic]` - Current epic or feature area
- `[Task Status]` - Current status (in-progress, completed, blocked, etc.)
- `[Brief description]` - Summary of main changes made
- `[Key accomplishments]` - What was achieved in this session
- `[Next steps/blockers]` - What comes next or current obstacles

## Integration Notes
- This workflow maintains continuity for GitHub Copilot sessions
- Checkpoints provide rich context for resuming development work
- Commit messages follow project conventions with emoji prefixes
- JSON format enables programmatic parsing and integration