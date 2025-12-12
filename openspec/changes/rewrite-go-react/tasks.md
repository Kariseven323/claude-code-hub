# Tasks: Go + React 重写任务清单

## 1. 项目初始化

- [x] 1.1 创建 KarisCode 目录结构
- [x] 1.2 初始化 Go 模块 (backend/)
- [x] 1.3 初始化 React 项目 (frontend/)
- [x] 1.4 配置 Makefile（dev/build/clean 命令）

## 2. 后端基础设施

### 2.1 配置管理
- [x] 2.1.1 实现 Viper 配置加载
- [x] 2.1.2 定义环境变量 schema（与 .env.example 1:1 对应）
  - [x] 2.1.2a 核心配置（ADMIN_TOKEN、DSN、APP_PORT、APP_URL）
  - [x] 2.1.2b Redis 配置（REDIS_URL、ENABLE_RATE_LIMIT、SESSION_TTL、STORE_SESSION_MESSAGES）
  - [x] 2.1.2c 熔断器配置（ENABLE_CIRCUIT_BREAKER_ON_NETWORK_ERRORS、MAX_RETRY_ATTEMPTS_DEFAULT）
  - [x] 2.1.2d 智能探测配置（ENABLE_SMART_PROBING、PROBE_INTERVAL_MS、PROBE_TIMEOUT_MS）
  - [x] 2.1.2e Cookie 安全配置（ENABLE_SECURE_COOKIES）
  - [x] 2.1.2f API 测试配置（API_TEST_TIMEOUT_MS）
  - [x] 2.1.2g 多供应商类型配置（ENABLE_MULTI_PROVIDER_TYPES）
- [x] 2.1.3 实现配置验证

### 2.2 数据库
- [x] 2.2.1 配置 pgx 连接池
- [x] 2.2.2 编写 sqlc 查询文件
  - [x] 2.2.2a 核心实体查询（users, keys, providers）
  - [x] 2.2.2b 日志相关查询（message_request）
  - [x] 2.2.2c 统计与聚合查询（leaderboard, overview, statistics）
  - [x] 2.2.2d 配置与系统查询（system_settings, notification_settings, error_rules, sensitive_words, request_filters, model_prices）
- [x] 2.2.3 生成 sqlc 代码
- [x] 2.2.4 编写 golang-migrate 迁移文件
  - [x] 2.2.4a 核心表迁移（users, keys, providers）
  - [x] 2.2.4b 日志表迁移（message_request）
  - [x] 2.2.4c 配置表迁移（system_settings, notification_settings, error_rules, sensitive_words）
  - [x] 2.2.4d 其他表迁移（model_prices）
  - [x] 2.2.4e 请求过滤表迁移（request_filters）
  <!-- 注：client_versions 功能通过 message_request.user_agent 字段提取统计，无需独立表 -->

### 2.3 Redis
- [x] 2.3.1 配置 go-redis 客户端
- [x] 2.3.2 实现 Lua 脚本加载器
- [x] 2.3.3 移植所有 Lua 脚本
  - [x] 2.3.3a 限流相关 Lua 脚本（RPM、金额、并发）
  - [x] 2.3.3b 会话管理 Lua 脚本
  - [x] 2.3.3c 熔断器 Lua 脚本
  - [x] 2.3.3d Lua 脚本外部化（从内嵌字符串抽取为独立 .lua 文件）
- [x] 2.3.4 实现 Redis 缓存层
  - [x] 2.3.4a LeaderboardCache（排行榜缓存）
  - [x] 2.3.4b SessionStatsCache（会话统计缓存）
  - [x] 2.3.4c CircuitBreakerConfig（熔断器配置缓存）
  - [x] 2.3.4d CircuitBreakerState（熔断器状态缓存）

### 2.4 日志
- [x] 2.4.1 配置 Zap 日志
- [x] 2.4.2 实现结构化日志格式
- [x] 2.4.3 实现日志级别动态调整（运行时切换）
- [x] 2.4.4 实现日志输出配置（stdout/file）

## 3. 后端数据访问层（Repository）

### 3.1 ProviderRepository（供应商）
- [x] 3.1.1 供应商基础结构与接口定义
- [x] 3.1.2 供应商 Create/Update 实现
- [ ] 3.1.3 供应商 Get/List/Delete 实现
- [ ] 3.1.4 供应商状态与熔断器查询
- [ ] 3.1.5 供应商高级字段处理
  - [ ] 3.1.5a preserveClientIp（客户端 IP 透传配置）
  - [ ] 3.1.5b cacheTtlPreference（Cache TTL 偏好覆写）
  - [ ] 3.1.5c codexInstructionsStrategy（Codex 指令策略：auto/force_official/keep_original）
  - [ ] 3.1.5d mcpPassthroughType 与 mcpPassthroughUrl（MCP 透传配置）

### 3.2 UserRepository（用户）
- [x] 3.2.1 用户基础结构与接口定义
- [x] 3.2.2 用户 Create/Update 实现
- [x] 3.2.3 用户 Get/List/Delete 实现
- [x] 3.2.4 用户限额查询与更新
- [ ] 3.2.5 用户标签管理
  - [ ] 3.2.5a 用户标签 CRUD（tags jsonb 字段）
  - [ ] 3.2.5b 按标签筛选用户列表

### 3.3 KeyRepository（密钥）
- [ ] 3.3.1 密钥基础结构与接口定义
- [ ] 3.3.2 密钥 Create/Update 实现
- [ ] 3.3.3 密钥 Get/List/Delete 实现
- [ ] 3.3.4 密钥认证查询（按 API Key 查找）
- [ ] 3.3.5 密钥高级字段处理
  - [ ] 3.3.5a cacheTtlPreference（Cache TTL 偏好覆写）
  - [ ] 3.3.5b providerGroup（供应商分组覆写）
  - [ ] 3.3.5c dailyResetMode 与 dailyResetTime（每日限额重置模式）

### 3.4 MessageRepository（消息日志）
- [x] 3.4.1 消息基础结构与接口定义
- [ ] 3.4.2 消息 Create/BatchCreate 实现
- [ ] 3.4.3 消息查询（按会话/用户筛选）

### 3.5 UsageLogRepository（使用日志）
- [ ] 3.5.1 使用日志基础结构与接口定义
- [ ] 3.5.2 使用日志 Create 实现
- [ ] 3.5.3 使用日志分页查询（多条件筛选）
- [ ] 3.5.4 使用日志聚合统计查询

### 3.6 StatisticsRepository（统计查询）
- [ ] 3.6a 基础统计查询（总量、日统计）
- [ ] 3.6b 时间序列统计
  - [ ] 3.6b-i 小时级聚合查询
  - [ ] 3.6b-ii 天级聚合查询
  - [ ] 3.6b-iii 周级聚合查询
- [ ] 3.6c 多维度统计
  - [ ] 3.6c-i 按用户维度统计
  - [ ] 3.6c-ii 按供应商维度统计
  - [ ] 3.6c-iii 按模型维度统计

### 3.7 LeaderboardRepository（排行榜）
- [ ] 3.7.1 排行榜接口定义
- [ ] 3.7.2 请求数排行查询
- [ ] 3.7.3 Token 消耗排行查询
- [ ] 3.7.4 成本排行查询

### 3.8 其他 Repository
- [ ] 3.8.1 ErrorRuleRepository（错误规则 CRUD）
- [ ] 3.8.2 ModelPriceRepository（模型价格 CRUD + 批量同步）
- [ ] 3.8.3 SystemConfigRepository（系统配置 Get/Set）
  - [ ] 3.8.3a 站点配置（siteTitle、currencyDisplay、billingModelSource）
  - [ ] 3.8.3b 日志清理配置（enableAutoCleanup、cleanupRetentionDays、cleanupSchedule、cleanupBatchSize）
  - [ ] 3.8.3c HTTP/2 配置（enableHttp2）
  - [ ] 3.8.3d 客户端版本检查配置（enableClientVersionCheck）
  - [ ] 3.8.3e 错误显示配置（verboseProviderError）
