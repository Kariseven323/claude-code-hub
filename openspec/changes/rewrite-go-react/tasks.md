# Tasks: Go + React 重写任务清单

## 1. 项目初始化

- [ ] 1.1 创建 KarisCode 目录结构
- [ ] 1.2 初始化 Go 模块 (backend/)
- [ ] 1.3 初始化 React 项目 (frontend/)
- [ ] 1.4 配置 Makefile（dev/build/clean 命令）

## 2. 后端基础设施

### 2.1 配置管理
- [ ] 2.1.1 实现 Viper 配置加载
- [ ] 2.1.2 定义环境变量 schema（与 .env.example 1:1 对应）
- [ ] 2.1.3 实现配置验证

### 2.2 数据库
- [ ] 2.2.1 配置 pgx 连接池
- [ ] 2.2.2 编写 sqlc 查询文件
- [ ] 2.2.3 生成 sqlc 代码
- [ ] 2.2.4 编写 golang-migrate 迁移文件（与 Drizzle schema 1:1 对应）

### 2.3 Redis
- [ ] 2.3.1 配置 go-redis 客户端
- [ ] 2.3.2 实现 Lua 脚本加载器
- [ ] 2.3.3 移植所有 Lua 脚本（限流、会话、熔断器）

### 2.4 日志
- [ ] 2.4.1 配置 Zap 日志
- [ ] 2.4.2 实现结构化日志格式

## 3. 后端数据访问层（Repository）

- [ ] 3.1 ProviderRepository（供应商 CRUD）
- [ ] 3.2 UserRepository（用户 CRUD）
- [ ] 3.3 KeyRepository（密钥 CRUD）
- [ ] 3.4 MessageRepository（消息日志）
- [ ] 3.5 UsageLogRepository（使用日志）
- [ ] 3.6 StatisticsRepository（统计查询）
- [ ] 3.7 LeaderboardRepository（排行榜查询）
- [ ] 3.8 ErrorRuleRepository（错误规则）
- [ ] 3.9 ModelPriceRepository（模型价格）
- [ ] 3.10 SystemConfigRepository（系统配置）
- [ ] 3.11 NotificationRepository（通知）
- [ ] 3.12 ClientVersionRepository（客户端版本）
- [ ] 3.13 SensitiveWordRepository（敏感词）
- [ ] 3.14 ActivityStreamRepository（活动流）

## 4. 后端业务逻辑层（Service）

### 4.1 会话管理
- [ ] 4.1.1 SessionManager（会话管理器）
- [ ] 4.1.2 SessionTracker（会话追踪）
- [ ] 4.1.3 SessionCache（5 分钟缓存）
- [ ] 4.1.4 DecisionChain（决策链记录）

### 4.2 熔断器
- [ ] 4.2.1 CircuitBreaker（三态管理：CLOSED/OPEN/HALF_OPEN）
- [ ] 4.2.2 CircuitBreakerProbe（智能探测）
- [ ] 4.2.3 CircuitBreakerState（Redis 状态存储）

### 4.3 限流服务
- [ ] 4.3.1 RateLimitService（多维限流）
- [ ] 4.3.2 RPM 限流（每分钟请求数）
- [ ] 4.3.3 金额限流（5 小时/周/月）
- [ ] 4.3.4 并发 Session 限流
- [ ] 4.3.5 Fail-Open 降级策略

### 4.4 错误处理
- [ ] 4.4.1 ErrorRuleDetector（错误规则检测）
- [ ] 4.4.2 ErrorRuleCache（规则缓存）

### 4.5 敏感词
- [ ] 4.5.1 SensitiveWordDetector（敏感词检测）
- [ ] 4.5.2 SensitiveWordCache（词库缓存）

### 4.6 价格同步
- [ ] 4.6.1 PriceSync（LiteLLM 价格同步）
- [ ] 4.6.2 PriceCache（价格缓存）

### 4.7 通知服务
- [ ] 4.7.1 NotificationService（通知服务）
- [ ] 4.7.2 WeChatNotifier（微信通知）

### 4.8 其他服务
- [ ] 4.8.1 ClientVersionChecker（客户端版本检查）
- [ ] 4.8.2 CodexInstructionsCache（Codex 指令缓存）
- [ ] 4.8.3 SystemSettingsCache（系统设置缓存）

## 5. 后端代理管道（Proxy Pipeline）

### 5.1 守卫链
- [ ] 5.1.1 AuthGuard（API Key 认证）
- [ ] 5.1.2 SessionGuard（会话管理）
- [ ] 5.1.3 RateLimitGuard（限流守卫）
- [ ] 5.1.4 SensitiveWordGuard（敏感词守卫）
- [ ] 5.1.5 VersionGuard（版本守卫）
- [ ] 5.1.6 RequestFilterGuard（请求过滤守卫）

