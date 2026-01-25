# Stellar 钱包密钥管理

Keybase Stellar 钱包在您的设备上既安全又方便地保存您的 Stellar 账户密钥。

### 摘要

当您将 Stellar 账户添加到您的 Keybase 钱包时，您的客户端会对私钥和账户名称进行加密。所有 Stellar 账户信息的捆绑包都存储在 Keybase 数据库中。会为您的主账户创建一个签名链 (sigchain) 链接，以便其他用户可以找到 Stellar 地址向您发送付款。

当您需要 Stellar 私钥进行付款时，客户端会从 Keybase 服务器下载账户密钥包，对其进行解密以获取密钥，并签署交易。密钥一旦不再需要，就会立即从内存中擦除。

虽然密钥存储在 Keybase 服务器上，但私钥是使用 Keybase 服务器无法访问的客户端密钥加密的。将加密密钥存储在 Keybase 服务器上允许您在所有设备上拥有所有 Stellar 账户。

### 基础

用户的 Stellar 数据包括：

1.  您的主 Stellar 账户 ID 在签名链中的链接。最新的是您当前的主账户。
2.  明文数据包，对用户和服务器可见，包含有关用户 Keybase 钱包中 Stellar 账户的信息。名称：**server visible**（服务器可见）。
3.  加密数据的全局包，包含有关用户 Keybase 钱包中所有 Stellar 账户的秘密元数据（即账户名称）。名称：**user private**（用户私有）。
4.  每个账户的加密数据，包含签署交易所需的私有 Stellar 账户密钥。名称：**account private**（账户私有）。

所有 Stellar 数据都存储在 Keybase 数据库中。服务器在必要时读取 **server visible**。它无法解密 **user private** 或 **account private**，因为它没有必要的加密密钥。客户端将从服务器获取 **server visible** 和 **user private**，以显示钱包账户、其余额、最近的交易。为了签署交易，客户端将获取 **account private** 包并在使用后将其丢弃。

为了加密这些数据，客户端使用每用户密钥 (PUK)。我们有关于 PUK 的 [完整文档](/docs/teams/puk)，但简单来说，它是一个为用户的所有 [设备密钥](/blog/keybase-new-key-model) 加密的种子。

用于加密的密钥是从用户的 PUK 种子和这些包特定的常量字符串派生的对称 NaCl 密钥。

对于 **user private** 包，它是：

    key = hmac(key=[puk seed], data="Derived-User-NaCl-SecretBox-StellarBundle-1")

对于 **account private**，它是：

    key = hmac(key=[puk seed], data="Derived-User-NaCl-SecretBox-StellarAcctBundle-1")

**user private** 数据通过 msgpack 打包成二进制数据。然后用随机 nonce 和派生的对称密钥对其进行密封。加密数据、nonce、加密数据的版本和 PUK 的生成代数被放入一个结构中。该结构通过 msgpack 打包成二进制数据。msgpack 数据随后通过 base64 编码为字符串。

**account private** 数据通过 msgpack 打包成二进制数据。然后用随机 nonce 和派生的对称密钥对其进行密封。加密数据、nonce、加密数据的版本和 PUK 的生成代数被放入一个结构中。该结构通过 msgpack 打包成二进制数据。msgpack 数据随后通过 base64 编码为字符串。

**server visible** 包结构通过 msgpack 打包成二进制数据。然后通过 base64 编码为字符串。

当您更改哪个 Stellar 账户是您的主账户时，会在您的 [签名链](/docs/sigchain) 中插入一个链接。这是为了让其他用户可以找到属于您的账户，以便他们可以向您发送 Stellar Lumens 或资产。

### 仅限移动设备模式

作为额外的安全措施，您可以将您的任何 Stellar 账户标记为“仅限移动设备”。由于移动设备应用程序具有更好的沙盒机制，流氓应用程序与 Keybase 应用程序交互以检索您的密钥的可能性较小。

一旦您将账户设置为仅限移动设备，服务器将仅向移动设备返回加密的 **account private** 包。

为了防止可以访问您的一台桌面设备的人配置新的移动设备并使用它来访问仅限移动设备的账户，服务器不会向任何少于 7 天的移动设备返回加密的 **account private** 包。除此之外，您还将收到大量关于新设备已添加到您的账户的通知，以便您可以在必要时采取适当的措施。

只有（足够旧的）移动设备才能关闭账户上的仅限移动设备设置。

### 发送给未来的 Keybase 用户或没有钱包的用户

一旦您拥有 Keybase 钱包，您可以向任何 Keybase 用户发送 XLM，即使他或她尚未建立任何 Stellar 账户，或者向任何未来的 Keybase 用户发送。

```bash
keybase wallet send serenawilliams@twitter 5 USD
```

（目前，Keybase 上还没有用户证明拥有 serenawilliams@twitter 账户，但您仍然可以给她发送 Lumens！）

我们使用所谓的“中继” (relay) 支付来做到这一点。

如果我们检测到您要发送的人要么没有与他们的 Keybase 账户关联的 Stellar 账户，要么甚至还不在 Keybase 上，那么我们会创建一个临时持有账户，我们将付款发送到那里。该账户的私钥针对由发送者和接收者组成的“团队”进行加密。

在上面发送给 Serena Williams 的例子中，Keybase 应用程序将创建一个新的随机账户，比如 `GCYMBZE2RB5ZMSGB5KVOFR5XOGT6ZKVQ426QUU7RHKI7XWLT5CUIO3YS`。它将使用与加密发送者和 `serenawilliams@twitter` 之间共享的聊天或 KBFS 文件类似的方法来加密该账户的私钥。中继账户的加密数据存储在 Keybase 数据库中。

一旦接收者在 Keybase 上创建一个账户并证明 `serenawilliams@twitter`，她的新客户端将创建一个 Stellar 账户密钥对。然后它会注意到有一笔中继付款在等她，所以它会创建一个账户合并交易，将所有资金从 `GCYMBZ...` 发送到她的新账户。

在接收者这样做之前，发送者可以随时取消中继付款。当这种情况发生时，账户合并交易将把所有资金从 `GCYMBZ...` 发送回发送者的账户。

### 数据清理

如果可能，我们会从数据库中清除任何 Stellar 数据。

例如，如果您吊销设备，对您透明的是，您的客户端将为您生成一个新的 PUK 并重新加密您的 Stellar **user private** 和 **account private** 包。一旦它们发布到服务器，以前的包版本（为您旧密钥加密的）将被永久删除。

当您从钱包中删除 Stellar 账户时，数据将被永久删除。

### 备份

我们建议用户存储其 Stellar 私钥的安全备份。根据设计，我们无法恢复私钥。如果您丢失了所有 Keybase 安装和纸质密钥，加密的密钥将无法解密。

### 链接

*   [下载它！](/download)
*   [所有其他文档](/docs)
*   [通过 GitHub 报告问题](https://github.com/keybase/client/issues)
