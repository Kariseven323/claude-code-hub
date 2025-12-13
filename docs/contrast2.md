# `chat-completions-handler.ts` / `codex-cli-adapter.ts` vs `KarisCode/` 重写对照

本文仅对照以下两个 Next.js/TypeScript 文件与 `KarisCode/`（Go）中对应“意图/职责”实现，判断是否达到 **对外行为语义（HTTP 契约 + 处理流程）** 的 1:1 复刻，并列出语义一致/不一致点。

- `src/app/v1/_lib/codex/chat-completions-handler.ts`
- `src/app/v1/_lib/codex/codex-cli-adapter.ts`

## 结论总览

| Next.js 文件 | 主要职责 | KarisCode 对应实现（按职责拆分） | 是否 1:1 复刻 | 关键结论 |
| --- | --- | --- | --- | --- |
| `src/app/v1/_lib/codex/chat-completions-handler.ts` | `/v1/chat/completions` + `/v1/responses` 的入口 handler：格式校验/标记 + 复用代理管线（auth/session/sensitive/rate/provider/forward/response） | **缺失 HTTP 入口**：`KarisCode/backend/cmd/server/main.go` 未挂载 `/v1/*`；仅存在底层组件：`KarisCode/backend/internal/proxy/*`、`KarisCode/backend/internal/service/converter/*`、`KarisCode/backend/internal/service/proxyforwarder/*` | 否 | KarisCode 目前没有等价的 handler/路由，因此对外行为无法 1:1 |
| `src/app/v1/_lib/codex/codex-cli-adapter.ts` | （存疑/可选）对 Codex 供应商注入“Codex CLI system instructions”并删除少量不兼容字段 | **无直接等价实现**；更接近的是“官方 Codex instructions 策略 + 协议转换”：`KarisCode/backend/internal/proxy/codex_adapter.go` + `KarisCode/backend/internal/service/converter/openai_to_codex.go` + `KarisCode/backend/internal/service/codexinstructions/*` | 否 | KarisCode 实现的是“官方 prompt 注入/清洗 + 格式转换”，不是此 TS 文件的“CLI instructions 注入器”；且 TS 文件在本仓库也未被调用 |

---

## `src/app/v1/_lib/codex/chat-completions-handler.ts`

### TS 侧真实入口（调用关系）

`src/app/v1/[...route]/route.ts` 将两个路径都指向同一个 handler：

- `POST /v1/chat/completions` → `handleChatCompletions`
- `POST /v1/responses` → `handleChatCompletions`

handler 内部通过请求体 shape 判别 **OpenAI Chat Completions**（`messages[]`）与 **Responses API**（`input[]`）。

### KarisCode 侧对应实现（按职责拆分）

KarisCode 目前没有对外的 `/v1/*` 代理路由（`KarisCode/backend/cmd/server/main.go` 仅注册了 `/health`、`/api/version` 与一系列 `/api/*` 管理/动作路由）。

但存在可复用的底层“拼图”：

- **格式检测（端点/请求体）**：`KarisCode/backend/internal/service/converter/format_mapper.go`
- **Codex/OpenAI/Claude 协议转换与策略**：`KarisCode/backend/internal/proxy/codex_adapter.go`
- **Session 结构与识别（包含 messages/input/gemini shapes）**：`KarisCode/backend/internal/proxy/session.go`
- **Guard Pipeline 抽象与若干 guard**：`KarisCode/backend/internal/proxy/guard_pipeline.go` + `KarisCode/backend/internal/proxy/{auth_guard,session_guard,rate_limit_guard,sensitive_word_guard,...}.go`
- **低层 HTTP 转发**：`KarisCode/backend/internal/service/proxyforwarder/forwarder.go`（含 proxy 配置、HTTP/2 回退、模型重定向、headers 处理等）

### 语义一致（已复刻/可对齐的子语义）

以下属于“功能拼图层”的一致性（注意：并不代表对外 handler 已 1:1）：

- **请求格式归一命名**：两边都有 `ClientFormat`（`response/openai/claude/gemini/gemini-cli`）与内部 `Format`（`codex/openai-compatible/claude/gemini-cli`）的映射思想：TS `src/app/v1/_lib/proxy/format-mapper.ts` ↔ Go `KarisCode/backend/internal/service/converter/types.go` + `format_mapper.go`。
- **Session 粘性/监控的“apiType”判断**：TS `session.originalFormat === "openai" ? "codex" : "chat"`（`src/app/v1/_lib/proxy/session-guard.ts`）↔ Go `ProxySession.APIType()` 将 `OriginalFormat=="openai"` 或路径命中 `/chat/completions`/`/responses` 视为 `codex`（`KarisCode/backend/internal/proxy/session.go`）。
- **Codex/OpenAI/Claude 的协议转换能力存在**：Go 明确标注多个 converter 为 “TS parity”，并在 `CodexAdapter` 中按 providerType 决定上游 endpoint（`/v1/messages`、`/v1/chat/completions`、`/v1/responses`）（`KarisCode/backend/internal/proxy/codex_adapter.go`）。

### 语义不一致（导致非 1:1）

这些差异是“对外行为语义”层面的硬缺失/不同：

