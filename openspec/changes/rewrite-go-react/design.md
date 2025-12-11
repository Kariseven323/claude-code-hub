# Design: Go + React 重写架构设计

## Context

Claude Code Hub 是一个生产级 AI API 代理平台，当前基于 Next.js 15 + Hono + TypeScript 实现。本次重写将使用 Go + React 技术栈，要求 100% 功能复刻，语义 1:1 对应，不允许任何简化。

### 约束条件
- 必须保持 API 兼容性（现有客户端无需修改）
- 必须保持数据库 schema 兼容性（支持无缝迁移）
- 必须保持配置文件兼容性
- 必须复刻所有功能，包括边缘情况处理

### 利益相关者
- 现有用户：需要无缝迁移
- 开发团队：需要清晰的代码结构
- 运维团队：需要简化的部署流程

## Goals / Non-Goals

### Goals
- 100% 功能复刻，语义 1:1 对应
- 保持 API 兼容性
- 保持数据库兼容性
- 提升性能（Go 的并发优势）
- 简化部署（单体二进制）

### Non-Goals
- 不添加新功能
- 不修改现有 API 接口
- 不修改数据库 schema
- 不简化任何现有逻辑

## Decisions

### 1. 项目结构

```
KarisCode/
├── backend/                    # Go 后端
│   ├── cmd/
│   │   └── server/
│   │       └── main.go        # 入口
│   ├── internal/
│   │   ├── config/            # 配置管理（Viper）
│   │   ├── database/          # 数据库连接（pgx）
│   │   ├── redis/             # Redis 客户端
│   │   ├── middleware/        # Gin 中间件
│   │   ├── handler/           # HTTP 处理器
│   │   │   ├── proxy/         # 代理 API
│   │   │   ├── admin/         # 管理 API
│   │   │   └── auth/          # 认证 API
│   │   ├── service/           # 业务逻辑
│   │   │   ├── session/       # 会话管理
│   │   │   ├── ratelimit/     # 限流服务
│   │   │   ├── circuitbreaker/# 熔断器
│   │   │   ├── provider/      # 供应商选择
│   │   │   └── converter/     # 格式转换
│   │   ├── repository/        # 数据访问层（sqlc 生成）
│   │   ├── model/             # 数据模型
│   │   └── pkg/               # 公共工具
│   ├── migrations/            # 数据库迁移（golang-migrate）
│   ├── sqlc/                  # sqlc 配置和查询
│   ├── docs/                  # Swagger 文档
│   ├── embed/                 # 嵌入前端静态文件
│   ├── go.mod
│   └── go.sum
│
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── api/               # API 客户端（Axios）
│   │   ├── components/        # React 组件
│   │   │   ├── ui/            # shadcn/ui 组件
│   │   │   └── customs/       # 自定义组件
│   │   ├── hooks/             # React Hooks
│   │   ├── pages/             # 页面组件
│   │   │   ├── dashboard/     # 仪表盘页面
│   │   │   ├── settings/      # 设置页面
│   │   │   └── auth/          # 认证页面
│   │   ├── store/             # Zustand 状态管理
│   │   ├── types/             # TypeScript 类型
│   │   ├── utils/             # 工具函数
│   │   ├── i18n/              # 国际化
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
└── Makefile
```

### 2. 代理管道架构（1:1 复刻）

```
请求入口 (Gin Router)
    │
    ▼
ProxySession.FromContext()     # 解析请求上下文
    │
    ▼
格式检测 (DetectFormatByEndpoint / DetectClientFormat)
    │
    ▼
GuardPipeline 守卫链：
    ├─ AuthGuard               # API Key 认证
    ├─ SessionGuard            # 会话管理（5 分钟缓存）
    ├─ RateLimitGuard          # 多维限流（RPM/金额/并发）
    ├─ SensitiveWordGuard      # 敏感词检测
    ├─ VersionGuard            # 客户端版本检查
    └─ RequestFilterGuard      # 请求过滤
    │
    ▼
ProviderSelector               # 供应商选择
    ├─ 会话复用检查
    ├─ 加权随机选择
    ├─ 分组筛选
    └─ 最多 3 次重试
    │
    ▼
ProxyForwarder                 # 请求转发
    ├─ 格式转换
    ├─ 模型重定向
    ├─ 代理配置
    ├─ 超时控制
    └─ MCP 透传
    │
    ▼
ResponseHandler                # 响应处理
    ├─ 格式转换回原始格式
    ├─ 成本计算
    ├─ 日志记录
    ├─ 决策链记录
    └─ 缓存处理
    │
    ▼
响应返回
```

### 3. 数据库设计

使用 sqlc 生成类型安全的数据库代码，保持与现有 Drizzle schema 完全兼容：

