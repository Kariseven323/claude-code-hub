# `compatible.ts` / `response.ts` / `request-sanitizer.ts` vs `KarisCode/` 重写对照

本文对照以下 3 个 Next.js/TypeScript 文件与 `KarisCode/`（Go）中最接近的对应实现，判断其是否达到 **对外行为语义（请求/响应契约 + 关键默认值/清洗策略）** 的 1:1 复刻，并列出 **语义一致** 与 **语义不一致/缺失** 的部分。

对照范围（按用户指定文件）：

- `src/app/v1/_lib/codex/types/compatible.ts`
- `src/app/v1/_lib/codex/types/response.ts`
- `src/app/v1/_lib/codex/utils/request-sanitizer.ts`

> 注意：其中 `compatible.ts` / `response.ts` 是 **类型定义**（不直接产生运行时行为），因此“语义”更多指它们定义/暗示的 **协议契约** 与仓库真实实现（TS 侧 converter/forwarder、Go 侧 handler/converter）是否一致。

## 结论总览

| TS 文件 | 主要职责（语义） | KarisCode 对应实现（最接近） | 是否 1:1 复刻 | 关键结论 |
| --- | --- | --- | --- | --- |
| `src/app/v1/_lib/codex/types/compatible.ts` | OpenAI Chat Completions（`/v1/chat/completions`）的**简化类型契约**（messages/tools/tool_choice/stream 等） | **无等价类型层**；行为/结构散落在：`KarisCode/backend/internal/service/converter/*openai*`、`KarisCode/backend/internal/handler/proxy/handlers.go` | 否 | KarisCode 的实际数据形状（尤其 `tool` role、`tool_calls`、`reasoning_content`、delta/toolcall chunk）明显超出/偏离该 TS 类型定义；无法称为 1:1 |
| `src/app/v1/_lib/codex/types/response.ts` | OpenAI Responses API（`/v1/responses`）的**类型契约**（input/output/SSE event type） | **无等价类型层**；Codex Responses 的真实形状由 converter 实现：`KarisCode/backend/internal/service/converter/openai_to_codex.go`、`codex_to_openai.go` | 否 | TS 文件本身的 `input/output` 建模与本仓库实际使用的 Codex Responses 形状（`function_call`/`function_call_output`、`include` 等）不一致；Go 侧实现更接近 TS 的 converter 文件而非此 types 文件 |
| `src/app/v1/_lib/codex/utils/request-sanitizer.ts` | **Codex 请求清洗**：官方客户端识别 + instructions 策略（auto/force/keep）+ 读取缓存纠偏 + 删除不支持参数 + 强制 stream/store/parallel_tool_calls | 部分拼图存在但**未 1:1**：`KarisCode/backend/internal/service/codexinstructions/*`、`KarisCode/backend/internal/service/converter/openai_to_codex.go`；以及未接入主链路的 `KarisCode/backend/internal/proxy/codex_adapter.go` | 否 | 关键差异：官方客户端 bypass、auto 策略语义、缓存对比覆盖、`_canRetryWithOfficialInstructions` 标记、以及“Responses 透传清洗”在 Go 主链路中缺失/未接入 |

---

## 1) `src/app/v1/_lib/codex/types/compatible.ts`

### TS 侧语义（文件本身）

该文件定义了 OpenAI Chat Completions 的简化契约：

- 请求：`ChatCompletionRequest`（`model`、`messages`、`tools`、`tool_choice`、`parallel_tool_calls`、`reasoning` 等）
- 非流式响应：`ChatCompletionResponse`（`choices[].message` + `usage`）
- 流式响应：`ChatCompletionChunk`（`choices[].delta` 仅包含 `role/content`）

并在注释中暗示“部分参数不支持/会被忽略”。

### KarisCode 侧最接近实现

KarisCode 并没有 1:1 的类型层定义（整体使用 `map[string]any` / `[]any`），但与该契约相关的结构/行为主要出现在：

- `/v1/chat/completions` 入口对 `messages[]`/`model` 的校验与 format 判别：`KarisCode/backend/internal/handler/proxy/handlers.go`
- OpenAI-compatible ↔ Codex/Claude/Gemini 的协议转换（包含 tools/tool_choice/image、stream chunk 形状）：`KarisCode/backend/internal/service/converter/*`