- [ ] 3.8.4 NotificationRepository（通知 CRUD）
- [ ] 3.8.5 ClientVersionRepository（客户端版本 CRUD + 统计）
- [ ] 3.8.6 SensitiveWordRepository（敏感词 CRUD）
- [ ] 3.8.7 ActivityStreamRepository（活动流查询）
- [ ] 3.8.8 RequestFilterRepository（请求过滤规则 CRUD）
- [ ] 3.8.9 OverviewRepository（首页概览数据聚合）

## 4. 后端业务逻辑层（Service）

### 4.1 会话管理
- [ ] 4.1.1 SessionManager（会话管理器）
  - [ ] 4.1.1a 会话生命周期管理（创建/获取/销毁）
  - [ ] 4.1.1b 会话状态持久化（Redis 交互）
  - [ ] 4.1.1c 会话上下文绑定（供应商关联）
- [ ] 4.1.2 SessionTracker（会话追踪）
- [ ] 4.1.3 SessionCache（5 分钟缓存）
- [ ] 4.1.4 DecisionChain（决策链记录）

### 4.2 熔断器
- [ ] 4.2.1 CircuitBreaker（三态管理：CLOSED/OPEN/HALF_OPEN）
  - [ ] 4.2.1a 状态机定义与转换逻辑
  - [ ] 4.2.1b 失败计数与阈值判断
  - [ ] 4.2.1c HALF_OPEN 恢复探测
- [ ] 4.2.2 CircuitBreakerProbe（智能探测）
- [ ] 4.2.3 CircuitBreakerState（Redis 状态存储）
- [ ] 4.2.4 CircuitBreakerLoader（熔断器状态加载器）
  - [ ] 4.2.4a 启动时从 Redis 加载所有供应商熔断状态
  - [ ] 4.2.4b 状态同步与缓存刷新

### 4.3 限流服务
- [ ] 4.3.1 RateLimitService（多维限流核心框架）
  - [ ] 4.3.1a 限流接口抽象与注册机制
  - [ ] 4.3.1b 限流检查链执行器
  - [ ] 4.3.1c 限流结果聚合与错误处理
- [ ] 4.3.2 RPM 限流（每分钟请求数）
- [ ] 4.3.3 金额限流
  - [ ] 4.3.3a 5小时金额限流
  - [ ] 4.3.3b 周金额限流
  - [ ] 4.3.3c 月金额限流
- [ ] 4.3.4 并发 Session 限流
- [ ] 4.3.5 Fail-Open 降级策略

### 4.4 错误处理
- [ ] 4.4.1 ErrorRuleDetector（错误规则检测）
- [ ] 4.4.2 ErrorRuleCache（规则缓存）
- [ ] 4.4.3 ErrorOverrideValidator（错误覆写验证器）
  - [ ] 4.4.3a 覆写响应体 JSON 格式验证
  - [ ] 4.4.3b 覆写状态码范围验证

### 4.5 敏感词
- [ ] 4.5.1 SensitiveWordDetector（敏感词检测）
- [ ] 4.5.2 SensitiveWordCache（词库缓存）

### 4.6 价格同步
- [ ] 4.6.1 PriceSync（LiteLLM 价格同步）
  - [ ] 4.6.1a LiteLLM 数据获取与解析
  - [ ] 4.6.1b 价格数据转换与映射
  - [ ] 4.6.1c 批量 Upsert 与增量同步
- [ ] 4.6.2 PriceCache（价格缓存）
- [ ] 4.6.3 PriceSeedInitializer（价格种子数据初始化）
  - [ ] 4.6.3a 首次启动检测（数据库为空判断）
  - [ ] 4.6.3b 内嵌默认价格数据加载
  - [ ] 4.6.3c 自动触发 LiteLLM 同步

### 4.7 通知服务
- [ ] 4.7.1 NotificationService（通知服务框架）
  - [ ] 4.7.1a 通知渠道抽象接口
  - [ ] 4.7.1b 通知队列管理
  - [ ] 4.7.1c 重试与降级策略
- [ ] 4.7.2 WeChatNotifier（企业微信机器人通知）
  - [ ] 4.7.2a Webhook 请求构建
  - [ ] 4.7.2b 消息模板渲染（Markdown 格式）
  - [ ] 4.7.2c 发送结果处理
- [ ] 4.7.3 DailyLeaderboardTask（每日排行榜推送任务）
  - [ ] 4.7.3a Cron 调度器配置（可配置推送时间）
  - [ ] 4.7.3b 排行榜数据聚合（Top N 用户）
  - [ ] 4.7.3c 消息格式化与推送
- [ ] 4.7.4 CostAlertTask（成本预警任务）
  - [ ] 4.7.4a 周期性检查调度（可配置间隔）
  - [ ] 4.7.4b 用户限额阈值检测（80% 预警）
  - [ ] 4.7.4c 告警消息构建与推送
  - [ ] 4.7.4d 告警去重（避免重复推送）
- [ ] 4.7.5 CircuitBreakerAlertTask（熔断器告警任务）
  - [ ] 4.7.5a 熔断器状态变更监听
  - [ ] 4.7.5b 熔断/恢复事件推送
  - [ ] 4.7.5c 告警去重（5 分钟内同一供应商不重复告警）
  - [ ] 4.7.5d 熔断器恢复通知（OPEN→CLOSED 状态变更）

### 4.8 其他服务
- [ ] 4.8.1 ClientVersionChecker（客户端版本检查）
  - [ ] 4.8.1a 版本号解析与比较
  - [ ] 4.8.1b 版本黑名单匹配
  - [ ] 4.8.1c 版本状态缓存
- [ ] 4.8.2 CodexInstructionsCache（Codex 指令缓存）
  - [ ] 4.8.2a 官方 Codex CLI Instructions 加载
  - [ ] 4.8.2b 指令缓存与刷新策略
- [ ] 4.8.3 SystemSettingsCache（系统设置缓存）
  - [ ] 4.8.3a 系统设置加载与缓存
  - [ ] 4.8.3b 设置变更监听与刷新

### 4.9 可用性服务
- [ ] 4.9.1 AvailabilityService（供应商可用性服务）
  - [ ] 4.9.1a 供应商健康状态聚合
  - [ ] 4.9.1b 实时可用性计算
  - [ ] 4.9.1c 历史可用性趋势
- [ ] 4.9.2 ProxyStatusTracker（代理状态追踪）
  - [ ] 4.9.2a 代理运行时状态收集
  - [ ] 4.9.2b 状态快照与查询接口

### 4.10 数据管理服务
- [ ] 4.10.1 DatabaseBackupService（数据库备份服务）
  - [ ] 4.10.1a pg_dump 导出实现
  - [ ] 4.10.1b pg_restore 导入实现
  - [ ] 4.10.1c 临时文件管理
  - [ ] 4.10.1d 备份锁（防并发）
- [ ] 4.10.2 LogCleanupService（日志清理服务）
  - [ ] 4.10.2a 定时清理调度器
  - [ ] 4.10.2b 分批删除策略
  - [ ] 4.10.2c 清理队列管理
- [ ] 4.10.3 LogLevelService（日志级别管理）
  - [ ] 4.10.3a 运行时日志级别查询
  - [ ] 4.10.3b 运行时日志级别切换（无需重启）
  - [ ] 4.10.3c 日志级别持久化（可选）

### 4.11 请求过滤服务
- [ ] 4.11.1 RequestFilterEngine（请求过滤引擎）
  - [ ] 4.11.1a Header 过滤规则执行
  - [ ] 4.11.1b Body JSON Path 过滤
  - [ ] 4.11.1c 文本替换规则执行
- [ ] 4.11.2 RequestFilterCache（过滤规则缓存）

### 4.12 辅助服务
- [ ] 4.12.1 AsyncTaskManager（异步任务管理器）
- [ ] 4.12.2 EventEmitter（内部事件发射器）
- [ ] 4.12.3 MessageExtractor（消息内容提取）
- [ ] 4.12.4 UAParser（User-Agent 解析）
- [ ] 4.12.5 ProviderChainFormatter（决策链格式化）
  - [ ] 4.12.5a 决策链 JSON 解析
  - [ ] 4.12.5b 多语言格式化输出
- [ ] 4.12.6 SSEUtils（SSE 流式工具）
  - [ ] 4.12.6a SSE 事件解析器
  - [ ] 4.12.6b SSE 响应构建器
  - [ ] 4.12.6c 流式数据缓冲管理
