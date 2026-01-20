# 团队加密 (Teams Crypto)

每个团队都有一组团队密钥（PTK）。具体细节与 [每用户密钥 (PUK)](/docs/teams/puk) 非常相似。
用户在发布 `team.root` 或 `team.subteam_head` 链接时会创建一组 PTK，
如 [团队：命名、Merkle 树集成和签名链](/docs/teams/details) 中所述。并且，用户会在 `team.rotate` 链接中
将这些密钥轮换到新的一代。

## PTK

每一代 PTK 的具体生成过程如下：

* 用户生成一个 32 字节的随机种子 _s_
* 她计算 _e_ = HMAC(_s_, `"Keybase-Derived-Team-NaCl-EdDSA-1"`) 并使用该值作为 EdDSA 签名密钥的私钥。然后她计算公钥部分，得到密钥对 (_E_, _e_)。
* 她计算 _d_ = HMAC(_s_, `"Keybase-Derived-Team-NaCl-DH-1"`) 并使用该值作为 Curve25519 DH 加密密钥的私钥。然后她计算公钥部分，
得到密钥对 (_D_,_d_)
* 她计算 _c_ = HMAC(_s_, `"Keybase-Derived-Team-NaCl-SecretBox-1"`) 用作
NaCl secretbox 的私钥，用于加密以前的种子 _s_。（详见下文）

其中 HMAC 使用 SHA512 计算，并截取前 32 个字节。

这个过程在每一代 _i_ 都会重复。在第 _i_ 代，密钥 <i>E<sub>i</sub></i>
和 <i>D<sub>i</sub></i> 被签名到团队的公共签名链中。每当添加新用户时，
<i>s<sub>i</sub></i> 会针对该用户的公共 PUK DH 密钥进行加密。这使得 <i>s<sub>i</sub></i> 在用户的每个设备上都可用。这个盒子（box）被写入主数据库。当前的 <i>s<sub>i</sub></i> 应该为每个团队成员（无论是隐式还是显式）都有一个盒子。

当团队成员撤销设备，或团队成员被重置，或者用户
离开或被移出团队时，PTK 必须轮换。这可以惰性地发生。
新的 PTK 密钥针对所有剩余成员进行加密，新的公钥
部分被写入团队的签名链中。此外，每当密钥滚动（roll over）时，
前一个种子 <i>s<sub>i</sub></i> 会通过 NaCl 的 SecretBox 对称加密
用 <i>c<sub>i+1</sub></i> 进行加密，就像用户一样。关于这种轮换是如何编排的更多细节，
请参阅 [级联惰性密钥轮换 (CLKR)](/docs/teams/clkr) 的描述。

## 应用程序密钥 (Application Keys)

团队成员从上述共享种子 <i>s<sub>i</sub></i> 派生应用程序密钥：

* 对于 KBFS: HMAC(<i>s<sub>i</sub></i>, `"Keybase-Derived-Team-KBFS-1"`) ⊕ <i>S<sub>i,KBFS</sub></i>
* 对于聊天: HMAC(<i>s<sub>i</sub></i>, `"Keybase-Derived-Team-Chat-1"`) ⊕ <i>S<sub>i,CHAT</sub></i>

也就是说，密钥是派生自团队共享秘密 <i>s<sub>i</sub></i> 的密钥
与服务器存储的 32 字节随机掩码的异或（XOR）。对于给定的团队，所有读者、作者、所有者
和显式管理员都可以看到这些 32 字节的掩码。服务器不对隐式管理员提供这些掩码，
从而阻止他们查看用这些密钥加密的聊天或文件。

在聊天中，所有消息都使用 NaCl 的 secret box 原语加密，密钥如上
派生。当密钥轮换时，新聊天使用新密钥加密，但旧聊天
不会重新加密。

对于 KBFS，这些派生密钥代替了 <i>s<sup>f,0</sup></i>