### 5.2 供应商选择
- [ ] 5.2.1 ProviderSelector（供应商选择器）
- [ ] 5.2.2 WeightedRandomSelection（加权随机选择）
- [ ] 5.2.3 SessionReuseStrategy（会话复用策略）
- [ ] 5.2.4 GroupFilterStrategy（分组筛选策略）
- [ ] 5.2.5 RetryStrategy（最多 3 次重试）

### 5.3 请求转发
- [ ] 5.3.1 ProxyForwarder（请求转发器）
- [ ] 5.3.2 ModelRedirector（模型重定向）
- [ ] 5.3.3 ProxyConfig（HTTP/HTTPS/SOCKS5 代理）
- [ ] 5.3.4 TimeoutConfig（超时控制）
- [ ] 5.3.5 MCPPassthroughHandler（MCP 透传）

### 5.4 响应处理
- [ ] 5.4.1 ResponseHandler（响应处理器）
- [ ] 5.4.2 StreamingHandler（流式响应处理）
- [ ] 5.4.3 CostCalculator（成本计算）
- [ ] 5.4.4 UsageLogger（使用日志记录）

### 5.5 格式转换器
- [ ] 5.5.1 FormatMapper（格式检测）
- [ ] 5.5.2 ClaudeToOpenAIConverter
- [ ] 5.5.3 OpenAIToClaudeConverter
- [ ] 5.5.4 ClaudeToCodexConverter
- [ ] 5.5.5 CodexToClaudeConverter
- [ ] 5.5.6 ClaudeToGeminiConverter
- [ ] 5.5.7 GeminiToClaudeConverter
- [ ] 5.5.8 OpenAIToCodexConverter
- [ ] 5.5.9 CodexToOpenAIConverter
- [ ] 5.5.10 ToolCallConverter（工具调用转换）
- [ ] 5.5.11 ReasoningFieldHandler（Reasoning 字段处理）

## 6. 后端 API 端点

### 6.1 代理 API
- [ ] 6.1.1 POST /v1/messages（Claude 消息 API）
- [ ] 6.1.2 POST /v1/chat/completions（OpenAI 兼容 API）
- [ ] 6.1.3 POST /v1/messages/count_tokens（Token 计数）

### 6.2 用户管理 API
- [ ] 6.2.1 POST /api/actions/users/getUsers
- [ ] 6.2.2 POST /api/actions/users/createUser
- [ ] 6.2.3 POST /api/actions/users/updateUser
- [ ] 6.2.4 POST /api/actions/users/deleteUser
- [ ] 6.2.5 POST /api/actions/users/getUserById

### 6.3 供应商管理 API
- [ ] 6.3.1 POST /api/actions/providers/getProviders
- [ ] 6.3.2 POST /api/actions/providers/createProvider
- [ ] 6.3.3 POST /api/actions/providers/updateProvider
- [ ] 6.3.4 POST /api/actions/providers/deleteProvider
- [ ] 6.3.5 POST /api/actions/providers/testProvider
- [ ] 6.3.6 POST /api/actions/providers/getProviderById

### 6.4 密钥管理 API
- [ ] 6.4.1 POST /api/actions/keys/getKeys
- [ ] 6.4.2 POST /api/actions/keys/createKey
- [ ] 6.4.3 POST /api/actions/keys/updateKey
- [ ] 6.4.4 POST /api/actions/keys/deleteKey
- [ ] 6.4.5 POST /api/actions/keys/getKeyById

### 6.5 日志和统计 API
- [ ] 6.5.1 POST /api/actions/usage-logs/getUsageLogs
- [ ] 6.5.2 POST /api/actions/statistics/getStatistics
- [ ] 6.5.3 POST /api/actions/active-sessions/getActiveSessions
- [ ] 6.5.4 POST /api/actions/leaderboard/getLeaderboard

### 6.6 错误规则 API
- [ ] 6.6.1 POST /api/actions/error-rules/getErrorRules
- [ ] 6.6.2 POST /api/actions/error-rules/createErrorRule
- [ ] 6.6.3 POST /api/actions/error-rules/updateErrorRule
- [ ] 6.6.4 POST /api/actions/error-rules/deleteErrorRule

### 6.7 敏感词 API
- [ ] 6.7.1 POST /api/actions/sensitive-words/getSensitiveWords
- [ ] 6.7.2 POST /api/actions/sensitive-words/createSensitiveWord
- [ ] 6.7.3 POST /api/actions/sensitive-words/updateSensitiveWord
- [ ] 6.7.4 POST /api/actions/sensitive-words/deleteSensitiveWord

### 6.8 价格表 API
- [ ] 6.8.1 POST /api/actions/model-prices/getModelPrices
- [ ] 6.8.2 POST /api/actions/model-prices/syncPrices

### 6.9 系统配置 API
- [ ] 6.9.1 POST /api/actions/system-config/getConfig
- [ ] 6.9.2 POST /api/actions/system-config/updateConfig

### 6.10 其他 API
- [ ] 6.10.1 GET /api/version
- [ ] 6.10.2 GET /api/availability/current
- [ ] 6.10.3 GET /api/proxy-status
- [ ] 6.10.4 POST /api/auth/login
- [ ] 6.10.5 POST /api/auth/logout

