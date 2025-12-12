# 重写差异对照（按原项目文件）

本文按“原项目文件”逐个列出：在 `KarisCode/` 重写版本中**缺少**（未实现/未接入/行为不等价）的内容。

## `src/instrumentation.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **启动入口未调用任何初始化链路**：原文件通过 Next.js instrumentation `register()` 在服务启动时执行一系列初始化；KarisCode 目前启动入口仅启动 Gin 与基础路由，未触发迁移/seed/调度等（`KarisCode/backend/cmd/server/main.go:15`）。
- **环境分支行为未复刻**：
  - CI 环境跳过初始化（`src/instrumentation.ts:36`）。
  - 生产环境在 DB 不可用时直接 `process.exit(1)`（`src/instrumentation.ts:51`）。
  - 开发环境也会运行迁移与价格表初始化（且禁用 Bull 队列）（`src/instrumentation.ts:94`）。
- **自动迁移开关语义未实现**：原逻辑受 `AUTO_MIGRATE !== "false"` 控制（`src/instrumentation.ts:45`）；KarisCode 虽有 `AUTO_MIGRATE` 配置项（`KarisCode/backend/internal/config/config.go:49`），但未在启动路径中使用。
- **数据库连接检查与迁移执行未接入**：原逻辑 `checkDatabaseConnection()` + `runMigrations()`（`src/instrumentation.ts:46`）。
- **价格表初始化未接入**：原逻辑 `ensurePriceTable()`（`src/instrumentation.ts:61`）。
- **默认错误规则同步（“用户自定义优先”策略）缺失**：原逻辑每次启动同步 `DEFAULT_ERROR_RULES` 到 DB，并按 `isDefault` 决定 update/skip（`src/instrumentation.ts:12`）；KarisCode 目前只有“从 DB reload 缓存”的能力，但没有“同步默认规则到 DB”的等价实现与接入点。
- **错误规则检测器初始化的降级语义未接入**：原逻辑对 detector 初始化失败“非关键，继续启动”（`src/instrumentation.ts:64`）。
- **日志清理任务调度未接入**：原逻辑 `scheduleAutoCleanup()`（`src/instrumentation.ts:75`）。
- **通知任务队列/调度未接入**：原逻辑 `scheduleNotifications()`（`src/instrumentation.ts:79`）。
- **智能探测调度器启动未接入**：原逻辑 `isSmartProbingEnabled()` 决定是否 `startProbeScheduler()`（`src/instrumentation.ts:83`）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 价格表 seed 初始化器：`KarisCode/backend/internal/service/price/seed_initializer.go:35`
- 日志清理服务（含生产环境定时调度）：`KarisCode/backend/internal/service/datamanagement/log_cleanup_service.go:101`
- 通知服务（含生产环境调度与队列）：`KarisCode/backend/internal/service/notification/service.go:94`
- 智能探测调度器：`KarisCode/backend/internal/service/circuitbreaker/probe_scheduler.go:107`
- 错误规则缓存 reload：`KarisCode/backend/internal/service/errorrules/error_rule_cache.go:56`

## `src/proxy.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **等价的“请求入口中间件”不存在**：原文件是 Next.js middleware（locale + Web UI 鉴权），对所有非 `/v1` 请求生效；KarisCode 目前没有对应的 HTTP middleware/路由层把这些规则挂到请求链路上（仍然是启动入口仅有基础路由，`KarisCode/backend/cmd/server/main.go:15`）。
- **/v1 直通规则未实现**：原逻辑对 `/v1`（API 代理）直接 `NextResponse.next()`，不做 locale 与 Web UI cookie 鉴权（`src/proxy.ts:30`）。
- **静态资源/Next 内部路径跳过规则未实现**：原逻辑跳过 `/_next` 与 `/favicon.ico`（`src/proxy.ts:35`）。
- **locale 检测/路由未实现**：原逻辑通过 `next-intl` middleware 处理 locale 并从 pathname 抽取 locale 前缀（`src/proxy.ts:40`）。
- **public path 放行策略未实现**：原逻辑 `PUBLIC_PATH_PATTERNS`（login/usage-doc/auth endpoints）直接放行（`src/proxy.ts:9`）。
- **read-only path 绕过 canLoginWebUi 逻辑未实现（在路由层）**：原逻辑 `READ_ONLY_PATH_PATTERNS` 允许 `canLoginWebUi=false` 的 key 访问只读页面（`src/proxy.ts:13`）。
- **cookie 缺失/无效的重定向与 cookie 清理未实现**：
  - 无 cookie 重定向到 `/{locale}/login?from=...`（`src/proxy.ts:72`）。
  - key 无效则删除 `auth-token` cookie 并重定向（`src/proxy.ts:84`）。
