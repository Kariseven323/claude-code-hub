# Claude Code Hub 重写技术栈

## 架构决策

- **开发模式**：前后端分离
- **部署模式**：单体（Go 嵌入前端静态文件）
- **API 风格**：RESTful

---

## 后端技术栈 (Go)

| 类别 | 技术 | 版本要求 | 说明 |
|------|------|----------|------|
| 语言 | Go | ≥1.22 | - |
| Web 框架 | Gin | v1.10+ | 高性能，中间件生态丰富 |
| 数据库驱动 | pgx/v5 | v5.x | PostgreSQL 原生驱动，性能优于 database/sql |
| 数据库代码生成 | sqlc | v1.27+ | 类型安全，编译时检查 |
| 数据库迁移 | golang-migrate | v4.x | 支持嵌入式迁移文件 |
| Redis 客户端 | go-redis/v9 | v9.x | 支持 Lua 脚本、Pipeline |
| 配置管理 | Viper | v1.x | 多格式支持，环境变量绑定 |
| 日志 | Zap | v1.x | 结构化日志，高性能 |
| API 文档 | Swag | v1.x | 注释生成 OpenAPI 3.0 |
| 静态文件嵌入 | embed | 标准库 | 单体部署用 |

---

## 前端技术栈 (React)

| 类别 | 技术 | 版本要求 | 说明 |
|------|------|----------|------|
| 框架 | React | v18+ | - |
| 构建工具 | Vite | v6+ | 快速 HMR，生产构建优化 |
| 路由 | React Router | v7+ | 稳定，文档完善 |
| 状态管理 | Zustand | v5+ | 轻量，API 简洁 |
| 请求管理 | TanStack Query | v5+ | 缓存、重试、乐观更新 |
| HTTP 客户端 | Axios | v1.x | 拦截器，错误处理 |
| UI 组件 | shadcn/ui | latest | 可定制，Tailwind 原生 |
| 样式 | Tailwind CSS | v3.4+ | 原子化 CSS |
| 类型 | TypeScript | v5+ | - |

---

## 基础设施

| 类别 | 技术 | 说明 |
|------|------|------|
| 数据库 | PostgreSQL | ≥14 |
| 缓存/限流 | Redis | ≥7.0 |
| 容器化 | Docker + Docker Compose | 开发与部署 |

---

## 包管理

| 端 | 工具 |
|----|------|
| Go | Go Modules |
| 前端 | Bun |
