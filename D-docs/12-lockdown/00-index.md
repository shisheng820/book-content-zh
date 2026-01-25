
# 锁定模式 (Lockdown Mode)

如果 Keybase 用户希望为其账户提供额外保护，可以选择开启_锁定模式_。这样做将禁用所有会修改或暴露敏感云托管数据的网站功能。一旦进入锁定模式，所有安全敏感功能必须在具有活跃签名密钥的有效 Keybase 设备上执行...

例如，当用户处于锁定模式时，以下功能需要 Keybase 设备：

  * 修改密码或恢复密码
  * 修改电子邮件地址
  * 修改你的全名、简介或头像
  * 关注或取消关注用户
  * 建立或移除身份证明（如 Twitter、Reddit 或 Bitcoin）
  * 团队管理操作
  * 添加或吊销设备
  * 更新或移除 PGP 密钥
  * 访问加密的 PGP 私钥（针对选择开启此功能的用户）
  * 重置账户
  * 删除账户

换句话说，锁定后的用户在 Keybase 网站上的视图大致相当于一个匿名、未登录的用户。

锁定模式提供的保护类似于传统基于服务器信任的服务上的 2FA（双因素认证）。如果你处于锁定状态，获得你电子邮件收件箱或 Keybase 口令控制权的攻击者无法对你的账户进行任何更改。此外，攻击者还需要物理访问你的其中一台*已解锁*设备，或远程后门访问（即已经“root”了你的设备）。与 2FA 不同，锁定模式没有用户体验上的不便，也不会让你到处翻找手机或密钥卡。

## 启用或禁用锁定模式

用户只能使用有效的 Keybase 设备启用或禁用锁定模式（当然，绝不能从网站上进行）。这可以通过以下方式完成：

  * 通过移动应用 (☰ → 高级 (Advanced) → "禁止从网站更改账户 (Forbid accounts changes from the Website)")
  * 通过桌面应用 (☰ → 设置 (Settings) → 高级 (Advanced) → "禁止从网站更改账户 (Forbid accounts changes from the Website)")
  * 通过命令行 (`keybase account lockdown --enable`)

你可以通过命令行查看账户所有与锁定相关的更改历史记录。例如：

```sh
$ keybase account lockdown --history
Learn more about lockdown mode: `keybase account lockdown -h`
Lockdown mode is: enabled
Changed to:    Change time:               Device:
enabled        2018-08-16 13:36:30 EDT    iphone 8 (75873ef47b4beb15f62880ae4f943818)
disabled       2018-08-15 11:40:41 EDT    Work iMac 5k 2015-11 (d3cd754f30775a297c1ef61e5f3e3018)
enabled        2018-08-15 06:48:53 EDT    home mac mini - meuse (bb74a26dac2deeb11d66c7f1959f1d18)
disabled       2018-08-14 22:29:31 EDT    home mac mini - meuse (bb74a26dac2deeb11d66c7f1959f1d18)
enabled        2018-08-09 13:36:53 EDT    Work iMac 5k 2015-11 (d3cd754f30775a297c1ef61e5f3e3018)
```

## 内部机制

锁定模式的实现很简单。对 Keybase 服务器的任何 API 请求都可以选择[传统的密码认证](/docs/api/1.0/call/login)或[非交互式会话令牌 (NIST) 认证](/docs/api/1.0/nist)。后者只有使用有效的 Keybase 设备才可能实现。因此，当用户启用锁定时，任何对安全敏感的服务器端端点的访问只有在附带有效的 NIST 令牌时才能继续。
