# WorkflowWiz

<p align="center">
  <img src=".github/logo.png" alt="WorkflowWiz Logo" width="200"/>
  <br/>
  <b>No-code Visual Workflow Automation for DevOps</b>
</p>

<p align="center">
  <a href="https://pypi.org/project/workflowwiz/">
    <img src="https://img.shields.io/pypi/v/workflowwiz?style=flat-square" alt="PyPI Version"/>
  </a>
  <a href="https://pypi.org/project/workflowwiz/">
    <img src="https://img.shields.io/pypi/pyversions/workflowwiz?style=flat-square" alt="Python Versions"/>
  </a>
  <a href="https://github.com/sdotwinter/workflowwiz/blob/main/LICENSE">
    <img src="https://img.shields.io/pypi/l/workflowwiz?style=flat-square" alt="License"/>
  </a>
</p>

---

## What is WorkflowWiz?

WorkflowWiz is a CLI tool that lets you create, visualize, and run automated DevOps workflows using simple YAML or JSON configuration files. No coding required—just define your steps and let WorkflowWiz handle the rest.

### Features

- 📋 **Visual Workflow Display** - See your entire pipeline at a glance with color-coded status indicators
- 🔄 **Step-by-Step Execution** - Execute workflows with real-time progress tracking
- 📦 **Template Library** - Quick-start templates for common DevOps tasks
- 🐳 **Docker & K8s Ready** - Built-in support for container workflows
- 🔀 **Conditional Steps** - Skip steps based on conditions
- 📊 **Rich Output** - Color-coded terminal output for easy debugging

## Installation

### From PyPI (Recommended)

```bash
pip install workflowwiz
```

### From Source

```bash
git clone https://github.com/sdotwinter/workflowwiz.git
cd workflowwiz
pip install -e .
```

## Quick Start

### 1. Create a new workflow

```bash
workflowwiz init my-deploy --description "Deploy to production"
```

This creates a `workflow.yaml` file:

```yaml
name: my-deploy
description: Deploy to production
version: 1.0.0
variables:
  ENV: production
  REGION: us-west-2
steps:
  - id: step_1
    name: Check prerequisites
    command: echo "Checking prerequisites..."
    enabled: true
  - id: step_2
    name: Deploy application
    command: echo "Deploying application..."
    enabled: true
  - id: step_3
    name: Run health check
    command: echo "Running health check..."
    enabled: true
```

### 2. Visualize your workflow

```bash
workflowwiz visualize workflow.yaml
```

Output:
```
▶ my-deploy
Deploy to production
Version: 1.0.0

Variables:
  • ENV = production
  • REGION = us-west-2

Steps:
  ○ Check prerequisites
  ○ Deploy application
  ○ Run health check
```

### 3. Run the workflow

```bash
workflowwiz run workflow.yaml
```

Output:
```
▶ my-deploy
Deploy to production
Version: 1.0.0

Steps:
  ◐ Check prerequisites
  ○ Deploy application
  ○ Run health check

  ● Check prerequisites done (0.02s)

  ● Deploy application done (0.02s)

  ● Run health check done (0.02s)

██████████████████████████████ 100%

✔ Workflow COMPLETED successfully
```

### 4. Dry run (preview without executing)

```bash
workflowwiz run workflow.yaml --dry-run
```

## Available Templates

```bash
workflowwiz templates
```

- **Docker Deploy** - Build and deploy Docker container
- **Kubernetes Rollout** - Deploy to Kubernetes with rollback
- **CI/CD Pipeline** - Full CI/CD pipeline
- **Database Migration** - Run database migrations safely
- **Server Health Check** - Comprehensive server health check

## Configuration Reference

### Workflow Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Workflow name |
| `description` | string | No | Human-readable description |
| `version` | string | No | Semantic version (default: 1.0.0) |
| `variables` | object | No | Key-value pairs for variable substitution |
| `steps` | array | Yes | List of workflow steps |