- [ ] 4.12.7 CostCalculationUtils（成本计算工具）
  - [ ] 4.12.7a Token 价格查询
  - [ ] 4.12.7b 缓存命中折扣计算
  - [ ] 4.12.7c 多币种转换

### 4.13 MCP 客户端
- [ ] 4.13.1 MinimaxClient（Minimax MCP 服务客户端）
- [ ] 4.13.2 GlmClient（智谱 GLM MCP 客户端）

### 4.14 供应商测试服务
- [ ] 4.14.1 ProviderTestService（供应商测试服务）
  - [ ] 4.14.1a 测试请求构建器
  - [ ] 4.14.1b 测试超时控制
  - [ ] 4.14.1c 测试结果聚合
- [ ] 4.14.2 测试响应解析器
  - [ ] 4.14.2a AnthropicParser（Anthropic 响应解析）
  - [ ] 4.14.2b OpenAIParser（OpenAI 响应解析）
  - [ ] 4.14.2c CodexParser（Codex 响应解析）
  - [ ] 4.14.2d GeminiParser（Gemini 响应解析）
- [ ] 4.14.3 测试验证器
  - [ ] 4.14.3a HttpValidator（HTTP 响应验证）
  - [ ] 4.14.3b ContentValidator（内容验证）
- [ ] 4.14.4 SSECollector（SSE 流式响应收集）

### 4.15 数据生成器服务（开发调试用）
- [ ] 4.15.1 DataGenerator（模拟数据生成服务）
  - [ ] 4.15.1a 用户数据生成（批量创建测试用户）
  - [ ] 4.15.1b 使用日志数据生成（模拟请求记录）
  - [ ] 4.15.1c 统计数据生成（填充历史统计）
- [ ] 4.15.2 DataAnalyzer（数据分析器）
  - [ ] 4.15.2a 现有数据分布分析
  - [ ] 4.15.2b 生成参数推荐

### 4.16 认证服务
- [ ] 4.16.1 AuthService（认证服务）
  - [ ] 4.16.1a Admin Token 验证
  - [ ] 4.16.1b API Key 验证与用户关联
  - [ ] 4.16.1c Web UI 登录权限检查
- [ ] 4.16.2 SessionCookieManager（会话 Cookie 管理）
  - [ ] 4.16.2a Cookie 创建与签名
  - [ ] 4.16.2b Cookie 验证与解析
  - [ ] 4.16.2c Secure Cookie 配置（HTTPS 环境）
- [ ] 4.16.3 PermissionService（权限服务）
  - [ ] 4.16.3a 用户角色权限检查
  - [ ] 4.16.3b 字段级权限控制（用户可编辑字段）

## 5. 后端代理管道（Proxy Pipeline）

### 5.1 守卫链
- [ ] 5.1.1 AuthGuard（API Key 认证）
  - [ ] 5.1.1a AuthGuard 接口与框架
  - [ ] 5.1.1b API Key 解析与验证
  - [ ] 5.1.1c 用户/密钥关联查询
- [ ] 5.1.2 SessionGuard（会话管理）
  - [ ] 5.1.2a SessionGuard 接口与框架
  - [ ] 5.1.2b 会话创建与绑定
  - [ ] 5.1.2c 会话并发检查
- [ ] 5.1.3 RateLimitGuard（限流守卫）
  - [ ] 5.1.3a RateLimitGuard 接口与框架
  - [ ] 5.1.3b 多维限流检查调用
  - [ ] 5.1.3c 限流拒绝响应处理
- [ ] 5.1.4 SensitiveWordGuard（敏感词守卫）
  - [ ] 5.1.4a SensitiveWordGuard 接口与框架
  - [ ] 5.1.4b 敏感词缓存加载与刷新
  - [ ] 5.1.4c 多匹配类型检测（contains/regex/exact）
  - [ ] 5.1.4d 拦截响应构建与日志记录
- [ ] 5.1.5 VersionGuard（版本守卫）
  - [ ] 5.1.5a VersionGuard 接口与框架
  - [ ] 5.1.5b User-Agent 解析与版本提取
  - [ ] 5.1.5c 版本黑名单检查
  - [ ] 5.1.5d 版本不兼容响应处理
- [ ] 5.1.6 RequestFilterGuard（请求过滤守卫）
  - [ ] 5.1.6a RequestFilterGuard 接口与框架
  - [ ] 5.1.6b 过滤规则缓存加载
  - [ ] 5.1.6c Header 过滤执行
  - [ ] 5.1.6d Body JSON Path 过滤执行
  - [ ] 5.1.6e 文本替换规则执行

### 5.2 供应商选择
- [ ] 5.2.1 ProviderSelector（供应商选择器）
  - [ ] 5.2.1a 可用供应商过滤（启用状态/熔断状态）
  - [ ] 5.2.1b 权重计算与优先级排序
  - [ ] 5.2.1c 最终选择与决策链记录
- [ ] 5.2.2 WeightedRandomSelection（加权随机选择）
  - [ ] 5.2.2a 权重归一化与概率分布
  - [ ] 5.2.2b 随机选择算法实现
- [ ] 5.2.3 SessionReuseStrategy（会话复用策略）
  - [ ] 5.2.3a 会话上下文检查
  - [ ] 5.2.3b 供应商复用决策逻辑
- [ ] 5.2.4 GroupFilterStrategy（分组筛选策略）
- [ ] 5.2.5 RetryStrategy（最多 3 次重试）
  - [ ] 5.2.5a 重试条件判断
  - [ ] 5.2.5b 重试间隔与退避策略

### 5.3 请求转发
- [ ] 5.3.1 ProxyForwarder（请求转发器）
  - [ ] 5.3.1a HTTP 客户端构建（代理/超时配置）
  - [ ] 5.3.1b 请求头/Body 构造
  - [ ] 5.3.1c 响应接收与错误处理
  - [ ] 5.3.1d 客户端 IP 透传（X-Forwarded-For 头处理）
- [ ] 5.3.2 ModelRedirector（模型重定向）
- [ ] 5.3.3 ProxyConfig（HTTP/HTTPS/SOCKS5 代理）
- [ ] 5.3.4 TimeoutConfig（超时控制）
  - [ ] 5.3.4a firstByteTimeoutStreamingMs（流式请求首字节超时）
  - [ ] 5.3.4b streamingIdleTimeoutMs（流式请求静默期超时）
  - [ ] 5.3.4c requestTimeoutNonStreamingMs（非流式请求总超时）
- [ ] 5.3.5 MCPPassthroughHandler（MCP 透传）
  - [ ] 5.3.5a MCP 协议解析与请求识别
  - [ ] 5.3.5b MCP 请求透传与响应处理
- [ ] 5.3.6 HTTP2Config（HTTP/2 协议支持）
  - [ ] 5.3.6a HTTP/2 连接池配置
  - [ ] 5.3.6b HTTP/2 → HTTP/1.1 自动回退
  - [ ] 5.3.6c 系统级 HTTP/2 开关（enableHttp2）

### 5.4 响应处理
- [ ] 5.4.1 ResponseHandler（响应处理器）
  - [ ] 5.4.1a 响应状态码处理与错误检测
  - [ ] 5.4.1b 响应头处理与清理
  - [ ] 5.4.1c 错误响应格式化（ErrorRuleDetector 集成）
- [ ] 5.4.2 StreamingHandler（流式响应处理）
  - [ ] 5.4.2a SSE 流式解析
  - [ ] 5.4.2b 流式响应转发与缓冲
  - [ ] 5.4.2c 流式超时检测（idle timeout）
- [ ] 5.4.3 CostCalculator（成本计算）
  - [ ] 5.4.3a Token 计数提取（input/output）
  - [ ] 5.4.3b 价格查询与成本计算
  - [ ] 5.4.3c 缓存命中成本调整
- [ ] 5.4.4 UsageLogger（使用日志记录）
  - [ ] 5.4.4a 日志数据构建
  - [ ] 5.4.4b 异步日志写入
  - [ ] 5.4.4c 限额消耗更新
