<!-- HEADER -->
[Previous](../l4nw1/answer.md) << [Index](../index.md) >> [Next](../l4nw2/answer.md)

---
<!-- /HEADER -->

# L4NW-2 (問題編)

## 前置き

前提

- [チュートリアル 7](../tutorial7/scenario.md): L4 基礎
- [L4NW-1](../l4nw1/question.md)

この問題で知ってほしいこと :

- ファイアウォール基礎設定
  - IP アドレスの集約・アドレス設計の考え方とファイアウォールルールの関係
  - パケットフィルタルールの考え方
- 通信フローとファイアウォール位置
  - L3 経路制御と通信フローの考え方を理解する (どこから、どこに、何が、どんな経路で流れるのか)
  - フローとファイアウォールの関係
    - ファイアウォールはなぜそこに置かれるのか?
    - ファイアウォールの位置、そこを流れる通信 (L3 経路制御) の関係
- 「通信要件」とファイアウォールの関係
  - ネットワークの設定（経路制御・ファイアウォールポリシ）を検討するために、なぜ「通信要件」の情報が必要になるのか?

<details>

<summary>この問題で使用するコマンド :</summary>

* インタフェースの一覧表示・設定確認
  * IP アドレス一の確認
    * `ip addr show [dev インタフェース名]`
* ノード内のプロセス操作
  * プロセス一覧表示
    * `ps -o pid,args` : `-o` 表示するフィールドの指定。長い文字列が途中で削られるのを防ぎたい場合は `--width 100` のように最大幅を数字で指定する。
  * プロセス停止
    * `kill プロセスID`
* ノード内でオープンされているポートの一覧
  * `ss -ltn` : `-l` (listen), `-t` (tcp), `-n` (numeric), オプションは適宜選択すること
* L3 の通信確認
  * `ping 宛先IPアドレス` (オプション `-c N` は送信するパケット数を指定します。)
* L3 通信経路の確認
  * `traceroute 宛先IPアドレス`
* ルーティングテーブルの確認
  * `ip route`
* ルーティングテーブルの操作 (静的経路の追加・削除)
  * `ip route add 宛先ネットワーク via 中継先ルータ(nexthop)IPアドレス`
  * `ip route del 宛先ネットワーク`
+ L4 の通信確認 (:customs: 演習内では L4 はすべて Web サーバになっています)
  * `curl URL`
* パケットキャプチャ (必要に応じて)
  * `tcpdump -l [-i インタフェース名]` : オプション `-l` がないとリアルタイムに表示されません。

</details>

## 構成図

図 1: l4nw2/question (`exercise/l4nw2/questsion.json`)

![Topology](topology.drawio.svg)

* [L4NW-1](../l4nw1/question.md) と同じトポロジです。
  * **L4NW-1 問題 2 の修正まで完了している状態** です。(ルータの経路設定や Server.A2 のプロセス起動方法などは修正済みです。)
* Router.B にファイアウォール機能をもたせた構造になっています。
  * ノード名は [L4NW-1](../l4nw1/question.md) で使用したときの名前のままですが、機能としては L4 パケットフィルタ機能を追加していて、ファイアウォールとして動作します。

## 問題1

Router.B はファイアウォールとして動作していますが、初期状態ではまだなにもパケットフィルタルールが設定されていません。初期状態では以下のようになっています。簡単に言えば、ICMP (ping) と TCP の通信は無条件で許可された状態です。

* ❶ 任意の送信元・先について、ICMP (ping) 通信が許可されています
* ❷ 任意の送信元・先について、TCP 通信が許可されています。
* ❸ 任意の送信元・先について、コネクションの確立した TCP 通信が許可されています。
* ❹ 上記以外は拒否されます。

```text
mininet> rb iptables -nvL
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy DROP 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
❶  0     0 ACCEPT     icmp --  *      *       0.0.0.0/0            0.0.0.0/0           
❷  0     0 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           
❸  0     0 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            state RELATED,ESTABLISHED
❹  0     0 REJECT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            reject-with icmp-port-unreachable

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
```

### 問題1A

Router.B 初期状態のルール ❷ を以下ルールに変更した際、Host.B から Server.A1/2 がもつ IP アドレスへの HTTP 通信が成功するかどうかを確認してください。

```sh
iptables -A FORWARD -s 192.168.0.16/30 -d 192.168.0.0/30 -p tcp --dport 8080 -j ACCEPT
#                                                    ^^^^
```

