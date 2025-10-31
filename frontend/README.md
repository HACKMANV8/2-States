# TestGPT Frontend

AI-powered automated testing agent that integrates with Slack and GitHub to perform Q/A testing on features.

## Overview

TestGPT is a modern web application built with Next.js that enables automated browser testing through natural language prompts. Users can configure test scenarios without writing code, and TestGPT generates and executes Playwright tests automatically.

## Features

### Core Functionality
- **Test Configuration Panel**: Create test scenarios using plain English prompts
- **Network Simulation**: Test with different bandwidth conditions (3G, 4G/5G, default)
- **Device Testing**: Configure tests for Desktop, Android, and iOS devices
- **Screen Size Configuration**: Custom screen resolutions and aspect ratios
- **Feature Flags**: Specify feature flags as JSON for conditional testing

### Test Execution & Monitoring
- **Test Dashboard**: Overview of all test executions with status cards
- **Test History**: View detailed logs and results from past test runs
- **Real-time Status**: Track running, passed, and failed tests
- **AI-Generated Tests**: Store and reuse AI-generated test code

### Integrations (Placeholder UI)
- **Slack Integration**: Trigger tests via Slack messages (e.g., "@TestGPT test this feature")
- **GitHub Integration**: Automatically test pull requests and post results as PR comments

## Tech Stack

- **Next.js 16** (App Router) + **React 19** + **TypeScript**
- **Tailwind CSS 4** + **Radix UI** + **shadcn/ui**
- **Drizzle ORM** + **SQLite**
- **date-fns**, **Lucide React**, **Zod**

## Getting Started

### Installation

```bash
# Install dependencies
npm install

# Set up database
npx drizzle-kit generate
npx drizzle-kit push

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

### Creating Your First Test

1. Navigate to **Test Configuration**
2. Enter a test name and prompt in plain English
3. Configure network mode, device type, and screen size
4. Click **Save Test Configuration**

Example prompt:
```
Navigate to the login page, enter valid credentials,
and verify successful login to the dashboard.
```

## Project Structure

```
frontend/
├── app/
│   ├── (dashboard)/          # Dashboard routes
│   │   ├── page.tsx          # Main dashboard
│   │   ├── test-config/      # Test configuration
│   │   ├── test-executions/  # Test history
│   │   ├── integrations/     # Slack & GitHub
│   │   └── settings/         # Settings
│   └── api/                  # API routes
├── components/
│   ├── ui/                   # Base UI components
│   ├── dashboard/            # Dashboard components
│   └── navigation.tsx        # Main navigation
├── lib/
│   ├── db/                   # Database schema & client
│   └── utils.ts
└── drizzle.config.ts
```

## API Endpoints

- `GET/POST /api/tests` - Test configurations
- `GET/POST /api/executions` - Test executions

## Key Features

### 1. Test Dashboard
View test execution statistics with status cards showing total, passed, failed, and running tests.

### 2. Test Configuration
Create tests without code using natural language prompts. Configure:
- Network conditions (low/high bandwidth)
- Device types (Desktop/Android/iOS)
- Screen sizes and aspect ratios
- Feature flags (JSON)

### 3. Test Executions
Browse all test runs with:
- Status indicators (pending/running/passed/failed)
- Execution details and logs
- GitHub PR integration info
- Slack trigger metadata

### 4. Integration Pages
- **Slack**: Connect workspace, configure triggers
- **GitHub**: Monitor repos, auto-test PRs

## Adapted from DreamOps

This frontend adapts patterns from [DreamOps](https://github.com/SkySingh04/DreamOps):
- Dashboard layout & navigation
- Card-based UI components
- Settings architecture
- Responsive design

Key differences: TestGPT focuses on testing automation (not incident management) and uses prompt-based testing triggered by Slack/GitHub.

## Development Status

**Phase 1 (Complete):**
- ✅ Full UI implementation
- ✅ Database schema
- ✅ API routes
- ✅ Placeholder integration pages

**Phase 2 (Planned):**
- Real Slack OAuth integration
- GitHub App for PR monitoring
- Playwright MCP execution
- Authentication & user management
- Real-time updates

## Database Schema

- `test_configurations`: Reusable test scenarios
- `test_executions`: Test run records with logs
- `integration_settings`: Slack/GitHub config
- `test_defaults`: Default parameters

## Available Scripts

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run start` - Production server
- `npx drizzle-kit studio` - Database GUI

## Known Limitations

- SQLite database (not production-ready)
- No authentication
- Integrations are placeholder UI
- No real-time updates
- Test execution requires Playwright MCP integration

---

Built with Next.js 16, TypeScript, and Tailwind CSS.
