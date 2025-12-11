# Project Context

## Purpose
Claude Code Hub 是一个智能 AI API 代理中转服务平台，面向团队提供多供应商统一接入、弹性调度与精细化运营能力。核心目标：
- 统一管理多家 AI 供应商（Claude、Codex、Gemini、OpenAI Compatible）
- 智能负载均衡与熔断保护，保障高可用
- 实时监控、日志审计与成本追踪
- Session 粘性优化缓存命中率

## Tech Stack
- **Runtime**: Bun ≥ 1.3, Node.js ≥ 20
- **Framework**: Next.js 15 (App Router) + Hono (API 路由)
- **Language**: TypeScript
- **Frontend**: React 19, Tailwind CSS, shadcn/ui
- **Database**: PostgreSQL + Drizzle ORM
- **Cache/Queue**: Redis (限流、Session 追踪)
- **Deployment**: Docker Compose

## Project Conventions

### Code Style
- Biome 配置：2 空格缩进、双引号、尾随逗号
- Tailwind 类与 JSX 同行，遵循 src/app 现有模式
- 工具函数单一职责，复用 src/lib 和 src/actions 中的 helpers
- 语气风格：简洁 + emoji（参考 README）

### Architecture Patterns
- **App 层**: `src/app/` - Dashboard、Settings、API Actions
- **Proxy 核心**: `src/app/v1/_lib/proxy-handler.ts` - Auth → Session → RateLimit → Provider → Forward → Response
- **业务逻辑**: `src/lib/` - 限流、Session、熔断器、代理、价格同步
- **数据访问**: `src/repository/` - Drizzle ORM 查询封装
- **API 文档**: Server Actions 自动生成 OpenAPI 3.1.0

### Testing Strategy
- 提交前必须运行：`bun run lint && bun run typecheck`
- CI 运行 Docker Build Test
- 本地验证容器构建：`docker compose build`

### Git Workflow
- **目标分支**: 所有 PR 必须指向 `dev`，`main` 仅用于发布
- **分支命名**: `feature/<desc>`, `fix/<scope>`, `hotfix/<scope>`, `chore/<scope>`
- **提交格式**: Conventional Commits（`feat:`, `fix:`, `chore:`, `refactor:`, `test:`）
- **合并策略**: Squash and merge

## Domain Context
- **供应商类型**: claude, claude-auth, codex, gemini-cli, openai-compatible
- **调度策略**: 权重 + 优先级 + 分组，内置熔断保护，最多 3 次故障转移
- **Session 管理**: 5 分钟上下文缓存，记录决策链，避免频繁切换供应商
- **限流维度**: RPM、金额（5 小时/周/月）、并发 Session
- **Fail-Open**: Redis 不可用时自动降级，不影响服务可用性

## Important Constraints
- 开源项目，开发人力有限（志愿者驱动）
- 赞助驱动的可持续发展模式
- MIT 许可证
- 用户自带供应商（BYOP 模式）

## External Dependencies
- **AI Providers**: Anthropic Claude API, OpenAI API, Google Gemini API
- **Database**: PostgreSQL（必需）
- **Cache**: Redis（限流和 Session 追踪，支持 Fail-Open 降级）
- **Container**: Docker + Docker Compose