- **Next.js matcher 选择器语义未实现**：原文件配置 `config.matcher` 影响哪些路径进入 middleware（`src/proxy.ts:103`）。

**KarisCode 中已存在但“未接入中间件链路”的相关实现（不等于完成 1:1）**

- `auth-token` cookie 读写/清理：`KarisCode/backend/internal/service/auth/cookies.go:8`
- `ValidateKey`（含 read-only 绕过 `can_login_web_ui` 的选项语义）：`KarisCode/backend/internal/service/auth/service.go:53`

## 数据库（Drizzle migrations vs KarisCode migrations）——已修复

**结论（最终结构）**

- KarisCode 已对齐当前项目 drizzle：`providers.allowed_models` 默认值为 `DEFAULT 'null'::jsonb`（`KarisCode/backend/migrations/000001_core_tables.up.sql:86` / `drizzle/0009_many_amazoness.sql:1`）。

**备注（迁移历史层面，非最终结构）**

- 当前项目 drizzle 的迁移历史包含“创建后又删除”的 `provider_schedule_logs`（`drizzle/0006_lame_matthew_murdock.sql:1` / `drizzle/0007_lazy_post.sql:1`），KarisCode migrations 中不存在对应历史；这不影响最终业务表集合，但意味着迁移集本身不是 1:1。

## `src/actions/active-sessions-utils.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **批量终止 Session 的“去重/缺失/越权”汇总逻辑未实现**：原文件提供 `summarizeTerminateSessionsBatch()`，用于在批量终止前对请求的 sessionIds 做去重、判定缺失、按当前用户/管理员权限划分 allowed vs unauthorized，并返回统计摘要（`src/actions/active-sessions-utils.ts:14`）。KarisCode 侧没有等价的汇总/鉴权分组逻辑。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 仅有“按 sessionId 删除 Redis 绑定与监控键”的基础终止能力：`KarisCode/backend/internal/service/session/session_manager.go:793`
- 基础批量终止（逐个调用 TerminateSession，无权限/缺失统计）：`KarisCode/backend/internal/service/session/session_manager.go:845`

## `src/actions/active-sessions.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层（Server Action）接口未落地/未对外提供**：原文件导出 `getActiveSessions/getAllSessions/getSessionMessages/hasSessionMessages/getSessionDetails/getSessionRequests/terminateActiveSession/terminateActiveSessionsBatch` 等一组“面向 UI 的权限/格式化/分页”动作；KarisCode 当前没有对应 HTTP handler/路由把这些能力对外暴露，启动入口目前仅可见基础路由注册（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **权限隔离语义未 1:1 复刻**：原实现对读取与终止都做“管理员全量可见/普通用户仅可见自己的 session”与所有权校验（`src/actions/active-sessions.ts:21`）。KarisCode 的 `TerminateSession` 只做 Redis 键删除，不包含 userId 级别的所有权校验（`KarisCode/backend/internal/service/session/session_manager.go:793`）。
- **数据源与口径不一致**：原实现依赖数据库聚合（`aggregateSessionStats/aggregateMultipleSessionStats/findRequestsBySessionId` 等）以确保与其他页面口径一致（`src/actions/active-sessions.ts:82`）。KarisCode 的 `GetActiveSessions` 走 Redis `session:*:info/usage` 直接拼装（`KarisCode/backend/internal/service/session/session_manager.go:648`），与 DB 聚合口径不是 1:1。
- **活跃/非活跃判定口径不一致**：原实现用 `lastRequestAt` 与固定 5 分钟窗口划分（`src/actions/active-sessions.ts:196`）。KarisCode 的 `GetAllSessionsWithExpiry` 用 `StartTime` 与 `SessionTTL` 窗口划分（`KarisCode/backend/internal/service/session/session_manager.go:680` / `KarisCode/backend/internal/config/config.go:28`），语义不等价。
- **活跃/非活跃判定口径不一致**：原实现用 `lastRequestAt` 与固定 5 分钟窗口划分（`src/actions/active-sessions.ts:192`）。KarisCode 的 `GetAllSessionsWithExpiry` 用 `StartTime` 与 `SessionTTL` 窗口划分（`KarisCode/backend/internal/service/session/session_manager.go:680` / `KarisCode/backend/internal/config/config.go:28`），语义不等价。
- **缓存策略未复刻**：原实现有 `active sessions` / `all sessions` / `session details` 的 in-memory cache（`src/actions/active-sessions.ts:36`）。KarisCode 未实现等价的 action 侧缓存层（目前仅看到 session Redis 存储与少量系统设置缓存，并非同一层面的策略）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- Redis session 追踪与并发计数（供“活跃 session 列表/并发数/按 provider 统计”使用）：`KarisCode/backend/internal/service/session/session_tracker.go:15`
- DB 侧 session 聚合统计与分页请求列表的仓库接口（但缺少对应 service/handler 编排与权限隔离）：`KarisCode/backend/internal/repository/message_repository.go:39`
- 读取/写入 session messages/response 的 Redis 存储能力（仍缺少“按用户权限公开”的动作层封装）：`KarisCode/backend/internal/service/session/session_manager.go:537`

