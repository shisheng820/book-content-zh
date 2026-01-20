# 服务器 (Server)

我们开发 Keybase.io 已经半年多了，我们希望它能成功，但我们也有一点紧张。我们越成功，我们就越成为有价值的目标。

以下是我们最担心的攻击：

  1. 服务器被 DDoS 攻击
  1. 服务器被入侵；攻击者破坏服务器端代码和密钥，向客户端发送坏数据
  1. 服务器被入侵；攻击者分发损坏的客户端代码

我们已经采取了一些措施来保护服务免受这些攻击，我们想描述一下它们，以便你知道该寻找什么。

## Keybase 实际上在做什么

在描述我们如何保护 Keybase 之前，我们必须描述它实际上在做什么，以及什么值得保护。Keybase 的核心功能是以标准化格式存储我们用户的公开签名。重要的签名形式如下：

   1. **身份证明 (Identity proofs)**："我是 Keybase 上的 Joe，也是 Twitter 上的 MrJoe"
   1. **关注者声明 (Follower statements)**："我是 Keybase 上的 Joe，我刚刚查看了 Chris 的身份"
   1. **密钥所有权 (Key ownership)**："我是 Keybase 上的 Joe，这是我的公钥"
   1. **撤销 (Revocations)**："我收回我之前说的话"

例如，当 Joe 想要建立与 Twitter 上身份的连接时，他会签署第一种形式的声明，然后将该声明发布在 Twitter 和 Keybase 上。外部观察者随后可以确信 Keybase 上的 Joe 和 Twitter 上的 MrJoe 是由同一个人控制的。这个人通常是预期的密钥持有者，但当然也可能是入侵了 **两个** 账户的攻击者。

