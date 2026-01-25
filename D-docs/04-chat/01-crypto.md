{% set page_title = "聊天加密" %}
# 聊天加密
## 高层概述

当 Alice 给 Bob 发送消息时，她使用的是与她在 `/keybase/private/alice,bob` 中保存文件时相同的密钥。（参见 [KBFS 加密文档](/docs/crypto/kbfs)。）这使得很多好事情立刻就能实现：

- Alice 和 Bob 共享一个对称加密密钥，他们通过将其加密到各自设备的公钥来通过服务器传递该密钥。
- 如果他们中的任何一方移除设备，他们的其他设备将创建并共享一个新的加密密钥。这保证了被移除的设备无法读取新消息，而无需依赖服务器来强制执行。
- 如果他们中的任何一方添加新设备，该设备将获得读取旧消息所需的所有密钥的副本。
- 即使 Bob 尚未加入 Keybase，Alice 也可以向他发送消息。如果她知道 Bob 在 Twitter 上是 `@bobbymcferrin`，她现在就可以给他发消息，随后她的设备之一将检查 `@bobbymcferrin` 的证明并自动与他共享密钥。

即使服务器无法伪造新消息，它可能会尝试耍一些花招。出于性能原因，服务器负责为每条消息分配一个顺序 ID。恶意服务器可能会尝试重新排序某些消息，或者遗漏其中一些。为了限制此类花招，每当 Alice 发送消息时，她都会包含一些她之前看到的其他消息的引用。Bob 的设备将检查该列表，以确保它与他看到的一致。这限制了恶意服务器可以进行的恶作剧，同时仍允许 Alice 在糟糕的网络上快速发送消息。

这种共享上下文可以防止服务器在未经 Alice 许可的情况下丢弃她的消息，但 Alice 仍然可以选择在她想要的时候删除它们，这一点很重要。为了在不丢失上下文的情况下实现这一点，每条消息分为两部分：头部和主体。头部包含前一条消息的引用，永远不会被删除。主体包含消息的文本，当 Alice 发送一条特殊的“删除”消息时，服务器将删除它。这样 Bob 就可以检查删除是否被允许。编辑消息的工作方式类似；Alice 发送一条 Bob 可以验证的特殊“编辑”消息。

签名和加密附件与常规消息几乎相同，只是它们可能非常大。如果 Alice 上传视频，Bob 可能只想看一部分而不需要下载整个文件。为了实现这一点，Alice 将她的附件分成块，并分别对它们进行签名和加密，以便 Bob 可以只验证他需要的块。所有这些都经过仔细处理（详情见下文），以确保事后没有人可以移动这些块。

大文件出现的另一个问题是，将其托管在第三方 CDN 上很有帮助。然而，即使是加密文件，对 CDN 的一个担忧是我们可能无法在想要删除文件时可靠地删除它们。为了解决这个问题，Alice 使用一组新的一次性密钥加密附件，并将这些密钥包含在附件消息主体中。这样，删除附件消息主体与删除大文件具有相同的效果。

## 具体细节

### 算法

我们的消息装箱方案有两个版本。现在使用的是 `MessageBoxedV2`。`MessageBoxedV1` 不再由客户端写入，但消息仍然存在，客户端需要理解它。

