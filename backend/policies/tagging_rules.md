# Tagging Rules Policy

**Version:** 1.0  
**Purpose:** Define the rules and conventions for tagging subtasks with seniority levels and required skills.

## Seniority Tags

Each subtask **must** have exactly **one** seniority tag from the following list:

- `intern`: Suitable for intern-level developers
  - Simple, well-defined tasks with clear instructions
  - Tasks with minimal risk and straightforward requirements
  - Good learning opportunities with guidance available

- `junior`: Suitable for junior developers
  - Tasks with established patterns and examples
  - Well-documented APIs or frameworks
  - Tasks with clear acceptance criteria

- `mid`: Suitable for mid-level developers
  - Tasks requiring some design decisions
  - Integration work with multiple systems
  - Tasks with moderate complexity

- `senior`: Suitable for senior developers
  - Tasks requiring architectural decisions
  - Complex problem-solving or optimization
  - Tasks with high impact or risk

## Skill Tags

Each subtask **must** have at least **one** skill tag indicating the required technical skills or domain knowledge.

### Core Technology Tags

- `python`: Python programming and development
- `javascript`: JavaScript/TypeScript programming
- `typescript`: TypeScript-specific development
- `rust`: Rust programming
- `go`: Go programming
- `java`: Java programming
- `sql`: SQL and database queries

### Domain Tags

- `frontend`: Frontend development (UI, React, Vue, etc.)
- `backend`: Backend development (APIs, services, etc.)
- `api`: API design and implementation
- `database`: Database design, queries, migrations
- `devops`: DevOps, infrastructure, deployment
- `testing`: Testing, QA, test automation
- `security`: Security-related work
- `performance`: Performance optimization
- `documentation`: Documentation writing
- `design`: UI/UX design
- `mobile`: Mobile app development
- `data`: Data engineering, analytics
- `machine-learning`: Machine learning and AI
- `blockchain`: Blockchain development

### Framework/Platform Tags

- `react`: React framework
- `vue`: Vue.js framework
- `angular`: Angular framework
- `fastapi`: FastAPI framework
- `django`: Django framework
- `flask`: Flask framework
- `nodejs`: Node.js platform
- `aws`: Amazon Web Services
- `gcp`: Google Cloud Platform
- `azure`: Microsoft Azure
- `docker`: Docker containerization
- `kubernetes`: Kubernetes orchestration

### Specialized Tags

- `graphql`: GraphQL API development
- `rest`: REST API development
- `websocket`: WebSocket development
- `microservices`: Microservices architecture
- `monitoring`: Monitoring and observability
- `logging`: Logging and log analysis
- `ci-cd`: CI/CD pipeline development
- `git`: Git and version control
- `linux`: Linux system administration
- `networking`: Network programming and configuration

## Tag Format Requirements

1. **Lowercase Only**: All tags must be lowercase
2. **Hyphens for Multi-Word**: Use hyphens to separate words (e.g., `machine-learning`, `ci-cd`)
3. **No Spaces**: Never use spaces in tags
4. **No Special Characters**: Avoid special characters except hyphens
5. **Be Specific**: Use specific tags rather than generic ones
   - Good: `fastapi`, `react`, `postgresql`
   - Poor: `web`, `code`, `stuff`

## Tag Combination Examples

### Example 1: Backend API Development
- **Seniority:** `mid`
- **Skills:** `python`, `fastapi`, `api`, `database`
- **Use Case:** Building a REST API endpoint with database integration

### Example 2: Frontend Component
- **Seniority:** `junior`
- **Skills:** `javascript`, `react`, `frontend`
- **Use Case:** Creating a reusable React component

### Example 3: Database Migration
- **Seniority:** `mid`
- **Skills:** `sql`, `database`, `python`
- **Use Case:** Writing and testing database migration scripts

### Example 4: Infrastructure Setup
- **Seniority:** `senior`
- **Skills:** `devops`, `aws`, `docker`, `kubernetes`
- **Use Case:** Setting up production infrastructure

### Example 5: Testing
- **Seniority:** `junior`
- **Skills:** `testing`, `python`, `api`
- **Use Case:** Writing integration tests for API endpoints

### Example 6: Documentation
- **Seniority:** `intern`
- **Skills:** `documentation`, `api`
- **Use Case:** Writing API documentation

## Validation Rules

When tagging subtasks, ensure:

1. **Exactly One Seniority Tag**: Must have one and only one from: `intern`, `junior`, `mid`, `senior`
2. **At Least One Skill Tag**: Must have at least one skill tag
3. **All Lowercase**: All tags must be lowercase
4. **Valid Format**: Tags must follow the format requirements (no spaces, hyphens for multi-word)
5. **Appropriate Combination**: Seniority level should match task complexity
6. **Relevant Skills**: Skill tags should accurately reflect what the task requires

## Tag Selection Guidelines

### Choosing Seniority Level

Consider:
- **Task Complexity**: How complex is the problem-solving required?
- **Decision Making**: Does the task require architectural or design decisions?
- **Risk Level**: What's the impact if the task is done incorrectly?
- **Guidance Available**: Is there existing code/patterns to follow?

### Choosing Skill Tags

Consider:
- **Primary Technology**: What's the main technology used?
- **Domain Area**: What domain does this fall into (frontend, backend, etc.)?
- **Specific Frameworks**: Are specific frameworks or tools required?
- **Supporting Skills**: What additional skills are needed (testing, database, etc.)?

## Common Tag Patterns

### Full-Stack Feature
- Seniority: `mid` or `senior`
- Skills: `frontend`, `backend`, `api`, `database`, plus specific tech tags

### Bug Fix
- Seniority: `junior` or `mid`
- Skills: Technology tags relevant to the bug area

### New Feature (Backend)
- Seniority: `mid` or `senior`
- Skills: `backend`, `api`, `database`, plus framework tags

### UI Component
- Seniority: `junior` or `mid`
- Skills: `frontend`, framework tag (e.g., `react`), `design` (if needed)

### Infrastructure
- Seniority: `senior`
- Skills: `devops`, cloud platform tag, `docker` or `kubernetes`

## Notes

- Tags should be selected based on what the task **requires**, not what it might use incidentally
- When in doubt, include more specific tags rather than generic ones
- Skill tags should reflect the primary technologies and domains, not every tool mentioned
- Seniority should reflect the complexity and decision-making required, not the person who might do it
