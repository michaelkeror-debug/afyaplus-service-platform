Contributing to AfyaPlus

1. Branch Policy

AfyaPlus uses Git for version control.

- "main" is the stable and production branch.
- New development should use feature or task branches.
- Changes should be tested before being merged into "main".

Branch naming conventions:

- "feature/<description>" — new functionality
- "fix/<description>" — bug fixes
- "security/<description>" — security changes
- "docs/<description>" — documentation changes

2. Commit Policy

Commits should represent a single logical change and use clear, descriptive messages.

Examples:

Add MCP delivery ETA tool
Fix JWT authorization check
Add agent grounding gate
Document Docker runtime secrets

Meaningful commit history should be maintained so changes can be traced to their purpose.

3. Merge Conflicts

When a merge conflict occurs, contributors should:

1. Identify the conflicting files.
2. Resolve the conflict while preserving the intended functionality.
3. Run the relevant tests.
4. Stage the resolved files.
5. Complete the merge commit.

Example:

git status
git add <resolved-files>
git commit -m "Resolve merge conflict"

4. Versioning

AfyaPlus follows Semantic Versioning:

MAJOR.MINOR.PATCH

- MAJOR — breaking or incompatible changes
- MINOR — backward-compatible functionality
- PATCH — backward-compatible fixes

Examples:

v1.0.0 → initial production release
v1.1.0 → new functionality
v1.1.1 → bug fix
v2.0.0 → breaking change

Production releases are identified using Git tags.

5. Docker Release Policy

Docker image tags must match the corresponding Git release tag.

Example:

Git tag:      v1.0.0
Docker image: afyaplus-triage:v1.0.0

This provides traceability between source code and the container release.

6. Testing and Security

Changes should be tested before release:

python -m pytest -v

MCP tools must include validation testing, including at least one deliberate invalid request.

Secrets must never be committed to Git or baked into Docker images. API keys, passwords, JWT secrets, credentials, and ".env" files containing secrets must be supplied at runtime through the deployment environment.

7. Release Checklist

Before a production release:

- [ ] Changes committed to Git
- [ ] Tests pass
- [ ] Authentication and authorization verified
- [ ] MCP tools tested, including invalid input
- [ ] Secrets excluded from source and Docker image
- [ ] Semantic Git tag created
- [ ] Docker tag matches Git tag
- [ ] Docker image size documented
- [ ] Relevant test, version-control, and observability evidence captured

Example:

git add .
git commit -m "Prepare production release"
git tag v1.0.0
docker build -t afyaplus-triage:v1.0.0 .