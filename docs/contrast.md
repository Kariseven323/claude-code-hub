# `claude-to-openai` 对比：claude-code-hub (TS) vs `KarisCode` (Go)

本文聚焦对比以下 2 个 TS 文件在 `KarisCode/` 内的“重写”是否属于 **1:1 复刻的完整实现**，并按“语义一致 / 语义不一致”逐条列出差异点。

## 对比范围与映射关系

TS 侧（本仓库）：
- `src/app/v1/_lib/converters/claude-to-openai/index.ts`
- `src/app/v1/_lib/converters/claude-to-openai/request.ts`

KarisCode 侧（Go）：
- `KarisCode/backend/internal/service/converter/registry.go`（`RegisterDefaults()` 中的注册逻辑，对应 `index.ts`）
- `KarisCode/backend/internal/service/converter/claude_to_openai_request.go`（对应 `request.ts`）

（补充：KarisCode 侧默认注册确实在运行时被使用：`KarisCode/backend/internal/handler/proxy/routes.go` 调用 `converter.NewDefaultRegistry()`。）

## 结论（是否 1:1 复刻）

**不是严格的 1:1 复刻。**

整体上 Go 侧 `TransformClaudeRequestToOpenAI` 明显是按 TS 逻辑“逐段镜像”实现的；但在若干输入边界/异常路径上，行为与 TS 不完全一致，因此不能称为“1:1 语义等价”的完整实现。

---

## 1) `index.ts`（转换器注册）对比

对应关系：
- TS：`src/app/v1/_lib/converters/claude-to-openai/index.ts`
- Go：`KarisCode/backend/internal/service/converter/registry.go` 的 `RegisterDefaults()`

### 语义一致
- **注册方向一致**：都注册 `claude` → `openai-compatible` 的 request transformer。
- **响应转换器同向绑定**：都为该方向绑定了 stream/non-stream 的响应转换器（名字与职责对应）。

### 语义不一致
- **注册触发机制不同**：
  - TS：依赖模块 import 副作用（加载 `index.ts` 即注册到全局 `defaultRegistry`）。
  - Go：依赖显式调用 `RegisterDefaults()` / `NewDefaultRegistry()`。
- **代码复用形态不同**：
  - TS：`index.ts` 从 `../openai-to-claude/response` 复用 `transformClaude*ToOpenAI`。
  - Go：直接使用 `claude_to_openai_response.go` 内实现的 `TransformClaude*ToOpenAI`（语义是否等价取决于 response 文件；但这已超出本文 request/index 的对比范围）。

---

## 2) `request.ts`（Claude → OpenAI ChatCompletions 请求转换）对比

对应关系：
- TS：`src/app/v1/_lib/converters/claude-to-openai/request.ts` 的 `transformClaudeRequestToOpenAI()`
- Go：`KarisCode/backend/internal/service/converter/claude_to_openai_request.go` 的 `TransformClaudeRequestToOpenAI()`

### 语义一致（核心路径）
- **顶层字段**：输出都以入参 `model` 为准，并显式写入 `stream`（忽略原请求体内可能的 `model/stream` 字段）。
- **`system` → 首条 system message**：
  - `system: string` 直接成为 `{"role":"system","content":...}`
  - `system: [{type:"text",text:"..."}...]` 拼接所有 `text`（无分隔符）后写入 system message
- **`messages[]` 基础映射**：
  - `content: string` → OpenAI `messages[]` 的 `content: string`
  - `content: []`（block 数组）→ 收集 `text`/`image` 转成 OpenAI 的多模态 `content` 数组
- **`image` block**：
  - `source.type=base64` → `data:{media_type};base64,{data}`
  - `source.type=url` → 直接使用 `url`
  - 都设置 `detail: "auto"`
- **`tool_use` block**：
  - 在遇到 `tool_use` 前会先 flush 已累计的 `text/image` contentParts 为一条消息
  - 生成一条 `role:"assistant"` 且 `content:null` 的消息，并填充 `tool_calls:[{id,type:"function",function:{name,arguments}}]`
- **`tool_result` block**：
  - 在遇到 `tool_result` 前会先 flush 已累计的 `text/image` contentParts 为一条消息
  - 生成一条 `role:"tool"` 消息，填充 `tool_call_id` 与 `content`
- **`tools[]` → OpenAI `tools[]`**：
  - `input_schema` → `function.parameters`
  - 跳过 `type === "web_search_20250305"` 的 Claude web search 工具
- **`tool_choice` 映射**：
  - `auto` → `"auto"`
  - `any` → `"required"`
  - `tool + name` → `{type:"function", function:{name}}`
- **透传标量**：`max_tokens / temperature / top_p` 在常规 JSON 输入下行为一致（注意差异点见下节）。
- **保持 TS 的既有“限制/瑕疵”**：只要出现过 `tool_use` 或 `tool_result`，循环结束后剩余的 `contentParts` 不会再被 append（可能导致“工具块后还有文本/图片”的尾部内容丢失）；Go 侧复刻了这一点。

### 语义不一致（边界/异常路径）
- **`tools` 字段“空数组 vs 缺省”**：
  - TS：只要 `req.tools` 非空进入转换，就会先 `output.tools = []`，即便全部被 `continue`（例如只有 `web_search_20250305`）最终也会输出 `tools: []`。
  - Go：只有在 `outTools` 最终 `len(outTools) > 0` 时才写入 `output["tools"]`；否则该字段缺省。
- **`tool_result.content` 为数组且元素是 object 时的字符串化差异**：
  - TS：对“非 text 对象”走 `String(item)`，通常得到 `"[object Object]"`（或 `"undefined"` 等 JS 字符串化结果）。
  - Go：对“非 text 对象”走 `jsonString(item)`，得到 JSON（例如 `{"foo":"bar"}`），且 marshal 失败会变成空串。
- **`tool_result.content` 为非 string / 非数组时的处理差异**：
  - TS：不会进入任何分支，`outputStr` 保持 `""`。
  - Go：会走 `default` 分支并用 `toString()`（最终 `jsonString(v)`）生成字符串。
- **`tool_use.input` 非 object（map）时的处理差异**：
  - TS：`JSON.stringify(part.input || {})`，若 `input` 是 truthy 的非对象（如数字/数组），会 stringify 成 `"123"` / `"[...]"`；若是 `0/""/false` 等 falsy，会退化成 `"{}"`。
  - Go：只接受 `map[string]any`；否则一律退化为 `"{}"`。
- **`temperature/top_p` 的数值类型兼容性差异**：
  - TS：只要不是 `undefined` 就会透传（包含 `0`、整数等）。
  - Go：仅在底层类型为 `float64` 时透传（JSON decode 通常是 `float64`，但若上层构造为 `int` 则会丢失该字段）。
- **JSON 序列化失败的行为差异**（对 arguments/content 影响）：
  - TS：`JSON.stringify(...)` 可能抛异常；在 TS 项目中该异常会被 registry 捕获并回退“透传原始请求体”（导致上游收到 Claude 格式而不是 OpenAI 格式）。
  - Go：`json.Marshal` 失败时返回空字符串，不会触发 panic；因此会继续输出“已转换但 arguments/content 为空串”的 OpenAI 请求形态。
