
# 每用户密钥 (Per-User Keys)

Keybase 上的用户拥有一个或多个[*设备密钥*](https://keybase.io/blog/keybase-new-key-model)，其公钥部分在用户的签名链中公布，而私钥部分则保留在生成它们的设备本地。用户还可以拥有*纸质密钥*，在从丢失设备中恢复时，它们充当设备密钥。

随着团队的推出，我们引入了一种新型密钥：每用户密钥或 PUK。
从概念上讲，每用户密钥的秘密部分是为用户的所有活动设备和纸质密钥加密的。公钥部分在用户的签名链中公布。当用户添加新设备时，PUK 的秘密部分仅为新设备加密。当用户撤销设备时，会生成新的 PUK，并且所有剩余设备都会获得新的秘密部分。

## 密码学细节

用户从 PUK 第 1 代开始。每次撤销设备时，他们都会增加版本号并轮换 PUK。在第 *i* 代：

*   用户生成一个 32 字节的随机种子 *s*。
*   计算 *e* = HMAC-SHA256(*s*, `"Derived-User-NaCl-EdDSA-1"`) 并将此值用作 EdDSA 签名密钥的密钥。然后计算公钥部分，产生密钥对 *(E,e)*
*   计算 *d* = HMAC-SHA256(*s*, `"Derived-User-NaCl-DH-1"`) 并将此值用作 Curve25519 DH 加密密钥的密钥。然后计算公钥部分，产生密钥对 *(D,d)*
*   计算 *c* = HMAC-SHA256(*s*, `"Derived-User-NaCl-SecretBox-1"`) 并将此值用作对称密钥。

这个过程在每一代 *i* 重复。在任何给定的一代中，公钥 *E* 和 *D* 都被签署到用户的公共签名链中。每当添加新设备时，*s* 都会为新设备的设备密钥加密。这是一个瞬时操作，并且显着提高了我们之前考虑和实施的设计的密钥性能。这些 NaCl 盒子被写入服务器并存储在主数据库中。当前的 *s* 应该为每个活动设备都有一个盒子。

在设备撤销时，撤销设备会生成一个新的 PUK，为所有剩余设备的私钥加密，并将新的 PUK 与撤销旧设备的声明一起写入签名链。此外，每当密钥轮换时，前一个种子 *s*<sub>i</sub> 都会通过 NaCl 的 [SecretBox](https://nacl.cr.yp.to/secretbox.html) 对称加密使用 *c*<sub>*i*+1</sub> 进行加密，带有一个随机的 24 字节随机数。参见 [newPerUserKeyPrev](https://github.com/keybase/client/blob/527fae6d5389e2899c41c5bdcb5b7097e4e5eb50/go/libkb/per_user_key.go#L79-L111) 和 [openPerUsrKeyPrev](https://github.com/keybase/client/blob/527fae6d5389e2899c41c5bdcb5b7097e4e5eb50/go/libkb/per_user_key.go#L113-L163) 分别了解加密和解密的实现。

## 签名链表示

PUK 的公开部分写入用户的公共签名链。为了通过示例演示这一点，[这里](https://keybase.io/max/sigchain#24a4189169cf5cec3b1788353c4cd801a7ed0543bd7269aef7999bec25c022b70f)是 [max](https://keybase.io/max) 的签名链中的链接，他的客户端为他添加了一个 PUK。

相关部分是：

```javascript
{
  "body": {
    "per_user_key": {
      "encryption_kid": "0121f34ae7417cafa12d9d52bce5d6bdf4582f344f5aaa15022ea84d9ee54b6fe4070a",
      "generation": 1,
      "reverse_sig": "hKRib2R5hqhkZXRhY2hlZMOpaGFzaF90eXBlCqNrZXnEIwEgIFKhz54YC6M3WCKriGhYqjQrAEZMaeLZXebu5r8obpsKp3BheWxvYWTFA+R7ImJvZHkiOnsia2V5Ijp7ImVsZGVzdF9raWQiOiIwMTAxM2VmOTBiNGM0ZTYyMTIxZDEyYTUxZDE4NTY5YjU3OTk2MDAyYzhiZGNjYzliMjc0MDkzNWM5ZTRhMDdkMjBiNDBhIiwiaG9zdCI6ImtleWJhc2UuaW8iLCJraWQiOiIwMTIwNWQyZTM0YTcxM2UwMmE1ZWM1MGMzZjQxZGNkY2RhMGI5YTFkZTc0YmI1NTQ0NGNmNmI0ZGZiZjU0MTQ4N2QyNjBhIiwidWlkIjoiZGJiMTY1Yjc4NzlmZTdiMTE3NGRmNzNiZWQwYjk1MDAiLCJ1c2VybmFtZSI6Im1heCJ9LCJtZXJrbGVfcm9vdCI6eyJjdGltZSI6MTQ5ODY3NTE1MywiaGFzaCI6IjE1YTI0ZjA0MmVhODIzNjNmYjVmZmI3ZGZlYjUzM2JmYzE4YzdkNzQ3NDRkMDllYzQ2OTNjY2I3NmM2MDdjNzFkMWRmNmM1NThiMjNiNjZhNjFjMDNjMGQ5ZjBlOWM4YmE5NjExMTUyNzY1NDUzYjkyYmYyZjA4NjE0ZGVkNzI0IiwiaGFzaF9tZXRhIjoiMDdiZDU2NzZhMzgwYmU4ZDg2NWYwNmZkNDUzYzMwMTNhNTMwYTE2MzVlODk5YTg2NDRlMzUyZThiOGJiMTg2MCIsInNlcW5vIjoxMTk5MTE3fSwicGVyX3VzZXJfa2V5Ijp7ImVuY3J5cHRpb25fa2lkIjoiMDEyMWYzNGFlNzQxN2NhZmExMmQ5ZDUyYmNlNWQ2YmRmNDU4MmYzNDRmNWFhYTE1MDIyZWE4NGQ5ZWU1NGI2ZmU0MDcwYSIsImdlbmVyYXRpb24iOjEsInJldmVyc2Vfc2lnIjpudWxsLCJzaWduaW5nX2tpZCI6IjAxMjAyMDUyYTFjZjllMTgwYmEzMzc1ODIyYWI4ODY4NThhYTM0MmIwMDQ2NGM2OWUyZDk1ZGU2ZWVlNmJmMjg2ZTliMGEifSwidHlwZSI6InBlcl91c2VyX2tleSIsInZlcnNpb24iOjF9LCJjbGllbnQiOnsibmFtZSI6ImtleWJhc2UuaW8gZ28gY2xpZW50IiwidmVyc2lvbiI6IjEuMC4yNSJ9LCJjdGltZSI6MTQ5ODY3NTE4NSwiZXhwaXJlX2luIjo1MDQ1NzYwMDAsInByZXYiOiJiYWUwNWNjYWY0NzA3NDI4ZDUyNmJlYzY0MDQwMzFmYWQxZDcyMTMwYjI3NjNlMmEwYzU4MTBmOTNkZmUwNTQxIiwic2Vxbm8iOjMxMywidGFnIjoic2lnbmF0dXJlIn2jc2lnxEAekn745bQbOQLMdvurkVCQy6iKU3Tn2em8aTQlQtF5c4X0Upc+nNnQbR2KqSYNpSP2Ed83VoY0/dMKNfSZfWoNqHNpZ190eXBlIKRoYXNogqR0eXBlCKV2YWx1ZcQgDx5WL2Mwr2vEFphfaTGDtFS1jUa84efjIEmVKEXwb0qjdGFnzQICp3ZlcnNpb24B",
      "signing_kid": "01202052a1cf9e180ba3375822ab886858aa342b00464c69e2d95de6eee6bf286e9b0a"
    },
    "type": "per_user_key",
  },
}
```

与任何签名密钥一样，*反向签名*是用新的签名密钥对整个 JSON 主体进行计算的，但反向签名设置为空。这证明用户知道对应于公布的 `signing_kid` 的私钥。

这些链接中的一个出现在每个 PUK 世代，或者大致上，每当用户*撤销*设备时。

## 团队

用户所在的团队将需要轮换其共享的对称密钥，但这可以懒惰地发生（在下一次写入之前）并且不在关键路径上（参见 [级联惰性密钥轮换 (CLKR)](/docs/teams/clkr)）。

## 推出

刚刚加入 Keybase 的用户在配置他们的第一台设备时会获得一个 PUK。
一些用户在 PUK 推出之前就很活跃，他们的客户端在软件升级时会机会主义地升级以包含 PUK。

注意，此更改引入了用户可能处于的新状态：他们已注册 keybase，拥有设备密钥，但没有上述的 PUK。新的 CLI 用户不会到达这里，但旧用户和新的 Web 用户会。这使得某些流程（如邀请用户加入团队）更加复杂。
