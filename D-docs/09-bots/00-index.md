# 机器人 (Bots)

这是机器人开发的技术文档。本部分正在开发中，请稍后回来查看更新！

## 键值存储 (Key-Value Storage)

Keybase 添加了一个加密的键值存储，旨在支持具有持久化状态的安全意识机器人开发。这是一个存储少量数据的地方，这些数据：

1. 为你自己（或你所在的团队中的任何人）加密
1. 跨登录持久化
1. 快速且持久

### 技术细节

如果你是一个需要持久化状态的机器人开发人员，你可能已经在将 KBFS 用于你的存储需求。我们为更轻量级的应用程序实现了键值存储功能，用于存储小块数据——也许你只需要存储一个会话密钥，或者你正在构建一个团队密码管理器。

键值存储公开了一个简单的 API 来放置 (put)、获取 (get)、列出 (list) 和删除 (delete) 条目。

条目值默认情况下为你自己加密（这可能就是你想要的），但你也可以指定一个团队：

1. 你加上任何其他 Keybase 用户列表（例如 `you,alice,bob`）
1. 一个命名的团队或子团队（例如 `myawesometeam.passwords`）

一个团队有许多命名空间 (namespaces)，一个命名空间有许多条目键 (entryKeys)，一个条目键有一个当前的条目值 (entryValue)。如果你已经 `put`（放置）了一个新版本或删除了它，你将无法获取数据的旧版本。

命名空间和条目键是明文的，Keybase 客户端服务将在进入时加密并签署条目值（以及在输出时解密和验证），因此 Keybase 服务器无法看到或伪造它。

如果你在命名空间或条目键前加上双下划线（例如 `__whatever`），它将无法从相应的 `list` 端点被发现。

#### 版本号 (Revision Numbers)

Keybase 服务器跟踪每个条目的最新版本号，并且要求客户端在每次更新请求时指定正确的版本号。当你放置一个新条目或更新一个现有条目时（删除也是这样工作的），你的 Keybase 客户端将首先为该条目运行一个 `get`（获取），以便它确切地知道服务器期望的版本（例如，对于一个全新的条目为 1）。这种复杂性对 API 隐藏了，因为你可能不需要它。但是，如果你想管理自己的版本（例如，你有两个不同的机器人绝对需要并发地共享和更新相同的条目），你可以传入一个版本，你的 Keybase 客户端将使用它。

例如，假设此条目以前未插入过，以下命令将插入一个版本为 1 的条目：

```
keybase kvstore api -m '{"method": "put", "params":
{"options": {"namespace": "pw-manager", "entryKey":
"geocities", "entryValue": "all my secrets"}}}'
```

如果我们此时显式地使用版本号 2 进行 `put`（如下面的命令中所做的那样），`put` 将失败，因为它期望版本 3：

```
keybase kvstore api -m '{"method": "put", "params": {"options":
{"namespace": "pw-manager", "revision": 2,
"entryKey": "geocities", "entryValue": "some update"}}}'
```

### 安全细节

许多元数据，包括命名空间、条目键以及数据库访问模式，对于 Keybase 服务器来说都是已知的。然而，条目值由写入者的设备密钥签名，然后为特定团队加密。这确保了服务器无法读取或伪造条目值，也无法证明它所知道的关于它的任何元数据。安全权衡是以聊天 (chat) 为模型设计的，并且非常相似。以下是一些区别细节。

#### 元数据 (Metadata)

我们使用 [带关联数据的认证加密 (AEAD)](https://en.wikipedia.org/wiki/Authenticated_encryption#Authenticated_encryption_with_associated_data_%28AEAD%29)，这是一种允许包含关联数据（在我们的例子中是一堆元数据）作为签名然后加密的一部分的构造。我们这样做是为了减轻服务器可能利用的几种可能的攻击。

先签名后加密消息的主要风险之一是，如果能够解密外层的人随后可以将签名的消息重新加密用于其他目的（例如，不同的条目键或以前的版本），会发生什么。在这个产品的背景下，像那样的攻击将需要 Keybase 服务器与团队的当前（或前任，取决于具体情况）成员之间的勾结。我们通过让写入者不仅对条目值签名，而且对一堆元数据的哈希进行签名来处理这一类问题（例如，包括恶意 Keybase 服务器在条目键之间交换你的条目值）。元数据指定了预期的签名和加密密钥以及预期的条目详细信息（团队、命名空间、条目键和版本）。并且每当 Keybase 客户端解密和验证条目时，都会检查此元数据哈希。

#### 回滚保护 (Rollback Protection)

因为服务器可以对相同的请求返回不同的响应（当给定条目键处的当前条目值更改时），每个客户端都会执行一些额外的验证：条目的版本号和团队密钥生成代数不能减少，并且相同的版本号总是映射到相同的条目值和团队密钥生成代数。

### 用法

你可以通过 Keybase CLI 与键值存储进行交互。要查看示例命令：

```
keybase kvstore api help
```

键值存储支持已在我们的三个机器人库中实现：[Python](https://github.com/keybase/pykeybasebot)、[JavaScript](https://github.com/keybase/keybase-bot) 和 [Golang](https://github.com/keybase/go-keybase-chat-bot)。为了让你开始，你还可以在这些库中找到使用键值存储的机器人实现的有用示例。我们自己的托管机器人 Jirabot（用于与 Jira 交互）也 [利用了键值存储](https://github.com/keybase/managed-bots/tree/master/jirabot)。试一试吧！

