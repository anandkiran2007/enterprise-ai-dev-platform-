# Event Schemas for Redis Streams

## Core Event Types

### 1. Repository Events

#### `repo.connected`
```json
{
  "event_id": "uuid",
  "type": "repo.connected",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "repository_id": "uuid",
    "project_id": "uuid",
    "full_name": "org/repo-name",
    "clone_url": "https://github.com/org/repo.git",
    "access_type": "github_app"
  }
}
```

#### `repo.sync.started`
```json
{
  "event_id": "uuid",
  "type": "repo.sync.started",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "repository_id": "uuid",
    "sync_type": "full|incremental",
    "trigger": "manual|webhook|scheduled"
  }
}
```

#### `repo.sync.completed`
```json
{
  "event_id": "uuid",
  "type": "repo.sync.completed",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "repository_id": "uuid",
    "file_tree_hash": "sha256-hash",
    "files_processed": 1250,
    "chunks_indexed": 342,
    "detected_changes": ["package.json", "src/api/routes/*.js"]
  }
}
```

### 2. Discovery Events

#### `discovery.started`
```json
{
  "event_id": "uuid",
  "type": "discovery.started",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "repository_id": "uuid",
    "discovery_type": "full|incremental"
  }
}
```

#### `discovery.completed`
```json
{
  "event_id": "uuid",
  "type": "discovery.completed",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "repository_id": "uuid",
    "discovery_report_id": "uuid",
    "detected_stack": {
      "language": "nodejs",
      "framework": "express",
      "database": "postgresql"
    },
    "service_boundaries": ["api", "auth", "orders"],
    "risk_score": 0.3
  }
}
```

### 3. Feature Request Events

#### `feature.request.created`
```json
{
  "event_id": "uuid",
  "type": "feature.request.created",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "feature_request_id": "uuid",
    "project_id": "uuid",
    "title": "Add pagination to Orders list",
    "description": "User wants pagination for large order datasets",
    "requester_id": "uuid"
  }
}
```

### 4. Planning Events

#### `planning.started`
```json
{
  "event_id": "uuid",
  "type": "planning.started",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "feature_request_id": "uuid",
    "execution_plan_id": "uuid",
    "planner_agent_id": "uuid"
  }
}
```

#### `planning.completed`
```json
{
  "event_id": "uuid",
  "type": "planning.completed",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "execution_plan_id": "uuid",
    "phases": [
      {
        "phase_number": 1,
        "name": "API Contract Update",
        "agent_type": "backend",
        "estimated_duration": "2h",
        "risk_level": "low"
      }
    ],
    "blast_radius": {
      "repositories_affected": ["api-service", "frontend-app"],
      "files_affected": 15,
      "api_endpoints_changed": 3
    }
  }
}
```

### 5. Agent Execution Events

#### `agent.execution.started`
```json
{
  "event_id": "uuid",
  "type": "agent.execution.started",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "agent_execution_id": "uuid",
    "agent_type": "backend",
    "phase_number": 1,
    "execution_plan_id": "uuid",
    "input_data": {
      "files_to_modify": ["src/api/orders.js"],
      "requirements": "Add pagination with limit/offset"
    }
  }
}
```

#### `agent.execution.completed`
```json
{
  "event_id": "uuid",
  "type": "agent.execution.completed",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "agent_execution_id": "uuid",
    "output_data": {
      "files_modified": ["src/api/orders.js"],
      "tests_generated": ["tests/orders.test.js"],
      "changes_summary": "Added pagination middleware and updated routes"
    },
    "token_usage": {
      "prompt_tokens": 1250,
      "completion_tokens": 890,
      "total_tokens": 2140
    }
  }
}
```

#### `agent.execution.failed`
```json
{
  "event_id": "uuid",
  "type": "agent.execution.failed",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "agent_execution_id": "uuid",
    "error_message": "Failed to parse existing API contract",
    "error_type": "validation_error",
    "retry_count": 2
  }
}
```

### 6. Pull Request Events

#### `pr.created`
```json
{
  "event_id": "uuid",
  "type": "pr.created",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "pull_request_id": "uuid",
    "repository_id": "uuid",
    "agent_execution_id": "uuid",
    "title": "feat: Add pagination to Orders API",
    "branch_name": "feature/orders-pagination",
    "pr_number": 1234,
    "url": "https://github.com/org/repo/pull/1234"
  }
}
```

#### `pr.merged`
```json
{
  "event_id": "uuid",
  "type": "pr.merged",
  "timestamp": "2024-01-16T20:01:00Z",
  "data": {
    "pull_request_id": "uuid",
    "merged_by": "uuid",
    "merge_commit_sha": "abc123"
  }
}
```

## Redis Streams Configuration

### Stream Names
- `repository-events` - Repo sync and discovery events
- `feature-events` - Feature request lifecycle
- `planning-events` - Planning agent events
- `execution-events` - Agent execution events
- `pr-events` - Pull request lifecycle

### Consumer Groups
- `sync-workers` - Repository sync workers
- `discovery-workers` - Discovery analysis workers
- `agent-workers` - Agent execution workers
- `pr-workers` - PR management workers

### Event Processing Rules
1. **Exactly-once processing** using consumer groups
2. **Event ordering** per aggregate (repository, feature_request, etc.)
3. **Dead letter queue** for failed events after 3 retries
4. **Event replay** capability for debugging and recovery

### Event Metadata
```json
{
  "event_id": "uuid",
  "type": "string",
  "timestamp": "ISO8601",
  "correlation_id": "uuid", // Links related events
  "causation_id": "uuid",   // Event that triggered this
  "source": "string",       // Service that produced event
  "version": "1.0"
}
```
