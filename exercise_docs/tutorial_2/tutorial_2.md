<!-- HEADER -->
[Previous](../tutorial_1/tutorial_1.md) << [Index](../index.md) >> [Next](../tutorial_3/tutorial_3.md)

---
<!-- /HEADER -->

<!-- TOC -->

- [チュートリアル2](#チュートリアル2)
  - [このチュートリアルの目的](#このチュートリアルの目的)
  - [単一のL2セグメントの動作](#単一のl2セグメントの動作)
  - [L2スイッチの設定情報を確認する](#l2スイッチの設定情報を確認する)
  - [通常のL2セグメント内の通信を見てみる](#通常のl2セグメント内の通信を見てみる)
  - [IPアドレス重複がある場合の動作を見てみる](#ipアドレス重複がある場合の動作を見てみる)
  - [チュートリアル2のまとめ](#チュートリアル2のまとめ)

<!-- /TOC -->

# チュートリアル2

## このチュートリアルの目的

使い方の理解

* 演習ネットワークとして用意されるものとその操作
  * スイッチ (ブリッジ)
  * スイッチの設定情報の確認
  * スイッチの状態の確認
  * 通信確認コマンドの動作 (ping)

ネットワーク知識の理解

* スイッチが "媒体 (メディア)" としてどのように動くかを確認する
* 単一の L2 セグメントの動作 : "同じ部屋の中の複数ノード" で通信がどう成立するかを見てみる
  * スイッチの forwarding table の内容
  * 障害をおこしてみる
    * IP アドレス重複

## 単一のL2セグメントの動作

チュートリアル 2 のネットワークを起動します。

- :warning: 見たい動作があるので、起動後は指示があるまで `ping` など通信確認系のコマンドを実行しないでください。

```bash
cd /exercise
./nw_training.py tutorial_2/tutorial_2.json
```

起動したら Mininet CLI で `nodes`, `links`, `net` を実行し、図のようなトポロジになっていることを確認してください。

![Topology A/B](topology.drawio.svg)

- ネットワークには 2 台スイッチがあります (Switch.1, Switch.2)。それぞれ 1 つのブリッジ (L2 セグメント = ブロードキャストドメイン) として動作します。
- 4 台のノードが Switch.1 に接続されています。
  - 4 台とも、192.168.0.0/24 のサブネットに所属しています。
  - Host.C と Host.D は同じ IP アドレスを持っています(IP アドレス重複)。

## L2スイッチの設定情報を確認する

スイッチは Open vSwitch というソフトウェアで構成されています。`ovs-vsctl show` (Shell ターミナル) で設定情報を確認できます。

```text
root@nwtraining01:/# ovs-vsctl show
83c670f3-306d-4f3f-be2f-a8f5d0c461ed
    Bridge sw2
        fail_mode: standalone
        Port sw2-eth1
            Interface sw2-eth1
        Port sw2
            Interface sw2
                type: internal
        Port sw2-eth0
            Interface sw2-eth0
    Bridge sw1
        fail_mode: standalone
        Port sw1-eth4
            Interface sw1-eth4
        Port sw1-eth10
            Interface sw1-eth10
        Port sw1-eth2
            Interface sw1-eth2
        Port sw1
            Interface sw1
                type: internal
        Port sw1-eth11
            Interface sw1-eth11
        Port sw1-eth1
            Interface sw1-eth1
        Port sw1-eth3
            Interface sw1-eth3
    ovs_version: "2.13.0"
```

以下の点を認識してください:

* 2 つのスイッチ (`Bridge`) がある
  * 1 つのスイッチが 1 つの L2 セグメントになる
* スイッチに対してポート (`Port`) が割り当てられている

:customs: 用語の使い分けについて:

* 以下の用語について、この演習の中では厳密な使い分けをしていません。同様の意味合いで見てください。
  * スイッチ/ブリッジ
  * ポート/インタフェース
* Open vSwitch (OVS) 設定のなかでは `Bridge`, `Port`, `Interface` を OVS 内部のデータモデル定義として使用しています。演習中で使用する「スイッチ」「ポート」「インタフェース」などの用語とは厳密に一致しているわけではないので注意してください。

## 通常のL2セグメント内の通信を見てみる

まず、同一 L2 セグメント内での一般的な通信がどのように行なわれているかを見てみます。Host.A のパケット送受信をパケットキャプチャで取りながら Host.A - Host.B 間で通信してみます。

(Shell ターミナル) パケットキャプチャ@Host.A

```text
root@nwtraining01:/# ip netns exec ha tcpdump -l
...
```

(Mininet ターミナル) ping Host.A → 192.168.0.2 (Host.B)

```text
mininet> ha ping -c3 192.168.0.2
PING 192.168.0.2 (192.168.0.2) 56(84) bytes of data.
64 bytes from 192.168.0.2: icmp_seq=1 ttl=64 time=0.350 ms
64 bytes from 192.168.0.2: icmp_seq=2 ttl=64 time=0.115 ms
64 bytes from 192.168.0.2: icmp_seq=3 ttl=64 time=0.108 ms

--- 192.168.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2037ms
rtt min/avg/max/mdev = 0.108/0.191/0.350/0.112 ms
mininet> 
mininet> ha arp
❶Address                HWtype  ❷HWaddress         Flags Mask            Iface
192.168.0.2              ether   b2:1f:c3:b2:9b:89   C                     ha-eth0
```

`arp` コマンドは、L3 ノードの **ARP テーブル** を表示しています。通信相手は L3 のアドレス (IP アドレス) で識別されますが、実際にデータを送信するためには 1 つ下のレイヤである L2 の情報が必要です。L2 = "声の届く空間" = "部屋" モデルで考えると、MAC アドレスは部屋内の席番号のようなものです。

* ARP テーブルは、❶ IP アドレス (L3) と ❷ **MAC アドレス** (L2) の対応関係を保持するテーブルです。上の実行例では、IP アドレス 192.168.0.2 を持っているのは MAC アドレス b2:1f:c3:b2:9b:89 の機器であることを意味します。
* MAC アドレスは L2 のプロトコルとして ethernet を使ったとき使われるアドレスで、通常はネットワークインタフェース (ハードウェア) ごとに設定されます。

ARP テーブルの情報は、ノード間で **ARP メッセージ** のやり取りをすることで取得されます。このとき Shell ターミナルで見ていたパケットキャプチャを見ると、**ARP request/reply** が行なわれてから ping (ICMP) 通信が実行されています。通常 (通信相手が一意に識別できる場合) はこのように、通信先(相手)の IP アドレスと MAC アドレス、L2/L3 情報の対応づけをした上で通信が行なわれます。

```text
...
14:34:31.302364 ❸ARP, Request who-has 192.168.0.2 tell 192.168.0.1, length 28
14:34:31.302549 ❹ARP, Reply 192.168.0.2 is-at b2:1f:c3:b2:9b:89 (oui Unknown), length 28
14:34:31.302571 IP 192.168.0.1 > 192.168.0.2: ICMP echo request, id 475, seq 1, length 64
14:34:31.302679 IP 192.168.0.2 > 192.168.0.1: ICMP echo reply, id 475, seq 1, length 64
14:34:32.316975 IP 192.168.0.1 > 192.168.0.2: ICMP echo request, id 475, seq 2, length 64
14:34:32.317044 IP 192.168.0.2 > 192.168.0.1: ICMP echo reply, id 475, seq 2, length 64
14:34:33.339395 IP 192.168.0.1 > 192.168.0.2: ICMP echo request, id 475, seq 3, length 64
14:34:33.339461 IP 192.168.0.2 > 192.168.0.1: ICMP echo reply, id 475, seq 3, length 64
...
```

❸ ARP request の ”この IP アドレスを持っているのは誰?"、❹ ARP reply の ”その IP アドレスは <MAC アドレス> にいるよ" というやり取りに注目してください。

ここで実行した tcpdump オプションだと L2 の送信元・先の情報が出ていませんが、ARP request は全員宛 (**ブロードキャスト**) になります。また、ARP reply は持ち主からの返答 (ユニキャスト) になります。(`tcpdump -l -e` として `-e` オプションをつけると L2 の送信元・送信先情報も出力されます。余裕があれば試してみてください。)

## IPアドレス重複がある場合の動作を見てみる

もし同一 L2 セグメントの中に同じ IP アドレスを持つノードが複数(ここでは 2 ノード)いるとどうなるでしょうか? Host.A と Host.C/D との通信で同様にパケットキャプチャを取ってみます。

(Shell ターミナル) パケットキャプチャの準備 @Host.A

```text
root@nwtraining01:/# ip netns exec ha tcpdump -l
...
```

(Mininet ターミナル) ping Host.A → 192.168.0.3 (Host.C or Host.D)

* いったん 192.168.0.3 についての ARP テーブルエントリをクリアしてから ping します

```text
mininet> ha arp -d 192.168.0.3
mininet> ha ping -c3 192.168.0.3
PING 192.168.0.3 (192.168.0.3) 56(84) bytes of data.
64 bytes from 192.168.0.3: icmp_seq=1 ttl=64 time=0.351 ms
64 bytes from 192.168.0.3: icmp_seq=2 ttl=64 time=0.038 ms
64 bytes from 192.168.0.3: icmp_seq=3 ttl=64 time=0.072 ms

--- 192.168.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2051ms
rtt min/avg/max/mdev = 0.038/0.153/0.351/0.140 ms
```

通信できていますが、これは Host.C/D どちらでしょうか?

```text
mininet> ha arp
Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.0.3              ether ❶46:2c:ed:3d:a3:f0   C                     ha-eth0
192.168.0.2              ether   b2:1f:c3:b2:9b:89   C                     ha-eth0
mininet> 
mininet> hc ip link show dev hc-eth0
2: hc-eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether ❷46:2c:ed:3d:a3:f0 brd ff:ff:ff:ff:ff:ff link-netnsid 0
mininet> 
mininet> hd ip link show dev hd-eth0
2: hd-eth0@if10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether ❸2e:fb:31:c8:6f:f1 brd ff:ff:ff:ff:ff:ff link-netnsid 0
```

Host.A の ARP テーブルを見ると、Host.C と通信していたようです。これは、Host.A の ARP テーブルで 192.168.0.3 を持っているのが ❶ MAC アドレス 46:2c:ed:3d:a3:f0 のノードであることからわかります。この MAC アドレスを持っているのは ❷ Host.C (hc-eth0) です。

* __:warning: 通信応答順(タイミング)等にもよるので、必ず同じ結果になるわけではありません。__ 自分の環境ではどちらと通信していたかを確認してください。

Host.A でとっていた、ping したときのパケットキャプチャも確認してみましょう。

* 1 回の ARP Request ❹ に対して 2 個の ARP Reply ❺❻ が返ってきている点に注目してください
  * ARP reply ❺ が返ってきて IP/MAC アドレスの解決ができた時点で ping 送信を開始しているようです

```text
...
14:44:51.565574 ❹ARP, Request who-has 192.168.0.3 tell 192.168.0.1, length 28
14:44:51.565767 ❺ARP, Reply 192.168.0.3 is-at 46:2c:ed:3d:a3:f0 (oui Unknown), length 28
14:44:51.565774 IP 192.168.0.1 > 192.168.0.3: ICMP echo request, id 481, seq 1, length 64
14:44:51.565788 ❻ARP, Reply 192.168.0.3 is-at 2e:fb:31:c8:6f:f1 (oui Unknown), length 28
14:44:51.565935 IP 192.168.0.3 > 192.168.0.1: ICMP echo reply, id 481, seq 1, length 64
14:44:52.575487 IP 192.168.0.1 > 192.168.0.3: ICMP echo request, id 481, seq 2, length 64
14:44:52.575571 IP 192.168.0.3 > 192.168.0.1: ICMP echo reply, id 481, seq 2, length 64
14:44:53.597171 IP 192.168.0.1 > 192.168.0.3: ICMP echo request, id 481, seq 3, length 64
14:44:53.597284 IP 192.168.0.3 > 192.168.0.1: ICMP echo reply, id 481, seq 3, length 64
...
```

このとき、Host.A から通信したいのが本当は Host.D だったとすると、Host.A は異なる宛先としか通信できない状況にあります。本来通信したい相手に投げたつもりのパケットが、同じ IP アドレスを持つ別なノードに「吸い込まれて」しまっている状態です。

(Mininet ターミナル) 通信できなかった側 (Host.D) から Host.A へ ping してみましょう。

```text
mininet> # [1]
mininet> ha arp
Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.0.3              ether ❼46:2c:ed:3d:a3:f0   C                     ha-eth0
192.168.0.2              ether   b2:1f:c3:b2:9b:89   C                     ha-eth0
mininet> 
mininet> # [2]
mininet> hd ping -c3 ha
PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.

--- 192.168.0.1 ping statistics ---
3 packets transmitted, 0 received, ❽100% packet loss, time 2044ms

mininet> 
mininet> # [3]
mininet> ha arp
Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.0.3              ether ❾2e:fb:31:c8:6f:f1   C                     ha-eth0
192.168.0.2              ether   b2:1f:c3:b2:9b:89   C                     ha-eth0
mininet> 
mininet> # [4]
mininet> hd ping -c3 ha
PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.
64 bytes from 192.168.0.1: icmp_seq=1 ttl=64 time=0.194 ms
64 bytes from 192.168.0.1: icmp_seq=2 ttl=64 time=0.041 ms
64 bytes from 192.168.0.1: icmp_seq=3 ttl=64 time=0.056 ms

--- 192.168.0.1 ping statistics ---
3 packets transmitted, 3 received, ❿0% packet loss, time 2043ms
rtt min/avg/max/mdev = 0.041/0.097/0.194/0.068 ms
```

1. 前提条件として、Host.A の ARP テーブルでは、192.168.0.3 を ❼ Host.C へ送るようになっています
2. そのため、Host.D から Host.A へ ping request を送ると、ping reply は Host.A から Host.C に送信されます。Host.D は応答を受信できずに、❽ 100％ packet loss となります。
3. その後、Host.A で再度 ARP テーブルを確認すると 192.168.0.3 が ❾ Host.D の MAC アドレスに変わっています。 (2. ping に際して Host.D-Host.A の ARP 更新が行なわれる)
4. この状態であれば、Host.D から Host.A への ping は正しく送受信できます(❿)

このように、同じサブネットの中で IP アドレスが重複する場合、通信先が ARP 応答や ARP テーブルエントリの変化のタイミングなどで変わってしまい、非常に不安定な状態になります。(ARP テーブルのエントリには有効期限があり、使用されないエントリは一定時間で消去されます。)

## チュートリアル2のまとめ

* Layer2 ネットワークの基本的な動作 (ARP と ping)
* IP アドレス重複問題

チュートリアル 2 はここまでです。演習ネットワークを終了させて[チュートリアル 3](../tutorial_3/tutorial_3.md) に進んでください。

```text
mininet> exit
```

<!-- FOOTER -->

---

[Previous](../tutorial_1/tutorial_1.md) << [Index](../index.md) >> [Next](../tutorial_3/tutorial_3.md)
<!-- /FOOTER -->
