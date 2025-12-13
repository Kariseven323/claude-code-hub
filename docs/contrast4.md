# `claude-to-codex/*`（TS） vs `KarisCode` 重写对照

对照范围（按用户指定文件）：

- `src/app/v1/_lib/converters/claude-to-codex/index.ts`
- `src/app/v1/_lib/converters/claude-to-codex/request.ts`
- `src/app/v1/_lib/converters/claude-to-codex/response.ts`

KarisCode 侧对应实现（按“同名职责”）：

- `KarisCode/backend/internal/service/converter/claude_to_codex_request.go`
- `KarisCode/backend/internal/service/converter/claude_to_codex_response.go`
- “注册/装配”不在单独的 `index` 文件中：`KarisCode/backend/internal/service/converter/registry.go`（`RegisterDefaults`）

---

## 总览结论（是否 1:1）

| TS 文件 | KarisCode 对应 | 是否 1:1 复刻 | 结论 |
| --- | --- | --- | --- |
| `src/app/v1/_lib/converters/claude-to-codex/index.ts` | `KarisCode/backend/internal/service/converter/registry.go` | 否 | TS 以“同一次转换链（请求 from→to）”绑定**反向**响应转换器（Codex→Claude）；Go 以“响应方向（provider→client）”注册响应转换器（Claude→Codex / Codex→Claude 分开注册），组织方式与方向约定不一致 |
| `src/app/v1/_lib/converters/claude-to-codex/request.ts` | `KarisCode/backend/internal/service/converter/claude_to_codex_request.go` | 基本一致（但非严格 1:1） | 主干逻辑基本对齐；在少数边界输入上输出不同（见下文“语义不一致”） |
| `src/app/v1/_lib/converters/claude-to-codex/response.ts` | `KarisCode/backend/internal/service/converter/claude_to_codex_response.go` | 否 | Go 侧对 SSE 解析/分块更完整，导致在“单 chunk 多事件/多 data 行”等场景下与 TS 输出序列不一致；另有若干默认值/映射细节差异 |

---

## 语义一致（Semantically Equivalent）

### A. `request.ts` / `claude_to_codex_request.go`：Claude → Codex 请求体转换

以下属于“主干路径”的一致性（同字段含义、同形状输出）：

1. **基础输出骨架一致**
   - `model` 透传参数 `model`
   - 固定设置：`parallel_tool_calls: true`、`reasoning: {effort:"low", summary:"auto"}`、`store:false`、`include:["reasoning.encrypted_content"]`
   - `stream` 都被强制为 `true`（忽略调用入参 `stream`）

2. **`system` → 首个 `input` message（role=user, input_text）**
   - `system` 为 string：直接作为 `input_text`
   - `system` 为数组：拼接所有 `type:"text"` 的 `text`

3. **`messages[]` → `input[]`（message / function_call / function_call_output）**
   - `content` 为 string：按 `role` 输出 `input_text`（user）或 `output_text`（assistant）
   - `content` 为数组：
     - `type:"text"`：同上按 role 输出 `input_text`/`output_text`
     - `type:"image"`：base64 → `data:<media>;base64,<data>`；url → `image_url`
     - `type:"tool_use"`：输出 `{"type":"function_call", call_id, name, arguments}`
     - `type:"tool_result"`：输出 `{"type":"function_call_output", call_id, output}`

4. **`tools[]` → Codex tools（input_schema → parameters + 工具名缩短）**
   - 普通工具：`{type:"function", name:<short>, parameters:<input_schema without $schema>, strict:false}`
   - 特例：`type:"web_search_20250305"` → `{type:"web_search", name:"", parameters:{}}`

5. **`tool_choice` / `max_tokens` 的映射一致**
   - Claude `tool_choice`：`auto`→`auto`，`any`→`required`，`tool`（有 name）→`required`
   - `max_tokens` → `max_output_tokens`

6. **“特殊指令”前置注入一致**
   - 若 `input[0]` 是 `message` 且其首段文本不是指定字符串，则在 `input` 最前插入一条 `role:user` 的 `input_text` 指令。

### B. `response.ts` / `claude_to_codex_response.go`：Claude → Codex 响应转换（主干事件映射）

