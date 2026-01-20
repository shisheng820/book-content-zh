# 命令行 (Command Line)

本页面仅作示例。[下载](https://keybase.io/download) Keybase 应用并使用内置帮助：

```bash
keybase help        # 通用帮助
keybase help follow # 关于关注他人的帮助
keybase help pgp    # 关于在 Keybase 中使用 PGP 密钥的帮助
keybase help prove  # 关于证明的帮助
                    # 等等
```

#### 常用命令

```bash
keybase version              # 打印版本号
keybase help                 # 获取帮助
keybase signup               # 如果你从未使用过 Keybase
keybase login                # 或者...如果你已经有一个账户
keybase prove twitter        # 证明你拥有某个 twitter 账户
keybase prove github         # 证明某个 github 账户
keybase prove reddit         # 证明某个 reddit 账户
keybase prove facebook       # 证明某个 facebook 账户
keybase prove hackernews     # 证明某个 HN 账户
keybase prove https you.com  # 证明某个网站
keybase prove http you.com   # 如果你没有合法的证书
keybase prove dns you.com    # 通过 DNS 条目证明
                             # ...更多证明类型即将推出...
```


#### 查找其他人 & 关注

```bash
keybase id max                     # 查找 "max"，验证身份
keybase id maxtaco@twitter         # 查找 twitter 上的 maxtaco
keybase follow max                 # 公开追踪 max 的身份
keybase follow maxtaco@reddit      # 关注一个 reddit 用户
```

#### 为什么要关注？(以前称为 "tracking" 追踪)

如果你关注了某人，后续命令将可以直接工作，无需你提供更多输入：

```bash
keybase encrypt maria -m "this is a secret"
# 成功！不再询问
```

而且，如果你上次关注他们之后，目标的任何信息发生了变化，你会收到一个有意义的错误提示。


#### 设备添加 + 移除

你在每台计算机上安装 Keybase 时，都会获得一个设备特定的密钥。这是对旧 PGP 模型的巨大改进，旧模型中你必须到处移动私钥。

```bash
keybase device list        # 列出你所有的设备 + 纸质密钥
keybase device remove [ID] # 撤销设备 ID (在设备列表中找到)
keybase device add         # 配置新设备
```

#### 纸质密钥 (Paper keys)

当你首次安装 Keybase 时，会被要求生成一个纸质密钥。它是一个全功能的密钥，就像设备密钥一样。

你可以拥有任意数量的纸质密钥。

```bash
keybase paperkey    # 制作一个新的纸质密钥
keybase device list # 查看你的纸质密钥
```

如果你丢失了纸质密钥，只需像移除其他设备一样将其移除即可。

#### 加密命令

通常：

  - `-m` 表示消息 (相对于 stdin 或输入文件)
  - `-i` 表示输入文件
  - `-o` 表示输出文件
  - `-b` 表示二进制输出，相对于 ASCII

```
# 给定 keybase 用户 "max"
keybase encrypt max -m "this is a secret"
echo "this is a secret" | keybase encrypt max
keybase encrypt max -i secret.txt
keybase encrypt max -i secret.mp3 -b -o secret.mp3.encrypted
```

#### 为 Keybase 用户加密

```bash
keybase encrypt max -m "this is a secret for max"
echo "secret" | keybase encrypt max
echo "secret" | keybase encrypt maxtaco@twitter
keybase encrypt max -i ~/movie.avi -o ~/movie.avi.encrypted
```

#### 解密

```bash
keybase decrypt -i movie.avi.encrypted -o movie.avi
keybase decrypt -i some_secret.txt
cat some_secret.txt.encrypted | keybase decrypt
```

#### 签名

```bash
keybase sign -m "I hereby abdicate the throne"
keybase sign -i foo.exe -b -o foo.exe.signed
```

#### 验证

```bash
cat some_signed_statement.txt | keybase verify
keybase verify -i foo.exe.signed -o foo.exe
```

#### 加密 PGP 消息

如果 Keybase 用户只有一个 PGP 密钥，或者你更愿意为此加密：

```bash
keybase pgp encrypt chris -m "secret"            # 加密
keybase pgp encrypt maxtaco@twitter -m "secret"  # 使用 twitter 名称
keybase pgp encrypt maxtaco@reddit -m "secret"   # 使用 Reddit 名称
keybase pgp encrypt chris -s -m "secret"         # 同时使用 -s 签名
keybase pgp encrypt chris -i foo.txt             # foo.txt -> foo.txt.asc
keybase pgp encrypt chris -i foo.txt -o bar.asc  # foo.txt -> bar.asc
echo 'secret' | keybase pgp encrypt chris        # 流式加密
```

#### 解密 PGP 消息

```bash
keybase pgp decrypt -i foo.txt.asc             # foo.txt.asc -> stdout
keybase pgp decrypt -i foo.txt.asc -o foo.txt  # foo.txt.asc -> foo.txt
cat foo.txt.asc | keybase pgp decrypt          # 解密流
```

#### 签名 PGP 消息

```bash
keybase pgp sign -m "Hello"                # 签名一条消息
keybase pgp sign --clearsign -m "Hello"    # 签名，但不编码内容
keybase pgp sign -i foo.txt --detached     # 生成 foo.txt.asc，仅包含签名
keybase pgp sign -i foo.txt                # 生成 foo.txt.asc，包含已签名的 foo.txt
echo "I rock." | keybase pgp sign          # 流式签名
```

#### 验证 PGP 消息

```bash
keybase pgp verify -i foo.txt.asc            # 验证自签名文件
keybase pgp verify -d foo.txt.asc -i foo.txt # 验证文件 + 分离的签名
cat foo.txt.asc | keybase pgp verify         # 流式验证自签名文件
```

#### 发布比特币地址

```bash
keybase btc 1p90X3byTONYhortonETC  # 签名并设置比特币地址
                                   # 到你的个人资料
```

#### 断言 (对脚本、cron 作业等有用)


```bash
# 这里我们为 maria 加密一份备份副本，
# 断言她已经在 twitter 和 github 上证明了她的密钥。
# 两者都必须通过。
#
# 如果我们要关注 maria，这是不必要的，
# 因为如果她的身份有任何损坏，命令将会失败。
cat some_backup.sql | keybase pgp encrypt -o enc_backup.asc \
  maria_2354@twitter+maria_booyeah@github+maria@keybase
```

#### 更多示例即将推出

使用 `keybase help` 了解可用的功能。


## Tor 支持

Keybase 命令行客户端支持 Tor。当然，匿名性是一个充满风险且微妙的属性。本文档解释了如何使用 Tor 和其他 Keybase 功能来保护你的身份。

**请注意，Keybase GUI 不支持 Tor 模式。**

如果你想通过 Tor 隧道传输整个应用程序，我们要建议在 [Tails VM](https://tails.boum.org) 中运行它。此外，我们的 Tor 支持未经审计，因此即使在严格模式下，也有可能潜入一些识别信息。

###先决条件

要使用带 Tor 的命令行客户端，你需要在本地运行 Tor SOCKS 代理。有关如何设置本地 Tor 代理的更多信息，请参阅 [Tor 项目文档](https://www.torproject.org/docs/installguide.html.en)。

### 启用 Tor 模式

如果你已经在后台运行 `keybase service`，简单地在命令中添加 `--tor-mode` 将不起作用——对于除 `service` 之外的命令，该标志仅在服务尚未运行时才有效，因此你必须使用以下任一方法：

#### 临时通过使用显式设置的标志运行服务

如果你只想在单个会话中以 Tor 模式使用 Keybase，请先运行 `keybase ctl stop` 关闭后台运行的服务，然后运行 `keybase --tor-mode=leaky|strict service`。当此服务运行时，其他终端中的所有 `keybase` 命令都将通过 Tor 网络访问我们的服务器。

**请注意，此时启动 Keybase GUI 将关闭该服务并以默认模式重新启动它。**

#### 永久通过更改服务的配置

```bash
# "leaky" (泄漏) 模式，简单地通过 Tor 隧道传输所有流量
keybase config set tor.mode leaky
# "strict" (严格) 模式，使请求完全匿名
keybase config set tor.mode strict

# 重启服务，确保 GUI 未运行
```

### 简短演示

要使用默认选项启用 Tor，只需将 Tor 模式标志设置为 `leaky`：

```bash
# 使用上述任一方法启用 leaky tor 模式
keybase id malgorithms@twitter
```

你会得到如下输出：

```markdown
▶ INFO Identifying chris
✔ public key fingerprint: 94AA 3A5B DBD4 0EA5 49CA BAF9 FBC0 7D6A 9701 6CB3
✔ "malgorithms" on twitter: https://twitter.com/malgorithms/status/433640580220874754
✔ "malgorithms" on github: https://gist.github.com/2d5bed094c6429c63f21
✔ admin of chriscoyne.com via HTTPS: https://chriscoyne.com/keybase.txt
✔ "malgorithms" on hackernews: https://news.ycombinator.com/user?id=malgorithms
✔ admin of DNS zone chriscoyne.com, but the result isn't reliable over Tor: found TXT entry keybase-site-verification=2_UwxonS869gxbETQdXrKtIpmV1u8539FmGWLQiKdew
```

所有网络流量现在都通过 Tor 保护，因此服务器或网络窃听者无法识别你的 IP 地址，但服务器仍然可以看到你的登录凭据。这种操作模式类似于 [Tor 匿名模式(3)](https://trac.torproject.org/projects/tor/wiki/doc/TorifyHOWTO#mode3:userwithnoanonymityusingToranyrecipient)。它不能保护你免受 Keybase 服务器泄露的影响，但可以防止你的 ISP（或任何其他恶意网络窥探者）知道你在使用 Keybase。

请注意，在上述尝试识别 `@malgorithms` 的过程中，并非所有内容都是可信的。Keybase CLI 打印出 `chriscoyne.com` 的 DNS 记录不可信，因为 DNS 和裸 HTTP 在 Tor 上本来就是不可靠的；中继节点可以捏造任何内容，恶意节点可以伪造证明。

### Strict (严格) 模式

**严格模式目前已损坏，我们正在修复。**

如果你想要更高级别的隐私，你可以要求 *strict* (严格) Tor 模式，这将向服务器隐瞒所有用户识别信息，类似于 [Tor 匿名模式(1)](https://trac.torproject.org/projects/tor/wiki/doc/TorifyHOWTO#mode1:useranonymousanyrecipient)。例如，试试这个：

```bash
# 使用上述任一方法启用 strict tor 模式
keybase follow malgorithms@twitter
```

你会得到如下输出：

```markdown
warn: In Tor mode: strict=true; proxy=localhost:9050
warn: Tor support is in alpha; please be careful and report any issues
warn: Tor strict mode: not syncing your profile with the server
info: ...checking identity proofs
✔ public key fingerprint: 20AA 7564 29A0 B9B9 5974 3F72 E1E4 B2A1 286B A323
✔ "btcdrak" on twitter: https://twitter.com/btcdrak/status/513395408845148160
✔ "btcdrak" on github: https://gist.github.com/e4435571fe4c7d55231b
✔ "btcdrak" on reddit: https://www.reddit.com/r/KeybaseProofs/comments/2gyyej/my_keybase_proof_redditbtcdrak_keybasebtcdrak/
Is this the btcdrak you wanted? [y/N] y
warn: Can't write tracking statement to server in strict Tor mode
info: ✔ Wrote tracking info to local database
info: Success!
```

注意发生了一些新事情。在输出的第三行，有一个警告，即客户端跳过了将其本地视图与服务器同步。如果它这样做了，分析服务器流量的人可能会正确猜出，紧接着查找 Alice 之后查找 Bob 意味着 Alice 正在关注或识别 Bob。所以 Alice 的查找被抑制了。还要注意，客户端不提供向服务器写入关注者声明，这也会泄露用户的身份。相反，它只是满足于将关注信息写入本地存储。

有些命令在严格模式下根本无法工作。例如，如果你尝试重新登录：

```bash
keybase logout
keybase login
```

你会得到：

```markdown
▶ WARNING Failed to load advisory secret store options from remote: We can't send out PII in Tor-Strict mode; but it's needed for this operation
▶ ERROR Login required: login failed after passphrase verified
```

### Web 支持

作为 Tor 支持的一部分，我们还将 `https://keybase.io` 作为隐藏地址公开；这比标准的匿名 Tor 浏览略有改进，因为你的流量不需要经过出口节点。我们的隐藏地址是：

```
http://keybase5wmilwokqirssclfnsqrjdsi7jdir5wy7y7iu3tanwmtp6oid.onion
```

请注意，命令行客户端默认在内部使用此隐藏地址。
