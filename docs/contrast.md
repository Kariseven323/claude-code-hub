# 重写差异对照（按原项目文件）

本文按“原项目文件”逐个列出：在 `KarisCode/` 重写版本中**缺少**（未实现/未接入/行为不等价）的内容。

## `src/instrumentation.ts`

**已补齐（KarisCode 已接入/实现的部分）**

- 启动入口已接入初始化链路（迁移/seed/调度/探测）：`KarisCode/backend/cmd/server/main.go:33`
- CI 跳过初始化：`KarisCode/backend/cmd/server/main.go:68`
- 生产环境 DB 不可用直接退出（用户选择“强制 DB”）：`KarisCode/backend/cmd/server/main.go:74`
- `AUTO_MIGRATE` 开关用于控制是否执行迁移与生产环境定时任务：`KarisCode/backend/cmd/server/main.go:80`
- 自动迁移实现（嵌入 migrations + 幂等记录 + advisory lock）：`KarisCode/backend/internal/database/migrate.go:53`，嵌入入口 `KarisCode/backend/migrations/embed.go:1`
- 价格表 seed：`KarisCode/backend/cmd/server/main.go:141`
- 默认错误规则同步（用户自定义优先）+ detector reload（非关键）：`KarisCode/backend/cmd/server/main.go:149`；同步实现 `KarisCode/backend/internal/service/errorrules/sync_default_rules.go:17`
- 生产环境启动日志清理调度：`KarisCode/backend/cmd/server/main.go:169`
- 生产环境启动通知调度：`KarisCode/backend/cmd/server/main.go:175`
- 智能探测调度器（可在开发/生产启用）：`KarisCode/backend/cmd/server/main.go:186`

**仍有差异（未做到严格 1:1 的点）**

- 错误规则默认列表在 Go 侧为手工镜像（存在与 TS `DEFAULT_ERROR_RULES` 漂移风险）：`KarisCode/backend/internal/service/errorrules/default_rules.go:1`
- TS 的 next.js instrumentation 把 detector 作为模块单例使用；Go 侧目前是在启动时 reload 一次，后续需要由调用方持有/注入 detector（是否要求“全局单例”取决于后续 proxy 组装方式）。

## `src/proxy.ts`

**已补齐（KarisCode 已接入/实现的部分）**

- 请求入口中间件已接入：`KarisCode/backend/cmd/server/main.go:197`
- `/v1` 直通：`KarisCode/backend/internal/middleware/webui_proxy.go:50`
- 静态资源/内部路径跳过：`KarisCode/backend/internal/middleware/webui_proxy.go:56`
- locale 前缀 always（缺失则重定向）+ `NEXT_LOCALE` cookie：`KarisCode/backend/internal/middleware/webui_proxy.go:71`
- public/read-only 路径策略：`KarisCode/backend/internal/middleware/webui_proxy.go:97`
- cookie 缺失/无效时重定向到 `/{locale}/login?from=...`，无效时清 cookie：`KarisCode/backend/internal/middleware/webui_proxy.go:112`
- 登录/登出接口（供 Web UI 使用）：`KarisCode/backend/internal/handler/auth/routes.go:17`

**仍有差异（未做到严格 1:1 的点）**

- Go 侧是“近似 next-intl”的 locale 处理（cookie/Accept-Language 解析 + 重定向），不可能 100% 等同 next-intl middleware 的全部边界行为：`KarisCode/backend/internal/middleware/webui_proxy.go:224`

