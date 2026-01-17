# Enterprise AI Development Platform

An AI-powered development platform that safely modifies existing enterprise multi-repo systems with intelligent planning, scoped changes, and automated PR creation.

## 🎯 MVP Goal

Connect multiple repositories, describe a feature, and the system will:
1. **Understand the codebase** without hallucinations
2. Produce **phased execution plans** with blast-radius analysis
3. Make **scoped changes** to the right repos/files
4. Open **PRs** with proper descriptions + test evidence
5. Maintain **centralized project memory** for session continuity

## 🏗️ Architecture

### Core Services
- **API Gateway** (FastAPI) - REST API and authentication
- **Web Dashboard** (React) - Project management UI
- **Agent Workers** (Python) - AI agent execution engine
- **PostgreSQL + pgvector** - Primary data and semantic search
- **Redis Streams** - Event bus for agent orchestration
- **S3/GCS** - Artifact storage

### Agent Types
- **Strategic Planner** - Enterprise brain for safe planning
- **Backend Agent** - Scoped backend modifications
- **Frontend Agent** - UI implementation with design systems
- **Code Reviewer** - Security and pattern compliance
- **QA Agent** - Automated testing and quality gates
- **UX Designer** - Wireframes and design specifications

## 📁 Project Structure

```
enterprise-ai-dev-platform/
├── docs/                          # Architecture documentation
│   ├── database-schema.sql        # PostgreSQL schema
│   ├── event-schemas.md          # Redis Stream events
│   ├── agent-contracts.md        # Agent interfaces
│   └── api-specification.md      # REST API docs
├── services/
│   ├── api/                      # FastAPI gateway
│   ├── agents/                   # Python agent workers
│   ├── web/                      # React dashboard
│   └── shared/                   # Shared utilities
├── migrations/                   # Database migrations
├── scripts/                      # Development scripts
├── tests/                        # Test suites
└── docker/                       # Docker configurations
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+ with pgvector
- Redis 6+
- Docker (optional)

### Development Setup
```bash
# Clone and setup
git clone <repository>
cd enterprise-ai-dev-platform

# Setup Python environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Setup Node.js environment
cd services/web
npm install
cd ../..

# Setup database
createdb enterprise_ai_dev
psql enterprise_ai_dev < docs/database-schema.sql

# Start services
docker-compose up -d redis postgres
python -m services.api.main
cd services/web && npm start
```

## 📋 MVP Acceptance Tests

1. **Multi-repo onboarding**: Connect 5-10 repos, generate discovery report
2. **Feature planning**: "Add pagination to Orders list" → shows impacted repos + API changes
3. **Safe changes**: Scoped modifications, PRs in correct repos only
4. **Memory resume**: New session continues without rereading everything
5. **Auditability**: Every decision links to artifact or code evidence

## 🔐 Security & Enterprise Features

- **GitHub App Integration** - Enterprise-grade repository access
- **RBAC** - Role-based access control (Admin/Editor/Viewer)
- **Audit Trail** - Complete event logging and replay
- **Token Control** - Cost management with per-agent limits
- **Pattern Compliance** - Enforces coding standards and security rules

## 📊 Current Status

- [x] Database schema design
- [x] Event system architecture
- [x] Agent contracts specification
- [x] API specification
- [ ] Core service implementation
- [ ] Agent development
- [ ] Web dashboard
- [ ] Integration testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Ensure all acceptance tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built for enterprise teams that need AI assistance without the chaos.**
