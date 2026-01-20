# Keybase 现在将数据写入 Stellar 区块链

(注意，我们之前是将数据写入 *Bitcoin* 区块链，请参阅之前的文章 [Keybase 现在将数据写入比特币区块链](/docs/server/merkle-root-in-bitcoin-blockchain)。)

你在 Keybase 上所做的每一个公开声明现在都由 Keybase 进行验证签名并哈希到 Stellar 区块链中。具体来说，包括所有这些：

- 宣布你的 Keybase 用户名
- 添加公钥
- 身份证明 (twitter, github, 你的网站等)
- 公开比特币地址声明
- 公开关注声明
- 撤销操作！
- 团队操作

### 快速背景

早些时候，在 [服务器安全概述](/docs/server) 中，我们描述了 Keybase 的服务器安全方法：(1) 每个用户都有自己的签名链，随着每次声明单调增长；(2) 服务器维护一个覆盖所有签名链的全局 Merkle 树；(3) 服务器对每个新的用户签名都会签名并发布 Merkle 树的根。这种配置强烈阻止了服务器通过遗漏来撒谎，因为客户端有工具可以当场抓住服务器的行为。

有一点我们略过了。一个老练的对手 Eve 可以劫持我们的服务器并将其 *分叉 (fork)*，向 Alice 和 Bob 展示不同版本的服务器状态。只要 Eve 从不尝试将 Alice 和 Bob 的视图合并回去，并且只要他们不进行带外通信，Eve 就可以侥幸成功。(关于分叉一致性的正式处理，请参阅 [Mazières 和 Shasha](http://cs.brown.edu/courses/cs296-2/papers/sundr.pdf))。

### 进入 Stellar 区块链

感谢 Stellar，我们现在是不可分叉的。

自 2020 年 1 月 20 日起，Keybase 定期将其 Merkle 根推送到 Stellar 区块链，并由 [密钥](https://keybase.io/.well-known/stellar.toml) [GA72FQOMHYUCNEMZN7GY6OBWQTQEXYL43WPYCY2FE3T452USNQ7KSV6E](https://stellar.expert/explorer/public/account/GA72FQOMHYUCNEMZN7GY6OBWQTQEXYL43WPYCY2FE3T452USNQ7KSV6E) 签名。现在，Alice 和 Bob 可以查询区块链以找到 Keybase Merkle 树的最近根。除非 Eve 能分叉 Stellar 区块链，否则 Alice 和 Bob 将看到相同的值，并且如果 Eve 试图分叉 Keybase，他们就能抓住她。

另一种思考这个属性的方式是将其倒过来。每当 Alice 上传一个签名的声明到 Keybase 服务器时，她就会影响 Keybase 的 Merkle 树，这反过来又会影响 Stellar 区块链，而 Bob 可以观察到这一点。当 Bob 观察到 Stellar 区块链的变化时，他可以反向推导看到 Alice 的更改。Eve 几乎无法在不被发现的情况下阻碍这一过程。

### 你的意思是我的签名会影响一个主要的加密货币区块链？

是的。这是验证它的方法。我们提供了 TypeScript 的示例 [代码](https://github.com/keybase/merkle-stellar)。顶层框架如下：

```typescript
// checkUid 从 stellar 根遍历到给定的 Uid，并
// 返回用户的完整签名链。
async checkUid(uid: Uid): Promise<ChainLinkJSON[]> {
  const groveHash = await this.fetchLatestGroveHashFromStellar()
  const pathAndSigs = await this.fetchPathAndSigs(groveHash, uid)
  const treeRoots = await this.checkSigAgainstStellar(pathAndSigs, groveHash)
  const rootHash = treeRoots.body.root
  const chainTail = this.walkPathToLeaf(pathAndSigs, rootHash, uid)
  const chain = await this.fetchSigChain(chainTail, uid)
  return chain
}
```

高层步骤是：

- `fetchLatestGroveHashFromStellar` - 从 Stellar 网络的观察者处获取 Keybase 发布到 Stellar 的最后一个 `groveHash`。`groveHash` 是 Keybase 发布的几棵 Merkle 树（一个树的 "grove"）的根的哈希。与本次讨论最相关的是我们所说的 "主" 树，它包含用户和团队的更新。

- `fetchPathAndSigs` - 从 Keybase 获取与我们刚从 Stellar 获得的哈希相匹配的 grove 的签名。此外，包括从主树的根到用户叶子的路径。请注意，有问题的 grove 可能不是最新的，因为尽管 Keybase 大约每秒更新一次，但它大约每小时才向 Stellar 区块链发布一次。

- `checkSigAgainstStellar` - 打开上一次调用的签名，根据 Keybase 已知的签名密钥进行验证，并检查此签名的哈希是否与我们从 Stellar 获得的哈希匹配。

- `walkPathToLeaf` - 从上面返回的根开始，沿着路径向下走到用户的叶子，沿途检查内部节点的哈希。

- `fetchSigChain` - 用户的叶子给了我们她签名链的尾部。获取整个链以检查它是否与树中的叶子匹配。

我们可以更详细地查看这些步骤中的每一个：

#### fetchLatestGroveHashFromStellar

首先，找到 Keybase 在 Stellar 区块链中的最新插入；它始终是由密钥 [GA72...SV6E](https://stellar.expert/explorer/public/account/GA72FQOMHYUCNEMZN7GY6OBWQTQEXYL43WPYCY2FE3T452USNQ7KSV6E) 发送的最新备注 (memo)。这里的代码主要是访问 Stellar SDK，并确保在 Stellar 区块链中找到的数据符合我们的预期：

```typescript
import {Server as StellarServer} from 'stellar-sdk'
// 注意我们可以使用任何 horizon 服务器，不仅仅是
// SDF 运行的那些。
const horizonServerURI = 'https://horizon.stellar.org'
const keybaseStellarAddr = 
   'GA72FQOMHYUCNEMZN7GY6OBWQTQEXYL43WPYCY2FE3T452USNQ7KSV6E'
async fetchLatestGroveHashFromStellar(): Promise<Sha256Hash> {
  const horizonServer = new StellarServer(horizonServerURI)
  const txList = await horizonServer
    .transactions()
    .forAccount(keybaseStellarAddress)
    .order('desc')
    .call()
  if (txList.records.length == 0) {
    throw new Error('did not find any transactions')
  }
  const rec = txList.records[0]
  const ledger = await rec.ledger()
  if (rec.memo_type != 'hash') {
    throw new Error('needed a hash type of memo')
  }
  const buf = Buffer.from(rec.memo, 'base64')
  if (buf.length != 32) {
    throw new Error('need a 32-byte SHA2 hash')
  }
  return buf.toString('hex') as Sha256Hash
}
```

你会得到一些新的东西，但在 2020 年 1 月 27 日星期一 11:54 EST，输出是：

```
e22a680b245c4e6512c8212a60a5f265af465587bd70cff61e416254d6a4a062
```

Keybase 服务器不断向自己发送 1XLM，但带有一个随着 Keybase Merkle 树 grove 更新而更新的备注。

#### fetchPathAndSigs

现在在 Keybase 上进行查找，以找到与我们在 Stellar 中发现的哈希相匹配的 grove 版本（回想一下它可能不是最新的）。为了节省往返行程，服务器包含了关于我们要查找的用户的特定信息，即从树根到用户叶子的哈希路径。

```typescript
async fetchPathAndSigs(metaHash: Sha256Hash, uid: Uid): Promise<PathAndSigsJSON> {
  const params = new URLSearchParams({uid: uid})
  params.append('start_hash256', metaHash)
  const url = keybaseAPIServerURI + 'merkle/path.json?' + params.toString()
  const response = await axios.get(url)
  const ret = response.data as PathAndSigsJSON
  if (ret.status.code != 0) {
    throw new Error(`error fetching user: ${ret.status.desc}`)
  }
  return ret
}
```

#### checkSigAgainstStellar

你可以检查来自 `fetchPathAndSigs` 的 JSON 输出以发现很多好东西，但目前，我们最关心的是对 Merkle grove 计算的签名。Keybase 制作了两个这样的签名，一个用于传统的 PGP 密钥，一个用于新的 EdDSA 密钥。我们检查发布到 Stellar 的值是否是后一个签名的哈希。下面的代码有点冗余，是为了展示 `kb.verify` 在做什么：

```typescript
async checkSigAgainstStellar(
  pathAndSigs: PathAndSigsJSON,
  expectedHash: Sha256Hash
): Promise<TreeRoots> {
  // 首先检查签名的哈希是否如预期那样
  // 反映在 stellar 区块链中。
  const sig = pathAndSigs.root.sigs[keybaseRootKid].sig
  const sigDecoded = Buffer.from(sig, 'base64')
  const gotHash = sha256(sigDecoded)
  if (expectedHash != gotHash) {
    throw new Error('hash mismatch for root sig and stellar memo')
  }

  // 验证签名有效，并且是用预期的密钥签名的
  const f = promisify(kb.verify)
  const sigPayload = await f({binary: sigDecoded, kid: keybaseRootKid})

  // 接下来的 5 行不是必须的，因为它们已经在
  // kb.verify 内部执行了，但我们在这里重复它们以
  // 明确 `sig` 对象也包含了
  // 签名所针对的文本（即 grove）。
  const object = decode(buf) as KeybaseSig
  const treeRootsEncoded = Buffer.from(object.body.payload)
  if (sigPayload.compare(treeRootsEncoded) != 0) {
    throw new Error('buffer comparison failed')
  }

  // 解析并返回根签名载荷
  return JSON.parse(treeRootsEncoded.toString('ascii')) as TreeRoots
}
```

哈，匹配了！`expectedHash` 与 `gotHash` 的检查确保了我们从 Stellar 获得的根签名的哈希与 Keybase 返回给我们的相匹配。现在签名匹配了，我们可以安全地打开它，以获得我们将要下降的 merkle 树的根：


```typescript
const rootHash = treeRoots.body.root
```

#### walkPathToLeaf

现在我们有了根，我们可以下降 Merkle 树以获取相应的用户数据。服务器在对 `merkle/path` 的初始 API 调用中包含了从根到用户叶子的路径。我们在这里逐步向下，确保包含来自上一层的正确哈希。回想一下，第一步是在签名中，该签名已包含在 Stellar 区块链中：

```typescript
walkPathToLeaf(
  pathAndSigs: PathAndSigsJSON,
  expectedHash: Sha512Hash,
  uid: Uid
): Sha256Hash {
  let i = 1
  for (const step of pathAndSigs.path) {
    const prefix = uid.slice(0, i)
    const nodeValue = step.node.val
    const childrenTable = JSON.parse(nodeValue).tab
    const gotHash = sha512(Buffer.from(nodeValue, 'ascii'))

    if (gotHash != expectedHash) {
      throw new Error(`hash mismatch at prefix ${prefix}`)
    }

    // node.type == 2 意味着它是一个叶子而不是内部
    // 节点。停止行走并在这里退出
    if (step.node.type == 2) {
      const leaf = childrenTable[uid]
      // 用户签名链尾部的哈希可以在
      // 相对于 merkle 树叶子中存储的内容的 .[1][1] 处找到。
      const tailHash = leaf[1][1] as Sha256Hash
      return tailHash
    }

    expectedHash = childrenTable[prefix]
    i++
  }
  throw new Error('walked off the end of the tree')
}
```

当使用 [max](https://keybase.io/max) 的 UID 运行时，在上述时间，我们得到我发布的最后一个签名的 SHA256 哈希，即关注 [doodlemania](https://keybase.io/doodlemania)。

我们可以更进一步，从链尾的哈希开始重放整个签名链。具体细节请参见示例代码中的 `fetchSigChain` 和 `checkLink`。

### 演示

在你自己的 uid/用户名或 Keybase 目录中的任何其他人身上尝试这段代码：

```
$ npm i -g keybase-merkle-stellar
$ keybase-merkle-stellar-check max
```

然后看到如下输出：

```
✔ 1. fetch latest root from stellar: returned #27980338, closed at 2020-01-29T13:00:06Z
✔ 2. fetch keybase path from root for max: got back seqno #14406067
✔ 3. check hash equality for 070202749f229c2b6a99bac9fd8fe8a0e429dc266c2e9dff2dbc51e0fe190a09: match
✔ 4. extract UID for max: map to dbb165b7879fe7b1174df73bed0b9500 via legacy tree
✔ 5. walk path to leaf for dbb165b7879fe7b1174df73bed0b9500: tail hash is 913358757a2e1c36cb17e70b4bc51496829e97179509f854f18641d80e57637f
✔ 6. fetch sigchain from keybase for dbb165b7879fe7b1174df73bed0b9500: got back 691 links
```
