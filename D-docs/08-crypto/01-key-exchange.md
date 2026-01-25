# Keybase 密钥交换 (KEX) 协议

本文档描述了 Keybase 使用现有设备配置新设备的协议。我们将该协议设计为对移动设备友好，因此用户无需在小触摸屏上输入加密数据的烦恼。

## 设计

KEX 协议的高级设计是两个设备希望通过加密、认证的通道进行对话，以传达一些重要的信息：

   * 被配置者 (Provisionee) → 配置者 (Provisioner)
      * 被配置者的新设备特定 EdDSA 公钥
      * 被配置者的新设备特定临时 Curve25519 DH 公钥
   * 配置者 → 被配置者
      * 从用户密码短语派生的数据，用于本地锁定密钥。
      * 用配置者现有设备特定 EdDSA 密钥对被配置者新设备特定 EdDSA 的签名
      * 会话令牌，以便被配置者无需直接登录即可获得与服务器的活动会话。被配置者需要会话来向用户的签名链发布新签名。
      * 用户最新的 [每用户密钥](/docs/teams/puk) (PUK) 种子。这些密钥始终在用户设备之间共享，并且可以由其中任何一个使用。
      * 用户最新的 [每用户临时密钥 (userEK) 种子](/docs/crypto/ephemeral)。这些密钥始终在用户设备之间共享，并且在活动时可以由其中任何一个使用。

密码短语信息和每用户密钥种子需要加密以保密，并且密钥交换需要进行 MAC 处理以确保控制通信通道的对手没有对交换进行中间人攻击 (MITM)。这两个属性都是通过交换的认证加密来实现的。因此，端点在通信开始之前共享一个离线秘密（如下所述的 *W*）。

虽然存在许多设备到设备的通道，但我们将做简单而天真的事情，即通过 Keybase 服务器转发消息。因此，Keybase 服务器可以控制通道，但由于终端主机进行认证和加密，此设计决策不会带来安全风险。

### 先决条件

在密钥交换开始之前，配置者（设备 *X*）和被配置者（设备 *Y*）必须拥有：

   * 配置者（设备 *X*）：
      * 设备 ID
      * 已配置的每设备 EdDSA 签名密钥
      * 用户最新的 PUK 种子
      * 用户最新的 userEK 种子
      * 用户当前的密码短语流（而不是已更新的旧密码短语流。）
      * 自己的登录会话
      * 它最终将与新配置的设备共享的登录会话
   * 被配置者（设备 *Y*）：
      * 新设备 ID
      * 新设备名称
      * 新的、未配置的每设备 EdDSA 签名密钥
      * 新的、未配置的每设备 Curve25519 DH 密钥
      * 新的、未配置的每设备临时 Curve25519 DH 密钥

一旦满足这些条件，设备就可以开始 KEX。请注意，设备 *Y* 不需要登录会话。这一点很关键，因为用户不应需要在新设备上输入密码短语。如果配置者或被配置者缺少临时密钥的组件，作为临时密钥支持推出时的后备方案，被配置者将在配置后生成新的密钥对。

### 派生会话密钥并共享秘密

*X* 和 *Y* 需要共享一个便于跨两个设备使用的强秘密。我们现在支持 3 种操作模式。第一种是 V1 桌面版，称为 V1d。第二种是 V1 移动版，称为 V1m。最后一种是 V2，随着客户端升级软件，我们将逐渐过渡到 V2。

秘密通过以下步骤生成。

   1. 从 [BIP0039](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt) 字典中随机选取 *J* 个单词。称此秘密为 *W*。在 V1d 和 V1m 中，*J* 为 8，意味着秘密有 88 位熵。在 V1m 中，附加单词 `"four"` 被追加到 *W* 以区分 V1d 和 V1m。正如我们将在下面看到的，这是为了让手机可以做更少的拉伸（否则它们会崩溃）。在 V2 中，*J* 为 9，意味着秘密有 99 位熵。

   1. 将 *W* 中的单词用 ASCII 空格 (`0x20`) 连接在一起，生成字符串 *W'*。

   1. 在 *W'* 上运行 scrypt(N,p=1,r=8) 并使用盐 *T*。对于 V1d，我们设置 *N = 2<sup>17</sup>*。对于 V1m 和 V2，我们设置 *N* = 2<sup>10</sup>，因为较高的值会使旧手机崩溃。对于 V1d 和 V1m，盐 *T* 为空。对于 V2，我们将 *T* 设置为用户的 UID。

   1. 取输出的前 256 位。称此秘密为 *S*。

   1. 从 *W'* 生成二维码，称为 *Q*。

   1. 生成公共会话标识符：*I* = HMAC-SHA256(*S*, `"Kex v2 Session ID"`)