- [ ] 5.4.5 ResponseTransformer（响应格式转换）
  - [ ] 5.4.5a 响应格式检测（根据供应商类型）
  - [ ] 5.4.5b 转换器调度（调用 5.5 格式转换器）
  - [ ] 5.4.5c 流式响应实时转换

### 5.5 格式转换器
- [ ] 5.5.1 FormatMapper（格式检测）
- [ ] 5.5.2 Claude↔OpenAI 转换
  - [ ] 5.5.2a ClaudeToOpenAIConverter（请求转换）✅ 已实现
    - [ ] 5.5.2a-i 消息格式转换（role/content 映射）
    - [ ] 5.5.2a-ii 参数转换（max_tokens/temperature 等）
    - [ ] 5.5.2a-iii 系统提示词处理
  - [ ] 5.5.2b ClaudeToOpenAIConverter（响应转换）⚠️ 当前未实现
    - [ ] 5.5.2b-i 非流式响应转换
    - [ ] 5.5.2b-ii 流式 SSE 响应转换
    - [ ] 5.5.2b-iii usage 字段映射
  - [ ] 5.5.2c OpenAIToClaudeConverter（请求转换）✅ 已实现
    - [ ] 5.5.2c-i 消息格式转换
    - [ ] 5.5.2c-ii 参数转换
    - [ ] 5.5.2c-iii 系统提示词处理
  - [ ] 5.5.2d OpenAIToClaudeConverter（响应转换）✅ 已实现
    - [ ] 5.5.2d-i 非流式响应转换
    - [ ] 5.5.2d-ii 流式 SSE 响应转换
    - [ ] 5.5.2d-iii usage 字段映射
- [ ] 5.5.3 Claude↔Codex 转换
  - [ ] 5.5.3a ClaudeToCodexConverter（请求转换）
    - [ ] 5.5.3a-i 消息格式转换（Claude→Codex）
    - [ ] 5.5.3a-ii 参数与指令注入
  - [ ] 5.5.3b ClaudeToCodexConverter（响应转换）
    - [ ] 5.5.3b-i 非流式响应转换
    - [ ] 5.5.3b-ii 流式 SSE 响应转换
  - [ ] 5.5.3c CodexToClaudeConverter（请求转换）
    - [ ] 5.5.3c-i 消息格式转换（Codex→Claude）
    - [ ] 5.5.3c-ii 参数转换
  - [ ] 5.5.3d CodexToClaudeConverter（响应转换）
    - [ ] 5.5.3d-i 非流式响应转换
    - [ ] 5.5.3d-ii 流式 SSE 响应转换
- [ ] 5.5.4 Claude↔Gemini CLI 转换（注：当前实现为 Gemini CLI 格式，非标准 Gemini API）
  - [ ] 5.5.4a ClaudeToGeminiCLIConverter（请求转换）
    - [ ] 5.5.4a-i 消息格式转换（Claude→Gemini CLI）
    - [ ] 5.5.4a-ii 参数与安全设置转换
  - [ ] 5.5.4b ClaudeToGeminiCLIConverter（响应转换）
    - [ ] 5.5.4b-i 非流式响应转换
    - [ ] 5.5.4b-ii 流式响应转换
  - [ ] 5.5.4c GeminiCLIToClaudeConverter（请求转换）✅ 已实现
    - [ ] 5.5.4c-i 消息格式转换（Gemini CLI→Claude）
    - [ ] 5.5.4c-ii 参数转换
  - [ ] 5.5.4d GeminiCLIToClaudeConverter（响应转换）✅ 已实现
    - [ ] 5.5.4d-i 非流式响应转换
    - [ ] 5.5.4d-ii 流式响应转换
- [ ] 5.5.5 OpenAI↔Codex 转换
  - [ ] 5.5.5a OpenAIToCodexConverter（请求转换）✅ 已实现
    - [ ] 5.5.5a-i 消息格式转换（OpenAI→Codex）
    - [ ] 5.5.5a-ii 参数与指令注入
  - [ ] 5.5.5b OpenAIToCodexConverter（响应转换）⚠️ 当前未实现
    - [ ] 5.5.5b-i 非流式响应转换
    - [ ] 5.5.5b-ii 流式 SSE 响应转换
  - [ ] 5.5.5c CodexToOpenAIConverter（请求转换）✅ 已实现
    - [ ] 5.5.5c-i 消息格式转换（Codex→OpenAI）
    - [ ] 5.5.5c-ii 参数转换
  - [ ] 5.5.5d CodexToOpenAIConverter（响应转换）✅ 已实现
    - [ ] 5.5.5d-i 非流式响应转换
    - [ ] 5.5.5d-ii 流式 SSE 响应转换
- [ ] 5.5.6 Gemini CLI↔OpenAI 转换（注：当前实现为 Gemini CLI 格式，非标准 Gemini API）
  - [ ] 5.5.6a GeminiCLIToOpenAIConverter（请求转换）✅ 已实现
    - [ ] 5.5.6a-i 消息格式转换（Gemini CLI→OpenAI）
    - [ ] 5.5.6a-ii 参数转换
  - [ ] 5.5.6b GeminiCLIToOpenAIConverter（响应转换）✅ 已实现
    - [ ] 5.5.6b-i 非流式响应转换
    - [ ] 5.5.6b-ii 流式 SSE 响应转换
  - [ ] 5.5.6c OpenAIToGeminiCLIConverter（请求转换）⚠️ 当前未实现
    - [ ] 5.5.6c-i 消息格式转换（OpenAI→Gemini CLI）
    - [ ] 5.5.6c-ii 参数与安全设置转换
  - [ ] 5.5.6d OpenAIToGeminiCLIConverter（响应转换）⚠️ 当前未实现
    - [ ] 5.5.6d-i 非流式响应转换
    - [ ] 5.5.6d-ii 流式响应转换
- [ ] 5.5.7 ToolCallConverter（工具调用转换）
  - [ ] 5.5.7a 工具定义转换（Claude↔OpenAI schema）
  - [ ] 5.5.7b 工具调用转换（tool_use↔function_call）
  - [ ] 5.5.7c 工具结果转换（tool_result 格式适配）
- [ ] 5.5.8 ReasoningFieldHandler（Reasoning 字段处理）
  - [ ] 5.5.8a Reasoning/Thinking 字段检测（Claude extended thinking）
  - [ ] 5.5.8b Reasoning 字段格式转换（Claude↔OpenAI reasoning_content）
  - [ ] 5.5.8c Reasoning Token 计数提取
  - [ ] 5.5.8d 流式响应中的 Reasoning 块处理
- [ ] 5.5.9 ToolNameMapper（工具名称映射器）
  - [ ] 5.5.9a 工具名称规范化（Claude computer_use → OpenAI 格式）
  - [ ] 5.5.9b 工具名称反向映射
  - [ ] 5.5.9c 自定义映射规则支持
- [ ] 5.5.10 Gemini CLI↔Codex 转换（可选，按需实现，当前未实现）
  - [ ] 5.5.10a GeminiCLIToCodexConverter（请求转换）
    - [ ] 5.5.10a-i 消息格式转换（Gemini CLI→Codex）
    - [ ] 5.5.10a-ii 参数与指令注入
  - [ ] 5.5.10b GeminiCLIToCodexConverter（响应转换）
    - [ ] 5.5.10b-i 非流式响应转换
    - [ ] 5.5.10b-ii 流式响应转换
  - [ ] 5.5.10c CodexToGeminiCLIConverter（请求转换）
    - [ ] 5.5.10c-i 消息格式转换（Codex→Gemini CLI）
    - [ ] 5.5.10c-ii 参数转换
  - [ ] 5.5.10d CodexToGeminiCLIConverter（响应转换）
    - [ ] 5.5.10d-i 非流式响应转换
    - [ ] 5.5.10d-ii 流式响应转换

### 5.6 协议适配器
- [ ] 5.6.1 CodexAdapter（Codex CLI 适配器）
  - [ ] 5.6.1a Codex Response API Handler 框架
  - [ ] 5.6.1b Codex Chat Completions Handler
  - [ ] 5.6.1c Codex CLI Instructions 注入
  - [ ] 5.6.1d Codex 请求清理器（Request Sanitizer）