当诚实的 Joe 签署这样的证明时，他也会签署他前一个签名的哈希值。因此，想要验证 Joe 所有签名的外部观察者只需验证链中的最后一个；其他的随之而来。例如，我最近签署了一份 [声明](https://keybase.io/_/api/1.0/sig/get.json?sig_id=5dc95450ceb878b3cdfe35d7ecd92695733046c6731132754fa303ebb3cac81a0f)，表示我关注 Keybase 用户 [al3x](https://keybase.io/al3x)。我签署了一个包含关于我和 Alex 的相关信息的 JSON 数据块，以及键值对 `"prev":"d0bd03..."`，其中 `d0bd03...` 是我签署的上一个 JSON 数据块的 SHA-256 哈希值。

对于给定用户，他们签名的总和捕捉了他们希望记住并向世界展示的状态。例如，我目前的个人资料显示我是 Twitter 上的 maxtaco，我曾是 GitHub 上的 TacoPlusPlus，但现在我在那里也是 maxtaco，并且我相信 Twitter 上的 malgorithms 和 GitHub 上的 malgorithms 是"正确"的 Chris Coyne。五个签名（其中一个是撤销）构成了这种状态；诚实的 Keybase 服务器应该始终向所有人展示这五个签名，以便我们可以在客户端忠实地重建我的状态。

## 攻击 1 和 2：DDoS 和数据损坏

我们提到了针对该系统的三种攻击。考虑前两种，旨在阻止诚实客户端检索诚实用户的签名数据。粗暴的攻击者可能会对 Keybase 的服务器进行 DDoS 攻击，阻止任何人访问 Keybase 的数据。更复杂的攻击者可能会获取 Keybase 服务器的 root 权限，破坏其签名密钥，并开始向诚实客户端发送损坏的数据。

由客户端和第三方观察者强制执行的两种机制可以防御这两种攻击：

   1. 所有用户签名链必须单调增长，永远不能"回滚"
   1. 每当用户向签名链发布添加内容时，站点必须签署并通告全局站点状态的更改，并且这些更新是 [全序的](http://en.wikipedia.org/wiki/Total_order)。


### 不受信任的镜像

这些要求的第一个含义是，不受信任的第三方可以镜像站点状态，客户端可以从 Keybase 服务器或镜像访问数据。根据要求 (2)，服务器必须发布并签署所有站点更新。客户端不关心这些更新来自哪里，只要签名通过验证，并且站点状态与签名一致即可。

（我们 *目前* 尚未意识到有第三方镜像，并且我们的参考客户端需要一些修改才能处理只读服务器。但是，我们鼓励所有人抓取我们的 API 以做准备。）

### 诚实否则被抓

这些要求的第二个含义是，受损的服务器可以选择像诚实服务器一样行事，或者犯下诚实用户可以检测到的"错误"。获得服务器控制权的攻击者可以：

   1. 选择性地回滚用户的签名链和/或抑制更新
   1. 伪造"密钥更新"，并在用户链的末尾附加签名
   1. 向不同用户展示不同版本的站点状态

自 v0.3.0 版本以来，Keybase [命令行客户端](/guides/command-line) 保护客户端免受这些服务器攻击。以当 [我](https://keybase.io/max) ["关注"](https://keybase.io/docs/server_security/following) [Alex](https://keybase.io/al3x) 时发生的情况为例。我的客户端从服务器下载我们两人的签名链，并对它们进行加密验证，检查我们的哈希链是否格式正确并已签名。它还会根据缓存数据检查新数据，并在服务器"回滚"任一链时报错。我的客户端防止受损服务器更改 Alex 密钥的方式与防止 Eve 冒充 Alex 的方式相同：它检查其他服务（如 Twitter、GitHub 和 DNS）上 Alex 身份和密钥证明的佐证。

为了防止服务器将我的站点数据视图与 Alex 的视图 ["分叉"](https://www.usenix.org/legacy/events/osdi04/tech/full_papers/li_j/li_j.pdf?q=untrusted)，我的客户端会检查所有签名链是否准确地捕获在站点的全局 [Merkle 树](http://en.wikipedia.org/wiki/Merkle_tree) 数据结构中。它从服务器下载这棵树的 [根](https://keybase.io/_/api/1.0/merkle/root.json?seqno=2728)，并根据站点的 [公钥](/docs/server/our-merkle-key) 对其进行验证。如果检查通过，它会获取 [已签名的根块](https://keybase.io/_/api/1.0/merkle/block.json?hash=c2cca49b3d84915ba7bcae1290bda223badce2d667bf769df87c3f81efb192ca268055a719693b4a3682d9391d8be8e42a75760f01cc39a330e6f42bb308518e)。我的 UID 是 `dbb165...`，所以我的客户端沿着树向下跟随 `db...` 路径，即块 [`68b5d3...`](https://keybase.io/_/api/1.0/merkle/block.json?hash=68b5d3599be9acbe97bcc45603a322f85f8a99b9cbc696592fe1088c3a099a45d929f0bc2fae2230f0b31b5e4b4122365f50b34fcf91a94a357df90a83e3b013)。现在，我的叶子可见，显示我的签名链结束于链接 42，哈希值为 `d0bd03...`，这与它之前获取的数据相匹配。我的客户端对 Alex 的链做同样的事情。所有检查成功后，我的客户端签署我的链、Alex 的链以及签名时的 Merkle 根；它将 [此签名](https://keybase.io/_/api/1.0/sig/get.json?uid=dbb165b7879fe7b1174df73bed0b9500&low=43) 作为关注者声明发布。

一个非常复杂的攻击者可以向我的客户端和 Alex 的客户端展示不同的签名 Merkle 根，但必须永久维护这些分叉并且 [永远无法合并](http://www.scs.stanford.edu/nyu/02fa/sched/sundr.pdf)。用户带外"比较笔记"会立即暴露服务器的欺诈行为。

## Keybase 客户端完整性

因此，广泛使用的 Keybase 客户端在保持 Keybase 服务器诚实方面起着至关重要的作用。它们检查用户签名链的完整性，并能发现恶意回滚的证据。当 Alice 对 Bob 的关注中断时（如果 Bob 或服务器受损），它们会提醒 Alice。它们根据已知的签名链检查站点发布的 Merkle 树根的一致性。当所有这些检查完成后，它们签署证明，建立已知的安全检查点，以便将来追究服务器的责任。

所以一切都取决于 Keybase 客户端的完整性，即它们正常运行且未受损。我们提供多种保障措施来保护客户端完整性。首先，我们保持开放 API 并声明我们的开源客户端只是一个 *参考客户端*，如果开发人员认为我们做得不好，他们可以自由地用不同的语言制作新的客户端。其次，我们签署对 Keybase 参考客户端的所有更新，并提供一种 [更新机制](https://github.com/keybase/node-installer/wiki/Update-Architecture) 来下载新客户端，而无需信任 HTTPS，只需信任我们密钥的完整性。我们将该私钥保持离线状态，以便在服务器受损的情况下它不会受损。

我们完全理解 Keybase Web 客户端的用户无法获得这些保证。但我们希望有足够多的用户使用 Keybase 命令行客户端来保护 Web 用户的安全，即在发生入侵时通过捕获服务器的不当行为。

## 下一步

本文的目的是解释 Keybase 系统目前已有的安全机制。展望未来，如果第三方有兴趣托管不受信任的镜像，那就太好了。这些镜像最终也可能成为审计员，允许 Alice 和 Bob 比较笔记并确信他们看到的是站点状态的一致视图。

而且...一个更新！我们现在正在将 Merkle 根发布到 [比特币区块链](/docs/server/merkle-root-in-bitcoin-blockchain) 中。

感谢阅读，祝 Keybase 使用愉快！



## 认识你的签名链 (sigchain)（以及其他人的）

每个 Keybase 账户都有一个公共签名链（称为 *sigchain*），这是一个关于账户随时间变化的有序声明列表。当你 [关注](/docs/server_security/following) 某人、添加密钥或连接网站时，你的客户端会签署一个新声明（称为 *链接*）并将其发布到你的签名链。

作为 JSON（删除了一些字段），签名链看起来像这样：

```json
[
	{
		"body": {
			"device": { "name": "squares" },
			"key": { "kid": "01208…" },
			"type": "eldest"
		},
		"prev": null,
		"seqno": 1
	},
	{
		"body": {
			"device": { "name": "squares" },
			"key": { "kid": "01208…" },
			"type": "web_service_binding",
			"service": { "name": "github", "username": "keybase" }
		},
		"prev": "038cd…",
		"seqno": 2
	},
	{
		"body": {
			"device": { "name": "rectangles" },
			"key": { "kid": "01208…" },
			"type": "sibkey",
			"sibkey": { "kid": "01204…", "reverse_sig": "g6Rib…" },
		},
		"prev": "192fe…",
		"seqno": 3
	},
	{
		"body": {
			"device": { "name": "squares" },
			"key": { "kid": "01208…" },
			"type": "track",
			"track": {
				"basics": { "username": "cecileb" },
				"key": { "kid": "01014…" },
				"remote_proofs": [
					{
						"ctime": 1437414090,
						"remote_key_proof": {
							"check_data_json": {
								"name": "twitter",
								"username": "cecileboucheron"
							},
						},
					},
				]
			},
		},
		"prev": "9fcc8…",
		"seqno": 3,
	}
]
```

这个签名链来自一个用户，他…

1. 从名为 "squares" 的设备注册了 Keybase，该设备生成了一个 [NaCl](http://nacl.cr.yp.to/) 设备密钥
2. 证明了他们的 GitHub 账户
3. 使用 squares 添加了另一个名为 "rectangles" 的设备，它有自己的密钥
4. 使用 rectangles 关注了 [cecileb](https://keybase.io/cecileb)

你可以尝试 [在线](https://keybase.io/max/sigchain) 或通过 [API](https://keybase.io/_/api/1.0/sig/get.json?uid=dbb165b7879fe7b1174df73bed0b9500) 浏览真实的签名链。由于签名链是 **公开的**，你可以对 Keybase 上的任何用户执行此操作！

每个签名链链接都由用户的一个密钥签名，并包含序列号和前一个链接的哈希值。正因为如此，服务器无法自行创建链接或在不使整个签名链无效的情况下省略链接。我们使用 [公共 Merkle 树](/docs/server_security) 使我们难以在不被注意的情况下将签名链回滚到早期状态。

## 兄弟密钥 (Sibkeys)

一个 Keybase 账户可以拥有任意数量的兄弟密钥（称为 *sibkeys*），它们都可以签署链接。这与 PGP 不同，PGP 有一个你应该藏在防火保险箱里的"主密钥"——因为如果你弄丢了存有副本的设备，你唯一的选择就是 [撤销整个密钥并从头开始](http://www.apache.org/dev/key-transition.html)。我们在 [一篇博客文章](/blog/keybase-new-key-model) 中讨论了这个问题。

你可以通过向签名链添加链接来添加和移除兄弟密钥。由于每个链接都根据 *该点签名链上的* 账户状态进行检查，因此即使旧链接的签名密钥后来被撤销，旧链接仍然有效。撤销密钥不会影响你的身份证明、其他密钥或关注者。

## 回放 (Playback)

要查找账户的当前状态（例如，当你运行 `keybase id max` 时），客户端首先假设 Merkle 树中为该账户指定的密钥是兄弟密钥，然后逐个链接地 *回放* 签名链，跟踪有效的兄弟密钥和其他链接的影响。

*一个实现细节：由于账户可以重置，它实际上是从 `eldest_kid` 与 Merkle 树中的匹配的最近链接开始回放。*

## 链接结构

上面签名链中第一个链接的完整版本如下所示：

```json
{
	"body": {
		"device": {
			"id": "ff07c…",
			"kid": "01208…",
			"name": "squares",
			"status": 1,
			"type": "desktop"
		},
		"key": {
			"host": "keybase.io",
			"kid": "01208…",
			"uid": "e560f…",
			"username": "sidney"
		},
		"type": "eldest",
		"version": 1
	},
	"client": {
		"name": "keybase.io go client",
		"version": "1.0.0"
	},
	"ctime": 1443241228,
	"expire_in": 504576000,
	"merkle_root": {
		"ctime": 1443217312,
		"hash": "06de9…",
		"seqno": 292102
	},
	"prev": null,
	"seqno": 1,
	"tag": "signature"
}
```

某些属性是每种类型链接通用的。概述如下：

- `body` – 特定于链接类型的信息，加上一些通用属性：
  - `type` – 链接的类型
  - `device` – 关于创建链接的设备的可选详细信息
  - `key` – 关于将签署链接的密钥的信息。包含这些属性：
    - `host` – 目前始终是 "keybase.io"
    - `eldest_kid` – 此子链中元老密钥 (eldest key) 的 [KID](/docs/api/1.0/kid)。如果缺失，则假定元老密钥是签名密钥（有助于识别账户重置）
    - `kid` – 密钥的 KID
    - `key_id`: 对于 PGP 密钥，其指纹的最后八个字节（旧版）
    - `fingerprint`: 对于 PGP 密钥，其完整指纹
    - `uid`: 签名链所有者的用户 ID