### 语义一致（可认为对齐的子集）

- **“messages + model” 作为 OpenAI chat 请求核心**：Go 入口同样把 `messages[]` 视为 OpenAI 格式，并要求 `model`（`KarisCode/backend/internal/handler/proxy/handlers.go` 的 `validateAndSetChatCompletionsFormat`）。
- **支持多模态的 `image_url` 思路**：Go 的 Codex↔OpenAI 互转中同样识别/生成 `type:"image_url"` 以及 `image_url.url`（例如 `KarisCode/backend/internal/service/converter/codex_to_openai.go`）。
- **工具调用与 `finish_reason=tool_calls` 的现实存在**：Go 的 Codex→OpenAI 响应转换会在 tool call 场景输出 `finish_reason:"tool_calls"`（例如 `KarisCode/backend/internal/service/converter/codex_to_openai.go`）。

### 语义不一致（契约层面不对齐）

以下差异会导致“按该 TS 类型理解的契约”与 KarisCode 的实际行为无法 1:1 对齐：

1. **role 枚举不完整**
   - TS `ChatMessage.role` 仅允许 `"system" | "user" | "assistant"`，但真实 OpenAI Chat Completions（以及本仓库 converter）会出现 `"tool"`（tool result）等角色。
   - Go 的 OpenAI→Codex 转换明确处理 `role=="tool"`、`tool_calls` 等（`KarisCode/backend/internal/service/converter/openai_to_codex.go`）。

2. **流式 chunk 的 delta 形状不完整**
   - TS `ChatCompletionChunk.choices[].delta` 仅包含 `role/content`。
   - Go 的转换会产生 `delta.reasoning_content`、`delta.tool_calls` 等字段（例如 `KarisCode/backend/internal/service/converter/codex_to_openai.go`），这在 TS 类型里不存在。

3. **非流式 `choices[].message.content` 的“必填”假设不稳**
   - TS 类型把 `ChatMessage.content` 设为必填。
   - Go 在 tool call-only 或仅 reasoning 的场景可能构造不带 `content` 的 message（`KarisCode/backend/internal/service/converter/codex_to_openai.go` 的 non-stream 组装逻辑会按存在性决定是否设置 `content`）。
   - 这不是“谁对谁错”，但说明 TS 类型并非对外契约的严格镜像，也无法作为 Go 端 1:1 的判据。

4. **“不支持参数会被忽略”的语义并非类型可保证**
   - 该 TS 文件把 `presence_penalty/frequency_penalty/stop/n` 标成“不支持/会忽略”，但这属于实现策略而非类型本身。
   - Go 在“无需转换”的路径（OpenAI→OpenAI-compatible 直通）会把这些字段原样转发到上游（由上游决定是否忽略/报错）；无法与该注释形成 1:1 的行为保证。

> 结论：`compatible.ts` 不是严格的协议契约；KarisCode 也没有等价的类型层约束，且其实际输出/处理的字段集合明显更宽，因此不能视为 1:1 复刻。

---

## 2) `src/app/v1/_lib/codex/types/response.ts`

### TS 侧语义（文件本身）

该文件尝试定义 `/v1/responses`（Responses API）的请求/响应/流式事件类型，包括：

- `ResponseRequest`：`model + input[] + stream/store/tools/tool_choice/...`
- `ResponseObject`：`output[]`（reasoning/message/tool_calls）+ `usage`
- `SSEEventType` 与若干 event data interface

### KarisCode 侧最接近实现

KarisCode 同样没有 1:1 的类型层，但对 Responses/Codex 形状的“真实解释”体现在 converter 中：

- OpenAI Chat → Codex Responses（构造 `input[]`、强制 stream/store/parallel_tool_calls/include）：`KarisCode/backend/internal/service/converter/openai_to_codex.go`
- Codex Responses → OpenAI Chat（解析 `response.*` SSE / non-stream response）：`KarisCode/backend/internal/service/converter/codex_to_openai.go`

### 语义一致（可认为对齐的子集）