|No.| HTTP request                                     | 成功? |
|---|--------------------------------------------------|-------|
| 1 | `hb curl http://192.168.0.2:8080/`  (hb → sa1 eth0) | ? |
| 2 | `hb curl http://192.168.0.10:8080/` (hb → sa1 eth1) | ? |
| 3 | `hb curl http://192.168.0.6:8080/`  (hb → sa2 eth0) | ? |
| 4 | `hb curl http://192.168.0.14:8080/` (hb → sa2 eth1) | ? |

ルールの変更は、次のように問題 1A 用スクリプト (`rb_fw_q1a.sh`) で実施できます。

```text
mininet> rb sh l4nw2/rb_fw_q1a.sh   
mininet> rb iptables -nvL 
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy DROP 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
    0     0 ACCEPT     icmp --  *      *       0.0.0.0/0            0.0.0.0/0           
    0     0 ACCEPT     tcp  --  *      *       192.168.0.16/30      192.168.0.0/30       tcp dpt:8080
    0     0 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            state RELATED,ESTABLISHED
    0     0 REJECT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            reject-with icmp-port-unreachable

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
```

### 問題1B

問題 1A で追加したルールを削除し、以下のルールに置き換えます。同様に各 IP アドレスに対して HTTP 通信が成功するかどうかを確認してください。

```sh
iptables -A FORWARD -s 192.168.0.16/30 -d 192.168.0.0/29 -p tcp --dport 8080 -j ACCEPT
#                                                    ^^^^
```

|No.| HTTP request                                     | 成功? |
|---|--------------------------------------------------|-------|
| 5 | `hb curl http://192.168.0.2:8080/`  (hb → sa1 eth0) | ? |
| 6 | `hb curl http://192.168.0.10:8080/` (hb → sa1 eth1) | ? |
| 7 | `hb curl http://192.168.0.6:8080/`  (hb → sa2 eth0) | ? |
| 8 | `hb curl http://192.168.0.14:8080/` (hb → sa2 eth1) | ? |

ルールの変更は、次のように問題 1B 用スクリプト (`rb_fw_q1b.sh`) で実施できます。

```text
mininet> rb sh l4nw2/rb_fw_q1b.sh
mininet> rb iptables -nvL
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy DROP 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
    0     0 ACCEPT     icmp --  *      *       0.0.0.0/0            0.0.0.0/0           
    0     0 ACCEPT     tcp  --  *      *       192.168.0.16/30      192.168.0.0/29       tcp dpt:8080
    0     0 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            state RELATED,ESTABLISHED
    0     0 REJECT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            reject-with icmp-port-unreachable

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
```

### 問題1C

問題 1A/1B の設定は何が異なっていて、どうしてその結果になるかを説明してください。

### 補足: パケットフィルタのルール操作

問題 1A/1B 用パケットフィルタ設定スクリプトは、いったんルールをリセットしてから各問題用のルールを書き込むようになっています。いつ実行しても同じ結果 (各問題用のフィルタルール) に設定されます。

> [!IMPORTANT]
> パケットフィルタのルール設定を間違えた場合は、リセット用のスクリプトで初期状態に戻すことができます。Router.B でリセット用のスクリプトを実行してください。

```text
mininet> rb sh l4nw2/rb_fw_init.sh
```

## 問題2

この問題は机上検討の問題です。

図 1 の環境で、Router.B のみがファイアウォールとして動作するものと考えます。この時 :

* サーバへの HTTP アクセスを遮断**できない**のは、以下の表のどれでしょうか?
  * ここでは、「HTTP アクセスの遮断」= ホストから送信した HTTP リクエストがサーバへ届かないようにすること、とします。
* それはなぜですか?

|No.| From   | To          | Router.Bで遮断可能? |
|---|--------|-------------|---------------------|
| 1 | Host.B | Server.A1 eth0 (192.168.0.2)  | ? |
| 2 | Host.B | Server.A2 eth1 (192.168.0.14) | ? |
| 3 | Host.C | Server.A1 eth0 (192.168.0.2)  | ? |
| 4 | Host.C | Server.A2 eth1 (192.168.0.14) | ? |


<!-- FOOTER -->

---

[Previous](../l4nw1/answer.md) << [Index](../index.md) >> [Next](../l4nw2/answer.md)
<!-- /FOOTER -->