## `src/actions/overview.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层/对外接口未落地**：原文件是 server action（登录校验 + 聚合并发数/今日指标）；KarisCode 启动入口未注册任何对应管理路由（`KarisCode/backend/cmd/server/main.go:40`）。
- **权限裁剪语义未复刻**：原逻辑基于 `allowGlobalUsageView`（或管理员）决定是否返回全站数据，否则返回全 0（`src/actions/overview.ts:41` / `src/actions/overview.ts:52`）；KarisCode 未见等价的 action/service 编排。
- **并发数来源与拼装链路未接入**：原并发数来自 Redis（`src/actions/overview.ts:46`，通过 `src/actions/concurrent-sessions.ts:10`）；KarisCode 虽有 session 追踪/计数能力，但未在 overview 输出中使用。
- **错误率口径不等价**：原输出包含 `todayErrorRate`（百分比）并在动作层计算（`src/repository/overview.ts:52`）；KarisCode 的 overview 查询只返回 `today_error_count`，未提供等价的 error rate 计算与输出（`KarisCode/backend/internal/repository/overview.sql.go:16`）。
- **timezone 参数类型疑似错误（硬缺陷）**：SQL 用 `AT TIME ZONE $1`，但 sqlc 生成的入参类型为 `pgtype.Interval`（`KarisCode/backend/internal/repository/overview.sql.go:34`），与“时区字符串”语义不匹配，存在运行时 scan/绑定失败风险。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- system_settings 缓存（含 `AllowGlobalUsageView`）：`KarisCode/backend/internal/service/systemsettings/system_settings_cache.go:33`
- overview 仓库查询（仅 DB 聚合行）：`KarisCode/backend/internal/repository/overview_repository.go:12`
- session 追踪/计数（可用于并发数）：`KarisCode/backend/internal/service/session/session_tracker.go:108`

## `src/actions/provider-slots.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层/对外接口未落地**：原文件输出 provider 并发插槽状态；KarisCode 目前只暴露 `/health` 与 `/api/version`，未接入等价接口（`KarisCode/backend/cmd/server/main.go:40`）。
- **权限控制语义未复刻**：原逻辑要求“管理员或 allowGlobalUsageView=true”才可查看（`src/actions/provider-slots.ts:45` / `src/actions/provider-slots.ts:49`）；KarisCode 未见等价的鉴权与返回契约。
- **provider 列表筛选 + Redis 并发计数的聚合输出未实现**：原实现从 DB 取启用 provider 并逐个读取 Redis 的 provider session 计数（`src/actions/provider-slots.ts:59` / `src/actions/provider-slots.ts:74`）；KarisCode 只有底层 SessionTracker，没有“provider slots”聚合层。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- provider/session 并发计数底层：`KarisCode/backend/internal/service/session/session_tracker.go:131`

## `src/actions/providers.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件包含 providers 的完整管理面 API（列表/分组建议/CRUD/健康状态/熔断重置/限额用量/连通性测试/明文 key 获取/presets 等，`src/actions/providers.ts:92`）；KarisCode 启动入口未注册任何对应路由（`KarisCode/backend/cmd/server/main.go:40`）。
- **管理员鉴权 + 返回契约未复刻**：原实现大量分支依赖 session 的管理员权限与 `ActionResult` 形状；KarisCode 缺少等价的 handler 编排，无法保证 1:1 的错误语义与输出结构。
- **输入校验/安全检查链路未复刻**：原实现使用 Zod 校验、proxy URL 校验、favicon URL 生成、以及多处错误分类/降级逻辑（`src/actions/providers.ts:28` / `src/actions/providers.ts:314`）；KarisCode 目前只有底层 service，缺少对外入口与一致的校验策略。
- **provider health status 输出未接入**：原实现提供 health status 聚合（`src/actions/providers.ts:599`）；KarisCode 有 circuit breaker 的 health snapshot，但未形成对外接口与返回结构。
- **限额用量/批量用量接口缺失**：原 `getProviderLimitUsage*` 依赖 Redis/DB 并输出特定结构（`src/actions/providers.ts:664`）；KarisCode 未见等价的聚合输出与对外接口。
- **“解密/明文 provider key”接口缺失**：原 `getUnmaskedProviderKey` 仅管理员可取明文（`src/actions/providers.ts:1020`）；KarisCode 未见等价对外接口与安全边界。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- provider 仓库（CRUD/分组/统计）：`KarisCode/backend/internal/repository/provider_repository.go:120`
- 熔断器 reset（底层）：`KarisCode/backend/internal/service/circuitbreaker/circuit_breaker.go:349`
- provider 连通性测试（统一测试服务 + presets）：`KarisCode/backend/internal/service/providertesting/service.go:19`