- **存在 `response.*` 的事件谱系与 delta 思路**：Go 的 Codex→OpenAI 流式转换同样以 `response.created / response.output_text.delta / response.completed` 等事件类型驱动（`KarisCode/backend/internal/service/converter/codex_to_openai.go`）。
- **`usage` 的核心语义（input/output/total tokens）**：Go 会从 Codex usage 映射到 OpenAI chat usage（`buildCodexUsagePayload`），与 TS 类型对 tokens 的关注方向一致。

### 语义不一致（类型与真实 payload 不吻合）

这些差异基本决定了“按 `response.ts` 理解的 Responses 契约”无法在 KarisCode 中 1:1 成立：

1. **`input[]` 的建模与本仓库实际使用的 Codex Responses 形状不一致**
   - TS `InputItem` 仅允许 `MessageInput | ToolOutputsInput`（`tool_outputs`）。
   - 但本仓库的 Codex Responses 互转（TS converter 与 Go converter）实际使用/生成的是 `type:"message" | "function_call" | "function_call_output"` 这套形状（见 `src/app/v1/_lib/converters/openai-to-codex/request.ts` 与 `KarisCode/backend/internal/service/converter/openai_to_codex.go`）。
   - 这意味着 `response.ts` 更像“另一版 Responses API”草图，而非本仓库 Codex 路径的真实契约。

2. **`output[]` 的 tool call 表达不同**
   - TS `ResponseObject.output` 中的工具调用是 `type:"tool_calls" + tool_calls:[...]`。
   - 但本仓库 Codex→OpenAI 的处理路径会遇到 `type:"function_call"`（流式为 `response.output_item.done` 且 `item.type=="function_call"`；非流式为 `output[]` 中的 `type=="function_call"`）（`KarisCode/backend/internal/service/converter/codex_to_openai.go`）。

3. **SSE event 的“承载方式”不同**
   - TS `response.ts` 把 SSE 抽象为 `{event, data}`。
   - 但本仓库的实际转换器（TS 与 Go）主要读取 `data:` 行里的 JSON，并以 `data.type` 作为事件类型（例如 `src/app/v1/_lib/converters/codex-to-openai/response.ts` 与 `KarisCode/backend/internal/service/converter/codex_to_openai.go`）。

4. **缺少 `include` 等关键字段**
   - Go 的 Codex 请求构造会显式设置 `include:["reasoning.encrypted_content"]`（`KarisCode/backend/internal/service/converter/openai_to_codex.go`）。
   - TS `ResponseRequest` 类型没有该字段，导致“类型层面”与真实请求体存在缺口。

> 结论：`response.ts` 与本仓库实际跑通的 Codex Responses 转换路径并非同一套 payload 形状；KarisCode 侧实现也自然不可能 1:1 对齐该 types 文件。

---

## 3) `src/app/v1/_lib/codex/utils/request-sanitizer.ts`

### TS 侧语义（真实运行时行为的一部分）

该文件在 TS 侧 **会被调用**（见 `src/app/v1/_lib/proxy/forwarder.ts` 的 Codex 分支），其语义可以概括为：

1. **识别官方 Codex 客户端**（按 `User-Agent` 前缀：`codex_vscode|codex_cli_rs`）。
2. **按策略处理 `instructions`**：
   - `force_official`：替换为官方 prompt（`getDefaultInstructions(model)`）。
   - `keep_original`：透传（不注入、不添加重试标记）。
   - `auto`（默认）：读取 `CodexInstructionsCache`，对比长度差异（阈值 5%）决定是否覆盖为缓存值；若不使用缓存则添加 `_canRetryWithOfficialInstructions=true`。
   - 且：官方客户端 + `auto` 时可 bypass（直接返回原始请求）。
3. **删除 Codex 不支持参数**（一组明确的 key）。
4. **强制/补齐 Codex 所需字段**：`stream`（缺省 true）、`store=false`、`parallel_tool_calls=true`。

### KarisCode 侧最接近实现（但并非 1:1）

KarisCode 中与上述语义相关的“拼图”包括：

