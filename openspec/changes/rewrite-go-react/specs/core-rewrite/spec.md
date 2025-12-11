# Spec: Core Rewrite (Go + React)

## ADDED Requirements

### Requirement: Go Backend Architecture
系统 SHALL 使用 Go 语言实现后端，采用以下技术栈：
- Web 框架：Gin v1.10+
- 数据库驱动：pgx/v5
- 数据库代码生成：sqlc v1.27+
- 数据库迁移：golang-migrate v4.x
- Redis 客户端：go-redis/v9
- 配置管理：Viper v1.x
- 日志：Zap v1.x
- API 文档：Swag v1.x

#### Scenario: Go 后端启动
- **WHEN** 启动 Go 后端服务
- **THEN** 服务 SHALL 加载配置、连接数据库和 Redis、启动 HTTP 服务器
- **AND** 服务 SHALL 在配置的端口上监听请求

#### Scenario: 静态文件嵌入
- **WHEN** 构建生产版本
- **THEN** 前端静态文件 SHALL 被嵌入到 Go 二进制文件中
- **AND** 单个二进制文件 SHALL 能够提供完整的前后端服务

---

### Requirement: React Frontend Architecture
系统 SHALL 使用 React 实现前端，采用以下技术栈：
- 框架：React v18+
- 构建工具：Vite v6+
- 路由：React Router v7+
- 状态管理：Zustand v5+
- 请求管理：TanStack Query v5+
- HTTP 客户端：Axios v1.x
- UI 组件：shadcn/ui
- 样式：Tailwind CSS v3.4+
- 类型：TypeScript v5+

#### Scenario: 前端开发模式
- **WHEN** 运行前端开发服务器
- **THEN** Vite SHALL 提供 HMR（热模块替换）
- **AND** API 请求 SHALL 被代理到后端服务

#### Scenario: 前端生产构建
- **WHEN** 构建前端生产版本
- **THEN** Vite SHALL 生成优化的静态文件
- **AND** 静态文件 SHALL 被复制到后端 embed 目录

---

### Requirement: Proxy Pipeline 1:1 复刻
系统 SHALL 完整复刻现有代理管道，包括以下组件：

1. **AuthGuard**：API Key 认证
2. **SessionGuard**：会话管理（5 分钟缓存）
3. **RateLimitGuard**：多维限流（RPM/金额/并发）
4. **SensitiveWordGuard**：敏感词检测
5. **VersionGuard**：客户端版本检查
6. **RequestFilterGuard**：请求过滤
7. **ProviderSelector**：供应商选择（权重/优先级/熔断）
8. **ProxyForwarder**：请求转发
9. **ResponseHandler**：响应处理

#### Scenario: 代理请求处理
- **WHEN** 收到代理请求
- **THEN** 请求 SHALL 依次通过所有守卫
- **AND** 任何守卫失败 SHALL 立即返回错误响应
- **AND** 所有守卫通过后 SHALL 选择供应商并转发请求

#### Scenario: 供应商选择
- **WHEN** 需要选择供应商
- **THEN** 系统 SHALL 首先检查会话复用
- **AND** 如果无法复用 SHALL 使用加权随机选择
- **AND** 如果供应商失败 SHALL 最多重试 3 次

#### Scenario: 熔断器保护
- **WHEN** 供应商连续失败达到阈值
- **THEN** 熔断器 SHALL 进入 OPEN 状态
- **AND** 后续请求 SHALL 跳过该供应商
- **AND** 经过配置的时间后 SHALL 进入 HALF_OPEN 状态尝试恢复

---

### Requirement: Format Converters 1:1 复刻
系统 SHALL 完整复刻所有格式转换器：

1. Claude ↔ OpenAI
2. Claude ↔ Codex
3. Claude ↔ Gemini CLI
4. OpenAI ↔ Codex
5. 工具调用转换
6. Reasoning 字段处理

#### Scenario: Claude 到 OpenAI 转换
- **WHEN** 客户端使用 Claude 格式请求 OpenAI 兼容供应商
- **THEN** 系统 SHALL 将请求转换为 OpenAI 格式
- **AND** 系统 SHALL 将响应转换回 Claude 格式

#### Scenario: 流式响应转换
- **WHEN** 处理流式响应
- **THEN** 系统 SHALL 逐块转换响应格式
- **AND** 系统 SHALL 保持流式传输的实时性

#### Scenario: 工具调用转换
- **WHEN** 请求包含工具调用
- **THEN** 系统 SHALL 正确转换工具定义格式
- **AND** 系统 SHALL 正确转换工具调用结果

---

### Requirement: Session Management 1:1 复刻
系统 SHALL 完整复刻会话管理功能：

1. 5 分钟上下文缓存
2. 会话粘性（同一用户复用供应商）
3. 并发计数追踪
4. 决策链记录

#### Scenario: 会话缓存
- **WHEN** 用户发起请求
- **THEN** 系统 SHALL 检查 Redis 中的会话缓存
- **AND** 如果存在有效会话 SHALL 复用相同供应商
- **AND** 会话 TTL SHALL 为 300 秒（5 分钟）