在“每个 chunk 恰好包含一个完整 SSE 事件（单 data 行）”的理想流式场景下，两边的事件映射是一致的：

- `message_start` → `response.created`
- `content_block_start (thinking)` → `response.reasoning_summary_part.added`
- `content_block_delta (thinking_delta)` → `response.reasoning_summary_text.delta`
- `content_block_start (text)` → `response.content_part.added`
- `content_block_delta (text_delta)` → `response.output_text.delta`
- `content_block_start (tool_use)` → `response.output_item.added`（function_call）
- `content_block_delta (input_json_delta)` → `response.function_call_arguments.delta`
- `content_block_stop` → 对应 `*.done`
- `message_delta + message_stop` → `response.completed`（stop_reason/stop_sequence/usage）

非流式（整包 JSON）转换同样对齐到 `type:"response.completed"`，并按 `content[]` 中的 `thinking/text/tool_use` 生成 `response.output[]` 项。

---

## 语义不一致（Semantically Different / Not 1:1）

### 1) `index.ts` 注册语义/方向约定不一致（装配方式非 1:1）

- TS：`src/app/v1/_lib/converters/claude-to-codex/index.ts` 在注册 `from:"claude" → to:"codex"` 时，把响应转换器设置为 **Codex→Claude**（引用 `src/app/v1/_lib/converters/codex-to-claude/response.ts`）。
- Go：`KarisCode/backend/internal/service/converter/registry.go` 的 `RegisterDefaults` 将响应转换器按 **provider→client** 方向分别注册：`claude→codex` 使用 `claude_to_codex_response.go`，`codex→claude` 使用 `codex_to_claude_response.go`。
- 结果：两边“把哪个响应转换器挂在哪个方向”的约定不同，因此无法称为对 `index.ts` 的 1:1 复刻（即便最终系统可能仍可实现等价的整体转换能力）。

### 2) `request.ts`：`tool_result.content[]` 的字符串化策略不同

当 `tool_result.content` 是数组且元素不是带 `text` 字段的对象时：

- TS：`String(item)`，对象会变成 `"[object Object]"`。
- Go：`toString(item)` 会对对象做 JSON 序列化（`jsonString(item)`）。

这会导致工具结果回填内容在边界输入上不同（并且 TS 的行为更可能是非预期的“退化输出”）。

### 3) `response.ts`：SSE 解析能力不同（导致输出事件序列/分块不同）

- TS：`parseSSELine()` 只“按 chunk”抽取一个 `event:` + 一个 `data:`（且 `data:` 多行会被覆盖，只保留最后一行）。
- Go：`sse.ParseSSEData()` 可解析：
  - 一个 chunk 内包含多个完整 SSE 事件块（空行分隔）
  - 一个事件块内包含多行 `data:`（按 `\n` 拼接）

因此在现实网络条件下（TCP 合包/拆包导致 chunk 边界不稳定），Go 会输出 **多个转换后事件**，而 TS 可能丢事件或丢部分 data，二者不可能严格 1:1。

### 4) `response.ts`：默认值与 “空字符串” 处理不一致（小概率但真实差异）

以下差异会在上游返回 `""`（空字符串）或缺字段时体现：

- `stop_reason`
  - TS：`response.stop_reason || "end_turn"`（空字符串会被替换为 `"end_turn"`）
  - Go：仅在 `nil` 时填 `"end_turn"`，空字符串会保留为空字符串
- `stop_sequence`
  - TS：`response.stop_sequence || null`（空字符串变 `null`）
  - Go：直接透传（空字符串保留为空字符串）
- `id`
  - TS：缺失时输出 `""`
  - Go：缺失时可能输出 `null`（取决于上游 JSON 反序列化结果）

### 5) `response.ts`：工具名映射规则不一致（版本后缀规范化）

- TS：`buildForwardMapFromRequest()` 只处理“长度 > 64”缩短，不做名称规范化。
- Go：`BuildForwardToolNameMapFromRequest()` 的映射器额外会把少量已知内建工具的版本后缀做规范化（例如 `web_search_YYYYMMDD` → `web_search`）。

若系统中出现这类版本化工具名，Go 与 TS 的输出 tool name 可能不同。