### 6.11 API 文档
- [ ] 6.11.1 配置 Swag 注释
- [ ] 6.11.2 生成 OpenAPI 3.0 文档
- [ ] 6.11.3 集成 Swagger UI
- [ ] 6.11.4 集成 Scalar UI

## 7. 前端基础设施

### 7.1 项目配置
- [ ] 7.1.1 配置 Vite
- [ ] 7.1.2 配置 TypeScript
- [ ] 7.1.3 配置 Tailwind CSS
- [ ] 7.1.4 配置 ESLint/Prettier

### 7.2 路由
- [ ] 7.2.1 配置 React Router v7
- [ ] 7.2.2 实现路由守卫（认证检查）
- [ ] 7.2.3 实现布局组件

### 7.3 状态管理
- [ ] 7.3.1 配置 Zustand
- [ ] 7.3.2 实现 AuthStore
- [ ] 7.3.3 实现 SettingsStore

### 7.4 API 客户端
- [ ] 7.4.1 配置 Axios
- [ ] 7.4.2 实现请求拦截器（Token 注入）
- [ ] 7.4.3 实现响应拦截器（错误处理）
- [ ] 7.4.4 配置 TanStack Query

### 7.5 国际化
- [ ] 7.5.1 配置 react-i18next
- [ ] 7.5.2 移植所有翻译文件

## 8. 前端 UI 组件

### 8.1 shadcn/ui 组件
- [ ] 8.1.1 安装和配置 shadcn/ui
- [ ] 8.1.2 导入所有使用的组件

### 8.2 自定义组件
- [ ] 8.2.1 DataTable（数据表格）
- [ ] 8.2.2 Pagination（分页）
- [ ] 8.2.3 SearchInput（搜索输入）
- [ ] 8.2.4 DateRangePicker（日期范围选择）
- [ ] 8.2.5 StatCard（统计卡片）
- [ ] 8.2.6 ChartCard（图表卡片）
- [ ] 8.2.7 ProviderStatusBadge（供应商状态徽章）
- [ ] 8.2.8 DecisionChainViewer（决策链查看器）
- [ ] 8.2.9 QuotaProgress（限额进度条）
- [ ] 8.2.10 ConfirmDialog（确认对话框）

### 8.3 表单组件
- [ ] 8.3.1 ProviderForm（供应商表单）
- [ ] 8.3.2 UserForm（用户表单）
- [ ] 8.3.3 KeyForm（密钥表单）
- [ ] 8.3.4 ErrorRuleForm（错误规则表单）
- [ ] 8.3.5 SensitiveWordForm（敏感词表单）
- [ ] 8.3.6 SystemConfigForm（系统配置表单）

## 9. 前端页面

### 9.1 Dashboard 页面
- [ ] 9.1.1 首页仪表盘（实时统计、图表）
- [ ] 9.1.2 用户管理页面
- [ ] 9.1.3 日志查询页面
- [ ] 9.1.4 排行榜页面
- [ ] 9.1.5 限额管理页面（用户/密钥/供应商）
- [ ] 9.1.6 会话管理页面
- [ ] 9.1.7 限流监控页面
- [ ] 9.1.8 可用性监控页面

### 9.2 Settings 页面
- [ ] 9.2.1 供应商配置页面
- [ ] 9.2.2 价格表管理页面
- [ ] 9.2.3 系统配置页面
- [ ] 9.2.4 错误规则页面
- [ ] 9.2.5 敏感词管理页面

### 9.3 其他页面
- [ ] 9.3.1 登录页面
- [ ] 9.3.2 个人使用统计页面
- [ ] 9.3.3 使用文档页面

## 10. 集成和部署

### 10.1 前后端集成
- [ ] 10.1.1 配置 Go embed 嵌入前端静态文件
- [ ] 10.1.2 配置开发模式代理

### 10.2 构建脚本
- [ ] 10.2.1 Makefile dev 命令（前后端分离运行）
- [ ] 10.2.2 Makefile build 命令（生成单体二进制）
- [ ] 10.2.3 Makefile clean 命令（清理构建产物）

### 10.3 文档
- [ ] 10.3.1 更新 README.md
- [ ] 10.3.2 编写部署指南（原生二进制部署）
- [ ] 10.3.3 编写迁移指南
- [ ] 10.3.4 更新 API 文档

## 11. 测试

### 11.1 后端测试
- [ ] 11.1.1 单元测试（Service 层）
- [ ] 11.1.2 集成测试（Repository 层）
- [ ] 11.1.3 API 测试（Handler 层）

### 11.2 前端测试
- [ ] 11.2.1 组件测试
- [ ] 11.2.2 页面测试

### 11.3 端到端测试
- [ ] 11.3.1 API 兼容性测试
- [ ] 11.3.2 功能完整性测试
- [ ] 11.3.3 性能对比测试
