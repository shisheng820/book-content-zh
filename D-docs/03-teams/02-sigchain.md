
# Keybase 签名链 V2

签名链 V2 是对签名链先前版本（[V1](https://keybase.io/docs/sigchain)）的扩展。
随着我们一直在构建 Keybase，特别是移动端和团队功能，我们发现了签名链的新需求，并相应地进行了（向后兼容的）更改：

*   压缩：目前的签名链非常臃肿。如果你开始与 [Chris Coyne](https://keybase.io/chris) 对话，你必须下载他的完整签名链，大小约为 6MB（压缩后 3MB）且还在增长。其中大部分是 Chris 关注的其他用户，这与他关键的密钥和设备更新混合在一起。目前每个签名链链接大约 6k 大。在移动设备上，这将非常痛苦，因为在你可以开始与 Chris 交谈之前，你必须下载大量数据（可能通过不稳定的连接）。
*   半私有链接：一些链接可能会对部分（大多数）查看者隐藏，因为它们包含私人信息（服务器可以看到）。例如团队成员。

本文档从高层次解释了 V2 的结构。

## 示例

假设你有一个 V1 链接，形式如下：

```javascript
var inner_link = {
  "body": {
    "key": {
      "eldest_kid": "01013ef90b4c4e62121d12a51d18569b57996002c8bdccc9b2740935c9e4a07d20b40a",
      "host": "keybase.io",
      "kid": "0120d3458bbecdfc0d0ae39fec05722c6e3e897c169223835977a8aa208dfcd902d30a",
      "uid": "dbb165b7879fe7b1174df73bed0b9500",
      "username": "max"
    },
    "track": {
      "basics": {
        "id_version": 38,
        "last_id_change": 1487592188,
        "username": "michael"
      },
      "id": "aa1e1ca79c2838d4b1da4569b5200500",
      "key": {
        "key_fingerprint": "b4df6d7c3e744d41bbab458177fff4cac061a1cc",
        "kid": "0101ed29008279a6cda883b6d415eac0abdaed27a3917a297378b8328dec83ebd0ef0a"
      },
      "pgp_keys": [
        {
          "key_fingerprint": "b4df6d7c3e744d41bbab458177fff4cac061a1cc",
          "kid": "0101ed29008279a6cda883b6d415eac0abdaed27a3917a297378b8328dec83ebd0ef0a"
        }
      ],
      "remote_proofs": [
        {
          "ctime": 1453792180,
          "curr": "6c2c8eece6d12328486280763e15439a114ac8615c993b870a8e061f3ac9a98d",
          "etime": 1958368180,
          "prev": "368186690020ceb2b25691551fe4a28f19dad95654cab776454bab4843f70216",
          "remote_key_proof": {
            "check_data_json": {
              "name": "twitter",
              "username": "mcoyne88"
            },
            "proof_type": 2,
            "state": 1
          },
          "sig_id": "10210278d9be8d8285dbf8554073b75980fc6b7dffa733a5b2f2e70a2cfd6e3d0f",
          "sig_type": 2
        },
        {
          "ctime": 1453790811,
          "curr": "3b583421a55b841a53107668850c83954b81f5a05a00bca54e66a20d0a64d983",
          "etime": 1611470811,
          "prev": "be74bcbe134a5bb016e54902896e4415c9c70e722bc9a2f5b19f9fee085e70b8",
          "remote_key_proof": {
            "check_data_json": {
              "name": "github",
              "username": "mcoyne88"
            },
            "proof_type": 3,
            "state": 1
          },
          "sig_id": "c89116cb21b780d395310052af136c3592376224b4852ae3e5938ee7e1442bd70f",
          "sig_type": 2
        },
        {
          "ctime": 1453791455,
          "curr": "d7b99d0dba2e1e3a6efe744510344da00f48383d7d205016d1d2538c16baba0b",
          "etime": 1611471455,
          "prev": "3b583421a55b841a53107668850c83954b81f5a05a00bca54e66a20d0a64d983",
          "remote_key_proof": {
            "check_data_json": {
              "name": "reddit",
              "username": "mcoyne88"
            },
            "proof_type": 4,
            "state": 1
          },
          "sig_id": "00cfd5d05426e0d02cac9cbcf779250209922a6430f40ea4b7c9f8569f95a9680f",
          "sig_type": 2
        }
      ],
      "seq_tail": {
        "payload_hash": "dd6f241934340e5ff22127dd1e2d09aed8a74bf1318c0370ccf13c3477a5b178",
        "seqno": 21,
        "sig_id": "a9dbd4ef50181b8eead339e9fb633a448ad02c4b35bbdb922ee45b52d3b7d8380f"
      }
    },
    "type": "track",
    "version": 1
  },
  "client": {
    "name": "keybase.io go client",
    "version": "1.0.18"
  },
  "ctime": 1487643163,
  "expire_in": 504576000,
  "merkle_root": {
    "ctime": 1487643103,
    "hash": "41d826585d8aaf84143b581797b25daebe9f5f20444e3a0ded49bbbafc50200227284b40ff009499955a9563b777343252305aa2a95c2cc0158f15da86cf3c5f",
    "seqno": 909161
  },
  "prev": "3e64903fc3e6e8249c1efe37c0106a16867b73d22d2f3b67ebcdbc075583e0e5",
  "seqno": 278,
  "tag": "signature"
}
```

你会注意到这个 JSON blob 有 2.4k 大（去除空格后）。在签名链 V2 中，我们引入了一个新的包装对象：

```javascript
var outer_link = msgpack.pack([
  2,
  278,
  (Buffer.from("PmSQP8Pm6CScHv43wBBqFoZ7c9ItLztn6828B1WD4OU=", "base64")),
  (Buffer.from("Nl6GvU1ABnORNY4s2sKRyxNl9Pyx1r/TQeA/eYRMnA4=", "base64")),
  3,
  1
])
```

相关组件包括：

*   **位置 0**: `version` — 对于所有 V2 链接，值为 `2`
*   **位置 1**: `seqno` — 在上面的示例中，值为 `278`，描述了此链链接在签名链中的序列号。一如既往，这必须是严格顺序的。它必须与内部链接的 `seqno` 匹配。
*   **位置 2**: `prev` — 上一个外部链接的完整 SHA2 哈希，经过 msgpack 编码后。在上面的示例中，值为 `PmSQP8Pm6CScHv43wBBqFoZ7c9ItLztn6828B1WD4OU=`（Base64）。
*   **位置 3**: `curr` — 内部链接的完整 SHA2 哈希；`hash(payload_json)`。在这个例子中，值为 `Nl6GvU1ABnORNY4s2sKRyxNl9Pyx1r/TQeA/eYRMnA4=`（Base64）。
*   **位置 4**: `type` — 签名链链接的类型，使用下面的数值表。在上面的示例中，我们的值为 `3`，对应于 `track`。
*   **位置 5**: `seqno_type` — 用户和团队可以拥有公共和“半私有”的签名链。在“半私有”链中，服务器可以看到内部链接的值，并可以根据访问控制机制选择性地公开它。如果不显式指定，这里的值是隐含的。用户链的默认值是 `1`，表示 `PUBLIC`（公开）。团队的默认值是 `3`，表示 `SEMIPRIVATE`（半私有）。

## 生成链链接

如果你在你的 Node 解释器中运行这个小程序，你会得到一个 75 字节大的缓冲区，比上面的节省了大量空间！

现在，当用户实际签署一个新链接到他们的签名链时，他们将签署该值：

```javascript
var input = Buffer.from(outer_link,"binary")
var sig = device_key.sign(input)
```

当客户端发布签名时，它现在发布：

*   `outer_link` 如上所示
*   `inner_link` 和以前一样
*   `sig(outer_link)`

当其他客户端重放签名链时，它们总是获得 `outer_links`，但有时不下载 `inner_links`，要么是为了节省带宽，要么是因为它们未被授权。解码完整签名链的客户端必须手动检查外部值是否与内部值匹配，并应拒绝不匹配的链接。

## 常量

从 [JavaScript](https://github.com/keybase/proofs/blob/c75faba42b3d6f17f972614e6bf1fe9a45716d26/src/constants.iced#L40-L68) 或 [Go](https://github.com/keybase/client/commit/da752f40b3ff4bce5fca8e4dce66fe3116802d03/go/libkb/chain_link_v2.go#L15-L43) 代码中，这里是所有证明类型的数值等价物：

```iced
sig_types_v2:
  eldest : 1
  web_service_binding : 2
  track : 3
  untrack : 4
  revoke : 5
  cryptocurrency : 6
  announcement : 7
  device : 8
  web_service_binding_with_revoke : 9
  cryptocurrency_with_revoke : 10
  sibkey : 11
  subkey : 12
  pgp_update : 13
  per_user_key : 14
  team :
    index : 32
    root : 33
    new_subteam : 34
    change_membership : 35
    rotate_key : 36
    leave : 37
    subteam_head : 38
    rename_subteam : 39
    invite : 40
    rename_up_pointer : 41
    delete_root : 42
    delete_subteam : 43
    delete_up_pointer : 44
```

同样，从 [JavaScript](https://github.com/keybase/proofs/blob/c75faba42b3d6f17f972614e6bf1fe9a45716d26/src/constants.iced#L88-L92) 和 [Go](https://github.com/keybase/client/blob/da752f40b3ff4bce5fca8e4dce66fe3116802d03/go/libkb/constants.go#L611-L615) 代码中，这里是签名链序列类型：

```iced
seq_types :
  NONE : 0
  PUBLIC : 1
  PRIVATE : 2
  SEMIPRIVATE : 3
```
