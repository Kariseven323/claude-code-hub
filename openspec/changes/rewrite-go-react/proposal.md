# Change: 使用 Go + React 重写 Claude Code Hub

## Why

当前项目基于 Next.js 15 + Hono + TypeScript 实现，虽然功能完善，但存在以下考量：
- Go 语言在高并发代理场景下性能更优，内存占用更低
- 前后端分离架构更利于独立部署和扩展
- Go 的静态编译特性便于单体部署（嵌入前端静态文件）
- 团队技术栈偏好 Go + React 组合

## What Changes

### 架构变更
- **开发模式**：前后端分离（backend/ + frontend/）
- **部署模式**：单体（Go embed 嵌入前端静态文件）
- **API 风格**：RESTful（保持与现有 API 兼容）

### 后端技术栈（Go）
| 类别 | 技术 | 版本 |
|------|------|------|
| 语言 | Go | ≥1.22 |
| Web 框架 | Gin | v1.10+ |
| 数据库驱动 | pgx/v5 | v5.x |
| 数据库代码生成 | sqlc | v1.27+ |
| 数据库迁移 | golang-migrate | v4.x |
| Redis 客户端 | go-redis/v9 | v9.x |
| 配置管理 | Viper | v1.x |
| 日志 | Zap | v1.x |
| API 文档 | Swag | v1.x |

### 前端技术栈（React）
| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | React | v18+ |
| 构建工具 | Vite | v6+ |
| 路由 | React Router | v7+ |
| 状态管理 | Zustand | v5+ |
| 请求管理 | TanStack Query | v5+ |
| HTTP 客户端 | Axios | v1.x |
| UI 组件 | shadcn/ui | latest |
| 样式 | Tailwind CSS | v3.4+ |
| 类型 | TypeScript | v5+ |

### 重写范围（100% 功能复刻）

#### 后端模块（1:1 语义对应）
1. **代理核心管道**
   - AuthGuard（认证守卫）
   - SessionGuard（会话守卫）
   - RateLimitGuard（限流守卫）
   - SensitiveWordGuard（敏感词守卫）
   - VersionGuard（版本守卫）
   - RequestFilterGuard（请求过滤守卫）
   - ProviderSelector（供应商选择器）
   - ProxyForwarder（请求转发器）
   - ResponseHandler（响应处理器）

2. **格式转换器**
   - Claude ↔ OpenAI
   - Claude ↔ Codex
   - Claude ↔ Gemini CLI
   - OpenAI ↔ Codex
   - 工具调用转换
   - Reasoning 字段处理

3. **业务逻辑**
   - SessionManager（会话管理，5 分钟缓存）
   - CircuitBreaker（熔断器，三态管理）
   - RateLimitService（多维限流，Lua 脚本）
   - ErrorRuleDetector（错误规则检测）
   - SensitiveWordDetector（敏感词检测）
   - PriceSync（价格同步）
   - NotificationService（通知服务）

4. **数据访问层**
   - ProviderRepository
   - UserRepository
   - KeyRepository
   - MessageRepository
   - UsageLogRepository
   - StatisticsRepository
   - LeaderboardRepository
   - ErrorRuleRepository
   - ModelPriceRepository
   - SystemConfigRepository

5. **API 端点**
   - 代理 API（/v1/messages, /v1/chat/completions）
   - 管理 API（39 个 REST 端点）
   - 认证 API（登录/登出）
   - 可用性 API

#### 前端页面（1:1 UI 复刻）
1. **Dashboard**
   - 首页仪表盘（实时统计、图表）
   - 用户管理
   - 日志查询
   - 排行榜
   - 限额管理
   - 会话管理
   - 限流监控
   - 可用性监控

2. **Settings**
   - 供应商配置
   - 价格表管理
   - 系统配置
   - 错误规则
   - 敏感词管理

3. **其他**
   - 登录页面
   - 个人使用统计
   - 使用文档

### **BREAKING** 变更
- 代码目录结构完全重组（KarisCode/backend + KarisCode/frontend）
- 技术栈从 TypeScript/Next.js 迁移到 Go/React
- 数据库迁移文件格式变更（Drizzle → golang-migrate）
- 移除 Docker 部署支持，改为原生二进制部署

## Impact

- **Affected specs**: 无现有 specs（首次创建）
- **Affected code**: 整个项目重写
- **Migration path**:
  - 数据库 schema 保持兼容
  - API 接口保持兼容
  - 配置文件格式保持兼容
  - 部署方式：直接运行 Go 二进制文件
