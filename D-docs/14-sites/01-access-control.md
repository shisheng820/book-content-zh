
## 使用 .kbp_config 进行访问控制

`.kbp_config` 是一个可选的 `json` 编码的配置文件。默认情况下，Keybase Pages 启用整个站点的读取和列表功能。如果你更喜欢关闭目录列表，或者想要使用 [HTTP 基本认证](https://tools.ietf.org/html/rfc2617) 进行简单的 ACL 控制，你可以在站点的根目录下创建这样一个文件。例如，如果你的站点配置为 `"kbp=/keybase/private/alice,kbpbot/my-site"`，那么 `.kbp_config` 应该位于 `/keybase/private/alice,kbpbot/my-site/.kbp_config`。

为了方便编辑配置文件，我们有一个命令行工具，可以完全取代手动编辑 .kbp_config。

使用 `go get` 安装它：

```
go get -u github.com/keybase/client/go/kbfs/kbpagesconfig
```

`kbpagesconfig` 在当前目录中操作（如果需要则创建）`.kbp_config`，所以通常你可以 `cd` 到站点根目录并使用它：

```bash
$ cd /keybase/private/yourname,kbpbot/my-site
$ kbpagesconfig ...
```

或者使用 `-d` 标志覆盖目录：

```bash
$ kbpagesconfig -d /keybase/private/yourname,kbpbot/my-site ...
```

观看[此 asciinema 录屏](https://asciinema.org/a/AOPxXIhC4vNCj04T1fzaydzZg)或继续阅读一些示例！


### Keybase Pages 如何使用 .kbp_config

如果 `.kbp_config` 存在，Keybase Pages 服务器假设一个预定义的结构，主要由两部分组成：一个用于 `users` 和（bcrypt 加密的）密码对的用户映射，以及一个定义每个指定路径权限的 `acls` 映射。当 Keybase Pages 服务器 (`kbpagesd`) 收到对站点的传入请求时，它大致会经过以下步骤：

1. 尝试使用 HTTP 基本认证验证请求，并将请求映射为匿名或预定义用户。

2. 在配置中查找最准确匹配请求路径的 ACL。例如，如果唯一的条目是 `/`，它匹配所有内容。如果 `/foo` 也被定义，那么它用于 `/foo` 及其下的所有内容，而 `/` 用于其他所有内容。

3. 使用 ACL 决定映射的用户是否有足够的权限访问请求的资源。对于没有 `index.html` 的目录，需要 `list` 权限。否则，需要 `read` 权限。

4. 如果需要，以 HTTP 状态码 401 响应，并带有一个 `WWW-Authenticate` 头来请求基本认证。否则返回资源。


每个路径的 ACL 对象有两个字段：

1. `anonymous_permissions`，定义所有访问者在给定路径上拥有的权限。这适用于未认证的匿名流量，以及具有 HTTP 基本认证头的请求。

2. `whitelist_additional_permissions`，定义认证用户在给定路径上可以获得的额外权限，这是在 `anonymous_permissions` 之外的。

把它们放在一起，`.kbp_config` 具有以下 `json` 格式：

```json
{
  "version": "v1",
  "users": {
    <username>: <bcrypt_password>,
    ...
  },
  "acls": {
    <path>: {
      "whitelist_additional_permissions": {
        <username>: <"read"|"list"|"read,list">,
      },
      "anonymous_permissions": <"read"|"list"|"read,list">
    },
    ...
  }
}
```

### 示例

#### 默认配置

如果站点缺少 `.kbp_config`，Keybase Pages 使用默认配置，允许整个站点的 `read` 和 `list` 权限，即：

```json
{
  "version": "v1",
  "users": {},
  "acls": {
    "/": {
      "whitelist_additional_permissions": null,
      "anonymous_permissions": "read,list"
    }
  }
}
```

#### `/friends` 和 `/no-listing`

这是一个更完整的示例，其中 `users` 映射已填充并在 `acls` 中引用，其中只有 `alice` 被允许访问 `/friends`，并且在 `/no-listing` 上禁用了目录列表：

使用 `kbpconfig`：

```bash
$ kbpagesconfig user add alice  # 添加用户 "alice"；这将提示输入密码
$ kbpagesconfig acl set default "" /friends  # 移除 /friends 及其子目录的默认（匿名）权限
$ kbpagesconfig acl set additional alice "read,list" /friends  # 给予 "alice" 读取和列表权限
$ kbpagesconfig acl set default "read" /no-listing # 将 /no-listing 的默认（匿名）权限覆盖为 `read`，即移除 `list`。
```

在 `json` 中：

```json
{
  "version": "v1",
  "users": {
    "alice": "$2a$10$Z3eJqq2H3nQUvvBNkUEvLuWo9nHivPvSjlXLcQI6rZvUNebJ7rEBG"
  },
  "acls": {
    "/": {
      "whitelist_additional_permissions": null,
      "anonymous_permissions": "read,list"
    },
    "/friends": {
      "whitelist_additional_permissions": {
        "alice": "read,list"
      },
      "anonymous_permissions": ""
    },
    "/no-listing": {
      "whitelist_additional_permissions": null,
      "anonymous_permissions": "read"
    }
  }
}
```