消息加密使用的是 NaCl 的 [`crypto_secretbox`](https://nacl.cr.yp.to/secretbox.html) (XSalsa20, Poly1305)。
在 `MessageBoxedV1` 中，头部签名使用的是 NaCl 的 [`crypto_sign`](https://nacl.cr.yp.to/sign.html) (Ed25519, SHA512)，头部加密使用的是 `crypto_secretbox`。
在 `MessageBoxedV2` 中，头部使用的是下文描述的签密 (signencryption)。
消息的发送者（或删除者、编辑者）执行以下步骤：

- 使用随机的 24 字节 nonce 加密消息主体。我们需要不需要顺序 nonce 来强制排序，因为我们在下面有前一条消息的引用，所以随机 nonce 是防止重用的最简单方法。在我们的例子中，主体是几种不同类型的结构之一（文本、附件、编辑、删除等），使用 [MessagePack](http://msgpack.org/index.html) 序列化。
- `MessageBoxedV1`：对消息主体的密文进行 SHA-256 哈希。
- `MessageBoxedV2`：对加密消息主体的 `version || nonce || ciphertext` 进行 SHA-256 哈希。
- 将该哈希添加到消息头部，连同其他元数据（如前一条消息引用的列表）。此结构也使用 MessagePack 序列化。
- `MessageBoxedV1`：对序列化的头部字节进行签名。
  使用另一个随机 nonce 加密签名的头部。
- `MessageBoxedV2`：使用另一个随机 nonce 对序列化的头部字节进行签密。
- 将头部明文、头部密文、主体密文和两个 nonce 发送给服务器。

头部中的字段对服务器不是保密的，实际上它需要知道其中的几个字段，比如消息类型。对头部进行先签名后加密/签密的原因是为了保持*签名本身*的私密性。即使服务器知道谁在和谁说话，因为它正在传递所有消息，但最好是它无法*证明*它所知道的。

签名的目的是防止聊天参与者相互冒充。认证加密足以防止聊天外部的人伪造消息，但由于所有参与者共享加密密钥，如果没有服务器信任，这不足以区分一个参与者与另一个参与者。

附件也使用签密。

#### 签密 (Signencryption)

签密是一种使用对称加密密钥和签名密钥对来加密和签名消息的结构，这种方式可以隐藏签名并支持安全的流式解密。

加密是以固定大小的块进行的，只有一个短块或空块来标记结束并检测截断。每个块的 nonce 是 16 个随机字节（所有块共享）加上一个 8 字节的顺序计数器（每个块唯一）。这防止了 nonce 重用、块重排序和包之间的块交换。加密层叠在签名之上以隐藏签名，签名包括加密密钥作为关联数据，以防止加密层被替换。

此方案在 [源代码](https://github.com/keybase/client/blob/dc664617ea326abdd5e5bca877aa0c25fb403efd/go/chat/signencrypt/codec.go) 中有详细文档。

### 密钥处理

本节中的细节与 KBFS 和 Keybase 应用程序的其余部分共享。

所有 Keybase 设备在首次配置时都会发布一个 [`crypto_box`](https://nacl.cr.yp.to/box.html) 公钥和一个 [`crypto_sign`](https://nacl.cr.yp.to/sign.html) 公钥。这些密钥位于用户的签名链中，通过相互签名与其他设备的密钥连接。用户的每个身份证明也由这些设备密钥之一签名并记录在签名链中。（PGP 密钥也可以参与签名链，但在聊天或 KBFS 中不行。）

聊天对称加密密钥是 32 个随机字节。它由聊天中的每个人共享，并且与他们在这些人共享的私有 KBFS 文件夹中用于加密文件的密钥相同。当新设备需要此共享密钥时，拥有该密钥的另一台设备将使用新设备的 `crypto_box` 公钥对其进行加密，然后将其上传到 Keybase 服务器。聊天签名密钥是上述特定于设备的 `crypto_sign` 密钥。

私钥存储在磁盘上，位于使用 `crypto_secretbox` 加密的文件中，密钥派生自用户的 Keybase 密码。当用户登录 Keybase 时，该密钥以纯文本形式存储在磁盘上（参见下文的权衡），或在 macOS 上存储在系统密钥环中。当用户登出 Keybase 时，该密钥被删除，并且他们的私钥在下次登录之前不可读。

磁盘上的缓存聊天消息使用 `crypto_secretbox` 加密，密钥派生自设备的 `crypto_box` 私钥。这样做是为了当私钥不可访问时（特别是当用户登出 Keybase 时），缓存的消息也不可访问。

### 头部布局

聊天头部字段在我们的 [`chat.1.local`](https://github.com/keybase/client/blob/dc664617ea326abdd5e5bca877aa0c25fb403efd/protocol/avdl/chat1/local.avdl#L168-L180) 协议中指定：

```
record HeaderPlaintextV1 {
    ConversationIDTriple conv;
    string tlfName;
    boolean tlfPublic;
    MessageType messageType;
    array<MessagePreviousPointer> prev;
    gregor1.UID sender;
    gregor1.DeviceID senderDevice;
    Hash bodyHash;
    union { null, OutboxInfo } outboxInfo;
    union { null, OutboxID } outboxID;
    union {null, SignatureInfo} headerSignature;
    union { null, MerkleRoot } merkleRoot;
}
```

这些字段是：

   * `ConversationIDTriple conv` — 一个 (TLFId, TopicType, TopicID) 三元组，唯一标识此聊天。第一个字段是一个随机的 16 字节 ID，唯一标识 TLF（“顶级文件夹”，一个 KBFS 共享）。请注意，从 TLF 名称到 ID 的映射并不完全固定，因为 TLF 可能早于其中一名成员加入的时间（通过“注册前共享”）。[`TopicType`](https://github.com/keybase/client/blob/dc664617ea326abdd5e5bca877aa0c25fb403efd/protocol/avdl/chat1/common.avdl#L28-L33) 指定此聊天的“类型”，因为未来的一些聊天可能是自动通信通道，而不仅仅是人与人之间的聊天。`TopicID` 是一个 16 字节的随机标识符，唯一标识此“主题”，以便最终每个 TLF 可以存在多个主题（具有可变名称）。

   * `string tlfName` — 此聊天的人类可读名称，如 `max,chris` 或 `max,BarackObama@twitter`。这在技术上是多余的，因为它传达了与前一字段中的 TLFId 相同的信息。然而，将其包含在头部允许客户端以密码学方式关联两者，并防止服务器将来恶意地重新关联它们。

   * `boolean tlfPublic` — 区分上述 `tlfName` 的公共和私有侧。

   * `MessageType messageType` — 到目前为止，可用的类型在 [这里](https://github.com/keybase/client/blob/dc664617ea326abdd5e5bca877aa0c25fb403efd/protocol/avdl/chat1/common.avdl#L15-L26) 给出。有些是聊天数据，但有些是元数据（例如，“更改此聊天的名称”），以及对以前发送的消息的编辑。

   * `array<MessagePreviousPointer> prev` — 指向先前接收到的聊天消息的指针，以防止服务器重新排序、删除或重放先前的聊天消息。指向上条消息 *m* 的 prev 指针由 *m* 的加密哈希和服务器分配给 *m* 的顺序 ID 组成。服务器的任务是维护聊天中消息的总顺序，客户端使用先前的指针来要求服务器遵守先前公布的顺序。

   * `gregor1.UID sender` 和 `gregor1.DeviceID senderDevice` — 发送者 UID 和设备 ID。

   * `Hash bodyHash` — 在 `MessageBoxedV1` 中是加密主体密文 `(.e)` 的 SHA-256 哈希。
     在 `MessageBoxedV2` 中是加密主体 `(.v || .n || .e)` 的 SHA-256 哈希。

   * `outboxInfo` 和 `outboxID` — 额外的发送者簿记数据，不用于安全性。

   * `union {null, SignatureInfo} headerSignature` — 在 `MessageBoxedV1` 中是对整个头部（包括上面的主体哈希）计算的签名。
     在 `MessageBoxedV2` 中此字段为 null，改为对整个头部进行签密。

   * `union {null, MerkleRoot } merkleRoot` 发送者观察到的最近的 merkle 根。
     在 `MessageBoxedV1` 中不存在。

## 局限性和权衡

### 前向保密 (Forward Secrecy)

**权衡：** 服务器上的消息没有前向保密性。也就是说，读取它们的密钥仍然存在于您的设备上，并且永远不会被删除。这意味着如果有人窃取了您的设备，他们可能能够读取您的旧消息。

**原因：** 这对于用户在新设备上读取他们的消息历史记录是必要的。当您允许在一个账户上使用多个设备时，前向保密性也会进入一个灰色地带。（如果您已经 6 个月没有打开另一部手机，并且您一直在向它发送消息，那么该手机上的临时密钥就不再那么临时了。）最后，如果您在同一设备上保留解密的消息历史记录，删除密钥对您没有多大帮助。请注意，当您移除设备时，我们确实会生成新的加密密钥，因此被移除的设备无法解密在其被移除后发送的消息。

### 可否认性 (Repudiability)

**权衡：** 聊天消息没有可否认性。也就是说，如果 Alice 给 Bob 发送一条消息，Bob 有可能向其他人证明 Alice 发送了它。

**原因：** 这是使用签名密钥验证消息的副作用。可否认认证在两个人之间的聊天中效果很好，而且比签名更便宜。但它不能很好地扩展到拥有大量人员的群聊，因为发送者需要为群组中的每个其他人单独验证每条消息。这也会使向现有群组添加新成员变得困难（我们将来可能会支持），因为在所有发送者上线之前，旧消息无法重新认证。

### 历史完整性 (History Integrity)

**权衡：** 服务器负责为新消息分配顺序 ID，并且服务器有可能以特定方式更改历史记录，例如延迟消息或重新排序尚未看到彼此消息的发送者。

**原因：** 消息应用中的良好性能需要允许不同的人同时发送消息，而不强迫他们同步或拥有完全最新的消息历史记录。这意味着服务器在决定实际发生的事情方面总是有很大的回旋余地。先前的消息引用保证了服务器不能将一条消息放在它回复的消息之前，或者在其他人看到消息后删除它们。

### 元数据 (Metadata)

**权衡：** Keybase 是一项中心化服务，服务器接收大量元数据。它知道谁在和谁说话，以及他们来回发送了多少数据。它还知道每条消息的类型，如“文本”、“附件”或“删除”。

**原因：** 去中心化服务使得随着时间的推移添加功能变得困难，除非开发人员可以破坏向后兼容性，这违背了去中心化的大部分目的。Moxie Marlinspike 写了一篇 [关于其中许多问题的文章](https://whispersystems.org/blog/the-ecosystem-is-moving/)。去中心化服务也可能*更容易*被监视，这取决于谁在进行监视。例如，运行一个恶意的 Tor 出口节点比闯入 Facebook 的服务器要容易得多。

### 磁盘上的密钥 (Keys on Disk)

**权衡：** Keybase 有时将私钥保存在磁盘上可访问的地方，而不是一直用您的密码加密它们。

**原因：** 现代操作系统使得全盘加密变得方便，因此应用程序特定加密存储的用例比以前有限得多。除非攻击者可以从您的磁盘读取任意文件但不能运行任意代码，否则这对您没有多大帮助。这可能发生，但这是一个非常特定的场景，即使它没有泄露您的密钥，它也会泄露您解密的文件。相比之下，向用户抛出额外的密码提示对每个人来说都是一个主要的缺点，特别是对于不知道如何选择好密码或管理它们的非专家来说。

Keybase 的中心化模型也使得从泄露的签名密钥中恢复比 PGP 更容易。每个人都会自动检查您签名链中的撤销。在您完全失去对账户的控制权并且根本无法发布撤销的最坏情况下，您仍然可以撤下与之关联的所有身份证明。