```sql
-- 核心表（与现有 schema 1:1 对应）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    rpm_limit INTEGER,
    daily_limit_usd DECIMAL(10,4),
    limit_5h_usd DECIMAL(10,4),
    limit_weekly_usd DECIMAL(10,4),
    limit_monthly_usd DECIMAL(10,4),
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    key VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    limit_5h_usd DECIMAL(10,4),
    limit_daily_usd DECIMAL(10,4),
    limit_weekly_usd DECIMAL(10,4),
    limit_monthly_usd DECIMAL(10,4),
    can_login_web_ui BOOLEAN NOT NULL DEFAULT false,
    provider_group VARCHAR(255),
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(1024) NOT NULL,
    key TEXT NOT NULL,
    provider_type VARCHAR(50) NOT NULL,
    weight INTEGER NOT NULL DEFAULT 1,
    priority INTEGER NOT NULL DEFAULT 0,
    cost_multiplier DECIMAL(10,4) NOT NULL DEFAULT 1.0,
    model_redirects JSONB,
    allowed_models TEXT[],
    limit_5h_usd DECIMAL(10,4),
    limit_daily_usd DECIMAL(10,4),
    limit_weekly_usd DECIMAL(10,4),
    limit_monthly_usd DECIMAL(10,4),
    max_retry_attempts INTEGER,
    circuit_breaker_failure_threshold INTEGER NOT NULL DEFAULT 5,
    circuit_breaker_open_duration INTEGER NOT NULL DEFAULT 30,
    proxy_url VARCHAR(1024),
    proxy_fallback_to_direct BOOLEAN NOT NULL DEFAULT false,
    first_byte_timeout_streaming_ms INTEGER NOT NULL DEFAULT 30000,
    streaming_idle_timeout_ms INTEGER NOT NULL DEFAULT 60000,
    request_timeout_non_streaming_ms INTEGER NOT NULL DEFAULT 120000,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    provider_group VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 其他表省略，完整 schema 见 migrations/
```

### 4. Redis 数据结构（1:1 复刻）

```
# 会话缓存
session:{session_id} -> JSON {
    user_id, key_id, provider_id, created_at, last_activity,
    request_count, decision_chain
}
TTL: 300s (5 分钟)

# 限流计数器
ratelimit:rpm:{key_id}:{minute} -> count
ratelimit:5h:{key_id}:{5h_window} -> cost_usd
ratelimit:weekly:{key_id}:{week} -> cost_usd
ratelimit:monthly:{key_id}:{month} -> cost_usd
ratelimit:concurrent:{key_id} -> count

# 熔断器状态
circuitbreaker:{provider_id} -> JSON {
    state, failure_count, last_failure_time, last_success_time
}

# 排行榜缓存
leaderboard:{period}:{metric} -> ZSET
```

### 5. 格式转换器设计

```go
// 转换器接口
type Converter interface {
    ConvertRequest(req *Request) (*Request, error)
    ConvertResponse(resp *Response) (*Response, error)
    ConvertStreamChunk(chunk []byte) ([]byte, error)
}

// 转换器注册表
type ConverterRegistry struct {
    converters map[string]Converter
}

// 支持的转换
// - claude_to_openai
// - openai_to_claude
// - claude_to_codex
// - codex_to_claude
// - claude_to_gemini
// - gemini_to_claude
// - openai_to_codex
// - codex_to_openai
```

### 6. 前端状态管理

```typescript
// Zustand stores
interface AuthStore {
    user: User | null;
    token: string | null;
    login: (token: string) => Promise<void>;
    logout: () => void;
}

interface ProviderStore {
    providers: Provider[];
    loading: boolean;
    fetchProviders: () => Promise<void>;
    createProvider: (data: CreateProviderInput) => Promise<void>;
    updateProvider: (id: number, data: UpdateProviderInput) => Promise<void>;
    deleteProvider: (id: number) => Promise<void>;
}

// TanStack Query for data fetching
const useProviders = () => useQuery({
    queryKey: ['providers'],
    queryFn: () => api.getProviders(),
});
```

## Risks / Trade-offs

### 风险 1: 功能遗漏
- **风险**: 重写过程中可能遗漏边缘情况
- **缓解**: 逐模块对照原代码实现，编写完整测试用例

### 风险 2: 性能差异
- **风险**: Go 实现可能在某些场景下行为不同
- **缓解**: 使用相同的算法和数据结构，进行性能对比测试

### 风险 3: 迁移风险
- **风险**: 现有用户迁移可能遇到问题
- **缓解**: 保持 API 和数据库完全兼容，提供迁移指南

### Trade-off 1: 开发时间 vs 完整性
- **选择**: 完整性优先
- **原因**: 用户要求 100% 复刻，不允许简化

### Trade-off 2: 代码复杂度 vs 可维护性
- **选择**: 保持与原实现相同的复杂度
- **原因**: 确保语义 1:1 对应

## Migration Plan

### 阶段 1: 基础设施
1. 创建项目结构
2. 配置构建工具
3. 设置数据库迁移

### 阶段 2: 后端核心
1. 实现数据访问层
2. 实现业务逻辑层
3. 实现代理管道
4. 实现 API 端点

### 阶段 3: 前端
1. 搭建 React 项目
2. 实现 UI 组件
3. 实现页面
4. 集成 API

### 阶段 4: 集成测试
1. API 兼容性测试
2. 功能完整性测试
3. 性能对比测试

### 回滚计划
- 保留原项目代码
- 数据库 schema 兼容，可随时切换

### 部署方式
- 开发环境：`make dev`（前后端分离运行）
- 生产环境：`make build` 生成单体二进制，直接运行
- 数据库/Redis：用户自行安装或使用云服务

## Open Questions

1. **国际化**: 是否需要保持 next-intl 的所有翻译？
   - 建议: 是，使用 react-i18next 实现相同功能

2. **OpenAPI 文档**: 是否需要保持自动生成？
   - 建议: 是，使用 Swag 注释生成

3. **部署方式**: 是否需要支持分离部署？
   - 建议: 支持单体部署（默认）和分离部署（可选）