## `src/actions/proxy-status.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层/对外接口未落地**：原文件是 server action（仅登录即可查看全用户 proxy status，`src/actions/proxy-status.ts:11`）；KarisCode 未注册等价路由/handler（`KarisCode/backend/cmd/server/main.go:40`）。
- **“基于 DB 聚合”的输出契约未对齐到可调用层**：KarisCode 有 tracker/repo，但缺少暴露层，因此无法验证与原 `ProxyStatusResponse` 的 1:1 行为一致性。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- proxy status tracker（DB 聚合）：`KarisCode/backend/internal/service/proxystatus/tracker.go:31`
- proxy status repository（3 组查询：users/active/last）：`KarisCode/backend/internal/repository/proxy_status_repository.go:36`

## `src/actions/rate-limit-stats.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层/对外接口未落地**：原文件是 admin-only 的 server action（`src/actions/rate-limit-stats.ts:22`）；KarisCode 未注册等价路由（`KarisCode/backend/cmd/server/main.go:40`）。
- **“rate_limit_metadata”解析 + 6 维聚合输出缺失**：原实现从 `message_request.error_message` 解析 `rate_limit_metadata` 并输出 `events_by_type/events_by_user/events_by_provider/events_timeline/avg_current_usage` 等（`src/repository/statistics.ts:818` / `src/repository/statistics.ts:947`）；KarisCode 目前只有原始事件列表查询，没有等价的聚合层与返回结构。
- **sqlc 生成类型疑似错误（硬缺陷）**：`DATE_TRUNC('hour', ...) AS hour` 应为 timestamp，但 sqlc 生成的 `ListRateLimitEventsRow.Hour` 是 `pgtype.Interval`（`KarisCode/backend/internal/repository/statistics.sql.go:960`），存在运行时 scan 失败/数据不可用风险。
- **timezone 参数类型疑似错误（硬缺陷）**：同样使用 `AT TIME ZONE $1`，但 sqlc 生成的 `ListRateLimitEventsParams.Timezone` 为 `pgtype.Interval`（`KarisCode/backend/internal/repository/statistics.sql.go:951`），与“时区字符串”语义不匹配。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- rate limit 事件列表查询（未聚合）：`KarisCode/backend/sqlc/queries/statistics.sql:457`
- statistics 仓库接口（含 `ListRateLimitEvents`）：`KarisCode/backend/internal/repository/statistics_repository.go:34`

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

## `src/actions/error-rules.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 list/create/update/delete/refresh/test/cacheStats 等 server actions（`src/actions/error-rules.ts:42`）。KarisCode 启动入口仅注册 `/health` 与 `/api/version`，没有任何 admin 路由/handler 可调用这些能力（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **默认规则同步（“用户自定义优先”策略）缺失**：原实现 `refreshCacheAction()` 里先 `syncDefaultErrorRules()`，再 reload detector，并按 `pattern/isDefault` 做 insert/update/skip/delete（`src/actions/error-rules.ts:396`）。KarisCode 目前只有“从 DB 拉取 active rules 并 reload 缓存”的能力，不包含“同步默认规则到 DB”的等价实现与接入点。
- **“编辑默认规则自动转自定义”语义缺失**：原 `updateErrorRuleAction()` 对 `currentRule.isDefault` 的规则会强制 `isDefault=false`，避免后续“同步规则”覆盖用户修改（`src/actions/error-rules.ts:274`）。KarisCode 目前缺少对应动作层编排。
- **写入前校验/返回契约未复刻**：原实现包含 matchType/category 白名单校验、overrideResponse/statusCode 校验、以及对 regex 模式的安全/语法检查（`src/actions/error-rules.ts:101`）。KarisCode 虽有覆写响应校验器，但缺少等价的“创建/更新入口”把这些校验与错误返回结构落到对外接口中。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 错误规则缓存 + 懒加载 reload：`KarisCode/backend/internal/service/errorrules/error_rule_cache.go:56`
- 错误规则检测器（contains/exact/regex）：`KarisCode/backend/internal/service/errorrules/error_rule_detector.go:31`
- 覆写响应体/状态码校验（Claude/Gemini/OpenAI 形状）：`KarisCode/backend/internal/service/errorrules/error_override_validator.go:14`
- DB CRUD（sqlc 产物）：`KarisCode/backend/internal/repository/error_rules.sql.go:43`