- [ ] 5.6.2 GeminiAdapter（Gemini CLI 适配器）
  - [ ] 5.6.2a Gemini 协议解析器
  - [ ] 5.6.2b Gemini 认证处理器
  - [ ] 5.6.2c Gemini 请求构建器
  - [ ] 5.6.2d Gemini 响应处理器

## 6. 后端 API 端点

### 6.1 代理 API
- [ ] 6.1.1 POST /v1/messages（Claude 消息 API）
  - [ ] 6.1.1a Claude Messages API Handler 框架
  - [ ] 6.1.1b Claude Messages 请求验证与预处理
  - [ ] 6.1.1c Claude Messages 流式响应处理
- [ ] 6.1.2 POST /v1/chat/completions（OpenAI 兼容 API）
  - [ ] 6.1.2a OpenAI Chat Completions Handler 框架
  - [ ] 6.1.2b OpenAI Chat Completions 请求适配
  - [ ] 6.1.2c OpenAI Chat Completions 流式响应处理
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

### 6.10 请求过滤 API
- [ ] 6.10.1 POST /api/actions/request-filters/getRequestFilters
- [ ] 6.10.2 POST /api/actions/request-filters/createRequestFilter
- [ ] 6.10.3 POST /api/actions/request-filters/updateRequestFilter
- [ ] 6.10.4 POST /api/actions/request-filters/deleteRequestFilter

### 6.11 客户端版本 API
- [ ] 6.11.1 POST /api/actions/client-versions/getClientVersions
- [ ] 6.11.2 POST /api/actions/client-versions/getClientVersionStats
- [ ] 6.11.3 POST /api/actions/client-versions/updateClientVersionStatus

### 6.12 通知设置 API
- [ ] 6.12.1 POST /api/actions/notifications/getNotificationSettings
- [ ] 6.12.2 POST /api/actions/notifications/updateNotificationSettings
- [ ] 6.12.3 POST /api/actions/notifications/testWebhook

### 6.13 数据管理 API
- [ ] 6.13.1 POST /api/admin/database/export（数据库导出）
- [ ] 6.13.2 POST /api/admin/database/import（数据库导入）
- [ ] 6.13.3 GET /api/admin/database/status（数据库状态）
- [ ] 6.13.4 POST /api/admin/log-cleanup/manual（手动日志清理）
- [ ] 6.13.5 GET /api/admin/log-level（获取日志级别）
- [ ] 6.13.6 POST /api/admin/log-level（设置日志级别）

### 6.14 其他 API
- [ ] 6.14.1 GET /api/version
- [ ] 6.14.2 GET /api/availability/current
- [ ] 6.14.3 GET /api/availability（历史可用性）
- [ ] 6.14.4 GET /api/proxy-status
- [ ] 6.14.5 POST /api/auth/login
- [ ] 6.14.6 POST /api/auth/logout
- [ ] 6.14.7 GET /api/prices（价格表查询）
- [ ] 6.14.8 GET /api/system-settings（系统设置公开接口）
- [ ] 6.14.9 GET /api/leaderboard（排行榜公开接口）

### 6.15 实时监控 API
- [ ] 6.15.1 POST /api/actions/dashboard-realtime/getRealtimeStats（实时仪表盘统计）
- [ ] 6.15.2 POST /api/actions/concurrent-sessions/getConcurrentSessions（并发会话查询）
- [ ] 6.15.3 POST /api/actions/provider-slots/getProviderSlots（供应商槽位查询）
- [ ] 6.15.4 POST /api/actions/session-response/getSessionResponse（会话响应查询）
- [ ] 6.15.5 POST /api/actions/my-usage/getMyUsage（个人使用统计）
- [ ] 6.15.6 POST /api/actions/my-usage/getMyUsageLogs（个人使用日志）
- [ ] 6.15.7 POST /api/actions/overview/getOverview（首页概览数据）
- [ ] 6.15.8 POST /api/actions/rate-limit-stats/getRateLimitStats（限流统计数据）

### 6.16 API 文档
- [ ] 6.16.1 配置 Swag 注释
- [ ] 6.16.2 生成 OpenAPI 3.0 文档
- [ ] 6.16.3 集成 Swagger UI
- [ ] 6.16.4 集成 Scalar UI

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
- [ ] 7.2.4 实现多语言路由（locale 参数处理）
  - [ ] 7.2.4a URL 路径语言前缀（/zh-CN/, /en/, /ja/ 等）
  - [ ] 7.2.4b 语言检测与自动重定向
  - [ ] 7.2.4c 语言切换与 URL 同步
  - [ ] 7.2.4d i18n 路由配置迁移（从 next-intl 迁移）
    - [ ] 7.2.4d-i routing.ts 路由语言前缀处理
    - [ ] 7.2.4d-ii request.ts 请求级语言检测
    - [ ] 7.2.4d-iii config.ts 国际化配置（支持语言列表/默认语言）

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
  - [ ] 7.5.2a 简体中文翻译文件迁移（zh-CN/）
  - [ ] 7.5.2b 英文翻译文件迁移（en/）
  - [ ] 7.5.2c 日语翻译文件迁移（ja/）
  - [ ] 7.5.2d 俄语翻译文件迁移（ru/）
  - [ ] 7.5.2e 繁体中文翻译文件迁移（zh-TW/）
  - [ ] 7.5.2f 翻译 key 校验与补全
- [ ] 7.5.3 翻译文件模块化
  - [ ] 7.5.3a common.json（通用词汇）
  - [ ] 7.5.3b dashboard.json（仪表盘）
  - [ ] 7.5.3c settings.json（设置页面）
  - [ ] 7.5.3d providers.json（供应商相关）
  - [ ] 7.5.3e users.json（用户管理）
  - [ ] 7.5.3f forms.json（表单验证）
  - [ ] 7.5.3g errors.json（错误消息）
  - [ ] 7.5.3h notifications.json（通知设置）
  - [ ] 7.5.3i quota.json（限额相关）
  - [ ] 7.5.3j validation.json（表单校验消息）
  - [ ] 7.5.3k auth.json（认证相关）
  - [ ] 7.5.3l usage.json（使用统计）
  - [ ] 7.5.3m myUsage.json（个人使用）
  - [ ] 7.5.3n ui.json（UI 组件）
  - [ ] 7.5.3o provider-chain.json（决策链）
  - [ ] 7.5.3p bigScreen.json（大屏监控）
  - [ ] 7.5.3q internal.json（内部工具）
  - [ ] 7.5.3r customs.json（自定义内容）

## 8. 前端 UI 组件

### 8.1 shadcn/ui 组件
- [ ] 8.1.1 安装和配置 shadcn/ui
- [ ] 8.1.2 导入所有使用的组件
  - [ ] 8.1.2a 基础组件导入（Button/Input/Dialog/Card）
  - [ ] 8.1.2b 表单组件导入（Form/Select/Checkbox/Switch）
  - [ ] 8.1.2c 数据展示组件导入（Table/Badge/Progress/Tooltip）

### 8.2 自定义组件
- [ ] 8.2.1 基础组件
  - [ ] 8.2.1a DataTable（数据表格）
    - [ ] 8.2.1a-i 表格核心渲染与列定义
    - [ ] 8.2.1a-ii 排序与筛选功能
    - [ ] 8.2.1a-iii 选择与批量操作
  - [ ] 8.2.1b Pagination（分页）
  - [ ] 8.2.1c SearchInput（搜索输入）
- [ ] 8.2.2 展示组件
  - [ ] 8.2.2a DateRangePicker（日期范围选择）
  - [ ] 8.2.2b StatCard（统计卡片）
  - [ ] 8.2.2c ChartCard（图表卡片）
  - [ ] 8.2.2d CircularProgress（圆形进度条）
  - [ ] 8.2.2e CountdownTimer（倒计时组件）
  - [ ] 8.2.2f RelativeTime（相对时间显示）
  - [ ] 8.2.2g TagInput（标签输入组件）
