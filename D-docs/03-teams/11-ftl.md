# 快速团队加载器 (FTL)

大团队的加载速度可能很慢，主要是在带宽方面，但也包括客户端处理方面。例如，以团队 [Keybasefriends](https://keybase.io/team/keybasefriends) 为例。对该团队进行完整的 [团队链加载](/docs/teams/loader) 涉及 3M 的签名数据，以及管理员的完整签名链。例如，[chris](https://keybase.io/chris) 的签名链压缩后超过 [2.5M](https://keybase.io/_/api/1.0/sig/get.json?uid=23260c2ce19420f97b58d7d95b68ca00)。因此，在全新安装的移动设备上加载聊天体验可能会很痛苦。（在有缓存的情况下，上述大部分内容可以省略）。

幸运的是，我们在这里可以采取一个主要的捷径。为了渲染聊天窗口或 UI 中的聊天“片段”，Keybase 加密引擎只需要知道聊天的加密密钥，以及任何子团队名称的创建或更改。团队签名链中发布的许多其他信息都是无关紧要的。在快速团队加载 ([FTL](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go)) 中，客户端只从服务器 [请求](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go#L631) 那些发布团队密钥更改或子团队更改的团队签名链链接。他们检查是否形成了 [正确的链](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go#L764)，链的尾部是否在全局 Merkle 树中 [正确发布](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go#L669)，以及该链的缩略视图是否与团队的完整加载一致（通过下文描述的 [审计](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go#L827) 机制）。当用户列出或编辑团队成员资格，或者他/她的客户端轮换团队密钥时，团队的完整加载仍然照常发生。一旦客户端下载了缩略的团队链，它就会下载这些密钥的加密秘密部分，[解密](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go#L679) 密钥，并 [检查](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go#L252) 密钥是否与下载步骤中的公钥匹配。它还 [检查](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/ftl.go#L142) 子团队名称的任何创建或更改，并确保最终结果与聊天服务器声称的一致。

上述过程中缺少的是对团队管理员所做签名的任何检查。因此，在协助客户端进行快速团队加载 (FTL) 时，服务器可以对团队的签名链进行大规模替换。它可以发布一个完全不同的团队，由不同的管理员签名，或者由正确管理员的伪造版本签名，因为它知道客户端不会费心检查这些签名。但是服务器不能随意执行这种交换；它必须永远致力于此，或者分叉 Merkle 树并永远维护该分叉。

如果客户端将来对同一个团队进行缓慢加载，或者如果队友在带外发现他们丢失了更新，或者如果用户对照比特币区块链中出现的内容检查他们当前客户端的 Merkle 树视图，他们就可以当场抓住服务器的行为。

## “奇偶”攻击和团队审计

考虑通过 FTL 加速首次进入团队聊天确实提出了一种攻击的可能性，这种攻击在加载团队时总是可能的，即使是慢速方式。想象一下，两个用户 Alice 和 Bob 想要查看团队 *acme*。服务器试图向他们提供团队的不同版本 A 和 B，而不致力于全局分叉。它可能会向 Merkle 树发布以下签名链尾部：

* GlobalMerkleSequenceNumber=1000: acme=[TeamSequenceNumber=10, TeamSigchainTailHash=aa001122]
* GlobalMerkleSequenceNumber=1001: acme=[TeamSequenceNumber=10, TeamSigchainTailHash=bb445566]
* GlobalMerkleSequenceNumber=1002: acme=[TeamSequenceNumber=10, TeamSigchainTailHash=aa001122]
* GlobalMerkleSequenceNumber=1003: acme=[TeamSequenceNumber=10, TeamSigchainTailHash=bb445566]

也就是说，在偶数全局 Merkle 序列号上，为了 Alice 的利益，它将发布 *acme* 的版本 A，而在奇数序列号上，为了 Bob 的利益，它将发布版本 B。然后它可以确定只向 Alice 展示偶数 Merkle 根，向 Bob 展示奇数 Merkle 根。当然，这种攻击存在许多变体。要点是 Alice 和 Bob 看到同一个团队的不同版本，而没有树的全局分叉，通过在这个叶子节点上的“模棱两可 (equivocation)”来实现。

我们马上注意到，全局审计员可以检测到这种攻击。虽然审计员看不到 *acme* 的链，但它可以看出有些不对劲，因为 *acme* 的序列号没有变动，但链尾哈希却变了。然而，我们希望给 Alice 和 Bob 一种在线检测此类攻击的方法，而不必咨询外部审计员。

在 2.7.0 及更高版本中，Keybase 每当加载团队时（无论是通过快速路径还是慢速路径）都会运行 [“团队审计”](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go)。回想一下，加载团队的第一步是从服务器请求团队的链团队，这将产生一个三元组：

* (GlobalMerkleSequenceNumber, TeamSequenceNumber, TeamSigchainTailHash)

然后客户端请求团队链的其余部分，在慢速加载的情况下是完整链，在快速加载的情况下是缩略链。

在最后的“审计”通过中，客户端 [挑选](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go#L349) 一组随机的历史 Merkle 根，并请求从该序列号的根向下到给定团队的路径。然后它：

* [确保](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go#L396) 最近的全局 Merkle 根指向这些历史根（通过哈希链指针）；
* 验证 TeamSequenceNumbers 是 [单调递增的](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go#L291-L293)；
* 并检查 TeamSigchainTailHashes 是否 [匹配](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go#L284) 发生快速或慢速加载时从服务器下载的那些。

因为客户端控制将被查询的随机数序列，并且 Alice 和 Bob 都进行此审计，所以邪恶服务器极不可能提前猜出如何配置链的两个视图。随着 Alice 和 Bob 探测更多的快照，服务器赢得游戏的难度呈指数级增加。

每个探测大约 25k 大小，因为它包括根和尾部之间的所有中间哈希，以及从当前 Merkle 根回到历史根的指针。在移动设备上，我们 [调低](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go#L29) 探测数量以节省宝贵的带宽。在桌面上，我们 [调高](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go#L20) 参数，假设带宽更充足。审计会持续 [进行](https://github.com/keybase/client/blob/cfffb80ff83dad98ca5d2366cc73d14e6abfcb86/go/teams/audit.go#L164)，以确保之前对团队链的更新保持明确。