## `src/actions/keys.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 add/edit/remove/list/statistics/limit-usage 等 server actions（`src/actions/keys.ts:24`）。KarisCode 启动入口未注册任何对应 HTTP 路由（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **关键业务约束未实现**：
  - Key 名称去重（同一用户“生效 key”不能重名）（`src/actions/keys.ts:66`）。
  - Key 限额不得超过用户限额（多字段逐项校验）（`src/actions/keys.ts:75`）。
  - providerGroup 必须是用户 providerGroup 的子集（`src/actions/keys.ts:103`）。
  - 禁止删除“该用户最后一个可用 key”（`src/actions/keys.ts:321`）。
- **实时限额使用口径不等价**：原 `getKeyLimitUsage()` 依赖 Redis cost window（含 daily reset mode/time）+ DB total cost + 并发 session 统计（`src/actions/keys.ts:452`）。KarisCode 当前 rate limit 服务仅覆盖 5h/weekly/monthly，缺少 daily（fixed/rolling）与 total 的等价实现，无法 1:1 复刻返回结构（`KarisCode/backend/internal/service/ratelimit/service.go:111`）。
- **“keys with statistics”缺失**：原实现提供 `getKeysWithStatistics()`（`src/actions/keys.ts:427`）；KarisCode 仓库层未见等价查询与对外聚合输出。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- Key 基础仓库（CRUD/按用户列出/软删/按 key 查找）：`KarisCode/backend/internal/repository/key_repository.go:14`
- 并发 session 计数底层能力（可用于 key 的 concurrentSessions）：`KarisCode/backend/internal/service/session/session_tracker.go:15`
- 成本限额（5h/weekly/monthly）检查与追踪：`KarisCode/backend/internal/service/ratelimit/service.go:111`

## `src/actions/model-prices.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 upload/process/list/paginated/has/sync 等 server actions（`src/actions/model-prices.ts:36`）。KarisCode 启动入口未注册任何管理路由（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **管理侧权限与返回契约未复刻**：原实现所有管理动作都基于 session 的管理员鉴权，并返回 `ActionResult` 形状（`src/actions/model-prices.ts:126`）。KarisCode 缺少等价的鉴权 + handler 编排，无法保证 1:1 的错误处理与返回结构。
- **“按 providerType 返回可选模型”接口缺失**：原 `getAvailableModelsByProviderType()` 输出“所有 chat 模型名”（`src/actions/model-prices.ts:217`）。KarisCode 目前没有等价的对外接口。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- LiteLLM 价格表拉取（含 cache fallback）+ 导入/更新/unchanged 归类：`KarisCode/backend/internal/service/price/price_sync.go:45`
- model_prices 仓库（latest view、分页/计数）：`KarisCode/backend/internal/repository/model_price_repository.go:13`

## `src/actions/my-usage.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 quota/today-stats/usage-logs/models/endpoints 等 server actions（`src/actions/my-usage.ts:143`）。KarisCode 目前没有“以当前 session/key 为主体”的对外接口与权限隔离。
- **配额/限额口径不等价**：原配额计算依赖 daily reset mode/time 的 cost window、总消费、并发 session 等（`src/actions/my-usage.ts:151`）。KarisCode 的 rate limit 目前缺少 daily（fixed/rolling）与 total 的等价实现（`KarisCode/backend/internal/service/ratelimit/service.go:111`），因此无法 1:1 复刻 `MyUsageQuota`。
- **今日统计聚合与 breakdown 未实现/未接入**：原 `getMyTodayStats()` 既返回聚合 totals，也返回按 model 的 breakdown，并受系统设置 `billingModelSource/currencyDisplay` 影响（`src/actions/my-usage.ts:230`）。KarisCode 未看到等价的 service/handler 输出结构。
- **usage logs 的过滤/分页返回契约未落地**：原 `getMyUsageLogs()` 支持多维过滤与分页，并在返回中携带 billingModel/currency 元信息（`src/actions/my-usage.ts:318`）。KarisCode 虽有仓库查询能力，但缺少对应的动作层封装与权限控制。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- message_request usage logs 的仓库查询与聚合：`KarisCode/backend/internal/repository/usage_log_repository.go:15`