现在设备 *X* 和 *Y* 可以通过随机单词字符串 *W'* 或二维码 *Q* 共享秘密 *S*。

### 会话建立

*X* 和 *Y* 需要建立会话。它们通过使用上述方法生成会话秘密来实现。称这些秘密为 *S<sub>X</sub>* 和 *S<sub>Y</sub>*。

双方都向 Keybase 服务器发送消息，通告会话发起；*X* 使用会话标识符 *I<sub>X</sub>* 进行此操作，而 *Y* 使用会话标识符 *I<sub>Y</sub>* 进行此操作。

一旦用户在设备 *Y* 上输入秘密 *S<sub>X</sub>*，或在设备 *X* 上输入 *S<sub>Y</sub>* —— 通过二维码或手动文本输入 —— 设备就可以计算相应的会话标识符，并建立通道。然后协议就可以开始了。

### 传输和数据包格式

通过服务器在 *X* 和 *Y* 之间发送的所有消息都通过 NaCl 的 SecretBox 密码进行保护，使用共享秘密（*S<sub>X</sub>* 或 *S<sub>Y</sub>*）作为会话密钥。从 *X* 发送到 *Y* 的每条消息都作为数组 [message-packed](http://msgpack.org) 成以下形式：

```
┌───────────────┬──────────────┬────────────┬────────────┬───────────────────┐
│   Sender ID   │  Session ID  │   Seqno    │   Nonce    │ Encrypted Payload │
│  (16 bytes)   │  (32 bytes)  │ (4 bytes)  │ (24 bytes) │    (arbitrary)    │
└───────────────┴──────────────┴────────────┴────────────┴───────────────────┘
```

加密负载计算为（同样是 message-packed 的）SecretBox：

```
┌───────────────┬──────────────┬────────────┬───────────────────┐
│   Sender ID   │  Session ID  │   Seqno    │ Plaintext Payload │
│  (16 bytes)   │  (32 bytes)  │ (4 bytes)  │    (arbitrary)    │
└───────────────┴──────────────┴────────────┴───────────────────┘
```

(sender ID, session ID, seqno) 三元组在所有消息中应该是唯一的，但在两个消息方向上有两个独立的序列号。

设备通过 Keybase 服务器将这些消息发送给另一个设备，并可以通过提供其自己的设备 ID、会话 ID 和最后接收的序列号来从另一方检索消息。

接收消息时，客户端解密，并检查加密外部的 (sender ID, session ID, seqno) 是否与内部的匹配。还会执行进一步的检查：(1) 接收到的第一条消息是序列号 1，后续消息的序列号单调递增 1；(2) 会话 ID 与从共享秘密 *S* 派生的会话 ID 匹配；(3) 接收到的消息中的发送者 ID 不得等于接收设备的设备 ID（这可以防止反射消息）。如果所有检查都通过，客户端将重新组装明文负载并给出简单数据流的假象。

在这个数据流之上，我们构建了一个消息协议，使用我们在其他地方使用的相同 [framed-msgpack-rpc](https://github.com/keybase/go-framed-msgpack-rpc)。Keybase 服务器不知道这种结构。

### 协议

KEX 中的所有协议消息都制定为 RPC，因此具有调用和回复。只有三个 RPC：

```
    ┌─────────────────┐                                      ┌─────────────────┐
    │ Provisioner (X) │                                      │ Provisionee (Y) │
    └─────────────────┘                                      └─────────────────┘

    1.                       [ NOTIFY: Start() ]
    ◀──────────────────────────────────────────────────────────────────────────────

    2.                 CALL: Hello2(uid,newSession,sibkeySig)
    ──────────────────────────────────────────────────────────────────────────────▶

    3.         REPLY: (sibkeySigSigned,dhPubKey,dhEphemeralPubKey)
    ◀──────────────────────────────────────────────────────────────────────────────

    4. CALL: DidCounterSign2(sibkeySigCounterSigned,ppsEncrypted,pukBox,userEKBox)
    ──────────────────────────────────────────────────────────────────────────────▶

    5.                        REPLY: (OK)
    ◀──────────────────────────────────────────────────────────────────────────────

```

以下是此协议的步骤：

  1. （可选）：如果在设备 *Y* 上输入了秘密 *S<sub>X</sub>*，则 *Y* 应向 *X* 发送 **Start** RPC 以启动协议。注意我们在这里使用 *notify* 消息，它不期望回复。

  1. 设备 *X* 向 *Y* 发送 **Hello** RPC，详细说明：
     * `uid` - 相关用户的 UID
     * `newSession` - 新设备应用于向服务器验证自身的会话
     * `sibkeySig` - *Y* 将用于将自己签署到用户签名链中的签名主体骨架

  此时，设备 *Y* 可能需要阻塞以等待用户输入，因为用户必须命名新设备。设备 *Y* 加载其用户的签名链以确定以前使用的设备名称，以便 *Y* 可以确定选择一个有效的设备名称（通过客户端输入检查）。

  1. 设备 *Y* 接收此 RPC，并填写其 `sibkeySig` 字段。即其设备 ID、其设备名称及其每设备 EdDSA 公钥。然后它对 blob 进行签名，并将结果存储为 `body.sibkey.reverse_sig`。这个新 blob 是 `sibkeySigBlobSigned`，它作为对上一步中 RPC 的 RPC 回复发送。设备 *Y* 还包括其设备特定和设备特定临时 Diffie-Hellman 密钥的公共部分；设备 *X* 将在下一步中需要它。

  1. 设备 *X* 接收带有由 *Y* 签名的 `reverse_sig` 的 JSON blob。设备 *X* 移除签名和 *Y* 提供的预期字段，并构建一个新的 JSON blob，验证 *Y* 对此结构的签名。*X* 重建 JSON blob 以匹配预期结构，以防止它们签署来自 *Y* 的任意声明。如果签名检查通过，*X* 对整个 JSON blob 进行反向签名 (counter-signs)，并将结果在 **DidCounterSign** RPC 中发送给 *Y*。设备 *X* 还发回用户的密码短语流（为设备 *X* 的公共设备密钥加密）和一个秘密临时 DH 密钥。加密包包括相应的临时公共 DH 密钥，以便设备 *X* 可以解密。此消息还附带 `pukBox`，其中包含为设备 *Y* 的加密密钥 NaCl Boxed 的用户最新每用户密钥种子。如果用户有临时用户密钥，则为设备 *Y* 的临时设备加密密钥 NaCl Boxed。

  1. 设备 *Y* 接收反向签名的 JSON 对象，然后准备将其发布到服务器。该发布包括此签名、授权新的每设备 Curve25519 DH 密钥（步骤 3 中发送的同一个）的后续签名、`pukBox`、`userEKBox` 和设备的新的 Curve25519 DH 设备临时密钥，服务器将作为一个事务接受或拒绝这些内容。

## 实现

### API 端点

以下是 KEX 中使用的端点：

   * **POST /_/api/1.0/kex2/send.json**
      * 参数：
         * `I` - 此消息的会话 ID
         * `sender` - 发送者的设备 ID
         * `seqno` - 此消息的序列号
         * `msg` - 与加密负载连接的 nonce，或用于标记 *EOF* 的空消息
      * 行为：(`I`, `sender`, `seqno`) 三元组必须是唯一的。服务器将立即将消息路由到相应的接收者，或者如果没有人接收，则将其缓冲大约一小时。

   * **GET /_/api/1.0/kex2/receive.json**
   	 * 参数：
   	 	* `I` - 此消息的会话 ID
   	 	* `receiver` - 接收者的设备 ID
   	 	* `low` - 获取大于或等于此序列号的消息
   	 	* `poll` - 如果消息未立即准备好，等待多长时间（以毫秒为单位）
   	 * 行为：服务器将检查会话 `I` 中所有不是由给定接收者发送且其 `seqno` 大于给定序列号的消息。它将所有这些消息返回给调用者。

   * **POST /_/api/1.0/new_session.json**
     * 行为：为当前用户获取一个新会话，以便在新设备上使用

   * **POST /_/api/1.0/key/multi.json**
     * 参数：
       * `sigs` - 一个 JSON 对象，包含一系列委派密钥的一个或多个签名
     * 行为：签名都在一个原子事务中被接受或拒绝，并且密钥被相应地委派。

### 传输层

传输层应作为一个独立模块实现，可以独立于代码库的其余部分进行测试和调试。

这是一种可能的接口：

```go

type DeviceID []byte
type SessionID []byte
type Secret []byte
type Seqno int

// MessageRouter is a stateful message router that will be implemented by
// JSON/REST calls to the Keybase API server.
type MessageRouter interface {

	// Post a message, or if `msg = nil`, mark the EOF
	Post(I SessionID, sender DeviceID, seqno Seqno, msg []byte) error

	// Get messages on the channel.  Only poll for `poll` milliseconds. If the timeout
	// elapses without any data ready, then `io.ErrNoProgress` is returned as an error.
	// Several messages can be returned at once, which should be processes in serial.
	// They are guaranteed to be in order; otherwise, there was an issue.
	// On close of the connection, Get returns an empty array and an error of type `io.EOF`
	Get(I SessionID, receiver DeviceID, seqno Seqno, poll int) (msg [][]byte, err error)
}

// conn implements the net.Conn interface
type conn struct {}

// NewConn makes a new connection given a MessageRouter and a Secret, which
// is both used to identify the Session and to encrypt/authenticate the connection
func NewConn(r MessageRouter, s Secret) (net.Conn, error) {}

// Read data from the connection, returning plaintext data if all
// cryptographic checks passed. Obeys the `net.Conn` interface.
func (c *conn) Read([]bytes) (int, error) {}

// Write data to the connection, encrypting and MAC'ing along the way.
// Obeys the `net.Conn` interface
func (c *conn) Write([]byte) (int, error) {}

// Close the connection to the server, sending a `Post()` message to the
// `MessageRouter` with `eof` set to `true`. Fulfills the
// `net.Conn` interface
func (c *conn) Close() error {}

// LocalAddr returns the local network address, fulfilling the `net.Conn interface`
func (c *conn) LocalAddr() (addr net.Addr) {}

// LocalAddr returns the remote network address, fulfilling the `net.Conn interface`
func (c *conn) RemoteAddr() (addr net.Addr) {}
```

### RPC 层

一旦我们有一个遵守 `net.Conn` 接口的传输（从服务器反弹），就很容易插入 RPC 系统。

### 取消和错误

如果一方在交换过程中断开连接，或者如果一方取消，会发生什么？有几种情况需要考虑，无论是在传输级别还是在 RPC 级别。

在传输级别，设备“取消”交换应向服务器发送 `Post()` 并设置 `msg = nil`，表示其挂断通道的意图。另一台设备将在下一次 `Get` 时收到此取消。

正是在 RPC 级别，应用程序将处理这些异常。在第一种情况下，设备发送了 RPC 但尚未收到回复，与此同时，对等设备挂断了。RPC 库随后将生成对 RPC `Call` 方法的错误响应。

第二种情况，设备充当 RPC 服务器，其对等方断开连接或取消。在这种情况下，它将永远不会收到协议序列中的下一条预期消息（或者将无法回复未完成的 RPC）。在这种情况下，它还将在底层连接上获得 EOF，并可以相应地解释这种取消。

就从应用程序级别生成这些 EOF 而言，应用程序只需在 `net.Conn` 上调用 `Close()`，这将向另一方发出取消信号。如果设备在完成协议之前崩溃或离线，另一方将在其 `Get()` 调用中看到超时，并应将 `Error` 传播到连接上的任何未完成的 `Read()` 调用。

## 术语表

这是本文档中使用的术语的快速术语表：

  * KEX - 密钥交换
  * SecretBox — [NaCl 库](http://nacl.cr.yp.to) 的认证加密函数。
  * passphrase stream (密码短语流) — 用户密码短语和随机盐的 scrypt(N=2<sup>15</sup>, r=8, p=1)（上面缩写为 *pps*）
  * userEK — [用户临时密钥](/docs/crypto/ephemeral)
