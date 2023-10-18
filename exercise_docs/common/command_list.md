<!-- HEADER -->
Previous << [Index](../index.md) >> [Next](../common/glossary.md)

---
<!-- /HEADER -->

# コマンドリスト

:warning: 演習コンテナ内での操作はすべて root 権限になっているので注意してください。

## 演習コンテナ操作

演習コンテナ外部での操作です。
[チュートリアル0](../tutorial0/scenario.md) も参照してください。

### コンテナの起動確認・起動

クローンされた本リポジトリで、"lab" コンテナが起動している (State: Up になっている) ことを確認してください。

```text
# cd ~
# git clone https://github.com/infra-handson/network-training.git
# 上記のように、$HOME にリポジトリをクローンしたと仮定して

$ cd ~/network-training
$ docker-compose --compatibility ps
         Name                       Command               State   Ports
-----------------------------------------------------------------------
network-training_lab_1   /bin/bash -c ovs-ctl start ...   Up
```

コンテナが起動していない (何も表示されない) 場合は下記のコマンドで起動させます。

```text
$ # cd ~/network-training
$ docker-compose --compatibility up -d
```

### コンテナに入る・出る

コンテナで bash を実行してコンテナ内に入ります。コンテナに入るとプロンプトが `root@nwtraining01` に変わります。

```text
$ docker-compose exec lab bash
root@nwtraining01:/#
```

または

```text
$ docker exec -it network-training_lab_1 bash
root@nwtraining01:/#
```

`exit` でコンテナ内で実行した bash を終了させるとコンテナから出ます。

## 演習ネットワークの操作

演習コンテナ内部での操作です。

### 起動・停止

