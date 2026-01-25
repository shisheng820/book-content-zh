# 用于阅后即焚消息的分层临时密钥

Keybase 现在支持“阅后即焚”消息，这些消息会在过期后自动删除。作为该功能的一部分，我们保证这些消息的前向保密性。这意味着除了删除消息本身之外，客户端还会删除用于加密它们的密钥。目标是即使攻击者从我们的服务器窃取了您的一条加密的阅后即焚消息，然后又窃取了您的一个设备及其上的所有密钥，攻击者仍然无法解密该消息。

## 高层设计

每个 Keybase 设备都会创建一个每日临时加密密钥对，用设备的长期签名密钥对其进行签名，并将公钥和该签名发布到 Keybase 服务器。每个密钥都是完全随机的，不是从任何先前的密钥或任何长期密钥派生的。使用这些密钥的任何密文的最长生命周期为一周。如果设备没有上线发布新密钥，发送者可以继续使用其最近的密钥，之后设备将推迟删除该密钥以进行补偿。在足够长的时间没有发布新密钥后，该设备被视为陈旧，并且无法再接收任何类型的临时消息。该陈旧窗口目前为三个月，以允许设备很少上线的情况。限制陈旧性意味着一个被封存的设备不会永远损害整个群组的前向保密性。

我们不在应用层直接使用设备临时密钥 (EK) 来加密聊天消息，而是在它们之上构建用户和团队密钥的层次结构。每个用户发布一个每日用户 EK，私钥为每个有效的设备 EK 加密。同样，团队发布团队 EK 并为属于团队成员的每个用户 EK 加密。这反映了我们长期的 [每用户](/docs/teams/puk) 和 [每团队](/docs/teams/crypto) 密钥的层次结构。所有这些更高级别的 EK 都具有与设备 EK 相同的一周生命周期。发布设备在加密这些密钥的副本进行传输时会跳过陈旧的设备和陈旧的用户。

在聊天应用层，我们总是使用可用的最新团队 EK 进行加密。这意味着无论为消息选择的生命周期如何（可能只有几分钟），加密密钥的生命周期约为一周。客户端和服务器会尽最大努力在消息生命周期结束后立即删除消息，但在密钥最终在约一周后被删除之前，保存的消息副本仍然可以用窃取的设备解密。

## 与 Signal 双棘轮的比较