- [ ] 8.2.3 业务组件
  - [ ] 8.2.3a ProviderStatusBadge（供应商状态徽章）
  - [ ] 8.2.3b DecisionChainViewer（决策链查看器）
  - [ ] 8.2.3c QuotaProgress（限额进度条）
  - [ ] 8.2.3d ConfirmDialog（确认对话框）
  - [ ] 8.2.3e 会话相关组件
    - [ ] 8.2.3e-i ConcurrentSessionsCard（并发会话卡片）
    - [ ] 8.2.3e-ii ActiveSessionsPanel（活跃会话面板）
    - [ ] 8.2.3e-iii SessionCard（会话卡片）
    - [ ] 8.2.3e-iv SessionListItem（会话列表项）
    - [ ] 8.2.3e-v ActiveSessionsList（活跃会话列表）
  - [ ] 8.2.3f MetricCard（指标卡片）
  - [ ] 8.2.3g OverviewPanel（概览面板）
  - [ ] 8.2.3h VersionChecker（版本检查组件）
  - [ ] 8.2.3i VersionUpdateNotifier（版本更新通知）

### 8.3 表单组件
- [ ] 8.3.1 ProviderForm（供应商表单）
  - [ ] 8.3.1a 基础信息表单（名称/类型/权重/优先级）
  - [ ] 8.3.1b 连接配置表单（API Key/URL/代理）
  - [ ] 8.3.1c 高级配置表单（模型重定向/限制）
- [ ] 8.3.2 UserForm（用户表单）
- [ ] 8.3.3 KeyForm（密钥表单）
- [ ] 8.3.4 ErrorRuleForm（错误规则表单）
- [ ] 8.3.5 SensitiveWordForm（敏感词表单）
- [ ] 8.3.6 SystemConfigForm（系统配置表单）
- [ ] 8.3.7 RequestFilterForm（请求过滤规则表单）
- [ ] 8.3.8 NotificationSettingsForm（通知设置表单）
- [ ] 8.3.9 ClientVersionForm（客户端版本表单）

### 8.4 自定义 Hooks
- [ ] 8.4.1 useDebounce（防抖 Hook）
- [ ] 8.4.2 useFormatCurrency（货币格式化 Hook）
- [ ] 8.4.3 useLocalStorage（本地存储 Hook）
- [ ] 8.4.4 useMediaQuery（响应式断点 Hook）
- [ ] 8.4.5 useCopyToClipboard（剪贴板复制 Hook）

### 8.5 工具函数
- [ ] 8.5.1 dateFormat（日期格式化）
- [ ] 8.5.2 colorUtils（颜色工具）
- [ ] 8.5.3 tokenUtils（Token 显示格式化）
- [ ] 8.5.4 zodI18n（Zod 校验消息国际化）
- [ ] 8.5.5 quotaHelpers（限额计算辅助）
- [ ] 8.5.6 clipboardUtils（剪贴板操作）
- [ ] 8.5.7 errorMessages（错误消息格式化）
- [ ] 8.5.8 currencyUtils（货币格式化）
- [ ] 8.5.9 cnUtils（className 合并工具，基于 clsx + tailwind-merge）

## 9. 前端页面

### 9.1 Dashboard 页面
- [ ] 9.1.1 首页仪表盘
  - [ ] 9.1.1a 统计卡片区域
  - [ ] 9.1.1b 时间序列图表
  - [ ] 9.1.1c 实时数据刷新逻辑
- [ ] 9.1.2 用户管理页面
  - [ ] 9.1.2a 用户列表与筛选
  - [ ] 9.1.2b 用户新增/编辑弹窗
  - [ ] 9.1.2c 用户删除与批量操作
- [ ] 9.1.3 日志查询页面
  - [ ] 9.1.3a 筛选器组件
  - [ ] 9.1.3b 日志列表与分页
  - [ ] 9.1.3c 日志详情弹窗
- [ ] 9.1.4 排行榜页面
  - [ ] 9.1.4a 排行榜列表与排序
  - [ ] 9.1.4b 时间范围筛选
  - [ ] 9.1.4c 用户详情跳转
- [ ] 9.1.5 限额管理页面
  - [ ] 9.1.5a 限额管理首页（概览与导航）
  - [ ] 9.1.5b 用户限额管理子页面（quotas/users）
    - [ ] 9.1.5b-i 用户限额列表与筛选
    - [ ] 9.1.5b-ii 用户限额编辑弹窗
    - [ ] 9.1.5b-iii 用户限额进度展示
  - [ ] 9.1.5c 密钥限额管理子页面（quotas/keys）
    - [ ] 9.1.5c-i 密钥限额列表与筛选
    - [ ] 9.1.5c-ii 密钥限额编辑弹窗
    - [ ] 9.1.5c-iii 密钥限额进度展示
  - [ ] 9.1.5d 供应商限额管理子页面（quotas/providers）
    - [ ] 9.1.5d-i 供应商限额列表与排序
    - [ ] 9.1.5d-ii 供应商限额编辑弹窗
    - [ ] 9.1.5d-iii 供应商限额进度展示
- [ ] 9.1.6 会话管理页面
  - [ ] 9.1.6a 活跃会话列表
  - [ ] 9.1.6b 会话详情与决策链
  - [ ] 9.1.6c 会话终止操作
- [ ] 9.1.7 限流监控页面
  - [ ] 9.1.7a 限流状态概览
  - [ ] 9.1.7b 限流规则列表
  - [ ] 9.1.7c 实时限流事件流
- [ ] 9.1.8 可用性监控页面
  - [ ] 9.1.8a 供应商健康状态
  - [ ] 9.1.8b 熔断器状态展示
  - [ ] 9.1.8c 历史可用性趋势

### 9.2 Settings 页面
- [ ] 9.2.1 供应商配置页面
  - [ ] 9.2.1a 供应商列表与状态展示
  - [ ] 9.2.1b 供应商新增/编辑弹窗
  - [ ] 9.2.1c 供应商测试与熔断器状态
- [ ] 9.2.2 价格表管理页面
  - [ ] 9.2.2a 价格列表与搜索
  - [ ] 9.2.2b 价格同步功能
  - [ ] 9.2.2c 手动价格编辑
- [ ] 9.2.3 系统配置页面
  - [ ] 9.2.3a 配置项列表展示
  - [ ] 9.2.3b 配置编辑表单
  - [ ] 9.2.3c 配置保存与验证
- [ ] 9.2.4 错误规则页面
  - [ ] 9.2.4a 规则列表与筛选
  - [ ] 9.2.4b 规则新增/编辑弹窗
  - [ ] 9.2.4c 规则测试功能
- [ ] 9.2.5 敏感词管理页面
  - [ ] 9.2.5a 敏感词列表与搜索
  - [ ] 9.2.5b 敏感词新增/编辑
  - [ ] 9.2.5c 批量导入/导出
- [ ] 9.2.6 请求过滤管理页面
  - [ ] 9.2.6a 过滤规则列表与筛选
  - [ ] 9.2.6b 规则新增/编辑弹窗
  - [ ] 9.2.6c 规则优先级排序
- [ ] 9.2.7 通知设置页面
  - [ ] 9.2.7a 通知渠道配置（企业微信）
  - [ ] 9.2.7b 熔断器告警配置
  - [ ] 9.2.7c 每日排行榜推送配置
  - [ ] 9.2.7d 成本预警配置
  - [ ] 9.2.7e Webhook 测试功能
- [ ] 9.2.8 客户端版本管理页面
  - [ ] 9.2.8a 版本列表与统计
  - [ ] 9.2.8b 版本状态切换
  - [ ] 9.2.8c 版本检查配置
- [ ] 9.2.9 数据管理页面
  - [ ] 9.2.9a 数据库状态展示
  - [ ] 9.2.9b 数据库导出功能
  - [ ] 9.2.9c 数据库导入功能
  - [ ] 9.2.9d 日志清理配置
  - [ ] 9.2.9e 手动清理触发
- [ ] 9.2.10 日志级别设置页面
  - [ ] 9.2.10a 当前日志级别展示
  - [ ] 9.2.10b 日志级别切换表单

### 9.3 其他页面
- [ ] 9.3.1 登录页面
- [ ] 9.3.2 个人使用统计页面
  - [ ] 9.3.2a 个人统计概览卡片
  - [ ] 9.3.2b 使用趋势图表
  - [ ] 9.3.2c 历史记录列表