- 演習ネットワークの構築には [Mininet](http://mininet.org/) を使用しています。
- Mininet をつかって演習ネットワークを自動構築・設定する演習スクリプト (`nw_training.py`) を使用するので Mininet コマンド (`mn`) を直接操作することはありません。
- Mininet CLI で `exit` を入力して終了すると、演習ネットワークは自動的に消去されます。

演習ネットワークの起動

```text
cd /exercise
./nw_training.py 演習ネットワーク定義ファイル(json)
```

### 強制リセット

- 演習スクリプト実行時・終了時にエラーが出る場合は、強制リセットコマンドで演習ネットワークをクリアします。
  - `mn -c`/`mn --clean` : Mininet の強制リセット
  - `nw_training.py` の中で一部ノード用 namespace に mininet CLI 外部から操作可能にするためのシンボリックリンクを設定しています。強制リセットする際には `/var/run/netns` も削除してください。

演習ネットワークの強制リセット操作

```sh
mn -c
rm -rf /var/run/netns
```

## Mininet CLI

### Mininet 固有のコマンド・操作

- コマンドヘルプ表示
  - `?` または `help`
- mininet CLI 終了
  - `exit` または `quit`
- 演習ネットワーク内ノード・インタフェース・リンク一覧表示、トポロジの確認
  - `nodes`
  - `intfs`
  - `links`
  - `net`
- (optional) 特定仮想ノードの端末を別ウィンドウで表示
  - `xterm ノード名`

### コンテナ shell でのコマンド実行

Mininet CLI から shell コマンドを呼び出せます。

```text
mininet> sh 任意のコマンド
```

## 演習ネットワーク中ノードでのコマンド実行

Mininet CLI から演習ネットワーク内のノード上でコマンドを実行したい場合は、下記の実行例のように、コマンドを実行したいノード名 + コマンドを入力してください。演習ネットワーク内の各ノードでは、演習環境コンテナに含まれているコマンドが使用できます。

```text
mininet> ノード名 コマンド
```

### 参考

\@IT Linux 基本コマンド Tips
- [【 ps 】コマンド――実行中のプロセスを一覧表示する](https://www.atmarkit.co.jp/ait/articles/1603/28/news022.html)
- [【 kill 】コマンド／【 killall 】コマンド――実行中のプロセスを終了させる](https://atmarkit.itmedia.co.jp/ait/articles/1604/05/news022.html)
- [【 curl 】コマンド――さまざまなプロトコルでファイルをダウンロード（転送）する](https://www.atmarkit.co.jp/ait/articles/1606/22/news030.html)
- [【 ping 】コマンド／【 ping6 】コマンド――通信相手にパケットを送って応答を調べる](https://www.atmarkit.co.jp/ait/articles/1709/14/news018.html)
- [【 traceroute 】コマンド／【 traceroute6 】コマンド――ネットワークの経路を調べる](https://www.atmarkit.co.jp/ait/articles/1709/15/news016.html)
- [【 ip 】コマンド（基礎編）――ネットワークデバイスのIPアドレスを表示する](https://www.atmarkit.co.jp/ait/articles/1709/22/news019.html)
- [【 ss 】コマンド――ネットワークのソケットの情報を出力する](https://www.atmarkit.co.jp/ait/articles/1710/06/news014.html)
- [【 arp 】コマンド――ARPテーブルを管理する](https://www.atmarkit.co.jp/ait/articles/1710/26/news034.html)

### ノード内のプロセス確認・停止

- `ps -Ho pid,args` (`-H`: process hierarchy, `-o format`: user defined format. see: `man ps`)
  - 長いコマンドが途中で切られてしまう場合、 `--width NN` で横幅を指定してください。
  - :warning: mininet で作成した仮想ノードは、プロセス空間が分離されていないので、`ps -e` などでは全ノードのプロセスが見えます。
- `kill プロセスID`
  - プロセスの停止
### 通信確認

- `ping 宛先IPアドレス　[-I 送信元IPアドレスまたはインタフェース名]`
  - 複数インタフェースを持つデバイスでは `-I` でどこから送付するか(送信元)を指定できる
- `traceroute 宛先IPアドレス`
  - 宛先までの L3 経路を調査する
- `curl http://IPアドレス:ポート/`
  - 接続タイムアウトの設定: `-m 秒数`
- `ss -nlt4` (`-n`: numeric, `-l`: listen, `-t`: tcp, `-4`: ipv4)
  - どのポートで listen しているかを表示する
- `tcpdump`
  - パケットキャプチャを取得する (多数のオプションがあるので別途検索してください)
  - :warning: リアルタイムに状況を確認するため `-l` オプションを指定してください (標準出力をバッファリングしない)
  - `-e` : Layer2 の送信元・送信先情報を表示します
  - `-I インタフェース名` : 指定したインタフェースで送受信しているパケットのみキャプチャします

### 通信設定 (インタフェース操作)

- `ip` コマンドの詳細については `man ip` か "iproute2" で検索してください。
- インタフェース一覧・MAC アドレスの確認
  - `ip link show [dev インタフェース名]`
  - ref: [Output format:](http://linux-ip.net/gl/ip-cref/ip-cref-node17.html)
- インタフェース IP アドレス一覧の確認
  - `ip addr show [dev インタフェース名]`
- インタフェースに対する IP アドレスの設定/削除
  - `ip addr add IPアドレス dev インタフェース名`
  - `ip addr del IPアドレス dev インタフェース名`
  - IP アドレスは "a.b.c.d/nn" 形式で指定
  - ref: [Output format:](http://linux-ip.net/gl/ip-cref/ip-cref-node34.html)
- インタフェースの up/down
  - `ip link set インタフェース名 up`
  - `ip link set インタフェース名 down`
- インタフェースの詳細情報を表示 (VLAN サブインタフェースでは vlan-id の確認)
  - `ip -d link show インタフェース名`

```text
mininet> sa ip -d link show sa-eth0.10
3: sa-eth0.10@sa-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 9a:12:ea:9f:5e:bb brd ff:ff:ff:ff:ff:ff promiscuity 0 minmtu 0 maxmtu 65535 
    vlan protocol 802.1Q id 10 <REORDER_HDR> addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
```

### 通信設定 (L2-L3テーブル操作)

- ARP テーブルの確認
  - `ip neigh show`
  - `arp [-n]`
    - `-n` (numeric): 数値をそのまま表示します (名前に置き換えません)。
- ARP テーブルのクリア
  - `ip neigh flush インタフェース名`
  - `arp -d IPアドレス`
- 経路情報 (ルーティングテーブル) の確認
  - `ip route show`
- 経路情報 (静的経路) の追加/削除
  - `ip route add 宛先ネットワークアドレス via ゲートウェイ(nexthop)IPアドレス`
  - `ip route del 宛先ネットワークアドレス`
  - 宛先ネットワークの範囲は "a.b.c.d/nn" 形式で指定
- 経路情報 (デフォルトルート) の追加/削除
  - `ip route add default via ゲートウェイ(nexthop)IPアドレス`
  - `ip route del default`

### 通信設定 (L4パケットフィルタ操作)

- フィルタルール（ポリシ）の確認 (`-v` (verbose) でルールにマッチしたパケットカウント, `--line-numbers` でルール行番号が表示されます)
  - `iptables -nvL [--line-numbers]`
- フィルタルールの全クリア (チェインポリシはリセットされません)
  - `iptables -F`
- Chain policy の変更(設定)
  - `iptables -P チェーン ポリシ`: 例 `iptables -P FORWARD ACCEPT` (FORWARD chain のポリシを許可 (accept) に設定する)
- ルールを追加
  - `iptables -A チェーン ルール` : 単純に(末尾に)追加されます。例 `iptables -A FORWARD -p icmp -j ACCEPT` (FORWARD chain に icmp を許可するルールを追加する)
- 行番号を指定してルールを挿入
  - `iptables -I チェーン 行番号 ルール`: 例 `iptables -I FORWARD 3 -p icmp -j DENY` (FORWARD chain の 3 行目にルールを挿入)
- 特定のフィルタルールの削除
  - `iptables -D チェーン 行番号`: 行番号でルールを指定して削除。例 `iptables -D FORWARD 5` (FORWARD chain の 5 行目の削除)
  - `iptables -D チェーン ルール`: 指定したルールを削除。例 `iptables -D FORWARD -p icmp -j ACCEPT` (FORWARD chain にある `-p icmp -j ACCEPT` ルールを削除)
- フィルタのルールは多数のオプションがあるので別途資料を参照してください
  - `[-p プロトコル] [-s 送信元アドレス] [--sport 送信元ポート] [-d 送信先アドレス] [--dport 送信先ポート] -j アクション`
  - [iptablesコマンドの使い方 - Qiita](https://qiita.com/hana_shin/items/956dfaca4539ba257c16)
  - [iptablesの仕組みを図解 - Carpe Diem](https://christina04.hatenablog.com/entry/iptables-outline)

## スイッチ基本操作

- OVS マニュアル類
  - [Project — Open vSwitch 2.15.90 documentation](https://docs.openvswitch.org/en/latest/)
  - [Open vSwitch 2.15.90 Documentation](https://www.openvswitch.org/support/dist-docs/)
    - OSDB Schema (図): http://www.openvswitch.org//ovs-vswitchd.conf.db.5.pdf
    - [ovs-vsctl](https://www.openvswitch.org/support/dist-docs/ovs-vsctl.8.txt)
    - [ovs-dpctl](http://www.openvswitch.org/support/dist-docs/ovs-dpctl.8.txt)
    - [ovs-appctl](https://www.openvswitch.org/support/dist-docs/ovs-appctl.8.txt)
- スイッチの設定情報確認
  - `ovs-vsctl show`
    - OVS は１つのサーバで複数のブリッジ(スイッチ)を作るので、全スイッチの情報が見えます。
  - 詳細な情報や状態の確認は OVSDB の検索が必要
    - 下記コマンドの `Bridge`, `Port` は OVSDB の特定のデータベースを指しています。
- スイッチ (ブリッジ) の状態確認
  - `ovs-vsctl list Bridge [スイッチ名]`
  - `ovs-vsctl --columns=name,status list Bridge [スイッチ名]` (必要な項目に限定)
    - 項目 `name` / `fail_mode` / `status` / `other_config` / `stp_enable` など
  - `ovs-vsctl --columns name,other_config,status list Bridge`
    - スイッチの STP 設定および状態確認 (`stp-priority` / `stp_bridge_id` / `stp_designated_root` / `stp_root_path_cost`)
- スイッチの MAC アドレステーブルの確認
  - `ovs-appctl fdb/show [スイッチ名]`
- スイッチの MAC アドレステーブルの消去
  - `ovs-appctl fdb/flush [スイッチ名]`
- ポート名とポート番号の確認
  - `ovs-dpctl show`
  - `ovs-vsctl --columns=name,ofport list Interface [ポート名]`
- ポート (インタフェース) の状態確認
  - `ovs-vsctl list Port [ポート名]`
  - `ovs-vsctl --columns=name,status list Port [ポート名]` (必要な項目に限定)
    - 項目 `name` / `statistics` / `status` / `tag` / `trunks` / `vlan_mode` など。
  - `ovs-vsctl --columns name,status list Port | grep -i blocking -B1`
    - STP blocking されているポートを検索

## 複数ノード操作

### (optional) 直接アクセス/ウィンドウシステムがある場合

Mininet CLI の `xterm` コマンドを使って、操作対象ノードで実行されるターミナルを起動してください。

### ブラウザアクセス/ウィンドウシステムがない場合

演習スクリプト `nw_training.py` で演習ネットワークを起動すると、スイッチ以外のノードについて　mininet CLI の外からアクセスできるようなっています。スイッチ以外のノードとは、設定ファイル中で `type: host` または `type: router` として定義されているノードです。Mininet 内のノードは、正確にはノードとして扱われる network namespace です。
したがって、mininet CLI の外からは `ip netns` コマンドを使ってその namespace にアクセスできます。

- ノード (ノード相当の netns) 一覧表示
  - `ip netns list`
- ノード内部でのコマンド実行
  - `ip netns exec ノード名 コマンド`
  - Mininet CLI の中で実行する `mininet> ノード名 コマンド` 操作と等価です

例: Mininet-CLI での操作と Mininet-CLI 外でそれと等価な操作

```text
mininet> nodes
available nodes are: 
hb hc rb rc sa1 sa2
mininet> hb ip addr show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: hb-eth0@if2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 16:04:d4:bd:80:89 brd ff:ff:ff:ff:ff:ff link-netns rb
    inet 192.168.0.18/30 brd 192.168.0.19 scope global hb-eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::1404:d4ff:febd:8089/64 scope link 
       valid_lft forever preferred_lft forever
mininet> 
```

```text
root@nwtraining01:~# ip netns list
sa2
hb
sa1
hc
rc
rb
root@nwtraining01:~# ip netns exec hb ip addr show 
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: hb-eth0@if2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 16:04:d4:bd:80:89 brd ff:ff:ff:ff:ff:ff link-netns rb
    inet 192.168.0.18/30 brd 192.168.0.19 scope global hb-eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::1404:d4ff:febd:8089/64 scope link 
       valid_lft forever preferred_lft forever
root@nwtraining01:~# 
```

例: Mininet-CLI で hb から sa1 に対して ping を撃ちながら、sa1 側で tcpdump してパケットダンプを見る

```text
mininet> hb ping -c 3 192.168.0.2 
PING 192.168.0.2 (192.168.0.2) 56(84) bytes of data.
64 bytes from 192.168.0.2: icmp_seq=1 ttl=63 time=0.050 ms
64 bytes from 192.168.0.2: icmp_seq=2 ttl=63 time=0.614 ms
64 bytes from 192.168.0.2: icmp_seq=3 ttl=63 time=0.076 ms

--- 192.168.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2058ms
rtt min/avg/max/mdev = 0.050/0.246/0.614/0.259 ms
mininet> 
```

```text
root@nwtraining01:~# ip netns exec sa1 tcpdump -i sa1-eth0 -l
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on sa1-eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
16:00:47.671989 IP 192.168.0.18 > 192.168.0.2: ICMP echo request, id 978, seq 1, length 64
16:00:47.672005 IP 192.168.0.2 > 192.168.0.18: ICMP echo reply, id 978, seq 1, length 64
16:00:48.701304 IP 192.168.0.18 > 192.168.0.2: ICMP echo request, id 978, seq 2, length 64
16:00:48.701810 IP 192.168.0.2 > 192.168.0.18: ICMP echo reply, id 978, seq 2, length 64
16:00:49.729748 IP 192.168.0.18 > 192.168.0.2: ICMP echo request, id 978, seq 3, length 64
16:00:49.729771 IP 192.168.0.2 > 192.168.0.18: ICMP echo reply, id 978, seq 3, length 64
16:00:52.827391 ARP, Request who-has 192.168.0.1 tell 192.168.0.2, length 28
16:00:52.827432 ARP, Request who-has 192.168.0.2 tell 192.168.0.1, length 28
16:00:52.827436 ARP, Reply 192.168.0.2 is-at ba:16:1d:61:e2:4f (oui Unknown), length 28
16:00:52.827443 ARP, Reply 192.168.0.1 is-at 46:09:82:2f:18:90 (oui Unknown), length 28
^C
10 packets captured
10 packets received by filter
0 packets dropped by kernel
root@nwtraining01:~# 
```

## コマンド実行のコンテキストのまとめ

コンテキスト = どこでコマンド(プロセス)を動かすか :

* 演習ネットワーク内ホストやルータ (virtual node) のシェル
* Mininet CLI
* コンテナ上のシェル (Mininet CLI の外)

| from \ to       | container shell | Mininet-CLI | virtual node |
|-----------------|-----------------|-------------|--------------|
| container shell | `COMMAND`       | n/a         | `ip netns exec HOST COMMAND` |
| Mininet-CLI     | `sh COMMAND`    | `COMMAND`   | `HOST COMMAND` |

<!-- FOOTER -->

---

Previous << [Index](../index.md) >> [Next](../common/glossary.md)
<!-- /FOOTER -->