[Signal 双棘轮](https://signal.org/docs/specifications/doubleratchet) 是一种广泛使用的管理临时消息密钥的设计。它是两种机制的结合：在使用密钥时对其进行哈希处理以提供前向保密性，以及持续执行 Diffie-Hellman 以从过去的泄露中恢复。双棘轮的优点是它能尽快为异步发送者实现前向保密性。在删除密钥之前没有一周的窗口期。相反，在活跃的对话中，它们会被立即删除。

我们不为 Keybase 的阅后即焚消息使用双棘轮主要有两个原因。首先是我们担心在拥有大量参与者的对话中的性能。Keybase 支持拥有数千名成员的团队，而这些成员中的每一个又有许多设备。在群组中使用双棘轮的标准方法是每个参与者为每个其他参与者维护一个单独的棘轮。这将使得向大型团队发送消息变得昂贵，无论是处理每个接收者所需的时间，还是发送长列表的认证器所需的带宽。Signal 支持一种 ["发送者密钥" 变体](https://signal.org/blog/private-groups/#the-textsecure-group-protocol)，可以在许多消息上分摊这项工作，但这仍然是需要在每个发送设备上完成的工作，硬件较弱或网络条件较差的发送者会受到影响。

第二个原因是我们希望避免将密钥管理与应用程序状态混合在一起。在 Signal 中，棘轮序列和消息序列是绑定在一起的。这对他们的用例很有效，并且它提供了一些重新排序和重放保护。然而，Keybase 应用程序更复杂，其方式难以用主要线性的密钥序列来建模：

- [团队聊天](https://keybase.io/docs/crypto/chat) 可以有多个不同的频道。
- 在“注册前共享”的情况下，您可以与尚未加入 Keybase 的人聊天，并在他们证明自己是谁后自动为他们重新加密。
- [Keybase 文件系统](https://keybase.io/docs/kbfs) 将来可能支持“阅后即焚文件”。
- [Saltpack 加密消息](https://saltpack.org/) 可以添加阅后即焚模式。
- 我们可以为第三方应用程序创建特定于应用程序的派生密钥，其中一些可能是临时的。

可以想象，我们可以通过添加更多棘轮并以有趣的方式管理它们来处理所有这些情况，但这会将大量复杂性推向应用层。相反，一个合约为“此密钥有效期为一周，随你处置”的 API 使构建应用程序变得简单得多。

## 临时密钥协议细节

我们的 [`keybase1/ephemeral.avdl`](https://github.com/keybase/client/blob/master/protocol/avdl/keybase1/ephemeral.avdl) 协议文件定义了我们在发布临时密钥时签名的对象。这是一个设备 EK 声明的布局。相应的用户和团队对象几乎相同。

```
  record DeviceEkMetadata {
    KID kid;
    Time ctime;
    Time deviceCtime;
    HashMeta hashMeta;
    EkGeneration generation;
  }

  record DeviceEkStatement {
    DeviceEkMetadata currentDeviceEkMetadata;
  }
```

- `kid` 是从临时秘密派生的 Curve25519 密钥对的公钥部分。给定临时秘密 `s`，密钥对的私钥部分是 `HMAC-SHA256(key=s, msg="Derived-Ephemeral-Device-NaCl-DH-1")`，公钥部分是私钥部分的 `crypto_scalarmult_base`。
- `ctime` 是种子创建的时间。客户端获取 Keybase Merkle 树的最新根并使用那里的 `ctime`，而不是使用自己的时钟（这可能会在时钟奇怪的机器上导致不良行为）。
- `deviceCtime` 是根据本地设备时钟的创建时间。如果客户端无法获取 Merkle 树根，则回退到此时间，从而启用离线设备密钥删除。
- `hashMeta` 是提供 `ctime` 的 Merkle 树根的 SHA256 哈希。
- `generation` 是此设备迄今为止发布的所有 EK 的递增计数器。
- `currentDeviceEkMetadata` 描述了此声明发布的具体设备 EK。

设备 EK 声明由设备的长期签名密钥签名。用户 EK 声明由当前每用户长期签名密钥签名，该密钥在用户的签名链中给出。团队 EK 声明由当前每团队签名密钥签名，该密钥在团队的签名链中给出。虽然设备长期密钥从不轮换，但当设备被撤销或团队成员被移除时，每用户和每团队密钥会轮换。作为轮换的一部分，客户端还会轮换用户/团队 EK 并发布由新长期密钥签名的新 EK 声明。

在发布新的用户 EK 和团队 EK 时，发布客户端为每个未过期的设备或团队成员加密一份临时秘密的副本，并将这些密文连同签名的 EK 声明一起上传。在配置新设备或向团队添加新成员时，客户端还会制作当前 EK 的另一个加密副本。在解密 EK 秘密时，客户端根据关联 EK 声明中的 `kid` 字段检查秘密派生的 Curve25519 公钥。

## 过期与删除

临时密文的有效期绝不会超过一周，但客户端需要将临时密钥保留稍长的时间。考虑以下场景：您的笔记本电脑发布了一个设备 EK (`laptop_dek`)，然后离线六天。在第 6 天，您的台式机发布了一个新的用户 EK (`uek`)，并为这个使用了 6 天但仍然有效的 `laptop_dek` 加密了一份 `uek` 的秘密副本。因此，虽然 `laptop_dek` 最初打算在第 7 天过期，但它可能在第 13 天才被需要用来解密 `uek` 的秘密。

解决这个问题的一种方法可能是根据密钥的使用情况推迟删除，直到没有剩余的有效密文需要解密为止。在服务器的帮助下，这在密钥层次结构中是可行的，但在应用层使用密钥时是不切实际的。这也要求客户端在线才能删除任何东西。

相反，我们应用以下规则：密钥在*下一*代发布一周后被删除。由于加密总是使用可用的最新 EK，并且没有临时密文的有效期超过一周，这保证了私钥会与为它们加密的任何密文一样长久地存在。在每天发布新 EK 的典型情况下，此规则意味着私钥在 8 天而不是 7 天后被删除。在几天没有发布新 EK 的情况下，删除也会相应推迟几天。我们将此延期限制在最大陈旧窗口（额外三个月），此时设备或用户被视为陈旧。

## 认证与可否认性

在阅后即焚和普通情况下，群组内的通信有三种认证选项：

1. "单一 MAC (One MAC)." 使用共享团队加密密钥对消息进行 MAC。
2. "成对 MAC (Pairwise MACs)." 在发送者和团队的每个成员之间制作单独的 MAC，可以针对每条消息或针对短期签名密钥。这就是 Signal 所做的。
3. "签名 (Signing)." 使用发送者的长期签名密钥对消息进行签名。这就是 Keybase 聊天所做的。

单一 MAC 方法不提供“特定于发送者的认证”。也就是说，共享加密密钥的团队成员可以在团队内相互冒充。虽然有些设计认为这是一种可否认性功能，但随着团队变大，以及成员之间不太可能完全信任彼此，这成为一个更大的问题。出于这个原因，Keybase 避免使用单一 MAC 方法。

成对 MAC 和签名之间的权衡不那么明确。成对 MAC 方法提供可否认性，因为成对认证器是可伪造的。公钥签名不可否认。另一方面，在大型群组中签名更便宜，因为您只需要对消息签名一次。此外，签名更灵活：如果将来有新成员加入群组，他们将能够验证旧签名，但不能验证旧的成对 MAC。这种成员资格的灵活性是 Keybase 使用签名来认证文件和聊天消息的决定性原因，代价是失去了可否认性。

然而，阅后即焚消息在这里可以做出不同的权衡。将消息标记为阅后即焚意味着发送者不太在乎让未来的团队成员阅读它，或者也许发送者故意想避免让未来的团队成员阅读它。阅后即焚消息也可能更敏感，因此发送者可能更在乎可否认性。（我们不知道现实世界中有谁使用可否认性作为辩护的案例，但这可能会发生！）出于这些原因，Keybase 在小型团队（100 名成员或更少）中对阅后即焚消息使用成对 MAC 而不是签名。

作为这些成对 MAC 的密钥，我们使用发送者和每个接收者的长期设备加密密钥的 Diffie-Hellman 输出，并与上下文宁字符串混合。这反映了我们在常规聊天消息和大型团队阅后即焚消息中的方法，在这些情况下我们使用设备长期签名密钥。

## 聊天协议示例

这是一个带有成对 MAC 的示例消息，格式化为 JSON 以便于阅读。常规消息和阅后即焚消息之间不同的字段已注释：

```js
{
  "version": 4,
  "clientHeader": {
    "conv": {
      "tlfid": "D5wy0MNOXPEoZCfq7WKVJA==",
      "topicType": 1,
      "topicID": "DfQoqZ9cH7qme28eeo5xIA=="
    },
    "tlfName": "testerralph,testerrudolph42",
    "tlfPublic": false,
    "messageType": 1,
    "supersedes": 0,
    "kbfsCryptKeysUsed": false,
    "deletes": null,
    "prev": [
      {
        "id": 4,
        "hash": "8WGonE+GG0v8sofu3v9EVSFLr/qZMwIeehrfDEghFSU="
      }
    ],
    "sender": "uq09RkWjBHbS+pfoNkZmGQ==",
    "senderDevice": "ghLxVqHLeZrqyA/udKijGA==",
    "merkleRoot": {
      "seqno": 3093864,
      "hash": "NodeXtrO3kEivPkF+UsAbLkVfuK7jFh+UqN70nGNzF2nP9znOxRdN+tDNClkvRKIIlT4oPYqNTamY7Fj+l029g=="
    },
    "outboxID": "dTxsmDsftUU=",
    "outboxInfo": {
      "prev": 4,
      "composeTime": 1529342305341
    },

    // "临时元数据"，指示此消息是阅后即焚的。
    // 当存在此部分时，客户端使用临时密钥而不是团队的长期密钥来解密主体。
    "em": {
      // 消息的"生命周期"，以秒为单位。604800 秒是一周。
      "l": 604800,
      // 用于加密主体的临时密钥的"代数"。
      "g": 1
    },

    // 用于认证此消息的"成对 MAC"，与每个 MAC 预期的接收者设备的公钥配对。
    // 当存在此部分时，接收者通过上面的 "sender" 和 "senderDevice" 字段查找发送设备的公钥，
    // 并使用它来验证用于其设备的 MAC。在此模式下，"verifyKey" 是一个公共常量，
    // 对应于全零私钥，头部密文本身不提供任何真实性。
    "pm": {
      "012105d72ff6d356715621baebcf5e138b15414232c189ef9925ccbe0f36b79693330a":
        "+4MjACPtaegHy+YwA9Gv3S0UOGaht/l5K2l/KbzNNus=",
      "01210f4a6a3fdf6c3530217f922bd1a9dd60dfa96959f0a421b0f8b4671d8dd5456f0a":
        "r9D8bL6SmVr2g8gZtmkIOnLLNxSxl6dUhU22G+pieEQ=",
      "012140900270a7819b043a8447e1d3e478b17c690c42755befbecd8de122a8c3ca600a":
        "E1GL5aBuxII4mVVFNzLsW1z8iuesNtHkPjZugySwGa0=",
      "012142660fd3920a31dc58f8de2ac6adeb476d8d65266f1a020cd50a10156b62cb4d0a":
        "QEwiu3qb6x9sENQFgk0FWrYHkuYwv3HpYQcPvjygwfQ=",
      "012144925855a68f635816ca756461d75279cd885e9b3ed99f335718239dedf5ca6c0a":
        "ieG85k0ZafSZeEolHRA0qCSrbOqZwB7E95jjGV9/7BE=",
      "012167fd6b41b6e1685b8edad39f02cbac9878e3972d2845311b589b98d9724b44500a":
        "BNwhcAKug5AzHiaPuy8uUEuVAOPRHWgFhMip1Vn+n94=",
      "0121688caad6aaa673980a7750c964f5c5c10d807864ec00de28646f54727bafe1010a":
        "TEMuaNCUT8T9EJVDev01JPpgNhCiZEVtXCIPEl6kJqM=",
      "012181d6969d53fcd873aa62c49e8984a3781455a6ce30c2302f73cf0b0f232302680a":
        "irW83fHUDG5XXOXdnYGqWcWC7r+H2ZagPddH3NfNnR0=",
      "01218693f54dc97bc0e298fb34b3826a6b36b49d50025346316879fd4235417788300a":
        "cKMNMZ1Z1rlvCK3hCTcs4vxQ1LfwHvzDBLh7OQI/vgo=",
      "01219b42147a162effff296676cb43c82bb6cdda404309537b58edf41e5d2e04631f0a":
        "fyzn9GgRw2tG10VLm45Wh3BZEraUqjR5a9UPgIQwGnE=",
      "01219bddbff2a921f8d0308347187d69ca470609ee1e2b11c51d16ab6269bbad92070a":
        "W13kNFT6t94hglL18n2GhFHxEFi1JJz22BizoEDbl9o=",
      "0121ba2e89682adc3c85a3cb0f1a745a11f602c6f1eb597b4634812538418fe14e620a":
        "u51e0wOmH2XcvgwpPF9gLKlm2s8I/iTNbaSsWeZm9k4=",
      "0121bcd7cef92c52445b4d6177318e543bf7b342ecdd60808693f419c633e6ef1a020a":
        "NuMXAzqdRgYPDbqa5KrIgbU9u2C/us9iBYOnfbY16lw=",
      "0121cd9f2ee4495fda2723f63221095546e71552b6f21b8bb247c531b4453cce9c230a":
        "Y5X12wngluGzsIvzujaJPBTXZTp0ShHp+5jaD2KAlEk=",
      "0121e0ffe7daa4e07fccd7f54f7deae67d4dc740b3f7582565aa34a0789cd3e23d410a":
        "w9DYIZ+RRLJpXOj0CSVCchmwhaYMTAAMO/fN0uRWEPk=",
      "0121e22f3a28b397e17255d5f6215c2fdea2653ec131d7a030fbbd7f973afe47570d0a":
        "ztz2Y/0KvqIDCysX8Ijn03qMOP9uw3P0p1rQEOdQemE=",
      "0121f6ef8f41a7104a110b4ba83618cf3d1b3bafac2ac065b1bd01ea018d8022b6360a":
        "edA3Qg4nQ2T5fSFgpu8VJqvqizwhPhWW9x8memLIKJc="
    }
  },

  // 头部元数据总是用下面 "keyGeneration" 指示的团队长期密钥加密，
  // 即使在阅后即焚消息中也是如此。它还在内部由 "verifyKey" 的私钥部分签名。
  // 解密的元数据包含主体密文的哈希，以便主体可以独立删除。
  "headerCiphertext": {
    "v": 1,
    "e": "dextrPkwdy/Y6Fk34UMNeKIujFlbFN+AU/FTupb13515mC4fWO6XGBQk2EoOptbQBZ2ZVN/2CF+xNLIXB60oHWNW6IwwcdWQjkwnayhjaKx5Ux6osysd9ssDJE6LMdOQw9IsOT3foXhHtTapXAoOkqdRErpPTle1YM6wk1arxogB8hcezTNSIdIhgH0V0HkrqBB1CV4Cn+m/4MmECP3czAt0iRIeUY5RQvthVHyL79GiFTExV3JGWgEg3YxNuhrPhKmVrM4Q3zmzY1f7DSQgS0sni8SsbQR808hD675briUho0ZcD2KjDeDqF6JMyyLd1uzZs9hBCrFxYeAf+hHOqQdEabdGdAcCfROeXzY+z+tDQtJ90G33pMJhrCH8OfUGGAxGHLMwtNwNmxcWNSjJ/HyFK0r3w1PzmUxFD2wnsv2JbGoRprtQV/umLHbj9ahxbbjOl7Xw4wiTlIny6pA1FD0iTaTdYFJKkDO6RsCuJlkdrUYuDjYxpK5MmZEGsPyCXY5bGNloA7nI7U4Z4pt6Vo7uBdEdT+WTT/bEi/oU80RrzzdQruYGBkt3BJAi/6Imz+X/PUh2HEqLeA2sqpJN7auXyVYpxf0v3fGnuM3sEM91ZqXQzo1otfpnyT2Cqw33zYpFUPk8K6qH8U4NrKW7rSpuvHwU6Ar1wCWHfrl2bZ2IEHP18y36l2u2ivSNu02Kra3Sh50Pvw2PkGOEEpTGvPt1eboSNu6h5U1L",
    "n": "OdPwtDykhMkegzPjyFxN9Q=="
  },

  // 在常规聊天消息中，主体使用与头部相同的密钥加密。
  // 在阅后即焚聊天消息中（由上面的 "em" 字段指示），主体使用临时密钥加密。
  "bodyCiphertext": {
    "v": 1,
    "e": "7U/UIEeq+CHLAhl3qwdFTuZ3wL7g7YHfJjMJFhnLTFer4Bx8D1nx4EgxsMYNrZHGbUSTQhlVd6Ek2TVeMqh43YgGm2YapKdSKSOQ5Ug=",
    "n": "0qjVyFRig0RWr5VkcPuF9EXJMeJu1TE3"
  },

  // 在带有成对 MAC 的消息中（像这条），这个 ed25519 公共签名密钥
  // 是从全零私钥生成的。否则接收者必须验证它是发送设备的长期签名密钥。
  "verifyKey": "ASA7aie8zrakLWKjqNAqbw1zZTIVdx3iQ6Y6wEihi1naKQo=",

  // 头部加密所使用的团队共享加密密钥的代数。
  // 在常规的非阅后即焚消息中，主体也使用此密钥加密。
  "keyGeneration": 1
}
```

## 未来工作方向

密钥计划可以扩展到包括更细粒度的密钥，例如一天或一小时过期的密钥。这可以减少双棘轮设计和我们的静态设计之间的差距。我们需要决定这些不同“层级”的密钥生命周期如何交互。（例如，如果一条消息应该用 1 小时密钥加密，是否可以对某些接收者默默地回退到 1 周密钥？或者是否应该将经常离线的设备排除在最短命的消息之外？）我们还需要小心不要在移动设备上过于频繁地唤醒。
