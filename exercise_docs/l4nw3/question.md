<!-- HEADER -->
[Previous](../l2nw3/answer.md) << [Index](../index.md) >> [Next](../l4nw3/answer.md)

---
<!-- /HEADER -->

<!-- TOC -->

- [L4NW-3 (問題編)](#l4nw-3-問題編)
  - [前置き](#前置き)
  - [構成図](#構成図)
  - [問題1](#問題1)
    - [(補足) Router.Bパケットフィルタの効果確認](#補足-routerbパケットフィルタの効果確認)

<!-- /TOC -->

# L4NW-3 (問題編)

## 前置き

- [L4NW-1](../l4nw1/question.md)
- [L4NW-2](../l4nw2/question.md)

この問題で知ってほしいこと :

* L3/L4 動作の組み合わせ
  * 「通信できない」のバリエーション: 何の通信がどこを通って、どのファイアウォールでフィルタされるか?
  * L3/L4 の知識を総合的に組み合わせた、実際的なトラブルシュート。経路制御によって規定される通信経路 (フローがどこを流れるか) と、その中でファイアウォールが何を見て通信を許可しているかを組み合わせて考えられること。

<details>

<summary>この問題で使用するコマンド :</summary>

* インタフェースの一覧表示・設定確認
  * IP アドレス一の確認
    * `ip addr show [dev インタフェース名]`
* ノード内のプロセス一覧
  * `ps -o pid,args` : `-o` 表示するフィールドの指定
    * 長い文字列が途中で削られるのを防ぎたい場合は `--width 100` のように最大幅を数字で指定する
* ノード内でオープンされているポートの一覧
  * `ss -ltn` : `-l` (listen), `-t` (tcp), `-n` (numeric), オプションは適宜選択すること
* ルーティングテーブルの確認
  * `ip route`
* L3 の通信確認
  * `ping 宛先IPアドレス` (オプション `-c N` は送信するパケット数を指定します。)
* L3 通信経路の確認
  * `traceroute 宛先IPアドレス`
+ L4 の通信確認 (:white_check_mark: 演習内では L4 はすべて Web サーバになっています)
  * `curl URL`
* Firewall パケットフィルタルールの一覧表示
  * `iptables -nvL`: オプション `--line-numbers` で行番号表示
* パケットキャプチャ (必要に応じて)
  * `tcpdump -l [-i インタフェース名]` : オプション `-l` がないとリアルタイムに表示されません。

</details>

## 構成図

図 1: l4nw3/question (`exercise/l4nw3/question.json`)

![Topology](topology.drawio.svg)

* [L4NW-1](../l4nw1/question.md) と同じトポロジです。
  * **L4NW-1 問題 2 の修正まで完了している状態** です。(ルータの経路設定や Server.A2 のプロセス起動方法などは修正済みです。)
* Router.B にファイアウォール機能をもたせた構造になっています。
  * ノード名は [L4NW-1](../l4nw1/question.md) で使用したときの名前のままですが、機能としては L4 パケットフィルタ機能を追加していて、ファイアウォールとして動作します。

## 問題1

下の表のように Host.B/C から Serer.A1/A2 の IP:Port に接続し、Web サーバに接続できるか確認してください。接続できない場合はその理由を挙げてください。

:bulb: curl の `-m` オプションはタイムアウト時間(秒)の指定です

|No.| Web 接続                       |Web 接続できる?|
|---|--------------------------------|---------------|
| 1 |`hb curl -m 3 192.168.0.2:8080` | ? |
| 2 |`hb curl -m 3 192.168.0.10:8080`| ? |
| 3 |`hb curl -m 3 192.168.0.6:8080` | ? |
| 4 |`hb curl -m 3 192.168.0.14:8080`| ? |
| 5 |`hc curl -m 3 192.168.0.2:8080` | ? |
| 6 |`hc curl -m 3 192.168.0.10:8080`| ? |
| 7 |`hc curl -m 3 192.168.0.6:8080` | ? |
| 8 |`hc curl -m 3 192.168.0.14:8080`| ? |

### (補足) Router.Bパケットフィルタの効果確認

Router.B で設定されているパケットフィルタの効果を確認したい場合、以下の操作を試してください。

1. 一度パケットフィルタのルールを全部クリアして、上記の表あるいは [L4NW-1 問題2](../l4nw1/question.md) で使用したテストスクリプトを実行してみてください。
2. 再度パケットフィルタルールを設定します。

```text
mininet> # [1]
mininet> rb sh ./l4nw3/rb_fw_clear.sh
mininet> rb iptables -nvL
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
mininet> sh ./nw_test.sh l4nw3
................

Total Duration: 0.438s
Count: 16, Failed: 0, Skipped: 0
mininet> 
mininet> # [2]
mininet> rb sh ./l4nw3/rb_fw.sh
mininet> rb iptables -nvL
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain FORWARD (policy DROP 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 ACCEPT     icmp --  *      *       0.0.0.0/0            0.0.0.0/0
    0     0 ACCEPT     tcp  --  *      *       192.168.0.16/30      192.168.0.0/29       tcp dpt:8080
    0     0 ACCEPT     tcp  --  *      *       192.168.0.24/30      192.168.0.0/30       tcp dpt:8080
    0     0 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            state RELATED,ESTABLISHED
    0     0 REJECT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            reject-with icmp-port-unreachable

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
mininet> 
```

<!-- FOOTER -->

---

[Previous](../l2nw3/answer.md) << [Index](../index.md) >> [Next](../l4nw3/answer.md)
<!-- /FOOTER -->
