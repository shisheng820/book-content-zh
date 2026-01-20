# Seitan 令牌 V2：向 TOFU 说不 (Seitan Tokens V2: Say No to TOFU)

当 Alice 想要邀请 Bob 加入她的 [团队](https://keybase.io/blog/introducing-keybase-teams)，而 Alice 只知道 Bob 的电话号码时，她可以通过 *Seitan 令牌* 来实现。通常，这种形式的共享是 *TOFU*，即“首次使用信任 (Trust On First Use)”。例如，Alice 可以请求服务器向 Bob 发送电子邮件、短信或推送通知，一旦 Bob 向服务器出示该令牌，Alice 就让他加入团队。Bob 已经证明了拥有服务器发送令牌的任何地址。然而，在这个例子中，Alice 相信服务器不会把令牌发给 Charlie。所以 Alice 必须相信服务器做了它声称要做的事，而且她没有机制来检测不当行为。一旦 Bob（或 Charlie）被允许进入，Alice 至少可以确保 Bob（或 Charlie）日后不会被调包。

Seitan 令牌更好。假设 Alice 与 Bob 之间有一个预先认证的通道（比如通过 iMessage 或 Signal），那么她可以确保 Bob 能进入，而且 Keybase 服务器不能强迫她暗中让 Charlie 进入。

Seitan 令牌 V2 通过防止另一个管理员窃取 Alice 为 Bob 生成的邀请，增强了初始 seitan ([V1](/docs/teams/seitan)) 的安全性。
我们通过不将 Alice 为 Bob 生成的秘密（`iKey`）存储在签名链中，而是生成一个 EdDSA 密钥对，只将公钥（`pubKey`）写入签名链来实现这一点。

## 高层描述

在 Seitan 令牌交换中，Alice 拿出一个随机令牌。她签署一份形式如下的声明：“任何证明知道此令牌的人都可以被接纳进团队。”Alice 不必是允许被邀请者进入团队的人；如果 Arnie 是团队管理员，他也可以这样做。

假设 Alice 和 Arnie 是团队 `acme` 的管理员，Alice 想邀请 Bob 加入团队。高层协议很简单：

1. Alice 选择一个随机的 83 位令牌（称为 `iKey`），并计算一些派生数据
1. `iKey` 被拉伸并解释为 EdDSA 密钥对的私钥
1. Alice 将密钥对的公钥（`pubKey`）的加密签名到 `acme` 的团队签名链中
1. Alice 通过 iMessage（或 Signal 等）将 `iKey` 发送给 Bob
1. Bob 像 Alice 一样计算密钥对，并将 signature(`msg`, `bob`) 发送到 Keybase 服务器，其中 `msg` 在 Keybase 内标识 Bob，以及从 `iKey` 派生的 `inviteID`（见下文）
1. Alice 或 Arnie 解密 `acme` 签名链中加密的 `pubKey`，并确保 Bob 发送的签名可以用 `pubKey` 验证。

## 详细规范

以下是上述步骤的更详细规范：

### 步骤 1：iKey 生成和令牌派生

#### 步骤 1a：iKey 生成

Alice 从字母表 `abcdefghjkmnpqrsuvwxyz23456789`（即所有字母和数字，除了 `i`, `l`, `o`, `t`, `0`, 和 `1`）中 [生成](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/seitan.go#L58-L88) 一个 17 个字符的随机字符串。在位置 6（0 索引）插入一个 `+` 字符。这被称为 `iKey` 或“邀请密钥”。例子看起来像：`zmh6ff+2jv975gh56p` 或 `bxsnrd+dj882d9mmq9`。

我们包含一个 `+` 号，以便这些令牌可以与团队名称和基于电子邮件的 TOFU 令牌区分开来。Keybase 客户端将 [任何带有 `+` 号、索引 >1 且超过 6 个字符的令牌](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/seitan_v2.go#L28-L34) 视为 seitan 令牌，以防拼写错误或损坏的令牌被意外作为团队名称或电子邮件令牌发送到服务器。

#### 步骤 1b：拉伸 iKey 以阻止服务器暴力破解

在上一步中生成的 `iKey` 只有约 83 位的熵。它最终将通过 iMessage 甚至 SMS 传输，所以我们在这里稍微受到空间限制。因此，Alice 通过 scrypt 进一步拉伸此密钥，以阻止对令牌空间的暴力耗尽：

Alice [计算](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/seitan.go#L146-L148) `siKey`，意为“扩展邀请密钥 (Stretched Invitation Key)”：`siKey` = **scrypt**(ikey, C = 2<sup>10</sup>, R=8, P=1, Len=32)

#### 步骤 1c：计算派生的“邀请 ID”

每当 Alice 想要邀请像 Bob 这样还没有加入 Keybase 的人进入团队时，Alice 必须生成一个“邀请 ID”来作为她邀请的键。通常这是随机完成的，但在这种情况下，它是从 `siKey` [派生](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/seitan_v2.go#L87-L101) 的：`inviteID` = **HMAC-SHA512**(`siKey`, **msgpack**(`{ "stage" : "invite_id", "version": 2}`)`[0:15]`。

也就是说，JSON blob `{"stage" : "invite_id", "version": 2}` 经过 Msgpack 编码，作为 payload 传递给以 `siKey` 为 MAC 密钥的 `HMAC-SHA512`。然后使用前 15 个字节作为“邀请 ID”。

#### 步骤 1d：生成 EdDSA 密钥对

使用 `siKey`，我们如下 [生成](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/seitan_v2.go#L103-L134) 一个 EdDSA 密钥对：`seed = HMAC(sikey, {"stage" : "eddsa", "version" : 2})[0:32]` 并且 `keyPair = NewEdDSA(seed)`，我们稍后使用它来生成签名以验证我们的邀请 ID。

### 步骤 2：加密和签署 pubKey

#### 步骤 2a：加密 pubKey

Alice [加密](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/seitan_v2.go#L136-L166) `pubKey`，以便她（和其他管理员）以后可以访问它，可能是在其他设备上。Alice 还在 `iKey` 上附加一个“标签”，这可能对应于 Bob 的 iMessage 句柄或电话号码。这样，如果她以后想取消邀请，她将有一个人类可读的标签来识别它。

数据 `keyAndLabel` 是通过将这两个字段打包到 [`SeitanKeyAndLabel`](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/protocol/avdl/keybase1/teams.avdl#L429-L433) 结构中计算出来的。为了加密 `keyAndLabel`，Alice 使用团队的私钥，以及对称密钥 [派生字符串](/docs/teams/crypto)：`"Keybase-Derived-Team-NaCl-SeitanInviteToken-1"`。随机数（nonce）是一个 24 字节的随机数，payload 是 `keyAndLabel`；这些参数通过 NaCl 的 [`crypto_secretbox`](https://nacl.cr.yp.to/secretbox.html) 运行。称此密钥为 `ekey`，即“加密密钥”。我们加密这些数据是为了不在签名链中泄露人类可读的标签，即 Bob 的电话号码（`pubKey` 包含在这个加密 blob 中，尽管它对于任何安全属性都不是必需的）。

#### 步骤 2b：打包 ekey

Alice 然后对这个密文进行版本控制和打包：`pkey = pack([2, g, nonce, ekey])`，其中 `g` 是用于加密 `pubKey` 的 [团队密钥](/docs/teams/crypto) 的“代数 (generation)”，因为它在不断轮换。这个“打包密钥” (`pkey`) 就是 Alice 发布给她自己和其他管理员以供将来参考的内容。

#### 步骤 2c：将 pkey 签名到团队链中

最后，Alice 将上一步生成的 [`pkey` 签名](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/teams.go#L859-L893) 到她的团队链中：

```json
"invites": {
    "writer": [
        {
            "id": inviteID, // 见步骤 1c
            "name": pkey, // 见步骤 2b
            "type": "seitan_invite_token"
        }
    ]
}
```

### 步骤 3：发送 iKey

Alice 然后通过她可用的任何方式将步骤 1a 中生成的 `iKey` 发送给 Bob。我们的 iPhone 应用程序自动使用 iMessage。

### 步骤 4：Bob 接受邀请

当 Bob 从 Alice 那里收到 `iKey` 时，他将其拉伸以生成 `siKey`，然后他可以像 Alice 一样计算 `inviteID` 和 EdDSA 密钥对。使用密钥对，Bob 可以创建一个 [签名](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/seitan_v2.go#L210-L224) (`sig`)，并将其发布到服务器，以声明他对团队中席位的所有权。

   `sig` = **Sign**(`privKey`, **pack**(`{"stage" : "accept", "uid" : uid, "eldest_seqno" : q, "ctime" : t, "invite_id": inviteID, "version": 2}`)).

Bob 用适当的值替换他的 `uid`、他的 `eldest_seqno`（以便 Alice 可以识别 Bob，不考虑任何帐户重置）、他计算的 `inviteID` 和 UTC 时间戳。然后他将此 `sig` 和 `inviteID` 发布到服务器。

### 步骤 5：Alice 完成协议

一旦 Bob 认领了团队中的席位，团队管理员就会从 Keybase 服务器收到一条消息，告知他们应该完成 Seitan 协议。他们收到一条带有 `(inviteID, sig)` 的消息，并可以根据 `inviteID` 索引从他们的团队链中读出相应的 `pkey`。管理员 [验证](https://github.com/keybase/client/blob/98327b58939a5b769fb2025743a31fcd08c7265b/go/teams/handler.go#L475-L503) 各种密钥的所有重要部分：

* 邀请尚未被使用
* 邀请尚未过期
* 邀请尚未被撤销
* `pkey` 解密正常
* 使用解密的 `pubKey` 验证给定 `inviteID`、`uid` 和 `eldest_seqno` 的签名匹配

假设所有这些加密检查都通过，那么 Alice（或 Arnie 或任何其他管理员）将 Bob 添加到群组中。

## 安全性分析

该协议实现了三个目标：(1) 它在邀请者 (Alice) 和被邀请者 (Bob) 之间共享一个秘密；(2) 它在群组的所有其他管理员之间共享验证秘密的能力；(3) 管理员不能窃取由不同管理员生成的秘密来邀请 Charlie；(4) 它允许 Bob 向让他进入团队的管理员证明知道该秘密。步骤 (1) 中的安全性取决于该系统范围之外的假设。例如，如果 Alice 通过 iMessage 与 Bob 共享秘密，她就是信任该系统的基于 *TOFU* 的密钥交换。