## `src/actions/client-versions.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 `fetchClientVersionStats()` 并做管理员权限校验（`src/actions/client-versions.ts:15`）。KarisCode 仅有服务层实现，缺少等价的 HTTP handler/路由与权限检查接入。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 客户端版本统计核心逻辑（含 GA 版本探测、活跃用户聚合、缓存策略）：`KarisCode/backend/internal/service/clientversion/client_version_checker.go:199`
- 最小登录/登出路由（用于设置 auth cookie），但未在启动入口注册：`KarisCode/backend/internal/handler/auth/routes.go:20` / `KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`

## `src/actions/concurrent-sessions.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 `getConcurrentSessions()`（`src/actions/concurrent-sessions.ts:10`）。KarisCode 目前没有等价的对外 API。
- **时间窗口口径不保证一致**：原注释明确“5分钟窗口”（`src/actions/concurrent-sessions.ts:8`）。KarisCode 的活跃窗口由 `SESSION_TTL` 决定（默认 300 秒，但可配置，语义不保证恒等）（`KarisCode/backend/internal/config/config.go:28` / `KarisCode/backend/internal/service/session/session_tracker.go:224`）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 全局活跃 session 计数（基于 ZSET 清理窗口并校验 `session:*:info` 是否存在）：`KarisCode/backend/internal/service/session/session_tracker.go:131`

## `src/actions/dashboard-realtime.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **“数据大屏一键聚合”编排动作未实现/未接入**：原文件 `getDashboardRealtimeData()` 并行拉取 overview、activity stream、各类 leaderboard、provider slots、statistics，并用 `allSettled` 做部分失败容错（`src/actions/dashboard-realtime.ts:88`）。KarisCode 缺少等价的 service/handler 把这些数据源组合成同一响应形状。
- **权限控制链路未复刻到入口**：原实现基于“管理员或 allowGlobalUsageView=true”控制全局数据可见性（`src/actions/dashboard-realtime.ts:99`）。KarisCode 虽有 `AllowGlobalUsageView` 系统设置缓存与默认初始化，但缺少等价的 dashboard endpoint 与权限判定接入点（`KarisCode/backend/internal/service/systemsettings/system_settings_cache.go:39`）。
- **providerSlots 维度未实现**：原实现把“供应商并发插槽状态”与“供应商流量榜”合并排序并裁剪（`src/actions/dashboard-realtime.ts:223`）。KarisCode 未看到等价的 ProviderSlotInfo 计算/输出结构与对外接口（目前只有底层 provider 活跃 session 计数与 provider 并发限制字段，并未形成 slots API）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 活动流查询仓库（支持“活跃 session 最新请求 + 最近请求补齐”）：`KarisCode/backend/internal/repository/activity_stream_repository.go:45`
- 排行榜聚合仓库（user/provider/model）：`KarisCode/backend/internal/repository/leaderboard_repository.go:10`
- 概览指标仓库：`KarisCode/backend/internal/repository/overview_repository.go:12`
- 统计（含 today/7d/30d 等）仓库：`KarisCode/backend/internal/repository/statistics_repository.go:12`
- Session tracker 的按 provider 计数批量接口（可作为 providerSlots 的底层数据之一，但当前未形成 dashboard 聚合输出）：`KarisCode/backend/internal/service/session/session_tracker.go:143`
