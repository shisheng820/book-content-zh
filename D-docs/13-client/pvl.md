
# 证明验证语言 (PVL)

## 概述

证明验证语言 (PVL) 是一种基于 JSON 的受限语言，用于描述客户端应如何验证 Keybase 证明。

它解决的问题是，如果证明服务（例如 Reddit）快速更改其展示方式，Keybase 客户端应能快速适应并继续验证证明。

Keybase 服务器更新活跃 PVL 指令的速度比我们更新客户端（特别是移动客户端）的速度要快。

如果证明服务更改其格式，客户端会从服务器获取最新的 PVL。PVL 的更改可以改变客户端获取和验证证明数据的方式。

## 安全性

客户端从 Keybase 服务器获取 PVL 指令，并在验证证明时使用它。Keybase 服务器将其提供的 PVL 的哈希值记录在可审计的 Merkle 树中。客户端总是根据 Merkle 树检查获取的 PVL，以保证它们只执行可审计的 PVL。

即使 Keybase 服务器受损并向客户端发送攻击者控制的 PVL，也不应导致客户端执行任意代码。PVL 将保持足够的限制以避免造成任何损害。

如果 Keybase 服务器受损并发送伪造的 PVL，可能会导致客户端接受不正确的验证。例如，如果 Eve 控制了 Keybase 服务器，她可以通过发布 Eve 自己对 Alice 用户名声明的签名，并向客户端推送针对 Twitter 的 PVL 更改（使它们从错误的用户 feed 获取），从而成功声称拥有 Alice 的 Twitter 账户。这是一个问题，但可以通过审计来抵消。

如果 Keybase 服务器曾向客户端发送错误的 PVL（并且被客户端接受），将会有审计踪迹。独立审计员将能够找出发送了什么恶意 PVL。重申一下，当前的 PVL 将被哈希到 Merkle 树中，客户端将始终根据 Merkle 树验证新的 PVL。

## 更新活跃 PVL

### 服务器

服务器为我们支持的每个 PVL 规范版本提供一个 PVL blob。因此，在某个时候，`pvl_version` 2 和 3 可能有不同的 blob，而版本 1 则没有。每个客户端只能运行一个版本的 PVL。所有 PVL blob 都被哈希到 Merkle 树中，以便可以进行验证。

如果服务器不为某个（旧）`pvl_version` 提供 PVL blob，那么该版本的客户端将丢弃其现有的 PVL blob，并且无法验证证明。这意味着如果我们在证明验证中发现安全漏洞，但无法在该版本的 PVL 规范中修复它，我们可以立即禁用这些客户端。

### (A) 客户端想要验证证明且没有本地 PVL

1. 客户端在生命周期开始时没有活跃的 PVL blob。当它第一次想要验证证明时，它必须从服务器获取其 `pvl_version` 的当前 PVL blob 以及将该 blob 绑定到 Merkle 树的链。
2. 如果没有为其 `pvl_version` 提供 PVL blob，它会通知用户客户端已过期并中止证明检查。
3. 如果 PVL 无效或无法通过 Merkle 树验证，它将丢弃 PVL 并中止。客户端可以稍后重试。
4. 客户端将经过验证的 blob 存储在其本地数据库中以备后用。
5. 然后它执行 PVL 来检查证明。

### (B) 现有客户端想要验证证明，且 PVL 未更改（常见情况）

1. 客户端从服务器获知其 `pvl_version` 的活跃 PVL blob 的哈希值。在这种情况下，它与当前版本相同。
2. 客户端执行其存储的 PVL 来检查证明。

### (C) 现有客户端想要验证证明，且 PVL 已更改

1. 客户端从服务器获知其 `pvl_version` 的活跃 PVL blob 的哈希值。在这种情况下，它不同或不存在。
2. 客户端丢弃其现有的 PVL 并按 A 中所述进行操作。

## 工具

要查看当前的 PVL 块和用于更新它的工具，请参阅 https://github.com/keybase/client/tree/master/pvl-tools

## 结构

本节描述 PVL 块的结构。

本文档中的示例均用 CoffeeScript (CSON) 编写。但将被签名并发送给客户端的格式是 JSON。如果你想查看本文档中某些内容的漂亮的 JSON 版本，请运行此命令并快速粘贴 CSON 版本：

```sh
cson2json | underscore print
```

