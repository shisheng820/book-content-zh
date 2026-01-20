{% set section_title = "命令行" %}

# 命令行

本页面仅作为示例。[下载](https://keybase.io/download) Keybase 应用并使用内置帮助：

```bash
keybase help        # 常规帮助
keybase help follow # 关注他人的帮助
keybase help pgp    # 在 Keybase 中使用 PGP 密钥的帮助
keybase help prove  # 证明的帮助
                    # 等等
```

### 常用命令

```bash
keybase version              # 打印版本号
keybase help                 # 获取帮助
keybase signup               # 如果你从未使用过 Keybase
keybase login                # 或者...如果你已有账户
keybase prove twitter        # 证明你拥有一个 twitter 账户
keybase prove github         # 证明一个 github 账户
keybase prove reddit         # 证明一个 reddit 账户
keybase prove facebook       # 证明一个 facebook 账户
keybase prove hackernews     # 证明一个 HN 账户
keybase prove https you.com  # 证明一个网站
keybase prove http you.com   # 如果你没有合法的证书
keybase prove dns you.com    # 通过 DNS 条目证明
                             # ...更多证明类型即将推出...
```


### 查找他人及关注

```bash
keybase search max                 # 查找像 "max" 这样的用户
keybase id max                     # 查找 "max"，验证身份
keybase id maxtaco@twitter         # 查找 twitter 上的 maxtaco
keybase follow max                 # 公开追踪 max 的身份
keybase follow maxtaco@reddit      # 关注一个 reddit 用户
```

### 为什么要关注？（以前称为“追踪”）

如果你关注了某人，后续命令将无需你提供更多输入即可工作：

```bash
keybase encrypt maria -m "this is a secret"
# 成功！不再询问问题
```

而且，如果你上次关注他们之后，目标的任何信息发生了变化，你会收到一个有意义的错误提示。


### 添加及移除设备

你在每台计算机上安装 Keybase 时，都会获得一个设备专用的密钥。这是对旧 PGP 模型的一个巨大改进，旧模型中你必须到处移动私钥。

```bash
keybase device list        # 列出你所有的设备 + 纸质密钥
keybase device remove [ID] # 撤销设备 ID（在设备列表中找到）
keybase device add         # 配置新设备
```

### 纸质密钥

当你首次安装 Keybase 时，会被要求生成一个纸质密钥。它是一个全功能的密钥，就像设备密钥一样。

你可以拥有任意数量的纸质密钥。在 Keybase 发布移动应用之前，你应该至少保留 1 个。

```bash
keybase paperkey    # 制作一个新的纸质密钥
keybase device list # 查看你的纸质密钥
```

如果你丢失了纸质密钥，只需像移除其他设备一样将其移除即可。

### 加密命令

通常：

  - `-m` 表示消息（相对于标准输入或输入文件）
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

### 为 Keybase 用户加密

```bash
keybase encrypt max -m "this is a secret for max"
echo "secret" | keybase encrypt max
echo "secret" | keybase encrypt maxtaco@twitter
keybase encrypt max -i ~/movie.avi -o ~/movie.avi.encrypted
```

### 解密

```bash
keybase decrypt -i movie.avi.encrypted -o movie.avi
keybase decrypt -i some_secret.txt
cat some_secret.txt.encrypted | keybase decrypt
```

### 签名

```bash
keybase sign -m "I hereby abdicate the throne"
keybase sign -i foo.exe -b -o foo.exe.signed
```

### 验证

```bash
cat some_signed_statement.txt | keybase verify
keybase verify -i foo.exe.signed -o foo.exe
```

### 加密 PGP 消息

如果 Keybase 用户只有 PGP 密钥，或者你更愿意为此加密：

```bash
keybase pgp encrypt chris -m "secret"            # 加密
keybase pgp encrypt maxtaco@twitter -m "secret"  # 使用 twitter 名称
keybase pgp encrypt maxtaco@reddit -m "secret"   # 使用 Reddit 名称
keybase pgp encrypt chris -s -m "secret"         # 同时使用 -s 签名
keybase pgp encrypt chris -i foo.txt             # foo.txt -> foo.txt.asc
keybase pgp encrypt chris -i foo.txt -o bar.asc  # foo.txt -> bar.asc
echo 'secret' | keybase pgp encrypt chris        # 流
```

### 解密 PGP 消息

```bash
keybase pgp decrypt -i foo.txt.asc             # foo.txt.asc -> stdout
keybase pgp decrypt -i foo.txt.asc -o foo.txt  # foo.txt.asc -> foo.txt
cat foo.txt.asc | keybase pgp decrypt          # 解密流
```

### 签名 PGP 消息

```bash
keybase pgp sign -m "Hello"                # 签名消息
keybase pgp sign --clearsign -m "Hello"    # 签名，但不编码内容
keybase pgp sign -i foo.txt --detached     # 生成 foo.txt.asc，仅签名
keybase pgp sign -i foo.txt                # 生成 foo.txt.asc，包含签名的 foo.txt
echo "I rock." | keybase pgp sign          # 流
```

### 验证 PGP 消息

```bash
keybase pgp verify -i foo.txt.asc            # 验证自签名文件
keybase pgp verify -d foo.txt.asc -i foo.txt # 验证文件 + 分离的签名
cat foo.txt.asc | keybase pgp verify         # 流式验证自签名文件
```

### 发布比特币地址

```
keybase btc 1p90X3byTONYhortonETC  # 签名并设置比特币
                                   # 地址到你的个人资料
```

{#
TODO:
</md>
<pre class="code code-highlighted">keybase btc 1p90X3byTONYhortonETC  <span class="hljs-comment"># 签名并设置比特币</span>
                                   <span class="hljs-comment"># 地址到你的个人资料</span>
</pre>
<md>
#}

### 断言（适用于脚本、cron 任务等）


```
# 这里我们为 maria 加密一份备份副本，
# 断言她已经在 twitter 和 github 上证明了她的密钥。
# 两者都必须通过。
#
# 如果我们已经关注了 maria，这是不必要的，因为
# 如果她的身份有任何问题，命令将会失败。
cat some_backup.sql | keybase pgp encrypt -o enc_backup.asc \
  maria_2354@twitter+maria_booyeah@github+maria@keybase
```

### 更多示例即将推出

使用 `keybase help` 了解可用功能。

{# Teams #}

{#
<style>
.gs-img {
  text-align:center;
  margin:40px 0;
}
#page-teams-alpha ul li {
  margin-bottom:10px;
}
#page-teams-alpha h3 {
  margin-top:50px;
}
</style>

<div id="page-teams-alpha">

      <md>
#}

## Keybase 团队


### 它是什么？

Keybase 团队是一组*命名的*人群，具有灵活的成员资格。如果你在一个名为 Acme 的项目上工作，你可以在 Keybase 上注册团队名称 `acme`。这个团队名称是*全局唯一*的；给定名称的 Keybase 团队只能有一个。

团队的加密文件可以在 `/keybase/team` 中找到：

![](https://keybase.io/images/teams/team_kbfs.png)

团队可以拥有聊天频道，有点像 Slack。但与 Slack 不同的是，Keybase 聊天是端到端加密的，并且你团队的管理员通过加密方式控制谁在团队中。

每个团队都有一个默认的 `#general` 聊天频道，但你可以创建更多。

在这个早期 alpha 阶段，团队管理完全通过命令行完成。如果你没问题，请继续阅读。

### 命令行简要说明：
```bash
# 创建团队
# -----------

> keybase team create dingbatz

# 查看你所在的团队
# ------------------------

> keybase team list-memberships
Team            Role      Username    Full name
keybase         owner     chris       Chris Coyne
dingbatz        owner     chris       Chris Coyne

# 添加一些人
# ---------------------------------------------

> keybase team add-member dingbatz --user max     --role=admin
> keybase team add-member dingbatz --user crudder --role=writer
> keybase team list-memberships dingbatz

# 端到端加密的 KBFS 文件夹
# ---------------------------------
> mv ~/Dropbox/Manifesto.pdf .

# 还有聊天！
# --------------------------------------------

> keybase chat send dingbatz "hello to my pals"

```

### 在图形界面中

我实际上运行了上面的命令，所以现在我在我的 UI 中看到了 "dingbatz #general" 聊天频道。Max 和 crudder 也看到了，因为我添加了他们。我们可以在 KBFS 中共享文件，并且我们可以聊天。如果我向团队添加其他人，他们也将获得访问文件和聊天记录的权限，因为我们会为他们重新加密密钥。

在即将发布的版本中，它会更漂亮，但现在团队聊天看起来像一个没有头像的普通聊天，并且前缀是那个丑陋的 `#general`。这是一个 MVP（最小可行产品），所以请多包涵。

![](https://keybase.io/images/teams/dingbatz.png)

### 临时团队和大型组织

我们要支持临时讨论（例如，pokerpals）和大型组织（例如，nytimes）。

为了服务更大的群体：

 * 应用中很快会有一个团队标签页，用于进行更复杂的管理
 * 我们已经内置了子团队支持。例如，`atlassian.usa.marketing` 或 `nytimes.devops`。

在接下来的 4-8 周内，所有管理都在 CLI 中进行。


### 最重要的命令

```bash
keybase team help
```

### 创建聊天频道

在我们 alpha 的最初几天，创建除 `#general` 以外的聊天频道有点烦人。你必须通过从 CLI 发送消息来启动它：

```bash
keybase chat send --channel '#hr-issues' uber "let's do this"
```

之后，你的团队可以在 GUI 中使用它——包括桌面和手机应用。任何想加入频道的人（目前）都可以通过命令行加入。

```bash
# 加入频道
keybase chat join-channel fyre '#festival2018'

# 或列出频道
keybase chat list-channels acme
```

哦，还有，@提及团队成员会将他们拉进来...所以最简单的做法就是创建一个频道，自己加入，然后在 GUI 中 ping 某人。

任何团队成员都可以加入聊天频道。例如，如果你有一个 `acme #design` 频道，`acme` 中的任何人都可以加入并阅读它。

如果你想在加密层面隔离聊天，这就是子团队的用途。详情见下文。


### 子团队

我们已经实现了子团队！例如，如果你是 `nike` 的所有者，你可以让顶层团队保持相当空闲，并将你的公司分为 `nike.usa` 和 `nike.marketing`，甚至更深层的团队，如 `nike.web.engineering.interns2017`。如果你与 Apple 建立了合作伙伴关系，你可以创建 `nike.apple_partnership`，并将一些在 Apple 工作的人放入该子团队。

```bash
# 假设你是 nike 的管理员
keybase team create nike.board
```

你组织中的每个子团队都有自己的聊天频道。因此，要与你的董事会进行加密讨论，你可以创建子团队 `acme.board`。在这个团队中，你可以为董事会讨论的内容创建聊天频道，如 `#plausible-deniability`（推诿责任）和 `#efficient-breach`（有效违约）。

`acme` 的成员不会知道有一个名为 `acme.board` 的子团队，除非他们是 `acme` 的管理员或被邀请加入 `acme.board`。

更多细节：

* 要创建子团队，你必须是其父团队的管理员
* 父团队管理员对子团队拥有某些管理控制权，即使他们不加入该团队。这可以防止丢失、孤立的子团队。如果你是 `acme` 的管理员并创建了 `acme.interns` 但不加入它，你将看不到它的聊天或文件；即使你拥有该组的加密密钥，服务器也会拒绝向你提供加密数据，除非你显式地将自己签入该团队，这会让所有成员都知道。
* 子团队成员不需要是父团队成员。所以 `acme.interns` 不需要是 `acme` 的成员。
* 团队成员无法知道他们未加入的子团队的名称或成员资格。低级的 `nike.interns` 无法看到 `nike.sweatshop`。
* 兄弟团队的成员无法看到彼此的名称或成员资格。
* 子团队的成员*可以*知道父团队的成员资格。
* 子团队可以重命名，不像根团队名称。



### 申请加入团队

你可以申请团队访问权限：

```bash
> keybase team request-access acme
```

作为局外人，你无法知道谁在团队中，所以 Keybase 会联系管理员并告知你已申请访问。他们可以添加你或忽略该请求。

### 通过社交媒体账号批准

最终，管理员是将 Keybase 用户的用户名 + 密钥链签入团队。持续的团队成员资格不需要维护特定的社交证明，因此如果管理员关心社交证明，他们应该在签入某人时进行检查。

尽管如此，有一种协议可以通过其他已证明的身份进行批准：

```bash
keybase team add-member --role writer --user acmeceo@twitter acme
```

1. 这在团队签名链中签署了一个管理员声明（对自己和其他管理员），说：“嘿，如果 twitter 上的 @acmeceo 证明了他们的账户，就把那个用户签入我们的团队。”

2. 管理员的客户端将遵守该管理员签署的链接并执行操作。

需要明确的是，该用户不需要无限期地维护 twitter 账户；如果 Twitter 宕机或他们放弃了该账户，他们不会被踢出团队。

### TOFU 体验：通过电子邮件快速建立团队

以下是一个常见的愿望，所以我们实现了它：

```bash
keybase team add-member --role writer --email wonderwoman@acme.com acme
```

当你运行此命令时会发生什么：

1. 你签署一份管理员声明，表示你想让 wonderwoman@acme.com 加入团队
2. **Keybase 服务器** 让 wonderwoman@acme.com 加入并建立用户名
3. 下一个上线的管理员会收到 ping，自动将她签入团队，信任 Keybase 检查了电子邮件。

这是“首次使用信任”（TOFU），因为你信任 Keybase 没有对电子邮件证明撒谎...就像你使用 Signal 或 WhatsApp 通过电话号码查找密钥时看到的 TOFU 一样。

一旦 wonderwoman 加入团队，她的身份就无法被替换。此外，随着她添加更多设备，你不必再次经历 TOFU，这不像人们在某些聊天应用中擦除/安装手机时那样。（那真的不是 TOFU，对吧？）

Keybase 无法滥用此功能向你的团队插入额外人员。它只有在你通过发布已签名的声明开始该过程，并且你团队的管理员验证已签名的声明时才有效，因为该声明在第 3 步中被检查。如果你改变主意，可以通过加密方式撤销邀请。

管理员权限不能通过 TOFU 授予。

### 了解角色

我们将很快把它移到一个表格中。这是一张电子表格的截图：

![](https://keybase.io/images/teams/roles.png)

在上面，子团队的“隐含管理员”是指父团队的管理员。

### 元数据

Keybase 服务器确实知道团队成员资格：团队名称、用户和角色。Keybase 服务器*无法*读取聊天或文件的内容，甚至不知道聊天频道或文件的名称，因为那是端到端加密的。**在任何时候，Keybase 都没有任何 KBFS 或聊天数据的私钥。**

### 关于团队签名链的不可变性

对团队的任何更改都会签名到链中，引用团队上次更改的哈希值。这个链本身挂在一个 Merkle 树上，可以确定性地找到它。如果你是 `acme` 的成员，你可以遍历树找到该链。这意味着你将看到与其他 acme 用户完全相同的 `acme` 链。[我们甚至将 Merkle 树的根写入比特币区块链](https://keybase.io/docs/server_security/merkle_root_in_bitcoin_blockchain)。

这是为了让你可以说或打字：“嘿 - 我们在 Keybase 上有一个叫 'lollipops' 的团队。加入 Keybase 并申请访问。” 或者 “期待来自团队 dunkindonuts 的邀请...那就是我。” 我们相信这种没有人指纹或代码的人类交流至关重要。拒绝你需要比较的十六进制字符串或 60 位数字。

团队没有“重置”或恢复的概念。一旦创建了团队，它就永远无法被 Keybase 窃取或交给其他人。链接只能由管理员添加到其签名链中，并且链接只能添加而不能删除。只能撤销。这可以防止服务器通过遗漏来撒谎。

如果你所有的管理员都丢失了所有的密钥，你将永久失去你的团队！Keybase 无法提供任何帮助，因为 Keybase 无法干扰你的团队。

### 团队出错的小概率

你是 Keybase 团队的首批测试者之一，所以有很小的机会我们会搞砸某些事情，你需要把数据取出来并选择一个新的团队名称。我们希望这不会发生。假设在 2017 年 7 月至 9 月期间发生这种情况的概率为 1%。

### 限制

在我们的测试期间：

- 团队人数限制为 20 人
- 子团队创建暂时禁用
- 你总共只能创建 100 个团队。请不要抢注你知道其他人会想要的公司和项目名称。

### 常见问题

**为什么团队名称是全局的？**

这样人们就可以只用名字来谈论团队，而不需要使用指纹或安全代码。

**为什么我不能重命名顶层团队？**

你可以重命名子团队，但顶层团队重命名是我们尚未准备好实现的功能。这需要在我们的 Merkle 树中进行重定向，更重要的是，需要广泛的用户体验考虑。所以我们可能永远不会实现它。如果你不喜欢你的团队名称，请创建一个新团队并邀请所有人。

**我的团队之外的人能知道我所在的团队吗？**

不能。如上面的元数据部分所述，出于各种用户体验和通知原因，Keybase 服务器需要知道。但团队签名链不像用户签名链那样公开，用户签名链是公开的。

**如果我“重置”我的账户会发生什么**

Keybase 上的账户重置是指你丢弃所有密钥并重新开始，并重做你的身份证明。**这会将你踢出所有团队。** 你需要被重新添加。

必须这样，否则 Keybase 可能会把你踢出团队并让其他人顶替你的位置。

**我该如何测试？**

只需安装 Keybase 并使用命令行创建一个团队。

**我如何发送反馈？**

```bash
# 如果你在桌面客户端遇到任何问题
> keybase log send
```

在手机应用中，你可以进入 **齿轮图标 > 反馈**。

对于一般的非 bug 反馈，你可以在 [https://github.com/keybase/client](https://github.com/keybase/client) 上创建一个 issue。

**这如何适应 Keybase 的商业模式？**

我们认为如果团队功能起飞，将来我们会对更大的团队收费。我们要么现在免费提供的任何东西都不会转变为付费模式，所以如果你现在创建一个 20 人的团队并开始使用它，你将来不会面临为了获取文件或消息而必须付费的情况。

**这真的是开源的吗？**

是的，所有客户端都是。

[https://github.com/keybase/client](https://github.com/keybase/client)

[安装说明在这里](https://keybase.io/download)

![](https://keybase.io/images/teams/acme.png)


## Tor 支持

Keybase 命令行客户端支持 Tor。当然，匿名是一个充满风险和微妙的属性。本文档解释了如何使用 Tor 和其他 Keybase 功能来保护你的身份。

*请注意，Keybase GUI 不支持 Tor 模式。* 如果你想通过 Tor 隧道传输整个应用程序，我们建议在 [Tails VM](https://tails.boum.org) 中运行它。此外，我们的 Tor 支持未经审计，因此即使在严格模式下，也可能潜入一些识别信息。

### 先决条件

要使用带有 Tor 的命令行客户端，你需要在本地运行 Tor SOCKS 代理。有关如何设置本地 Tor 代理的更多信息，请参阅 [Tor 项目的文档](https://www.torproject.org/docs/installguide.html.en)。

### 启用 Tor 模式

如果你已经在后台运行 `keybase service`，仅仅向命令添加 `--tor-mode` 是不起作用的 - 对于除 `service` 以外的命令，该标志仅在服务尚未运行时有效，因此你必须使用以下任一方法：

#### 通过显式设置标志运行服务来临时启用

如果你想仅在单次会话中使用 Tor 模式的 Keybase，请首先运行 `keybase ctl stop` 关闭后台运行的服务，然后运行 `keybase --tor-mode=leaky|strict service`。当此服务运行时，其他终端中的所有 `keybase` 命令都将通过 Tor 网络访问我们的服务器。

*请注意，此时启动 Keybase GUI 将关闭该服务并以默认模式重新启动它。*

#### 通过更改服务配置永久启用

```bash
# "leaky" 模式，简单地通过 Tor 隧道传输所有流量
keybase config set tor.mode leaky
# "strict" 模式，使请求完全匿名
keybase config set tor.mode strict

# 重启服务，确保 GUI 未运行
```

### 简短演示

要使用默认选项启用 Tor，只需将 Tor 模式标志设置为 `leaky`：

```bash
# 使用上述任一方法启用 leaky tor 模式
keybase id malgorithms@twitter
```

你会得到类似如下的输出：

```
▶ INFO Identifying chris
✔ public key fingerprint: 94AA 3A5B DBD4 0EA5 49CA BAF9 FBC0 7D6A 9701 6CB3
✔ "malgorithms" on twitter: https://twitter.com/malgorithms/status/433640580220874754
✔ "malgorithms" on github: https://gist.github.com/2d5bed094c6429c63f21
✔ admin of chriscoyne.com via HTTPS: https://chriscoyne.com/keybase.txt
✔ "malgorithms" on hackernews: https://news.ycombinator.com/user?id=malgorithms
✔ admin of DNS zone chriscoyne.com, but the result isn't reliable over Tor: found TXT entry keybase-site-verification=2_UwxonS869gxbETQdXrKtIpmV1u8539FmGWLQiKdew
```

所有网络流量现在都通过 Tor 保护，因此服务器或网络窃听者无法识别你的 IP 地址，但服务器仍然可以看到你的登录凭据。这种操作模式类似于 [Tor 匿名模式(3)](https://trac.torproject.org/projects/tor/wiki/doc/TorifyHOWTO#mode3:userwithnoanonymityusingToranyrecipient)。它不能保护你免受 Keybase 服务器泄露的影响，但它可以防止你的 ISP（或任何其他恶意网络窥探者）知道你在使用 Keybase。

请注意，在上述识别 `@malgorithms` 的尝试中，并非所有内容都是可信的。Keybase CLI 打印出 `chriscoyne.com` 的 DNS 记录不可信，因为 DNS 和裸 HTTP 在 Tor 上本质上是不可靠的；中继节点可以编造任何它们想要的内容，恶意节点可以伪造证明。

### 严格模式

*严格模式目前已损坏，我们正在修复。*

如果你想要更高程度的隐私，你可以要求 *strict*（严格）Tor 模式，这将向服务器隐瞒所有用户识别信息，类似于 [Tor 匿名模式(1)](https://trac.torproject.org/projects/tor/wiki/doc/TorifyHOWTO#mode1:useranonymousanyrecipient)。例如，尝试这个：

```bash
# 使用上述任一方法启用 strict tor 模式
keybase follow malgorithms@twitter
```

你会得到类似如下的输出：

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

注意发生的一些新事情。在输出的第三行，有一个警告，客户端跳过了将其本地视图的个人资料与服务器同步。如果它同步了，服务器上分析流量的人可能会正确地猜出，直接查找 Bob 之后的查找 Alice 意味着 Alice 正在关注或识别 Bob。因此，对 Alice 的查找被抑制了。还要注意，客户端不提供向服务器写入关注者声明，这也将泄露用户的身份。相反，它只是满足于将关注信息写入本地存储。

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

{#
<h3>配置 Tor 支持</h3>

<p>相关选项包括：</p>
<ul>

  <li><strong>启用 Tor</strong>：开启 Tor 支持。默认为如上所述的匿名模式(3)。
    <ul class="sub-ul">
      <li>命令行：`--tor-mode=[strict|leaky]`</li>
      <li>配置文件：`{ "tor" : { "enabled" : true }}`</li>
      <li>环境变量：`TOR_ENABLED=1`</li>
      <li>默认值：OFF</li>
    </ul>
  </li>

  <li><strong>启用 Tor 严格模式</strong>：向服务器隐藏所有识别用户信息，
     并通过给定的 Tor SOCKS 代理路由所有流量（匿名模式(1)）。如果存在，意味着
     Tor 模式已开启。
     <ul class="sub-ul">
      <li>命令行：`--tor-strict`</li>
      <li>配置文件：`{ "tor" : { "strict" : true } }`</li>
      <li>环境变量：`TOR_STRICT=1`</li>
      <li>默认值：OFF</li>
     </ul>
  </li>

  <li><strong>启用 Tor "Leaky" 模式</strong>：如果你在配置或环境
     中指定了 <em>strict</em> 模式，但想暂时关闭严格模式
     （例如，登录），你可以指定此标志。
     <ul class="sub-ul">
      <li>命令行：`--tor-leaky`</li>
      <li>环境变量：`TOR_LEAKY=1`</li>
      <li>默认值：OFF</li>
     </ul>
   </li>

  <li><strong>Tor 隐藏地址</strong>：指定 Keybase 服务器（或镜像）的 Tor 隐藏地址。
    如果指定，意味着 Tor 模式应该开启。
     <ul class="sub-ul">
      <li>命令行：`--tor-hidden-address foofoobar.onion:80`</li>
      <li>配置文件：`{ "tor" : { "hidden_address" : "foofoobar.onion:80"} }`</li>
      <li>环境变量：`TOR_HIDDEN_ADDRESS=foofoobar.onion:80`</li>
      <li>默认值：`keybase5wmilwokqirssclfnsqrjdsi7jdir5wy7y7iu3tanwmtp6oid.onion`</li>
     </ul>
  </li>

  <li><strong>Tor 代理</strong>：指定 Tor 代理的主机和端口。
    如果指定，意味着 Tor 模式应该开启。
     <ul class="sub-ul">
      <li>命令行：`--tor-proxy localhost:9050`</li>
      <li>配置文件：`{ "tor" : { "proxy" : "localhost:9050"} }`</li>
      <li>环境变量：`TOR_PROXY=localhost:9050`</li>
      <li>默认值：`localhost:9050`</li>
     </ul>
  </li>

</ul>
#}

### Web 支持

作为 Tor 支持的一部分，我们也公开了 `https://keybase.io` 作为隐藏地址；这比标准的匿名 Tor 浏览略有改进，因为你的流量不需要经过出口节点。我们的隐藏地址是：

> *http://keybase5wmilwokqirssclfnsqrjdsi7jdir5wy7y7iu3tanwmtp6oid.onion*

请注意，命令行客户端默认在内部使用此隐藏地址。