- **缺失对外路由与 handler 绑定**：TS 实际对外提供 `ALL /v1/*`（且 `/chat/completions` 与 `/responses` 指向同一 handler）；KarisCode `main.go` 当前没有任何 `/v1` 路由注册，因此无法谈 1:1 行为复刻。
- **缺失 TS handler 的输入校验与错误响应语义**：TS 对请求体执行 shape 校验并在缺字段时返回 `400`（如缺少 `messages`/`input`，或 OpenAI 格式缺 `model`）；KarisCode 目前没有等价入口执行同样的校验/错误 body 结构。
- **缺失 TS handler 的“复用代理管线”编排语义**：TS 顺序明确：`auth → session → sensitive → rateLimit → providerResolver → messageContext → forward → responseHandler`；KarisCode 虽有 guard 组件，但未见一个与 TS 等价的“代理入口”将它们按同样顺序串联并对外暴露。
- **缺失 TS handler 的请求记录/状态追踪语义**：TS 会创建 message context、在 provider 不可用时落库失败记录、并通过 `ProxyStatusTracker` 标记请求开始；KarisCode 在现有 HTTP 入口路径中未实现对应的“请求日志 + 状态 tracker”整体语义（guard 内虽有“敏感词拦截 best-effort 落库”，但不是同一层面的等价实现）。

---

## `src/app/v1/_lib/codex/codex-cli-adapter.ts`

### TS 文件的实际语义（只看文件本身）

该文件的导出函数 `adaptForCodexCLI(request)` 的语义是：

1. **（可选）**当 `ENABLE_CODEX_CLI_INJECTION` 打开且请求未包含 Codex CLI instructions 时，注入 `CODEX_CLI_INSTRUCTIONS`（来源 `src/app/v1/_lib/codex/constants/codex-cli-instructions.ts`）。
2. **（总是）**删除少量“Codex CLI 不支持”的字段：`temperature`、`top_p`、`user`、`truncation`。

但在本仓库中该函数 **没有被引用**（`rg adaptForCodexCLI` 仅命中定义处），因此它对当前 Next.js 运行时行为没有贡献。

### KarisCode 侧可能对应的“意图”实现

KarisCode 中更接近的实现不是“CLI instructions 注入器”，而是：

- **官方 Codex prompt（GPT-5/GPT-5-codex）判定与选择**：`KarisCode/backend/internal/service/codexinstructions/codex_instructions_cache.go`
- **OpenAI Chat → Codex Responses 的协议转换（并强制设置 Codex 所需字段）**：`KarisCode/backend/internal/service/converter/openai_to_codex.go`
- **按 provider 的 `codex_instructions_strategy` 应用 prompt 策略 + 清理官方 prompt**：`KarisCode/backend/internal/proxy/codex_adapter.go`

### 语义一致（已复刻/可对齐的子语义）

- **“官方 instructions”前缀判定**：TS `isOfficialInstructions()`（`src/app/v1/_lib/codex/constants/codex-instructions.ts`）↔ Go `codexinstructions.IsOfficialInstructions()`（`KarisCode/backend/internal/service/codexinstructions/codex_instructions_cache.go`）。
- **“默认 instructions 按模型名（是否含 codex）选择”**：TS `getDefaultInstructions()` ↔ Go `codexinstructions.GetDefaultInstructions()`。
- **Codex 上游对参数更严格的现实假设**：TS 在 Codex 清洗中会删除不支持参数并强制补齐 `stream/store/parallel_tool_calls`（`src/app/v1/_lib/codex/utils/request-sanitizer.ts`）；Go 的 OpenAI→Codex converter 也通过“重建请求体”的方式强制设置 `stream/store/parallel_tool_calls/include` 等字段，并丢弃不支持的 OpenAI 参数（`KarisCode/backend/internal/service/converter/openai_to_codex.go`）。

### 语义不一致（导致非 1:1）

- **“注入内容”不是同一个东西**：TS `codex-cli-adapter.ts` 的注入目标是 `CODEX_CLI_INSTRUCTIONS`（较短的 Codex CLI system instructions）；KarisCode 的注入/策略围绕的是“官方 Codex prompt”（`GPT5Prompt`/`GPT5CodexPrompt`），两者不是同一份文本，也不是同一语义层级。
- **默认开关/策略语义不同**：TS 文件里 `ENABLE_CODEX_CLI_INJECTION = false`，即默认不注入；KarisCode 的 `TransformOpenAIRequestToCodex()` 会无条件设置 `instructions` 为官方 prompt（随后 `CodexAdapter` 还可能按策略覆盖），默认行为更接近“强制官方 prompt”。
- **Responses API 原样透传时的字段清洗缺失**：TS 实际运行时对 Codex 请求会走 `sanitizeCodexRequest()`（会删除大量不支持字段并补齐必需字段）；而 KarisCode 的 `CodexAdapter` 在 `clientFmt == response && targetFmt == codex` 的分支中会将 body 视为“已是 Codex 形状”并基本透传（只做官方 prompt 清理/策略），未见与 TS 等价的“Responses API 透传清洗器”（这在将来真正挂载 `/v1/responses` 时会直接影响兼容性）。
- **TS 文件当前不生效 vs KarisCode 也未对外暴露**：TS 的 `codex-cli-adapter.ts` 目前未被调用；KarisCode 虽有相关 converter/adapter，但整体代理入口未挂载 `/v1/*`。两边在“是否影响线上行为”上都不是同一个层面的可比对象，因此更不能称为 1:1 复刻。