你需要 [cson2json](https://www.npmjs.com/package/cson) 和 [underscore-cli](https://www.npmjs.com/package/underscore-cli)

### 顶层

在顶层，PVL 是从证明服务名称到描述如何验证证明的服务条目的映射。

```coffeescript
pvl_version: 1 # 编写此 PVL 规范的版本
revision: 1    # 我们正在使用的脚本验证脚本的修订版
services:
  coinbase: [...]
  dns: [...]
  github: [...]
  reddit: [...]
  rooter: [...]
  twitter: [...]
  web: [...]
```

### 服务条目

每个服务条目都是脚本列表。每个脚本都是指令列表。每个脚本在一个短路 OR（或）逻辑中逐个尝试。如果任何脚本成功，则证明是好的。如果所有脚本都失败，则证明无效。这样做是为了如果我们发现服务处于拆分测试或部署中间，我们可以为每种类型的响应编写一个脚本。

当客户端运行脚本时，脚本对 RemoteProofChainLink 和来自 Keybase 服务器的提示具有有限的访问权限。从服务器获取 `hint_url`，即证明数据所在的 URL。

每个脚本描述了如何首先验证提示 URL，然后获取并验证证明。

这是一个包含 1 个脚本的服务条目示例：

```coffeescript
generic_web_site: [[
  # URL 验证。必须是 HTTP 或 HTTPS。必须是证明域名的已知路径。
  { assert_regex_match: {
    , pattern: "^%{protocol}://%{hostname}/(?:\\.well-known/keybase\\.txt|keybase\\.txt)$"
    , from: "hint_url"
    , error: ["BAD_API_URL", "Bad hint from server; didn't recognize API url: \"%{hint_url}\""]} },
  { fetch: {
    , kind: "string"
    , from: "hint_url"
    , into: "blob" } },
  # 验证并查找签名。
  { assert_find_base64: {
    , needle: "sig"
    , haystack: "blob"
    , error: ["TEXT_NOT_FOUND", "signature not found in body"] } },
]]
```

这也是 JSON 格式的：

```json
"generic_web_site": [[
  {"assert_regex_match": {
    "pattern": "^%{protocol}://%{hostname}/(?:\\.well-known/keybase\\.txt|keybase\\.txt)$",
    "from": "hint_url",
    "error": ["BAD_API_URL", "Bad hint from server; didn't recognize API url: \"%{hint_url}\""] } },
  {"fetch": {
    "kind": "string",
    "from": "hint_url",
    "into": "blob" } },
  {"assert_find_base64": {
    "needle": "sig",
    "haystack": "blob",
    "error": ["TEXT_NOT_FOUND", "signature not found in body"] } }
]]
```

### 寄存器

指令可以读取和写入命名寄存器。每个寄存器存储一个字符串值，只能设置一次，并且在设置之前不能读取。寄存器必须根据 `[a-z0-9_]+` 命名。

某些寄存器在运行脚本之前已预先填充。下表描述了这些特殊寄存器。其中一些特殊寄存器在某些证明类型中没有意义，例如 `username_service` 在 DNS 证明中没有意义。此类寄存器在这些情况下被禁止，不能读取或设置。

当寄存器值被代入正则表达式时，它们会被客户端进行正则转义。打开证明签名是为了导出较短的签名 ID。

这是预设寄存器的完整列表：

| 变量名 | 含义 | 示例值 | 注释 |
|--------------------|------------------------------|---------------------------------------|-----------------------------------------------------------|
| `hint_url` | 来自 Keybase 服务器的提示 URL | https://gist.github.com/github/etc.md | |
| `username_service` | 服务上的用户名 | cjbprime | 在 web/dns 证明中被禁止 |
| `username_keybase` | Keybase 上的用户名 | cjb | |
| `sig` | 证明的完整签名 | owG...HAA | base64 编码的证明签名 |
| `sig_id_medium` | 中等长度的签名 ID | BYA...Q1I | |
| `sig_id_short` | 短签名 ID | 970...icQ | |
| `hostname` | DNS 或 web 的主机名 | printf.net | 除 web/dns 证明外被禁止。已验证。 |
| `protocol` | web 证明的协议 | https | 除 web 证明外被禁止。已验证并规范化。 |

还有一点隐藏存储。当发生 HTML 或 JSON 获取时，解析的响应存储在只有 `selector_css` 或 `selector_json` 指令可以隐式访问的地方。`assert_find_base64` 使用签名的字节版本，因此只能在 sig 变量上运行。

### 脚本指令

每个脚本指令都是一个 json 对象；从指令名称到包含其参数的另一个映射的映射。脚本指令按顺序运行。脚本不能为空。每个脚本必须以断言结束。脚本中最多可以存在一个 fetch 指令。

最后，脚本要么成功（在这种情况下证明有效），要么因错误而失败（在这种情况下证明无效）。有关更多信息，请参见下面的错误报告部分。如果脚本运行到最后，则表示成功。

#### assert_regex_match
此指令断言提供的正则 `pattern` 匹配 `from` 中命名的寄存器的值。提供的正则表达式必须是 `^body$` 的形式，其中 body 可以包含寄存器替换。`^$` 是必需的，因为它们很容易被遗忘。可以使用 `^.*stuff.*$` 显式完成子字符串搜索。寄存器替换的形式为 `%{varname}`。值必须由客户端进行正则转义。其他选项 `case_insensitive`、`multiline` 和 `negate` 是可选的，默认为 false。

```coffeescript
{ assert_regex_match: {
  , pattern: "^keybaseproofs$"
  , case_insensitive: true
  , from: "subreddit_from_url" } }
```

#### assert_find_base64
断言可以在 `haystack` 命名的寄存器值中找到 `needle` 命名的寄存器值。使用自定义 base64 值查找函数，如 `base64_finder.go` 中的 [`FindBase64Block`](https://github.com/keybase/client/blob/master/go/libkb/base64_finder.go#L116)，这些函数对空格特别有弹性。`sig` 是唯一可以使用的有效变量。

```coffeescript
{ assert_find_base64: {
  , needle: "sig"
  , haystack: "selftext" } }
```

#### assert_compare
断言 `a` 和 `b` 命名的两个寄存器包含根据比较函数 `cmp` 等效的值。

可能的比较是：
- `exact`: 精确字符串比较
- `cicmp`: 不区分大小写的比较
- `stripdots-then-cicmp`: 去除 `'.'` 字符然后进行不区分大小写的比较。

```coffeescript
{ assert_compare: {
  , cmp: "stripdots-then-cicmp"
  , a: "username_from_url"
  , b: "username_service" } }
```

#### whitespace_normalize

规范化空格，使所有连续的空格运行变为一个空格。修剪字符串开头和结尾的空格。从寄存器 `from` 读取并写入寄存器 `into`。

```coffeescript
{ whitespace_normalize: {
  , from: "header"
  , into: "header_nw" } }
```

#### regex_capture

断言正则 `pattern` 匹配寄存器 `from`。允许像 `assert_regex_match` 一样的替换和选项。正则表达式应至少有一个捕获组。如果正则表达式匹配，则捕获组结果将加载到 `into` 数组指定的寄存器中。如果没有足够的匹配项，则指令失败。

```coffeescript
{ regex_capture: {
  , pattern: "^ *(?:@[a-zA-Z0-9_-]+\\s*)* *Verifying myself: I am ([A-Za-z0-9_]+) on Keybase\\.io\\. (\\S+) */.*$"
  , case_insensitive: true
  , from: "tweet_contents_nw"
  , into: ["username_from_tweet_contents", "sig_from_tweet_contents"] } }
```

#### replace_all
将 `from` 寄存器中所有出现的字符串 `old` 替换为字符串 `new`，并将结果放入 `into` 寄存器。

```coffeescript
{ replace_all: {
  , old: "-\\-\\"
  , new: "--"
  , from: "fcc1"
  , into: "fcc2" } },
```

#### parse_url
从寄存器 `from` 获取 url，断言它是有效的 url，并将其解析为片段。可以可选地指定片段 `path`、`host` 和 `scheme`，并将 url 的这些部分加载到指定的寄存器中。

```coffeescript
{ parse_url: {
  , from: "username_link"
  , path: "link_path" } },
```

#### fetch
获取由 `from` 命名的寄存器中包含的 URL，类型为 `html`、`json` 或 `string` 之一。DNS 没有选项，因为 DNS 是特殊处理的。对于 HTML 和 JSON，响应会被解析并隐藏在选择器指令可以读取的特殊存储中。在字符串获取的情况下，必须指定一个 `into` 寄存器，其中将包含响应。

脚本中最多可以存在一个 fetch 指令。

```coffeescript
{ fetch: {
  , kind: "string"
  , from: "hint_url"
  , into: "profile" } },
```

#### parse_html
将寄存器 `from` 的内容解析为 html。生成的 DOM 存储在选择器指令可以读取的特殊存储中。它会覆盖原始页面加载。

```coffeescript
{ parse_html: {
  , from: "ihavehtml" } },
```

#### selector_json
遍历 json 文档并选择一个元素。如果值不是字符串，它将根据 json 进行序列化。`selectors` 列表是键或索引的列表。所以下面的例子与 javascript 中的 `root_object[0]["data"]["children"][0]["data"]["author"]` 相同。如果无法跟随选择器，脚本将使证明失败。

`selector_json` 指令只能出现在具有 json 类型 fetch 的脚本中。这将作为验证 PVL 块的一部分进行检测。

如果索引为负数，它会像 python 风格一样从末尾查找该元素。如果索引是特殊的 `{all: true}` 对象，则选择器的其余部分将在数组的所有元素或对象的值上运行，并将结果字符串用分隔空格连接起来。

```coffeescript
{ selector_json: {
  , selectors: [0, "data", "children", 0, "data", "author"]
  , into: "author" } }
```

#### selector_css
从文档中选择一个 html 元素并将文本或属性提取为字符串。选择始终从 fetch 结果的根目录开始。提供 CSS 选择器字符串或索引的列表。每个选择器/索引按顺序跟随。如果选择不包含任何元素，脚本将使证明失败。

`attr` 字符串字段指定要从元素中提取什么属性。
`data` 布尔字段指定是否获取每个选择元素的第一个节点的数据（包括注释）。
如果不存在 `attr` 字段且 `data` 为 false（默认值），则提取选择的文本内容。

如果索引为负数，它会从末尾查找该元素。

如果选择器条目是特殊值 `{contents: true}`，则相当于调用 jquery 中的 `.contents()`。

可以提供可选的 `multi` 键，如果其值为 true，则如果末尾的选择包含多个元素，结果字符串将用分隔空格连接。默认情况下，如果选择器匹配多个元素，脚本将失败。

```coffeescript
{ selector_css: {
  , selectors: [ "div.permalink-tweet-container div.permalink-tweet", 0 ]
  , attr: "data-screen-name"
  , into: "screen_name" } }
```

#### fill
用字符串 `with` 填充寄存器 `into`。`with` 可以包含像 `assert_regex_match` 一样的寄存器替换，但在此步骤中它们不会被正则转义。

```coffeescript
{ fill: {
  , with: "https://coinbase.com/%{username_service}/public-key"
  , into: "our_url" } },
```

## 错误报告

有几种类型的失败（见 `prove_common.avdl`）：

- 可重试的软错误 (100): 例如 HTTP 500。
- 中等错误 (200): 例如 HTTP 400。
- 硬错误 (300): 例如签名错误。
- PVL 无效（在 300 范围内）

如果 PVL 块无效并且无法读取证明类型的脚本，检查器将报告 `INVALID_PVL`。

对于验证证明时发生的错误，PVL 解释器将报告默认错误，单个指令可以覆盖这些错误。

如果运行 `fetch` 指令时发生失败，解释器将执行正确的操作。

对于自定义报告，每个指令都支持额外的 `error` 字段。`error` 字段必须包含一对错误名称和描述字符串，这些字符串将报告给用户。

```coffeescript
error: ["CONTENT_FAILURE", "Bad author; wanted \"%{username_service}\", got \"%{author_from_tweet}\""]
```

## DNS
DNS 有点特殊。而且也不会比我们更新应用程序更快地更改其协议。所以这是它的工作原理。

DNS 脚本不能包含任何 fetch 指令。

获取 `hostname` TXT 记录。每个 DNS 脚本都针对每个 txt 记录运行，`txt` 寄存器设置为记录值。如果脚本在*任何*记录上成功，则证明成功。如果这不起作用，则对 `_keybase.proof.domain` 重复该过程。

这是 DNS 服务条目，预计不会更改：

```coffeescript
dns: [[
  { assert_regex_match: {
    , pattern: "^keybase-site-verification=%{sig_id_medium}$"
    , from: "txt"
    , error: ["NOT_FOUND", "matching DNS entry not found"] } },
]]
```

## 限制
PVL 无法运行从多个 URL 获取的脚本。

没有分支或循环，每次运行脚本时，相同的指令以相同的顺序执行。

## 示例
### 完整 PVL
此示例旨在捕获我们要当前 (11/18/2016 5e09b59) 的证明验证规则。

```coffeescript
pvl_version: 1
revision: 1
services:
  coinbase: [[
    # 构造 url（我们不需要提示）
    { fill: {
      , with: "https://coinbase.com/%{username_service}/public-key"
      , into: "our_url" } },
    # fetch
    { fetch: {
      , kind: "html"
      , from: "our_url" } },
    # 查找签名
    { selector_css: {
      , selectors: ["pre.statement", 0]
      , into: "haystack"
      , error: ["FAILED_PARSE", "Couldn't find a div $(pre.statement)"] } },
    { assert_find_base64: {
      , needle: "sig"
      , haystack: "haystack" }
      , error: ["TEXT_NOT_FOUND", "signature not found in body"] },
  ]]
  dns: [[
    # DNS 没有提示。并且它检查两个域上的每个 txt 记录。错误被特殊处理。
    # 所以一切都有点不同。
    # 在每个 txt 条目上检查此正则表达式。如果有任何匹配，检查成功。
    { assert_regex_match: {
      , pattern: "^keybase-site-verification=%{sig_id_medium}$"
      , from: "txt"
      , error: ["NOT_FOUND", "matching DNS entry not found"] } },
  ]]
  facebook: [[
    # 检查声称的用户名是否没有斜杠或可能欺骗我们检查不同 url 的滑稽业务。
    # Facebook 用户名实际上不允许任何特殊字符，但恶意用户仍然可能
    # *声称*他们的名字中有一些斜杠和问号，希望能欺骗我们点击一个完全无关的 URL。
    # 通过检查声称的名字中的特殊字符来防止这种情况发生。
    { assert_regex_match: {
      , pattern: "^[a-zA-Z0-9\\.]+$"
      , from: "username_service"
      , error: ["BAD_USERNAME", "Invalid characters in username '%{username_service}'"] } },

    # 检查提供的 url 并提取用户名和路径。
    # 接受移动或桌面 url。获取的 url 稍后将被重写。
    # 我们想要严格控制 url 的结构。
    # 没有查询参数，帖子 ID 中没有意外字符。
    { regex_capture: {
      , pattern: "^https://(m|www)\\.facebook\\.com/([^/]*)/posts/([0-9]+)$"
      , from: "hint_url"
      , into: ["unused1", "username_from_url", "post_id"]
      , error: ["BAD_API_URL", "Bad hint from server; URL should start with 'https://m.facebook.com/%{username_service}/posts/', got '%{hint_url}'"] } },

    # 检查声称的用户名是否与 url 匹配。
    # 在这里检查正确的用户名至关重要。我们依靠此检查来证明相关用户实际上写了帖子。
    # （请注意，移动站点*不*强制执行 URL 的这一部分。只有桌面站点执行。）
    { assert_compare: {
      , cmp: "stripdots-then-cicmp"
      , a: "username_from_url"
      , b: "username_service"
      , error: ["BAD_API_URL", "Bad hint from server; username in URL should match '%{username_service}', received '%{username_from_url}'"] } },

    # 使用验证的用户名和（未验证的）帖子 ID 创建桌面 url。
    { fill: {
      , with: "https://www.facebook.com/%{username_from_url}/posts/%{post_id}"
      , into: "our_url" } },
    { fetch: {
      , kind: "html"
      , from: "our_url" } },

    # 获取第一个 <code> 块内的第一个（唯一）注释的内容。
    # 信不信由你，此注释包含下面的帖子标记。
    { selector_css: {
      , selectors: ["code", 0, {contents: true}, 0]
      , into: "first_code_comment"
      , data: true
      , error: ["FAILED_PARSE", "Could not find proof markup comment in Facebook's response"] } },

    # Facebook 在将文本插入注释时将 "--" 转义为 "-\-\"，将 "\" 转义为 "\\"。
    # 取消转义这些。
    { replace_all: {
      , old: "-\\-\\"
      , new: "--"
      , from: "first_code_comment"
      , into: "fcc2" } },
    { replace_all: {
      , old: "\\\\"
      , new: "\\"
      , from: "fcc2"
      , into: "fcc3" } },

    # 将取消转义的注释作为 html 加载
    { parse_html: {
      , from: "fcc3"
      , error: ["FAILED_PARSE", "Failed to parse proof markup comment in Facebook post: %{fcc3}"] } },
