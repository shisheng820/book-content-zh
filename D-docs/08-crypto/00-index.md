# Keybase 加密文档

这是描述整个 Keybase 系统中起作用的加密技术的文档集合。

## 核心安全

[此文档](/docs/server) 描述了我们系统安全的高级方法：即，Keybase 客户端从我们的服务器获取提示和原始数据，但不信任它，并检查其所有工作。

我们发布了 [后续公开文档](/docs/server/merkle-root-in-bitcoin-blockchain)，描述了我们如何使用比特币区块链来增强安全保证。

随着我们推出每设备密钥，我们发布了另一份 [文档](/docs/server#meet-your-sigchain-and-everyone-elses)，描述了用户签名链的具体细节，以及用户如何将权限委派给新密钥并吊销旧密钥。

## 密钥交换

当用户配置新设备时，他们会交换密钥，以便现有设备签署新设备使其投入运行，并且新设备可以访问一些秘密数据，否则这些数据只有在用户输入密码短语时才可用（我们在移动设备上尽量避免这种情况）。此 [文档](/docs/crypto/key-exchange) 描述了该协议，一旦协议经过审查，最终将公开。

## 本地密钥存储 (LKS)

Keybase 的一个可用性要求是用户应该只需要记住一个密码短语，并且如果该密码短语在一台设备上更改，所有其他设备应立即反映该更改。通常，我们试图尽量少用密码短语，但对于像锁定本地密钥这样的某些操作，密码短语可能是不可避免的。此 [文档](/docs/crypto/local-key-security) 描述了本地密钥安全系统。

## 文件系统

Keybase 文件系统 (KBFS) 现在正在积极开发中，将是我们发布的第一个产品。此 [文档](/docs/crypto/kbfs) 描述了设计中的加密决策。本文档还涉及我们的组织计划，该计划尚未开发。

{##

## 账户边缘情况

用户如何更改密码、处理丢失的设备、更改电子邮件地址等？这些问题都是相关的，并在关于“账户边缘情况”的此 [文档](/docs/crypto/account-corner-cases) 中涵盖。

##}

## SaltPack 消息格式

我们需要像 PGP 消息那样但更简单、更现代且更易于实现的东西。我们现在涵盖的两个重要案例是 [认证加密消息](https://saltpack.org/encryption-format-v2) 和 [公开签名声明](https://saltpack.org/signing-format-v2)。我们称这个系统为 "SaltPack"，因为它一半是 [NaCl](http://nacl.cr.yp.to/)，一半是 [message pack](http://msgpack.org)。更多详细信息请访问 [saltpack.org](https://saltpack.org)。
