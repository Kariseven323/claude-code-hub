# converters 核心模块对比：claude-code-hub (TS) vs KarisCode (Go)

本文对比以下 4 个 TS 文件在 KarisCode 文件夹内的“重写”是否属于 **1:1 复刻的完整实现**，并按“语义一致 / 语义不一致”逐条列出差异点。

## 对比范围与映射关系

TS 侧（本仓库）：
- `src/app/v1/_lib/converters/index.ts`
- `src/app/v1/_lib/converters/registry.ts`
- `src/app/v1/_lib/converters/tool-name-mapper.ts`
- `src/app/v1/_lib/converters/types.ts`

KarisCode 侧（Go，主要落在 backend converter 包）：
- `KarisCode/backend/internal/service/converter/registry.go`
- `KarisCode/backend/internal/service/converter/tool_name_mapper.go`
- `KarisCode/backend/internal/service/converter/types.go`

注意：
- Go 侧的“类型定义”并非 1:1 按文件拆分：`RequestTransform/ResponseTransform/TransformState` 等定义放在 `registry.go`，`types.go` 仅包含 `Format`（以及额外的 `ClientFormat`）。
- TS 侧 `index.ts` 的“自动注册”（通过 import 副作用）在 Go 侧对应为 `NewDefaultRegistry()/RegisterDefaults()`（显式注册）。

## 结论（是否 1:1 复刻）

**不是 1:1 复刻的完整实现。**

KarisCode 的 Go 实现总体上在“概念结构”上与 TS 版本接近（Format/Registry/ToolNameMapper 三件套都存在），但在若干关键语义上存在显著偏差，尤其是：
- ToolNameMapper 增加了“版本后缀归一化 / 自定义规则”，改变了映射触发条件与输出。
- Registry 的错误/异常兜底语义与 TS 不一致（panic 发生时可能返回 `nil` 而非原始数据/原始 chunk）。
- Registry 的 `HasResponseTransformer` 判定规则更严格，与 TS 的“仅看注册与否”的行为不同。
- TS `types.ts` 暴露的部分类型/配置（如 `TransformerConfig/TransformerMetadata`）在 Go 侧缺失或不对应。

下面按文件逐项对比。

---

## 1) `index.ts`（自动注册入口） vs Go 的默认注册

对应关系：
- TS：`src/app/v1/_lib/converters/index.ts`
- Go：`KarisCode/backend/internal/service/converter/registry.go` 中的 `NewDefaultRegistry()` / `RegisterDefaults()`

### 语义一致
- 都提供了“默认注册集合”的概念：不需要调用方手动逐个注册转换器。
- 注册的“方向集合”基本一致（Claude/Codex/OpenAI-Compatible/Gemini-CLI 的若干互转方向都覆盖）。

### 语义不一致
- **注册机制不同**：TS 依赖 import 副作用（模块加载即修改全局单例 `defaultRegistry`）；Go 依赖显式调用 `RegisterDefaults()` 或构造 `NewDefaultRegistry()`。
  - 影响：TS 里“是否 import 了 index.ts”直接决定默认 registry 是否可用；Go 里“是否调用构造/注册函数”才决定。
- **默认 registry 的生命周期不同**：
  - TS：`defaultRegistry` 是全局单例（进程内共享）。
  - Go：`NewDefaultRegistry()` 每次返回一个新实例（除非调用方自己维护全局变量）。
- **响应转换器是否注册**在部分方向上不一致：
  - Go 的 `RegisterDefaults()` 对某些方向仅注册 request-side（`ResponseTransform{}`），而 TS 侧这些方向往往也注册了 response-side（即使其实际语义是否正确另说）。

---

## 2) `registry.ts`（TransformerRegistry） vs `registry.go`

对应关系：
- TS：`src/app/v1/_lib/converters/registry.ts`
- Go：`KarisCode/backend/internal/service/converter/registry.go`（同名 `TransformerRegistry`）

### 语义一致
- **数据结构与职责一致**：维护两张映射表（request transformers / response transformers），支持注册、查询、执行转换。
- **未注册时回退**（大体一致）：
  - request：找不到 transformer 时返回原始请求体。
  - response：找不到对应 stream/non-stream transformer 时返回原始 chunk / 原始响应。
- **接口形状一致**：
  - request：`(model, raw, stream) -> raw'`
  - stream response：`(ctx, model, originalReq, transformedReq, chunk, state) -> chunks[]`
  - non-stream response：`(ctx, model, originalReq, transformedReq, response) -> response'`

### 语义不一致（关键）
- **异常/兜底行为不一致（严重）**：
  - TS：`try/catch` 捕获异常，明确回退到 `rawJSON` / `[chunk]` / `response`。
  - Go：用 `recover()` 捕获 panic，但 **没有保证回退到原始数据**：
    - `TransformRequest()`：transformer panic 时会被 recover，函数将直接返回 `nil`（Go map 的零值），而不是 `raw`。
    - `TransformStreamResponse()`：transformer panic 时会被 recover，函数将直接返回 `nil`（Go slice 的零值），而不是 `[]string{chunk}`。
  - 这与 TS 的“失败即透传原始数据”语义不一致，且可能导致上层对返回值的处理出现空值分支（甚至丢数据）。
