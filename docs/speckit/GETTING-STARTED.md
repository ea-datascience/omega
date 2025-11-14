# Spec Kit Quick Start Guide

This is a condensed guide to get you started with Spec Kit in the Omega project immediately.

## Prerequisites Check

Spec Kit is already installed in Omega. Verify it's working:

```bash
specify check
```

You should see GitHub Copilot and other tools listed as available.

## 5-Minute Workflow

### 1. Create Project Principles (2 minutes)

In GitHub Copilot, run:

```
/speckit.constitution Create principles for Omega agentic migration system focused on:
- Intelligent automation for monolith-to-microservices migration
- Code quality and maintainability standards
- Professional communication (no emojis)
- Docker containerization and Python development
- Integration with existing Omega tools and Spring Modulith reference
```

### 2. Specify Your First Feature (1 minute)

```
/speckit.specify Build a dependency analyzer that can parse Java Spring Boot applications and identify service boundaries based on package structure, class dependencies, and annotation patterns.
```

### 3. Create Implementation Plan (1 minute)

```
/speckit.plan Use Python with AST parsing libraries, integrate with existing Omega tools structure, output JSON dependency graphs, and provide Docker container execution.
```

### 4. Generate Tasks and Implement (1 minute)

```
/speckit.tasks
/speckit.implement
```

## Essential Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `/speckit.constitution` | Set project principles | Create standards for migration tools |
| `/speckit.specify` | Define requirements | Describe what to build |
| `/speckit.plan` | Technical planning | Choose tech stack and architecture |
| `/speckit.tasks` | Break down work | Generate actionable tasks |
| `/speckit.implement` | Build the feature | Execute the implementation |

## Quality Enhancement Commands

- `/speckit.clarify` - Ask questions about unclear requirements
- `/speckit.analyze` - Check consistency across specifications
- `/speckit.checklist` - Generate validation checklists

## Omega-Specific Tips

1. **Reference existing structure**: Always mention `/workspace/tools/`, `/workspace/data/codebase/spring-modulith/`, and existing documentation
2. **Use Docker context**: Leverage the dev container environment in your plans
3. **Follow Omega standards**: Professional communication, no emojis, comprehensive documentation
4. **Integrate with checkpoints**: Create checkpoints before and after major spec work

## Common Omega Use Cases

### Migration Analysis Engine
```
/speckit.specify Build an engine that analyzes Spring Boot monoliths and recommends microservices boundaries based on domain-driven design principles.
```

### Dependency Mapper
```
/speckit.specify Create a tool that visualizes dependencies between classes, packages, and modules in Spring applications to guide decomposition strategies.
```

### Refactoring Assistant
```
/speckit.specify Develop an assistant that suggests code refactoring patterns for extracting microservices from monolithic Spring Boot applications.
```

## Troubleshooting

**Slash commands not working?**
- Ensure you're in GitHub Copilot
- Check that `.speckit` directory exists in `/workspace`
- Restart your IDE

**CLI commands failing?**
```bash
# Reinstall if needed
./tools/src/setup-speckit.sh --reinstall

# Check system status
specify check
```

## Next Steps

1. Start with `/speckit.constitution` to establish project principles
2. Pick a migration-related feature to specify
3. Follow the 5-step workflow above
4. Use quality commands for complex features
5. Integrate results with Omega's existing tools and documentation

See the full [README.md](README.md) for comprehensive documentation and advanced usage patterns.