- 官方 prompt 与“是否官方 instructions”判定：`KarisCode/backend/internal/service/codexinstructions/codex_instructions_cache.go`
- Redis 缓存（声称 port 自 TS）：`KarisCode/backend/internal/service/codexinstructions/codex_instructions_cache.go`
- OpenAI→Codex 请求构造时的强制字段与丢弃不支持参数（通过“重建请求体”达成）：`KarisCode/backend/internal/service/converter/openai_to_codex.go`
- 但：最像“sanitizer+strategy”的实现是 `KarisCode/backend/internal/proxy/codex_adapter.go`，而它目前**未接入**主 proxy handler 链路（仅见于该包测试引用）。

### 语义一致（已复刻/可对齐的子语义）

- **官方 instructions 的前缀判定 + 默认 prompt 选择**：
  - TS `isOfficialInstructions()` / `getDefaultInstructions()`（`src/app/v1/_lib/codex/constants/codex-instructions.ts`）
  - Go `codexinstructions.IsOfficialInstructions()` / `codexinstructions.GetDefaultInstructions()`（`KarisCode/backend/internal/service/codexinstructions/codex_instructions_cache.go`）
- **“通过重建请求体”强制设置 Codex 所需字段的思路**：
  - TS `transformOpenAIRequestToCodex()` 与 sanitizer 都会强制 `stream=true/store=false/parallel_tool_calls=true`
  - Go `TransformOpenAIRequestToCodex()` 同样强制这些字段并设置 `include`（`KarisCode/backend/internal/service/converter/openai_to_codex.go`）

### 语义不一致/缺失（导致非 1:1 的关键点）

1. **官方客户端识别与 bypass 缺失**
   - TS：官方 Codex CLI + `auto` 策略可直接 bypass sanitizer（保持请求原样）。
   - Go：主链路中未见等价的 “User-Agent → official client” 判定，也没有“official + auto bypass”分支。

2. **`auto` 策略的本质语义不同**
   - TS `auto`：默认不“强制官方 prompt”，而是倾向于透传，并用缓存对比做纠偏；同时用 `_canRetryWithOfficialInstructions` 作为后续降级/重试的信号。
   - Go（若使用 `codex_adapter.go`）：`auto` 会在 instructions 缺失/非官方时直接注入官方 prompt（`applyCodexInstructionsStrategy`），与 TS `auto` 的“透传优先”不同。

3. **缓存对比覆盖与 `_canRetryWithOfficialInstructions` 标记缺失**
   - TS：`auto` 下会读取 `CodexInstructionsCache` 并按 5% 长度阈值覆盖，且在非缓存路径添加 `_canRetryWithOfficialInstructions=true`。
   - Go：虽然有 Redis cache 的 `Get/Set`（`codexinstructions.CodexInstructionsCache`），但主链路与 `codex_adapter.go` 均未实现“长度阈值对比覆盖”，也没有 `_canRetryWithOfficialInstructions` 这种重试标记字段。

4. **“Responses 透传清洗”缺失**
   - TS：无论请求是否经过格式转换，只要上游是 Codex，都会执行 `sanitizeCodexRequest()`（删除不支持字段 + 强制 stream/store/parallel_tool_calls 等）。
   - Go：主 proxy handler 仅在“from!=to”时做 converter 变换；若客户端本身就是 Responses（`input[]`）且上游也是 Codex，则基本会直通，不会做等价的“删除不支持字段/补齐默认值”的清洗步骤。

5. **策略未接入主链路（落地缺失）**
   - TS：provider 的 `codexInstructionsStrategy` 会影响 sanitizer 行为（见 `src/app/v1/_lib/proxy/forwarder.ts` 的 Codex 分支）。
   - Go：provider 的 `CodexInstructionsStrategy` 仅在 `KarisCode/backend/internal/proxy/codex_adapter.go` 中被使用，但该 adapter 未被 `KarisCode/backend/internal/handler/proxy/handlers.go` 调用，导致策略在运行时不生效（无法形成 1:1 的行为语义）。

> 结论：KarisCode 侧只复刻了“官方 prompt 判定/默认 prompt/部分强制字段”的零散片段，但缺少 TS sanitizer 的核心决策逻辑与接入点，因此无法称为 1:1。