#### Scenario: 决策链记录
- **WHEN** 完成请求处理
- **THEN** 系统 SHALL 记录完整的决策链
- **AND** 决策链 SHALL 包含供应商选择原因、熔断器状态、重试信息

---

### Requirement: Rate Limiting 1:1 复刻
系统 SHALL 完整复刻多维限流功能：

1. RPM（每分钟请求数）
2. 金额限制（5 小时/周/月）
3. 并发 Session 限制
4. Redis Lua 脚本原子操作
5. Fail-Open 降级策略

#### Scenario: RPM 限流
- **WHEN** 用户请求超过 RPM 限制
- **THEN** 系统 SHALL 返回 429 错误
- **AND** 响应 SHALL 包含重试时间信息

#### Scenario: 金额限流
- **WHEN** 用户消费超过金额限制
- **THEN** 系统 SHALL 返回 429 错误
- **AND** 响应 SHALL 说明超出的限额类型

#### Scenario: Fail-Open 降级
- **WHEN** Redis 不可用
- **THEN** 系统 SHALL 跳过限流检查
- **AND** 系统 SHALL 记录降级日志
- **AND** 请求 SHALL 继续处理

---

### Requirement: API Compatibility
系统 SHALL 保持与现有 API 完全兼容：

1. 代理 API（/v1/messages, /v1/chat/completions）
2. 管理 API（39 个 REST 端点）
3. 认证 API（登录/登出）
4. 可用性 API

#### Scenario: 代理 API 兼容
- **WHEN** 客户端使用现有 API 格式请求
- **THEN** 系统 SHALL 返回相同格式的响应
- **AND** 错误响应格式 SHALL 保持一致

#### Scenario: 管理 API 兼容
- **WHEN** 管理界面调用管理 API
- **THEN** 请求和响应格式 SHALL 与现有实现完全一致
- **AND** 所有字段名称和类型 SHALL 保持不变

---

### Requirement: Database Compatibility
系统 SHALL 保持与现有数据库 schema 完全兼容：

1. 所有表结构保持不变
2. 所有字段类型保持不变
3. 所有索引保持不变
4. 支持无缝迁移

#### Scenario: 数据库迁移
- **WHEN** 从现有系统迁移
- **THEN** 数据库 SHALL 无需任何修改
- **AND** 所有现有数据 SHALL 保持完整

#### Scenario: 新部署
- **WHEN** 全新部署系统
- **THEN** golang-migrate SHALL 创建与 Drizzle 相同的 schema
- **AND** 所有表、字段、索引 SHALL 完全一致

---

### Requirement: Frontend UI 1:1 复刻
系统 SHALL 完整复刻所有前端页面和功能：

1. Dashboard（仪表盘、用户管理、日志、排行榜、限额、会话、限流、可用性）
2. Settings（供应商、价格表、系统配置、错误规则、敏感词）
3. 其他（登录、个人使用、使用文档）

#### Scenario: 仪表盘页面
- **WHEN** 访问仪表盘
- **THEN** 页面 SHALL 显示实时统计数据
- **AND** 页面 SHALL 显示与现有实现相同的图表和布局

#### Scenario: 供应商管理页面
- **WHEN** 访问供应商管理
- **THEN** 页面 SHALL 支持所有 CRUD 操作
- **AND** 表单字段 SHALL 与现有实现完全一致

#### Scenario: 国际化支持
- **WHEN** 切换语言
- **THEN** 所有文本 SHALL 正确翻译
- **AND** 翻译内容 SHALL 与现有实现一致

---

### Requirement: Configuration Compatibility
系统 SHALL 保持与现有配置完全兼容：

1. 所有环境变量名称保持不变
2. 所有配置项语义保持不变
3. 默认值保持不变

#### Scenario: 环境变量兼容
- **WHEN** 使用现有 .env 文件
- **THEN** 系统 SHALL 正确读取所有配置
- **AND** 配置行为 SHALL 与现有实现一致

---

### Requirement: Project Structure
系统 SHALL 使用以下目录结构：

```
KarisCode/
├── backend/           # Go 后端
│   ├── cmd/          # 入口
│   ├── internal/     # 内部包
│   ├── migrations/   # 数据库迁移
│   ├── sqlc/         # sqlc 配置
│   ├── docs/         # Swagger 文档
│   └── embed/        # 嵌入前端
├── frontend/          # React 前端
│   ├── src/          # 源代码
│   └── public/       # 静态资源
└── Makefile
```

#### Scenario: 开发模式
- **WHEN** 运行开发模式
- **THEN** 后端和前端 SHALL 独立运行
- **AND** 前端 SHALL 代理 API 请求到后端

#### Scenario: 生产构建
- **WHEN** 构建生产版本
- **THEN** 前端 SHALL 被构建并嵌入后端
- **AND** 生成单个可执行文件
