# 对比：`/api/admin/database/status`（Next.js） vs `KarisCode` 重写

## 结论

`KarisCode` 已对 `GET /api/admin/database/status` 做到**语义 1:1 对齐**（以主项目 `src/app/api/admin/database/status/route.ts` 为准）。

- 主项目：`src/app/api/admin/database/status/route.ts`
- KarisCode：`KarisCode/backend/internal/handler/admin/database_status.go` + `KarisCode/backend/internal/handler/admin/routes.go`

---

## 对应关系（Mapping）

### 主项目（TypeScript / Next.js）

- 路由文件：`src/app/api/admin/database/status/route.ts`
- HTTP：`GET /api/admin/database/status`
- 依赖：
  - 管理员鉴权：`getSession()`（cookie session）并要求 `session.user.role === "admin"`（`route.ts#L20-L24`）
  - DSN 配置：`getDatabaseConfig()`（`src/lib/database-backup/db-config.ts`）
  - 连接探测：`checkDatabaseConnection()`（`src/lib/database-backup/docker-executor.ts`）
  - 详情查询：`getDatabaseInfo()`（`src/lib/database-backup/docker-executor.ts`）
  - 返回模型：`DatabaseStatus`（`src/types/database-backup.ts`）

### KarisCode（Go / Gin）

- HTTP handler：`KarisCode/backend/internal/handler/admin/database_status.go`
  - 路由：`GET /api/admin/database/status`（注册于 `KarisCode/backend/internal/handler/admin/routes.go`）
  - 管理员鉴权：cookie `auth-token` → `AuthService.ValidateKey()` → role=admin
  - DSN 解析：按 TS `parseDatabaseDSN()` 语义解析 host/port/user/password/database
  - 连接探测：`pg_isready`
  - 信息查询：`psql -t -A -c <query>` 并按 TS 规则解析输出

- 共享类型/服务（备份相关复用）：`KarisCode/backend/internal/service/datamanagement/database_backup_service.go`

---

## 语义一致（Semantically Equivalent）

以下部分可以认为是“语义上对齐/等价”的实现（不代表行为逐字节一致）：

1. **返回结构字段对齐**
   - TS：`DatabaseStatus` 字段为 `isAvailable/containerName/databaseName/databaseSize/tableCount/postgresVersion/error?`（`src/types/database-backup.ts`）
   - Go：`DatabaseStatus` JSON tag 与字段含义一致（`database_backup_service.go#L25-L34`）

2. **连接探测使用 `pg_isready`**
   - TS：`checkDatabaseConnection()` spawn `pg_isready ...`，以退出码是否为 0 判定可用（`src/lib/database-backup/docker-executor.ts#L473-L505`）
   - Go：`CheckDatabaseConnection()` 使用 `pg_isready ...`，以命令是否成功运行判定可用（`database_backup_service.go#L79-L103`）

3. **数据库信息查询 SQL 目标一致**
   - TS：`getDatabaseInfo()` 查询 `pg_database_size/current_database()`、public schema 下 base table 数量、`version()`（`src/lib/database-backup/docker-executor.ts`）
   - Go：`GetStatus()` 使用同样的 SQL 结构获取 size/table_count/version（`database_backup_service.go#L136-L156`）

4. **“连接不可用”不被当作“路由级错误”**
   - TS：连接不可用时仍返回 HTTP 200 + `isAvailable:false`（`route.ts#L32-L50`）
   - Go：`GET /api/admin/database/status` 连接不可用时同样返回 HTTP 200 + `isAvailable:false`，并使用相同的中文 `error` 文案
   - 这两者的意图一致：把“数据库不可用”当作状态信息而不是异常

---

## 语义不一致（Semantically Different / Missing）

（A/B/C/D/F 已通过补全 handler 与调整实现对齐，不再列为差异项。）

### E. “Unauthorized” 响应体类型与前端使用方式冲突（主项目自身问题）

- TS：未授权时返回纯文本 `new Response("Unauthorized", { status: 401 })`（`route.ts#L21-L24`），不是 JSON。
- 现有 UI（`src/app/[locale]/settings/data/_components/database-status.tsx`）在 `!response.ok` 时会 `await response.json()`（这在 401 文本时会抛异常），所以错误显示会变得不可控。
- KarisCode 为保持 1:1，对该 endpoint 同样返回纯文本 `"Unauthorized"`。