## `src/actions/notifications.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供读取/更新通知设置、以及 webhook 连通性测试（`src/actions/notifications.ts:80` / `src/actions/notifications.ts:87` / `src/actions/notifications.ts:118`）。KarisCode 启动入口未注册任何对应路由（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **“更新后重调度”链路未复刻**：原 `updateNotificationSettingsAction()` 更新后在生产环境触发重新调度（`src/actions/notifications.ts:93`）。KarisCode 虽有 `RequestReschedule()` 能力，但缺少“设置更新入口”去调用它（`KarisCode/backend/internal/service/notification/service.go:144`）。
- **webhook 测试与 SSRF 防护缺失**：原 `testWebhookAction()` 在测试前做 internal/private network 检测并拒绝（`src/actions/notifications.ts:15`）。KarisCode 的通知发送实现直接对 webhook URL 发起 HTTP 请求，缺少等价的 SSRF 防护与“测试接口”（`KarisCode/backend/internal/service/notification/wechat_notifier.go:44`）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 通知服务（生产环境调度 + best-effort 队列执行）：`KarisCode/backend/internal/service/notification/service.go:94`
- notification_settings 仓库（读/默认插入/更新）：`KarisCode/backend/internal/repository/notification_repository.go:12`

## `src/actions/request-filters.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 list/create/update/delete/refresh 等 server actions（`src/actions/request-filters.ts:46`）。KarisCode 启动入口未注册任何对应管理路由（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **管理员鉴权与返回契约未复刻**：原实现基于 session 的 admin 权限，并返回 `ActionResult`/空数组等约定形状（`src/actions/request-filters.ts:46` / `src/actions/request-filters.ts:68`）。KarisCode 缺少等价的 handler 编排与错误返回结构。
- **“修改后立即刷新内存过滤器”的链路缺失**：原 create/update/delete/refresh 会触发 `requestFilterEngine.reload()` 并 revalidate（`src/actions/request-filters.ts:87` / `src/actions/request-filters.ts:170`）。KarisCode 虽有 cache/engine，但缺少“更新入口 → 触发 reload”的接入点。
- **校验语义不等价**：原实现对 `text_replace + regex` 做 ReDoS 风险校验，并在更新时读取旧值防绕过（`src/actions/request-filters.ts:38` / `src/actions/request-filters.ts:120`）。KarisCode 当前没有对外 create/update 入口承载这些校验；如果直接落库非法 regex，Go 侧会在应用阶段跳过该规则而不是拒绝写入（`KarisCode/backend/internal/service/requestfilter/request_filter_engine.go:121`）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- request_filters 仓库 CRUD（sqlc 包装）：`KarisCode/backend/internal/repository/request_filter_repository.go:10`
- request filter 内存 cache（fail-open reload + 稳定排序）：`KarisCode/backend/internal/service/requestfilter/request_filter_cache.go:41`
- request filter engine（header/body 变换）：`KarisCode/backend/internal/service/requestfilter/request_filter_engine.go:22`
- proxy guard（应用过滤器到请求）：`KarisCode/backend/internal/proxy/request_filter_guard.go:11`

## `src/actions/sensitive-words.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 list/create/update/delete/refresh/stats 等 server actions（`src/actions/sensitive-words.ts:13` / `src/actions/sensitive-words.ts:212`）。KarisCode 启动入口未注册任何对应管理路由（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **管理员鉴权与返回契约未复刻**：原实现对所有动作做 admin 鉴权，并用 `ActionResult` 返回错误（`src/actions/sensitive-words.ts:37`）。KarisCode 缺少等价的 handler 编排与错误返回形状。
- **“增删改后立即刷新 detector 缓存”的链路缺失**：原 create/update/delete 会调用 `sensitiveWordDetector.reload()`（`src/actions/sensitive-words.ts:76` / `src/actions/sensitive-words.ts:142` / `src/actions/sensitive-words.ts:188`）。KarisCode 虽有 Reload，但缺少对应的对外入口触发它。
- **正则校验语义不等价**：原实现对 `matchType=regex` 的 word 做语法校验并拒绝写入（`src/actions/sensitive-words.ts:61`）。KarisCode 当前没有等价的写入入口承载校验；若 DB 中存在非法 pattern，Go 侧会记录错误并跳过该条（`KarisCode/backend/internal/service/filter/sensitive_word_cache.go:131`）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- sensitive_words 仓库 CRUD（sqlc 包装）：`KarisCode/backend/internal/repository/sensitive_word_repository.go:10`
- detector/cache（contains/exact/regex 分组 + fail-open reload）：`KarisCode/backend/internal/service/filter/sensitive_word_cache.go:41`
- proxy guard（命中敏感词直接拒绝并记录）：`KarisCode/backend/internal/proxy/sensitive_word_guard.go:17`