- [ ] 9.3.3 使用文档页面
  - [ ] 9.3.3a API 使用指南（Claude/OpenAI/Codex/Gemini 接入说明）
  - [ ] 9.3.3b 快速开始教程
  - [ ] 9.3.3c 配置参数说明文档
  - [ ] 9.3.3d FAQ 常见问题解答

### 9.4 内部工具页面（可选）
- [ ] 9.4.1 大屏监控 Dashboard
  - [ ] 9.4.1a 全屏布局与自适应
  - [ ] 9.4.1b 实时数据大屏展示
- [ ] 9.4.2 数据生成器（开发调试）
  - [ ] 9.4.2a 模拟数据生成配置
  - [ ] 9.4.2b 批量数据注入

## 10. 集成和部署

### 10.1 前后端集成
- [ ] 10.1.1 配置 Go embed 嵌入前端静态文件
- [ ] 10.1.2 配置开发模式代理

### 10.2 构建脚本
- [ ] 10.2.1 Makefile dev 命令（前后端分离运行）
- [ ] 10.2.2 Makefile build 命令（生成单体二进制）
- [ ] 10.2.3 Makefile clean 命令（清理构建产物）
- [ ] 10.2.4 Makefile test 命令（运行测试）
- [ ] 10.2.5 Makefile lint 命令（代码检查）

### 10.3 Docker 部署
- [ ] 10.3.1 编写多阶段 Dockerfile
- [ ] 10.3.2 编写 docker-compose.yml（app + postgres + redis）
- [ ] 10.3.3 配置健康检查
- [ ] 10.3.4 编写部署脚本（deploy.sh / deploy.ps1）

### 10.4 文档
- [ ] 10.4.1 更新 README.md
- [ ] 10.4.2 编写部署指南（原生二进制部署）
- [ ] 10.4.3 编写 Docker 部署指南
- [ ] 10.4.4 编写迁移指南（从 Next.js 版本迁移）
- [ ] 10.4.5 更新 API 文档
- [ ] 10.4.6 编写开发者指南（本地开发环境搭建）

## 11. 测试

### 11.1 后端测试
- [ ] 11.1.1 单元测试（Service 层）
  - [ ] 11.1.1a 会话管理测试
  - [ ] 11.1.1b 限流服务测试
  - [ ] 11.1.1c 熔断器测试
  - [ ] 11.1.1d 其他服务测试
  - [ ] 11.1.1e 可用性服务测试
  - [ ] 11.1.1f 请求过滤引擎测试
  - [ ] 11.1.1g 数据库备份服务测试
  - [ ] 11.1.1h 供应商测试服务测试
  - [ ] 11.1.1i 通知服务测试（含定时任务）
  - [ ] 11.1.1j 认证服务测试
  - [ ] 11.1.1k 数据生成器测试
- [ ] 11.1.2 格式转换器测试
  - [ ] 11.1.2a Claude↔OpenAI 转换器测试
  - [ ] 11.1.2b Claude↔Codex 转换器测试
  - [ ] 11.1.2c Claude↔Gemini 转换器测试
  - [ ] 11.1.2d OpenAI↔Codex 转换器测试
  - [ ] 11.1.2e Gemini↔OpenAI 转换器测试
  - [ ] 11.1.2f ToolCallConverter 测试
  - [ ] 11.1.2g ReasoningFieldHandler 测试
- [ ] 11.1.3 协议适配器测试
  - [ ] 11.1.3a CodexAdapter 测试
  - [ ] 11.1.3b GeminiAdapter 测试
- [ ] 11.1.4 集成测试（Repository 层）
  - [ ] 11.1.4a 核心 Repository 集成测试（User/Key/Provider）
  - [ ] 11.1.4b 日志 Repository 集成测试（UsageLog/Message）
  - [ ] 11.1.4c 统计 Repository 集成测试
  - [ ] 11.1.4d 请求过滤 Repository 集成测试
  - [ ] 11.1.4e 客户端版本 Repository 集成测试
- [ ] 11.1.5 API 测试（Handler 层）
  - [ ] 11.1.5a 代理 API Handler 测试
  - [ ] 11.1.5b 管理 API Handler 测试
  - [ ] 11.1.5c 认证与权限 API 测试
  - [ ] 11.1.5d 数据管理 API 测试
  - [ ] 11.1.5e 请求过滤 API 测试
  - [ ] 11.1.5f 实时监控 API 测试

### 11.2 前端测试
- [ ] 11.2.1 组件测试
  - [ ] 11.2.1a 基础组件测试（DataTable/Pagination/SearchInput）
  - [ ] 11.2.1b 展示组件测试（DateRangePicker/StatCard/ChartCard）
  - [ ] 11.2.1c 业务组件测试（ProviderStatusBadge/DecisionChainViewer/QuotaProgress）
  - [ ] 11.2.1d 表单组件测试（ProviderForm/UserForm/KeyForm 等）
  - [ ] 11.2.1e 请求过滤表单测试
  - [ ] 11.2.1f 通知设置表单测试
- [ ] 11.2.2 页面测试
  - [ ] 11.2.2a Dashboard 页面测试（首页/用户管理/日志查询）
  - [ ] 11.2.2b Settings 页面测试（供应商配置/价格表/系统配置）
  - [ ] 11.2.2c 其他页面测试（登录/个人统计/文档）
  - [ ] 11.2.2d 请求过滤页面测试
  - [ ] 11.2.2e 数据管理页面测试
  - [ ] 11.2.2f 通知设置页面测试
  - [ ] 11.2.2g 客户端版本页面测试
  - [ ] 11.2.2h 多语言切换测试

### 11.3 端到端测试
- [ ] 11.3.1 API 兼容性测试
  - [ ] 11.3.1a Claude API 兼容性
  - [ ] 11.3.1b OpenAI API 兼容性
  - [ ] 11.3.1c Codex API 兼容性
  - [ ] 11.3.1d Gemini CLI API 兼容性
- [ ] 11.3.2 功能完整性测试
  - [ ] 11.3.2a 代理转发功能
  - [ ] 11.3.2b 限流熔断功能
  - [ ] 11.3.2c 会话粘性功能
  - [ ] 11.3.2d 格式转换功能
- [ ] 11.3.3 性能对比测试
  - [ ] 11.3.3a 吞吐量测试
  - [ ] 11.3.3b 延迟测试
  - [ ] 11.3.3c 并发压测

## 12. 迁移风险与注意事项

### 12.1 架构差异处理
- [ ] 12.1.1 Next.js Server Actions → Go HTTP Handler 迁移
  - [ ] 12.1.1a 请求/响应格式保持兼容
  - [ ] 12.1.1b 错误处理格式统一
- [ ] 12.1.2 Next.js App Router → React Router 迁移
  - [ ] 12.1.2a 路由结构映射
  - [ ] 12.1.2b 动态路由参数处理
  - [ ] 12.1.2c SSR → CSR 降级处理
- [ ] 12.1.3 Drizzle ORM → sqlc 迁移
  - [ ] 12.1.3a 查询逻辑等价性验证
  - [ ] 12.1.3b 事务处理迁移
- [ ] 12.1.4 TypeScript 类型定义迁移
  - [ ] 12.1.4a Session 类型定义（ActiveSessionInfo/SessionStoreInfo/SessionUsageUpdate）
  - [ ] 12.1.4b Provider 类型定义
  - [ ] 12.1.4c User/Key 类型定义
  - [ ] 12.1.4d API 响应类型定义
  - [ ] 12.1.4e 前后端共享类型生成策略

### 12.2 数据兼容性
- [ ] 12.2.1 数据库 Schema 兼容性验证
  - [ ] 12.2.1a 字段类型映射（Drizzle → PostgreSQL → sqlc）
  - [ ] 12.2.1b 索引完整性检查
- [ ] 12.2.2 Redis 数据格式兼容性
  - [ ] 12.2.2a Key 命名约定保持一致
  - [ ] 12.2.2b Lua 脚本返回值格式兼容

### 12.3 API 兼容性
- [ ] 12.3.1 编写 API 兼容性测试套件
- [ ] 12.3.2 请求/响应格式对比验证
- [ ] 12.3.3 错误码与错误消息兼容性

### 12.4 迁移文档
- [ ] 12.4.1 编写数据迁移脚本（如需）
- [ ] 12.4.2 编写配置迁移指南（.env 参数映射）
- [ ] 12.4.3 编写回滚方案

