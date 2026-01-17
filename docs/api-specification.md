# API Specification (FastAPI)

## Core API Endpoints

### Authentication & Authorization

```python
# POST /auth/github
{
  "code": "string",  # GitHub OAuth code
  "redirect_uri": "string"
}
# Response
{
  "access_token": "jwt_token",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "organizations": [
    {
      "id": "uuid",
      "name": "Acme Corp",
      "role": "admin"
    }
  ]
}
```

### Organizations

```python
# GET /organizations
# Response
{
  "organizations": [
    {
      "id": "uuid",
      "name": "Acme Corp",
      "slug": "acme-corp",
      "created_at": "2024-01-16T20:01:00Z",
      "member_count": 5
    }
  ]
}

# POST /organizations
{
  "name": "New Organization",
  "slug": "new-org"
}

# GET /organizations/{org_id}/members
{
  "members": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe"
      },
      "role": "admin",
      "created_at": "2024-01-16T20:01:00Z"
    }
  ]
}
```

### Projects

```python
# GET /organizations/{org_id}/projects
{
  "projects": [
    {
      "id": "uuid",
      "name": "E-commerce Platform",
      "description": "Main e-commerce application",
      "status": "active",
      "repository_count": 5,
      "last_activity": "2024-01-16T20:01:00Z",
      "created_at": "2024-01-16T20:01:00Z"
    }
  ]
}

# POST /organizations/{org_id}/projects
{
  "name": "New Project",
  "description": "Project description"
}

# GET /projects/{project_id}
{
  "id": "uuid",
  "name": "E-commerce Platform",
  "description": "Main e-commerce application",
  "status": "active",
  "memory_snapshot": {...},
  "repositories": [...],
  "created_at": "2024-01-16T20:01:00Z"
}
```

### Repository Management

```python
# GET /projects/{project_id}/repositories
{
  "repositories": [
    {
      "id": "uuid",
      "name": "api-service",
      "full_name": "acme/api-service",
      "clone_url": "https://github.com/acme/api-service.git",
      "branch": "main",
      "sync_status": "completed",
      "last_synced_at": "2024-01-16T20:01:00Z",
      "discovery_status": "completed",
      "detected_stack": {
        "language": "nodejs",
        "framework": "express"
      }
    }
  ]
}

# POST /projects/{project_id}/repositories
{
  "full_name": "acme/new-repo",
  "access_type": "github_app",  # or "pat", "ssh"
  "branch": "main"
}

# POST /repositories/{repo_id}/sync
{
  "sync_type": "full"  # or "incremental"
}

# GET /repositories/{repo_id}/discovery
{
  "id": "uuid",
  "detected_stack": {...},
  "service_boundaries": [...],
  "dependency_graph": {...},
  "risk_hotspots": [...],
  "file_index_summary": {...}
}
```

### Feature Requests

```python
# GET /projects/{project_id}/features
{
  "features": [
    {
      "id": "uuid",
      "title": "Add pagination to Orders list",
      "description": "Users need pagination for large order datasets",
      "status": "planning",
      "requester": {
        "id": "uuid",
        "name": "John Doe"
      },
      "execution_plan": {
        "id": "uuid",
        "status": "draft",
        "phases": [...]
      },
      "created_at": "2024-01-16T20:01:00Z"
    }
  ]
}

# POST /projects/{project_id}/features
{
  "title": "Feature title",
  "description": "Detailed description",
  "priority": "high"  # high, medium, low
}

# GET /features/{feature_id}
{
  "id": "uuid",
  "title": "Add pagination to Orders list",
  "description": "Detailed description",
  "status": "planning",
  "execution_plan": {...},
  "agent_executions": [...],
  "pull_requests": [...],
  "created_at": "2024-01-16T20:01:00Z"
}
```

### Execution Plans

```python
# GET /features/{feature_id}/plan
{
  "id": "uuid",
  "feature_request_id": "uuid",
  "status": "approved",
  "phases": [
    {
      "phase_number": 1,
      "name": "API Contract Update",
      "agent_type": "backend",
      "estimated_duration": "2h",
      "risk_level": "low",
      "repositories_affected": ["api-service"],
      "files_affected": ["src/api/orders.js"],
      "dependencies": []
    },
    {
      "phase_number": 2,
      "name": "Frontend Implementation",
      "agent_type": "frontend",
      "estimated_duration": "4h",
      "risk_level": "medium",
      "repositories_affected": ["frontend-app"],
      "files_affected": ["src/components/OrdersList.jsx"],
      "dependencies": [1]
    }
  ],
  "blast_radius": {
    "repositories_affected": 2,
    "files_affected": 15,
    "api_endpoints_changed": 3,
    "risk_score": 0.4
  },
  "risk_assessment": {
    "breaking_changes": false,
    "database_migrations": false,
    "security_impact": "low",
    "performance_impact": "low"
  },
  "test_strategy": {
    "unit_tests_required": true,
    "integration_tests_required": true,
    "e2e_tests_required": false
  }
}

# POST /features/{feature_id}/plan/approve
{
  "approved": true,
  "notes": "Plan looks good, proceed with implementation"
}
```