## `src/actions/session-response.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 `getSessionResponse(sessionId)` 的 server action（`src/actions/session-response.ts:15`）。KarisCode 没有对应 HTTP 路由/handler（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **权限/所有权校验未复刻（安全缺口）**：原实现要求“管理员可查看所有，普通用户仅可查看自己的 session”，并通过 DB 聚合校验 session 归属（`src/actions/session-response.ts:42`）。KarisCode 当前仅有 Redis 读写能力，未见等价的“读取前校验归属”的服务/接口层封装。
- **返回契约与错误语义不等价**：原返回 `{ ok: true; data } | { ok: false; error }` 且带中文错误信息（`src/actions/session-response.ts:17`）。KarisCode 缺少对外接口，无法保证 1:1 形状与提示文案。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- session 响应体存储（5 分钟 TTL，支持按 requestSequence 分桶）：`KarisCode/backend/internal/service/session/session_manager.go:553`
- proxy finalize 阶段写入 session response（best-effort）：`KarisCode/backend/internal/service/proxyresponse/finalize.go:79`

## `src/actions/statistics.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 `getUserStatistics(timeRange)` 的 server action（`src/actions/statistics.ts:35`）。KarisCode 没有对应 HTTP 路由/handler（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **“users/keys/mixed” 模式选择与裁剪语义未复刻**：原逻辑结合管理员身份与 `allowGlobalUsageView` 决定输出口径，并在 mixed 模式下拼接“其他用户”虚拟实体（`src/actions/statistics.ts:56` / `src/actions/statistics.ts:76` / `src/actions/statistics.ts:87`）。
- **图表数据拼装/字段命名规则未复刻**：原实现将 DB 行归并成 `ChartDataItem[]`，并用 `${dataKey}_cost/_calls` 生成动态字段（`src/actions/statistics.ts:98` / `src/actions/statistics.ts:129`）。KarisCode 未见等价的数据转换与输出结构。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- 统计查询仓库（today/7d/30d/thisMonth + key/others aggregate）：`KarisCode/backend/internal/repository/statistics_repository.go:12`
- system_settings 读取缓存（含 AllowGlobalUsageView）：`KarisCode/backend/internal/service/systemsettings/system_settings_cache.go:17`

## `src/actions/system-config.ts`

**缺少的内容（KarisCode 未 1:1 实现/未接入）**

- **动作层接口未落地/未对外提供**：原文件提供 fetch/save 系统设置的 server actions（`src/actions/system-config.ts:12` / `src/actions/system-config.ts:27`）。KarisCode 没有对应 HTTP 路由/handler（`KarisCode/backend/cmd/server/main.go:41` / `KarisCode/backend/cmd/server/main.go:48`）。
- **输入校验语义未复刻**：原实现用 Zod schema 校验并规范化输入（trim 等）（`src/actions/system-config.ts:47`）。KarisCode 未见等价的“更新入口 → 校验 → 写库”的封装。
- **更新后 cache 失效链路未接入**：原实现更新后显式 invalidate system settings cache（`src/actions/system-config.ts:62`）。KarisCode 虽有 `Invalidate()`，但缺少“更新入口”去调用它（`KarisCode/backend/internal/service/systemsettings/system_settings_cache.go:107`）。

**KarisCode 中已存在但“未串起来”的相关实现（不等于完成 1:1）**

- system_settings 仓库（get/insert default/update）：`KarisCode/backend/internal/repository/system_config_repository.go:10`
- system_settings TTL cache + fail-open fallback：`KarisCode/backend/internal/service/systemsettings/system_settings_cache.go:17`