- **`HasResponseTransformer()` 判定规则不一致**：
  - TS：只要 `responses[from]` 中存在 `to` 的条目即返回 true（即使该条目里 `stream/nonStream` 都缺失也算“存在”）。
  - Go：必须存在条目且 `Stream` 或 `NonStream` 至少一个非 nil 才返回 true。
- **返回 `nil` 的处理语义不一致**：
  - TS：`transformStreamResponse()` 约定返回 `string[]`，并在本层逻辑上基本保证“无 transformer -> `[chunk]`；异常 -> `[chunk]`”。
  - Go：`TransformStreamResponse()` 在 `out == nil` 时返回 `nil`，而不是“透传 chunk”；这属于额外语义。
- **调试/枚举接口不一致**：
  - TS：`getRegisteredTransformers()` 返回 `{requests:[{from,to}], responses:[{from,to}]}`。
  - Go：`Registered()` 返回两个 `[2]Format` 列表（类型与结构不同）。

---

## 3) `tool-name-mapper.ts`（ToolNameMapper） vs `tool_name_mapper.go`

对应关系：
- TS：`src/app/v1/_lib/converters/tool-name-mapper.ts`
- Go：`KarisCode/backend/internal/service/converter/tool_name_mapper.go`

### 语义一致
- 都解决“工具名称（tool/function name）最大 64 字符限制”的问题。
- 缩短策略一致：
  - `md5(name)` 取前 8 个 hex 字符作为后缀
  - 前缀截断到 `64 - 1 - 8 = 55` 字符
  - 组合成：`prefix + "_" + hash8`
- 都维护双向映射（original -> mapped / mapped -> original），并提供：
  - “构建映射”（从 Claude tools 列表扫描）
  - “获取映射名”（Forward / getShortenedName）
  - “恢复原名”（Restore / restoreName）
  - “从请求体 tools 字段构建 forward/reverse map”

### 语义不一致（关键）
- **映射触发条件不一致**：
  - TS：仅当 `name.length > 64` 才会建立映射（否则直接跳过）。
  - Go：只要 `mapped != original` 就会建立映射；而 `mapped != original` 不仅包括“超长截断”，还包括后述归一化/自定义规则。
- **Go 增加了“版本后缀归一化”语义（TS 没有）**：
  - Go：对少量内置工具名，若匹配 `^([a-z0-9_]+)_[0-9]{8}$`，会将其归一化为 base（例如 `web_search_20250305 -> web_search`）。
  - TS：不会对版本后缀做任何归一化；只关心长度是否超限。
- **Go 增加了“自定义映射规则”语义（TS 没有）**：
  - Go：`NewToolNameMapper(custom map[string]string)` 支持对特定原名做精确替换（并参与反向恢复）。
  - TS：无 custom rule 参数与行为。
- **构建 map 的键集合可能不同**：
  - TS：`buildForwardMapFromRequest()/buildReverseMapFromRequest()` 只会包含“超长 tool name”的映射条目。
  - Go：这些 map 可能包含“归一化 / custom rule / 超长截断”的综合映射条目。
- **API 命名与兼容别名不同**：
  - TS：`buildForwardMapFromRequest/buildReverseMapFromRequest`。
  - Go：`BuildForwardToolNameMapFromRequest/BuildReverseToolNameMapFromRequest`，并提供 `BuildForwardMapFromClaudeRequest/BuildReverseMapFromClaudeRequest` 作为兼容别名。

---

## 4) `types.ts`（类型定义） vs `types.go` + `registry.go` 的类型

对应关系：
- TS：`src/app/v1/_lib/converters/types.ts`
- Go：`KarisCode/backend/internal/service/converter/types.go`（`Format`） + `registry.go`（transform function types / TransformState / ResponseTransform）

### 语义一致
- `Format` 值集合一致：`claude` / `codex` / `gemini-cli` / `openai-compatible`。
- 都支持流式与非流式两类响应转换，并允许跨 chunk 维护状态：
  - TS：`TransformState` 是 interface + index signature（可扩展）。
  - Go：`TransformState` 是 `map[string]any`（自由扩展）。

### 语义不一致
- **TS 额外暴露的类型在 Go 侧缺失/不对应**：
  - TS：`TransformerConfig`、`TransformerMetadata`（以及 `supportedModels` 等元信息字段）。
  - Go：对应的配置/元信息类型不在该 converter 包中（至少不在对标文件中出现）。
- **Go 额外引入 `ClientFormat`（TS 该文件没有）**：
  - Go：`types.go` 还定义了 `ClientFormat`（路由/请求体检测用的格式名），并注明“镜像 TS 的 format-mapper”。
  - TS：`types.ts` 仅定义 transformer 内部 `Format`。

---

## 小结：哪些差异会影响行为

如果严格以“运行时行为等价”为标准，以下差异会带来可观的行为偏移：
- Registry panic/recover 的回退语义：TS 明确“失败透传”，Go 可能返回 `nil`（潜在丢请求/丢 chunk）。
- ToolNameMapper 的归一化/custom rule：会改变映射表内容与最终工具名（即使未超长）。
- `HasResponseTransformer` 判定策略：会改变上层“是否启用转换”的分支选择。
