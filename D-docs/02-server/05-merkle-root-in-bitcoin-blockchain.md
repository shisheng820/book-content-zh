## Keybase 现在将数据写入比特币区块链

**弃用通知**：我们现在将数据写入 [stellar 区块链](/docs/server/stellar)。

你在 Keybase 上所做的每一个公开声明现在都由 Keybase 进行验证签名并哈希到比特币区块链中。具体来说，包括所有这些：

* 宣布你的 Keybase 用户名
* 添加公钥
* 身份证明 (twitter, github, 你的网站等)
* 公开比特币地址声明
* 公开关注声明
* 撤销操作！

### 快速背景

早些时候，在 [服务器安全概述](/docs/server) 中，我们描述了 Keybase 的服务器安全方法：(1) 每个用户都有自己的签名链，随着每次声明单调增长；(2) 服务器维护一个覆盖所有签名链的全局 Merkle 树；(3) 服务器对每个新的用户签名都会签名并发布 Merkle 树的根。这种配置强烈阻止了服务器 *通过遗漏来撒谎*，因为客户端有工具可以当场抓住服务器的行为。

有一点我们略过了。一个老练的对手 Eve 可以劫持我们的服务器并将其 *分叉 (fork)*，向 Alice 和 Bob 展示不同版本的服务器状态。只要 Eve 从不尝试将 Alice 和 Bob 的视图合并回去，并且只要他们不进行带外通信，Eve 就可以侥幸成功。(关于分叉一致性的正式处理，请参阅 [Mazières 和 Shasha](http://cs.brown.edu/courses/cs296-2/papers/sundr.pdf))。

### 进入比特币区块链

感谢比特币，我们现在是不可分叉的。

自 2014 年 6 月 16 日起，Keybase 定期将其 Merkle 根推送到比特币区块链，并由密钥 [1HUCBSJeHnkhzrVKVjaVmWg2QtZS1mdfaz](https://blockchain.info/address/1HUCBSJeHnkhzrVKVjaVmWg2QtZS1mdfaz) 签名。现在，Alice 和 Bob 可以查询区块链以找到 Keybase Merkle 树的最近根。除非 Eve 能分叉比特币区块链，否则 Alice 和 Bob 将看到相同的值，并且如果 Eve 试图分叉 Keybase，他们就能抓住她。

另一种思考这个属性的方式是将其倒过来。每当 Alice 上传一个签名的声明到 Keybase 服务器时，她就会影响 Keybase 的 Merkle 树，这反过来又会影响比特币区块链，而 Bob 可以观察到这一点。当 Bob 观察到比特币区块链的变化时，他可以反向推导看到 Alice 的更改。Eve 几乎无法在不被发现的情况下阻碍这一过程。


### 你的意思是我的签名会影响比特币区块链？

是的。这是验证它的方法。我们提供了 Python 和 [IcedCoffeeScript](http://maxtaco.github.io/coffee-script/) 的示例代码 - 这些应该可以直接在你的 REPL 中运行，所以请继续，启动 python 或 iced，并开始尝试。

首先，找到 Keybase 在比特币区块链中的最新插入；它始终是 [1HUCBSJeHnkhzrVKVjaVmWg2QtZS1mdfaz](https://blockchain.info/address/1HUCBSJeHnkhzrVKVjaVmWg2QtZS1mdfaz) 的最新支出：

Python:
```python
from   urllib2 import urlopen
import json
from_addr = "1HUCBSJeHnkhzrVKVjaVmWg2QtZS1mdfaz"
uri       = "https://blockchain.info/address/%s?format=json" % (from_addr)
to_addr   = json.load(urlopen(uri))['txs'][0]['out'][0]['addr']
```

或者 IcedCoffeeScript: 
```coffeescript
request = require 'request'
addr    = "1HUCBSJeHnkhzrVKVjaVmWg2QtZS1mdfaz"
uri     = "https://blockchain.info/address/#{addr}?format=json"
await request {uri : uri, json : true }, defer err, res, json
to_addr = json.txs[0].out[0].addr
```

你会得到一些新的东西，但在 2014 年 7 月 14 日星期一 11:33 EST，输出是：

```
168bJepnpoZkoW5AWE7TxNhvuNPmsNmyvS
```

Keybase 服务器向该地址发送了少量的比特币，打算永远不收回它，而是使用该地址的 160 位来捕获其 Merkle 根的哈希值。使用标准的比特币数学将此地址转换为十六进制编码的哈希值：

```python
from pycoin.encoding import bitcoin_address_to_hash160_sec, hash160
from binascii import hexlify
to_addr_hash = hexlify(bitcoin_address_to_hash160_sec(to_addr))
print to_addr_hash
```

```coffeescript
btcjs = require 'keybase-bitcoinjs-lib' # 普通的 'bitcoinjs-lib' 也可以
to_addr_hash = btcjs.Address.fromBase58Check(to_addr).hash.toString('hex')
console.log to_addr_hash
```

输出：`38482d2daf98ee6c04b2e2fd32981de6e78a3b60`

现在在 Keybase 上进行查找以找到与该哈希匹配的根块：

```python
kb        = "https://keybase.io/_/api/1.0"
uri       = "%s/merkle/root.json?hash160=%s" % (kb, to_addr_hash)
root_desc = json.load(urlopen(uri))
print root_desc
```

```coffeescript
kb  = "https://keybase.io/_/api/1.0"
uri = "#{kb}/merkle/root.json?hash160=#{to_addr_hash}"
await request { uri : uri, json : true }, defer err, res, root_desc
console.log root_desc
```

你可以检查这个 JSON 输出以发现很多好东西，但实际上我们关心的是 `sig` 字段，它包含根块哈希的签名，并且此签名的哈希应与我们在比特币区块链中找到的值匹配：


```
import re
from base64 import b64decode
keybase_kid = '010159baae6c7d43c66adf8fb7bb2b8b4cbe408c062cfc369e693ccb18f85631dbcd0a'
sig = b64decode(re.compile(r"\n\n((\S|\n)*?)\n=").search(root_desc['sigs'][keybase_kid]['sig']).group(1))
assert (to_addr_hash == hexlify(hash160(sig)))
```

```coffeescript
assert = require 'assert'
keybase_kid = '010159baae6c7d43c66adf8fb7bb2b8b4cbe408c062cfc369e693ccb18f85631dbcd0a'
sig = Buffer.from root_desc.sigs[keybase_kid].sig.match(/\n\n([\na-zA-Z0-9\/\+=]*?)\n=/)[1], 'base64'
assert.equal hash, btcjs.crypto.hash160(sig).toString('hex')
```
  
哈，匹配了！你可能会问，那些正则代码是干什么的。签名字段本身是一个标准的 PGP 签名，带有熟悉的 `---- BEGIN PGP ----` 框架、注释字段和校验和。正则表达式剥去表皮，只留下肉。

我们目前使用 [PGP 密钥](/docs/api/1.0/kid) [010159baae6c7d...](/docs/server_security/our_merkle_key) 来签署我们的承诺，但计划在未来过渡到 EdDSA 密钥。我们将把这些签名发布在 `sigs` 对象的不同键下，对应于该新密钥的 KID。

现在我们已经验证了此签名的哈希已写入区块链，我们可以通过 `gpg` 验证签名，或者尝试一些快速而粗略的方法来剥离签名的有效载荷数据。对于此演示，后者就足够了。如下提取根块的哈希：

```python
root_hash = re.compile(r"\"root\":\"([a-f0-9]{128})\"").search(sig).group(1)
```

```coffeescript
root_hash = sig.toString("utf8").match(/"root":"([a-f0-9]{128})"/)[1]
```

现在我们有了根，我们可以下降 Merkle 树以获取相应的用户数据。让我们查找我的数据，但请随意尝试你自己的：

```python
username = "max"
uri      = "%s/user/lookup.json?username=%s" % (kb, username)
uid      = json.load(urlopen(uri))['them']['id']
print uid
```

```coffeescript
username = "max"
uri      = "#{kb}/user/lookup.json?username=#{username}"
await request { uri : uri, json : true }, defer err, res, json
uid      = json.them.id
```

下降 Merkle 树的工作原理如下。首先，查找对应于根哈希的实际根块：

```python
uri = "%s/merkle/block.json?hash=%s" % (kb, root_hash)
value_string = json.load(urlopen(uri))['value_string']
```

```coffeescript
uri = "#{kb}/merkle/block.json?hash=#{root_hash}"
await request { uri : uri, json : true }, defer err, res, json
```

接下来，检查服务器关于块内容是否撒谎：
```python
from hashlib import sha512, sha256
computed_hash = hexlify(sha512(value_string).digest())
assert(computed_hash == root_hash)
```

```coffeescript
{createHash} = require 'crypto'
computed_hash = createHash('sha512').update(json.value_string).digest('hex')
assert.equal computed_hash, root_hash
```

然后沿着从树根到我叶子的路径向下走。
第一个节点用我 UID 的第一个十六进制字符索引；
下一个节点用我 UID 的前两个十六进制字符索引；
依此类推，直到我们到达一个叶子节点：

```python
for i in range(1,len(uid)):
    tab = json.loads(value_string)['tab']
    prefix = uid[0:i]
    nxt = tab.get(prefix)
    if nxt == None:
      break
    uri = "%s/merkle/block.json?hash=%s" % (kb, nxt)
    value_string = json.load(urlopen(uri))['value_string']
my_triple = tab[uid][1]
```

```coffeescript
for i in [1...uid.length]
    tab = JSON.parse(json.value_string).tab
    prefix = uid[0...i]
    nxt = tab[prefix]
    break unless nxt?
    uri  = "#{kb}/merkle/block.json?hash=#{nxt}"
    await request { uri : uri, json : true }, defer err, res, json
my_triple = tab[uid][1]
```

此时，我们可以再次使用与上述相同的技术检查服务器是否在 Merkle 树中的这个块上对我们撒谎。在我们这样做之后，我们就到了树的叶子，可以跳转到我的记录：

```python
link_hash = my_triple[1]
```

```coffeescript
link_hash = my_triple[1]
```

三元组包含：(0) 我签名链的长度；(1) 我签名的最后一个事物的哈希；(2) 我签名的最后一个事物的签名的哈希。

我们快到了！现在让我们获取我的整个签名链，跳转到最后一个链接，检查它是否与我们上面得到的哈希匹配，并将其转储出来（漂亮打印）

```python
uri           = "%s/sig/get.json?uid=%s" % (kb, uid)
payload       = json.load(urlopen(uri))['sigs'][-1]['payload_json']
computed_hash = hexlify(sha256(payload).digest())
assert(computed_hash == link_hash)
print json.dumps(json.loads(payload), indent=4)
```

```coffeescript
uri = "#{kb}/sig/get.json?uid=#{uid}"
await request { uri : uri, json : true }, defer err, res, json
payload_json = json.sigs[-1...][0].payload_json
computed_hash = createHash('sha256').update(payload_json).digest('hex')
assert.equal computed_hash, link_hash
console.log JSON.stringify(JSON.parse(payload_json), null, 4)
```

在我的例子中，我签名的最后一件事是我的 Facebook 证明的声明。
总之，该声明被哈希到我的签名链中，签名链被哈希到 Keybase 的 Merkle 树中，最终被注入比特币区块链，直到永远。这是一个强有力的保证。