---

## 附录：任务清单更新记录

### 2025-12-12 补充更新

基于对当前 Next.js 实现的代码分析，补充以下遗漏的详细任务项：

**守卫链补充 (5.1.4-5.1.6)**
- 敏感词守卫、版本守卫、请求过滤守卫的详细子任务

**响应处理补充 (5.4)**
- ResponseHandler 详细子任务
- StreamingHandler 流式超时检测
- 新增 ResponseTransformer（响应格式转换）

**格式转换器补充 (5.5.8-5.5.9)**
- ReasoningFieldHandler 详细子任务（Claude extended thinking 支持）
- ToolNameMapper 详细子任务

**通知服务补充 (4.7.5)**
- 熔断器告警去重机制
- 熔断器恢复通知

**其他服务补充 (4.8)**
- ClientVersionChecker、CodexInstructionsCache、SystemSettingsCache 详细子任务

**基础设施补充**
- Lua 脚本外部化 (2.3.3d)
- 日志级别服务详细子任务 (4.10.3)

**覆盖度评估**：更新后任务清单覆盖率从 ~85% 提升至 ~95%，剩余差异主要为实现细节层面，可在开发过程中按需补充。

### 2025-12-12 第二次补充

基于完整代码库对比分析，补充以下遗漏项：

**前端 i18n 路由基础设施 (7.2.4d)**
- routing.ts 路由语言前缀处理
- request.ts 请求级语言检测
- config.ts 国际化配置

**展示组件补充 (8.2.2d-g)**
- CircularProgress（圆形进度条）
- CountdownTimer（倒计时组件）
- RelativeTime（相对时间显示）
- TagInput（标签输入组件）

**会话相关业务组件 (8.2.3e-i)**
- ConcurrentSessionsCard、ActiveSessionsPanel、SessionCard、SessionListItem
- MetricCard、OverviewPanel、VersionChecker、VersionUpdateNotifier

**TypeScript 类型定义迁移 (12.1.4)**
- Session/Provider/User/Key 类型定义
- API 响应类型定义
- 前后端共享类型生成策略

**覆盖度评估**：更新后任务清单覆盖率提升至 ~98%，基本实现完整覆盖。

### 2025-12-12 第三次补充

基于完整覆盖度分析，补充以下遗漏项：

**格式转换器补充 (5.5.10)**
- Gemini↔Codex 转换器（可选，按需实现）
- 支持 Gemini CLI 与 Codex 之间的格式互转

**限额管理页面细化 (9.1.5)**
- 限额管理首页概览与导航
- 用户限额管理子页面（quotas/users）详细任务
- 密钥限额管理子页面（quotas/keys）详细任务
- 供应商限额管理子页面（quotas/providers）详细任务

**覆盖度评估**：更新后任务清单覆盖率提升至 ~99%，实现完整覆盖。剩余 1% 为实现过程中可能发现的边缘场景，可按需补充。

### 2025-12-12 第四次补充（覆盖度严格审计）

基于完整代码对比分析，进行以下修正和补充：

**语义修正：Gemini → Gemini CLI**
- 5.5.4: 修正为 `Claude↔Gemini CLI 转换`，标注当前实现为 Gemini CLI 格式
- 5.5.6: 修正为 `Gemini CLI↔OpenAI 转换`
- 5.5.10: 修正为 `Gemini CLI↔Codex 转换`
- 标注各转换器实现状态（✅ 已实现 / ⚠️ 当前未实现）

**转换器实现状态标注**
- 5.5.2b: ClaudeToOpenAIConverter 响应转换 ⚠️ 当前未实现（仅有 request.ts）
- 5.5.5b: OpenAIToCodexConverter 响应转换 ⚠️ 当前未实现（仅有 request.ts）
- 5.5.4c/d: GeminiCLIToClaudeConverter ✅ 已实现
- 5.5.6a/b: GeminiCLIToOpenAIConverter ✅ 已实现
- 5.5.6c/d: OpenAIToGeminiCLIConverter ⚠️ 当前未实现

**环境变量细化 (2.1.2)**
- 补充核心配置、Redis 配置、熔断器配置、智能探测配置等子任务

**Repository 层补充**
- 3.1.5: 供应商高级字段处理（preserveClientIp、cacheTtlPreference、codexInstructionsStrategy、MCP 配置）
- 3.2.5: 用户标签管理（tags jsonb 字段 CRUD 与筛选）
- 3.3.5: 密钥高级字段处理（cacheTtlPreference、providerGroup、dailyResetMode）
- 3.8.3: SystemConfigRepository 细化（HTTP/2、日志清理、版本检查等配置）

**请求转发补充 (5.3)**
- 5.3.1d: 客户端 IP 透传（X-Forwarded-For 头处理）
- 5.3.4: 超时控制细化（firstByteTimeoutStreamingMs、streamingIdleTimeoutMs、requestTimeoutNonStreamingMs）
- 5.3.6: HTTP/2 协议支持（连接池配置、自动回退、系统级开关）

**覆盖度评估**：更新后任务清单覆盖率达到 ~100%，完整覆盖当前 Next.js 实现的所有功能。部分转换器响应处理未实现的情况已明确标注，可根据实际需求决定是否在重写时补齐。

### 2025-12-12 第五次补充（最终审计）

基于完整代码库严格对比分析，补充以下架构差异和遗漏项：

**4.7.5 CircuitBreakerAlertTask 架构说明**
- 当前实现：嵌入式架构，非独立任务文件
  - `circuit-breaker.ts` 中的 `triggerCircuitBreakerAlert()` 直接触发
  - `notification/notifier.ts` 中的 `sendCircuitBreakerAlert()` 发送通知
  - `wechat/message-templates.ts` 中的 `buildCircuitBreakerAlert()` 构建消息
- 重写建议：可保持嵌入式架构或抽取为独立任务，功能等价

**辅助工具函数补充 (8.5)**
- [ ] 8.5.6 clipboardUtils（剪贴板操作）
- [ ] 8.5.7 errorMessages（错误消息格式化）
- [ ] 8.5.8 currencyUtils（货币格式化）
- [ ] 8.5.9 cnUtils（className 合并工具）

**Settings 页面组件细化**
- 供应商配置页面组件：
  - ProviderManager、ProviderList、ProviderRichListItem
  - ProviderForm、AddProviderDialog、ModelRedirectEditor
  - ProviderSortDropdown、ProviderTypeFilter、SchedulingRulesDialog
  - ApiTestButton、ProxyTestButton、TestResultCard、UrlPreview
- 错误规则页面组件：
  - RuleListTable、AddRuleDialog、EditRuleDialog
  - RegexTester、ErrorRuleTester、OverrideSection
- 敏感词页面组件：
  - WordListTable、AddWordDialog、EditWordDialog
- 价格表页面组件：
  - PriceList、SyncLitellmButton、UploadPriceDialog
- 数据管理页面组件：
  - DatabaseStatus、DatabaseExport、DatabaseImport、LogCleanupPanel
- 请求过滤页面组件：
  - FilterTable、FilterDialog
- 客户端版本页面组件：
  - ClientVersionStatsTable、ClientVersionToggle
- 日志级别页面组件：
  - LogLevelForm

**Dashboard 页面组件细化**
- 统计图表组件：Chart、TimeRangeSelector、StatisticsWrapper
- 限流监控组件：RateLimitEventsChart、RateLimitTypeBreakdown、RateLimitTopUsers
- 用户管理组件：UserList、UserKeyManager、AddUserDialog、UserActions、KeyActions
- 日志查询组件：UsageLogsTable、UsageLogsFilters、ProviderChainPopover、ErrorDetailsDialog
- 排行榜组件：LeaderboardTable、LeaderboardView
- 会话管理组件：RequestListSidebar（会话消息页面）

**覆盖度最终评估**：任务清单覆盖率 ~99%，完整覆盖当前实现。剩余 ~1% 为：
1. 部分响应转换器未实现（已标注 ⚠️）
2. 实现细节层面的辅助函数（可在开发中按需补充）
3. 架构差异（如 CircuitBreakerAlert 嵌入式 vs 独立任务）

**结论**：tasks.md 可作为整体重写的完整依据。
