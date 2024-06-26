<!-- HEADER -->
Previous << [Index](../index.md) >> [Next](../tutorial1/scenario.md)

---
<!-- /HEADER -->

# チュートリアル0

## このチュートリアルの目的

使い方の理解

* 演習環境へのアクセス
* 演習ネットワークの起動・停止の方法

## 演習環境に接続する

演習環境にブラウザでアクセスします。

> [!WARNING]
> ブラウザ拡張機能によっては、ブラウザ内で起動するアプリ(code-server)の操作と干渉することがあります。動作がおかしい場合はゲストモードで試してみてください。

![Login](csvr_login.png)

- 運営から指定された接続情報を用意する
  - 接続先 IP アドレス・ポート番号
  - パスワード
- 指定されたアドレス・ポート番号でブラウザからアクセスする
- パスワード入力が要求されるので、指定されたパスワードを入力する

パスワード認証が通ると、ブラウザで code-server (VSCode, Visual Studio Code) が起動します。

![Initial code-server](csvr_init.png)

## Code-server の表示操作

> [!NOTE]
> Code-server (VSCode) の画面構成要素の名称については [Visual Studio Code User Interface](https://code.visualstudio.com/docs/getstarted/userinterface) を参照してください。

### ターミナルが表示されない・閉じてしまった

アクティビティバーのメニューから[表示]-[ターミナル]等でターミナルを表示してください。

![Show terminal](csvr_show_terminal.png)

### ファイルエクスプローラー(サイドバー)の開閉

アクティビティバーのファイルエクスプローラーボタンでサイドバーを開閉できます。チュートリアル・演習はターミナル操作が中心になります。ファイルエクスプローラー (サイドバー) が不要な場合は閉じてターミナルを広く使えるようにしてください。

![Open/Close File Explorer (sidebar)](csvr_file_explorer.png)

### エディタグループの開閉

ターミナルパネル右上のパネル最大化・元に戻すボタンでエディタグループの開閉 (ターミナルパネルの最大化・戻す) ができます。チュートリアル・演習はターミナル操作が中心になります。エディタグループが不要な場合は閉じて (ターミナルパネルを最大化して) ターミナルを広く使えるようにしてください。

![Open/Close editor group](csvr_terminal_panel.png)


### ターミナルを2面用意する

演習の中で、ターミナルを 2 枚表示した上で並行操作する箇所があります。ターミナルパネルのメニューから「ターミナルの分割」を選択してターミナルを分割してください。

![Split terminal](csvr_terminal_split.png)

図のようにターミナルを 2 面表示します。

![Split terminal panel](csvr_terminal.png)

## 演習ネットワークの起動・停止・リセット

### 作業ディレクトリへの移動

用意した 2 面のターミナルのどちらも、現在のディレクトリが `~/network-training` になっていない場合はこのディレクトリへ移動してください。

> [!IMPORTANT]
> チュートリアル・演習用の環境はコンテナとして提供されます。
> コンテナ操作 (`docker-compose` コマンド) をするには、設定ファイル ([docker-compose.yml](/docker-compose.yml)) がある `~/network-training` ディレクトリにいる必要があります。

```sh
cd ~/network-training
```

### 事前確認: コンテナ起動

演習コンテナ `network-training_lab_1`  が `Up` になっていることを確認してください。(コンテナは常時起動するように設定していますが念のため。)

```sh
docker-compose --compatibility ps
```
```text
[root@ip-10-0-190-203 ~/network-training]$ docker-compose --compatibility ps
         Name                       Command               State   Ports
-----------------------------------------------------------------------
network-training_lab_1   /bin/bash -c ovs-ctl start ...   Up
```

コンテナが起動していない場合は下記のコマンドで起動させてください。

```sh
cd ~/network-training
docker-compose --compatibility up -d
```

### コンテナに入る

> [!IMPORTANT]
> 複数のターミナルを使用する場合、どのターミナルでも `docker-compose exec lab bash` してコンテナ内に入ってからチュートリアル・演習作業をしてください。code-server はコンテナ外 (docker host) で動いているのでコンテナ内に入る操作が必要になります。

コンテナ内に入ると、下記のように `root@nwtraining01` プロンプトに変化します。

```sh
docker-compose exec lab bash
```
```text
[root@ip-10-0-190-203 ~/network-training]$ docker-compose exec lab bash
# --compatibility オプションがない場合 WARNING が出るかもしれませんが無視してください
root@nwtraining01:/#
```

<details>

<summary>コンテナに「入る」とは?</summary>

コンテナに「入る」としていますが、正確には、コンテナとして区切られたアプリケーション実行用の空間で shell プロセスを実行しています。プロセス (bash) は Linux OS 上で動作しますが、プロセスに見える OS 上の計算機リソースが限定されています。

コンテナ内でプロセスを実行するとこで、そのコンテナ内 (限定された、仮想的なプロセス実行用の空間) のなかで通常の対話的なコマンド実行ができます。あたかも、仮想マシン (ホスト OS 上のリソースの一部を使う別の OS) の中で操作しているかのように見えます。

</details>

### 起動

コンテナ内、`/exercise` ディレクトリに演習ネットワークを起動するためのスクリプトがあります。

チュートリアル 1 用のネットワークを起動してみましょう。

```sh
cd /exercise
./nw_training.py tutorial1/scenario.json
```

起動すると下記のように `mininet>` プロンプトが表示されます。

![Mininet CLI](csvr_terminal_type.png)

:customs: 以降、上の図のように 2 つのターミナルを使って操作します。各ターミナルを以下のように呼びます。
- **Mininet ターミナル**: Mininet CLI を実行しているターミナル
- **Shell ターミナル**: 通常のシェルを実行しているターミナル

### 停止

Mininet ターミナルで `exit` を入力すると Mininet CLI が終了して起動していた演習ネットワークが全部クリアされます。

> [!WARNING]
> 演習ネットワーク内で設定した情報等は残りません。(残しておきたいものは終了前に記録してください。)

```text
mininet> exit
*** Stopping 0 controllers

*** Stopping 1 links
.
*** Stopping 0 switches

*** Stopping 2 hosts
ha hb 
*** Done
root@nwtraining01:/exercise# 
```

停止後、また別の演習ネットワークを起動できます。

> [!WARNING]
> `nw_training.py` は同時に複数起動できません。(同じ名前のリソースを作ろうとして競合が発生してしまうため。)

### リセット

> [!IMPORTANT]
> 起動がうまくいかない場合は、停止した際に何かしらのゴミが残っていることが想定されます。その場合、Mininet のクリーニングコマンド (`mn -c`) および `rm -rf /var/run/netns/*` を実行してください。

```sh
mn -c
rm -rf /var/run/netns/*
```
```text
root@nwtraining01:/exercise# mn -c
*** Removing excess controllers/ofprotocols/ofdatapaths/pings/noxes

[省略]

*** Cleanup complete.
root@nwtraining01:/exercise# rm -rf /var/run/netns/*
root@nwtraining01:/exercise# 
```

## チュートリアル0のまとめ

* 演習環境操作の基本
  * ブラウザから演習環境にアクセスする
  * Code-server (VSCode) の操作方法
  * ターミナルの表示と呼称の設定
  * 演習ネットワークの起動・停止・リセット

チュートリアル 0 はここまでです。演習ネットワークを終了させて[チュートリアル 1](../tutorial1/scenario.md) に進んでください。

```text
mininet> exit
```

<!-- FOOTER -->

---

Previous << [Index](../index.md) >> [Next](../tutorial1/scenario.md)
<!-- /FOOTER -->