### Step Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique step identifier |
| `name` | string | Yes | Human-readable step name |
| `command` | string | Yes | Shell command to execute |
| `enabled` | boolean | No | Whether to execute (default: true) |

### Variable Substitution

Use `{{variable}}` syntax in commands:

```yaml
variables:
  REGION: us-west-2
  ENV: production

steps:
  - id: deploy
    name: Deploy to {{ENV}}
    command: kubectl apply -f deploy-{{REGION}}.yaml
```

## Example Workflows

### Docker Build & Push

```yaml
name: Docker Build & Push
description: Build Docker image and push to registry
version: 1.0.0
variables:
  IMAGE_NAME: myapp
  TAG: latest
  REGISTRY: docker.io

steps:
  - id: build
    name: Build Docker image
    command: docker build -t $IMAGE_NAME:$TAG .

  - id: tag
    name: Tag for registry
    command: docker tag $IMAGE_NAME:$TAG $REGISTRY/$IMAGE_NAME:$TAG

  - id: push
    name: Push to registry
    command: docker push $REGISTRY/$IMAGE_NAME:$TAG
```

### Kubernetes Rollout with Health Check

```yaml
name: K8s Deploy with Health Check
description: Deploy to Kubernetes and verify health
version: 1.0.0

steps:
  - id: apply
    name: Apply Kubernetes manifests
    command: kubectl apply -f deployment.yaml

  - id: wait
    name: Wait for rollout
    command: kubectl rollout status deployment/myapp

  - id: health
    name: Check health endpoint
    command: curl -f http://myapp/health

  - id: status
    name: Show deployment status
    command: kubectl get pods,svc
```

### What's Sponsorware?

Sponsorware is a licensing model where:
1. The source code is freely available (MIT License)
2. **New features** are developed exclusively for sponsors
3. Sponsor-only features are locked until you sponsor

### Current Sponsor Features

- ✨ **Advanced Variable Substitution** - Environment-based variable loading
- ✨ **Workflow Chaining** - Run multiple workflows in sequence
- ✨ **Secret Management** - Securely store and inject secrets
- ✨ **Slack/Discord Notifications** - Get notified on workflow completion

### How to Sponsor

1. Go to [github.com/sponsors/sdotwinter](https://github.com/sponsors/sdotwinter)
2. Select your tier
3. You'll receive access to sponsor-only features within 24 hours

### Former Sponsorware (Now Free!)

The following features were previously sponsor-only but are now free:

- ✅ Basic CLI tool (this repo)
- ✅ YAML/JSON workflow definitions
- ✅ Visual workflow display
- ✅ Template library
- ✅ Step-by-step execution

---

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- 📖 [Documentation](https://workflowwiz.dev/docs)
- 🐛 [Issue Tracker](https://github.com/sdotwinter/workflowwiz/issues)
- 💬 [Discord Community](https://discord.gg/workflowwiz)
- 📧 [Email Support](mailto:hello@workflowwiz.dev)

---

<p align="center">
  Made with ❤️ by the WorkflowWiz team
</p>

## Sponsorship

This project follows the App Factory sponsorship model:

### $5/month - Supporter
- Sponsor badge on your GitHub profile
- Monthly sponsor update

### $25/month - Builder Circle
- Everything in Supporter
- Name listed in project Sponsors section (monthly refresh)
- Access to private sponsor Discord channel

### $100/month - Priority Maintainer
- Everything in Builder Circle
- Priority bug triage for your reports (max 2 issues/month)
- Response target: within 5 business days

### $1,000/month - Operator Advisory
- Everything in Priority Maintainer
- Dedicated async advisory support
- Service boundary: guidance and review only (no custom development included)

### $5,000 one-time - Custom Project Engagement
- Custom contract engagement
- Discovery required before kickoff
- Scope, timeline, and deliverables agreed in writing

Sponsor: https://github.com/sponsors/sdotwinter