### Agent Executions

```python
# GET /plans/{plan_id}/executions
{
  "executions": [
    {
      "id": "uuid",
      "agent_type": "backend",
      "phase_number": 1,
      "status": "completed",
      "input_data": {...},
      "output_data": {...},
      "token_usage": {
        "prompt_tokens": 1250,
        "completion_tokens": 890,
        "total_tokens": 2140
      },
      "started_at": "2024-01-16T20:01:00Z",
      "completed_at": "2024-01-16T20:03:00Z"
    }
  ]
}

# GET /executions/{execution_id}
{
  "id": "uuid",
  "agent_type": "backend",
  "status": "completed",
  "input_data": {
    "files_to_modify": ["src/api/orders.js"],
    "requirements": "Add pagination with limit/offset"
  },
  "output_data": {
    "files_modified": ["src/api/orders.js"],
    "tests_generated": ["tests/orders.test.js"],
    "changes_summary": "Added pagination middleware"
  },
  "artifacts": [
    {
      "id": "uuid",
      "type": "code_changes",
      "storage_path": "artifacts/execution_123/changes.zip"
    }
  ]
}
```

### Pull Requests

```python
# GET /projects/{project_id}/pull-requests
{
  "pull_requests": [
    {
      "id": "uuid",
      "repository": {
        "id": "uuid",
        "name": "api-service",
        "full_name": "acme/api-service"
      },
      "title": "feat: Add pagination to Orders API",
      "status": "opened",
      "pr_number": 1234,
      "url": "https://github.com/acme/api-service/pull/1234",
      "agent_execution": {
        "id": "uuid",
        "agent_type": "backend"
      },
      "created_at": "2024-01-16T20:01:00Z"
    }
  ]
}

# GET /pull-requests/{pr_id}
{
  "id": "uuid",
  "title": "feat: Add pagination to Orders API",
  "description": "## Summary\nAdded pagination support to Orders API\n\n## Changes\n- Added pagination middleware\n- Updated route handlers\n- Generated unit tests\n\n## Test Results\n✅ Unit tests: 15/15 passing\n✅ Integration tests: 8/8 passing\n\n## Risk Assessment\n- Breaking changes: None\n- Security impact: Low",
  "repository": {...},
  "agent_execution": {...},
  "status": "opened",
  "url": "https://github.com/acme/api-service/pull/1234",
  "metadata": {
    "files_changed": 5,
    "lines_added": 127,
    "lines_removed": 23,
    "test_coverage": 95
  }
}
```

### Artifacts

```python
# GET /projects/{project_id}/artifacts
{
  "artifacts": [
    {
      "id": "uuid",
      "type": "discovery_report",
      "repository": {
        "id": "uuid",
        "name": "api-service"
      },
      "storage_path": "artifacts/discovery_repo_123.json",
      "size_bytes": 15420,
      "created_at": "2024-01-16T20:01:00Z"
    }
  ]
}

# GET /artifacts/{artifact_id}/download
# Returns file stream or signed URL
```

### Event Stream

```python
# GET /projects/{project_id}/events
{
  "events": [
    {
      "id": "uuid",
      "event_type": "agent.execution.completed",
      "aggregate_id": "uuid",
      "aggregate_type": "agent_execution",
      "data": {...},
      "timestamp": "2024-01-16T20:01:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "total_pages": 10,
    "total_count": 100
  }
}

# WebSocket: /ws/projects/{project_id}/events
# Real-time event streaming
```

### Dashboard & Analytics

```python
# GET /projects/{project_id}/dashboard
{
  "summary": {
    "repository_count": 5,
    "active_features": 3,
    "completed_features": 12,
    "open_prs": 4,
    "total_tokens_used": 125000
  },
  "recent_activity": [...],
  "agent_performance": {
    "strategic_planner": {
      "executions": 15,
      "success_rate": 0.93,
      "avg_tokens": 3500
    }
  },
  "repository_health": [...]
}

# GET /organizations/{org_id}/analytics
{
  "usage_metrics": {
    "total_tokens": 1500000,
    "total_cost": 45.67,
    "active_projects": 3,
    "active_users": 8
  },
  "agent_efficiency": [...],
  "project_velocity": [...]
}
```

## API Response Format

### Success Response
```json
{
  "success": true,
  "data": {...},
  "pagination": {  // Only for list endpoints
    "page": 1,
    "limit": 20,
    "total_pages": 5,
    "total_count": 100
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "repository_name",
      "issue": "Repository name is required"
    }
  },
  "request_id": "uuid"
}
```

## Authentication

### JWT Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "org": "organization_id",
  "role": "admin",
  "exp": 1705440000,
  "iat": 1705353600
}
```

### Required Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Request-ID: <uuid>
```

## Rate Limiting

- **Standard endpoints**: 100 requests/minute
- **Agent execution endpoints**: 10 requests/minute
- **File upload/download**: 50 requests/minute

## Pagination

All list endpoints support:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field (default: created_at)
- `order`: Sort order (asc/desc, default: desc)
