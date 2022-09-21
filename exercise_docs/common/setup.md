<!-- HEADER -->
Previous << [README](/README.md) >> [Next](../common/make_exercise.md)

---
<!-- /HEADER -->

<!-- TOC -->

- [環境セットアップ](#%E7%92%B0%E5%A2%83%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97)
  - [システム構成](#%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E6%A7%8B%E6%88%90)
  - [必要なツール](#%E5%BF%85%E8%A6%81%E3%81%AA%E3%83%84%E3%83%BC%E3%83%AB)
  - [code-server インストール](#code-server-%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB)
    - [Amazon Linux with code-server](#amazon-linux-with-code-server)
    - [Ubuntu20 Server with code-server](#ubuntu20-server-with-code-server)
    - [code-server 設定](#code-server-%E8%A8%AD%E5%AE%9A)
  - [リポジトリのクローン](#%E3%83%AA%E3%83%9D%E3%82%B8%E3%83%88%E3%83%AA%E3%81%AE%E3%82%AF%E3%83%AD%E3%83%BC%E3%83%B3)
  - [Composeファイルのバージョンと警告メッセージ](#compose%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E3%83%90%E3%83%BC%E3%82%B8%E3%83%A7%E3%83%B3%E3%81%A8%E8%AD%A6%E5%91%8A%E3%83%A1%E3%83%83%E3%82%BB%E3%83%BC%E3%82%B8)
  - [演習コンテナイメージを用意する](#%E6%BC%94%E7%BF%92%E3%82%B3%E3%83%B3%E3%83%86%E3%83%8A%E3%82%A4%E3%83%A1%E3%83%BC%E3%82%B8%E3%82%92%E7%94%A8%E6%84%8F%E3%81%99%E3%82%8B)
    - [イメージのダウンロードpull](#%E3%82%A4%E3%83%A1%E3%83%BC%E3%82%B8%E3%81%AE%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89pull)
    - [イメージのビルド](#%E3%82%A4%E3%83%A1%E3%83%BC%E3%82%B8%E3%81%AE%E3%83%93%E3%83%AB%E3%83%89)
    - [イメージのプッシュ](#%E3%82%A4%E3%83%A1%E3%83%BC%E3%82%B8%E3%81%AE%E3%83%97%E3%83%83%E3%82%B7%E3%83%A5)
  - [演習コンテナを起動する](#%E6%BC%94%E7%BF%92%E3%82%B3%E3%83%B3%E3%83%86%E3%83%8A%E3%82%92%E8%B5%B7%E5%8B%95%E3%81%99%E3%82%8B)
  - [演習環境を閉じる](#%E6%BC%94%E7%BF%92%E7%92%B0%E5%A2%83%E3%82%92%E9%96%89%E3%81%98%E3%82%8B)
  - [Optional 演習コンテナの消費リソースログを取る](#optional-%E6%BC%94%E7%BF%92%E3%82%B3%E3%83%B3%E3%83%86%E3%83%8A%E3%81%AE%E6%B6%88%E8%B2%BB%E3%83%AA%E3%82%BD%E3%83%BC%E3%82%B9%E3%83%AD%E3%82%B0%E3%82%92%E5%8F%96%E3%82%8B)
  - [Optional Mininet で xterm コマンドを使用したい場合](#optional-mininet-%E3%81%A7-xterm-%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%97%E3%81%9F%E3%81%84%E5%A0%B4%E5%90%88)

<!-- /TOC -->

# 環境セットアップ

## システム構成

:warning:[2021-08-16]構成上の問題点

1-VM : N-Container 構成の場合、特定の問題を複数コンテナ内部で起動した際に問題がおきる。

* コンテナ内部で mininet が作成した veth インタフェースはホスト側 OS で作成されている。複数コンテナで同じ演習ネットワークを起動しようとすると、同名のインタフェースを作ろうとしてエラーになる。
  * コンテナ内部で mininet が作成する論理ネットワークリソースは Linux OS 側で用意するもの。コンテナは OS の機能についてはコンテナホスト側の機能を使用している。そのため別コンテナであっても OS 側で同じリソースを複数作ろうとする状況が起きると競合が発生してしまう。
  * 少なくとも root namespace で起動している OVS に接続する veth についてはホスト Linux 側から見える状態になっている。OVS を namespace 内に閉じて使う機能は mininet にはない。(OVS 自体、kernel module を使っていたり unix domain socket 経由の client/server 型になっていたりでそうした分割隔離した環境で動かす想定がない。)

**演習コンテナは 1-OS : 1-Container 形式で使用すること**

![structure](structure.drawio.svg)

<details>

<summary>Obsoleted (過去情報/ 1-VM : N-Container 構成)</summary>

下の図のような構成で、複数人が使える演習環境を想定。

- 図では VirtualBox 構成を仮定
  - 少人数ハンズオンで使用する際、PC で OS を入れ替えが難しい場合を想定する
- VirtualBox 利用時のオプション
  - NAT 接続する際はポートフォワード設定が必要
  - bridge 接続してよいのであれば (NAT 接続が不要であれば) ポートフォワード設定は不要なはず

![obsoleted structure](structure_obsoleted.drawio.svg)

</details>

## 必要なツール

* curl
* docker
* docker-compose
* Git
* X Window system and `xhost` utility[optional]

特権モードでコンテナを起動できること

ホスト側は t2.micro 相当あれば動作します。

* 1 Core
* 1 GB Memory
* 8 GB Storage

## code-server インストール

<details>
<summary>経緯</summary>

もともと、1-OS : N-Container 構成の想定だったため、コンテナ内にフロントエンド (Gotty) を同梱していましたが、この構成はうまく動かないことがわかりました。そのため 1-OS : 1-Container 構成とします。この構成ではフロントエンドを OS (Docker ホスト) 側に入れる構成が選択肢に入ってきます。
</details>

ホスト側で使う Web フロントエンドとして [code-server: VS Code in the browser](https://github.com/cdr/code-server) を使用します。

### Amazon Linux with code-server

<details>

<summary>Amazon Linux (EC2 Instance) でcode-serverを構築するときの手順</summary>

```sh
## rootで実行すること（code-serverをroot以外のユーザで動かすのが上手くいっていないため）

# git, docker, treeインストール
yum install -y git
yum install -y docker

# docker-composeインストールとコマンド補完設定
curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
curl -L https://raw.githubusercontent.com/docker/compose/$(docker-compose version --short)/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose

# docker起動と自動起動設定
systemctl start docker
systemctl enable docker

# 環境変数の定義
echo "export PS1=\"\[\e[1;36m\][\u@\h \w]\$\[\e[m\] \"" > /etc/profile.d/init-env.sh
echo "export TZ=Asia/Tokyo" >> /etc/profile.d/init-env.sh

# code-server
## インストールと自動起動設定
curl -fsSL https://code-server.dev/install.sh | sh
systemctl start code-server@$USER
systemctl enable code-server@$USER
## アドオンのインストール
code-server --install-extension MS-CEINTL.vscode-language-pack-ja
code-server --install-extension oderwat.indent-rainbow
code-server --install-extension PKief.material-icon-theme

# ユーザ設定
mkdir -p ~/.local/share/code-server/User/
```

</details>

### Ubuntu20 Server with code-server

<details>

<summary>Ubuntu Server 20 でcode-serverを構築するときの手順</summary>

```sh
# update
sudo apt update
sudo apt upgrade
# clean cache
sudo apt clean

# install docker/docker-compose
sudo apt install docker.io docker-compose
# ユーザに対して docker group つける
# つけないと受講者が docker exec するときに sudo が必要になる
sudo usermod -a -G docker $USER

# 環境設定
sudo timedatectl set-timezone Asia/Tokyo

# code-server
## インストールと自動起動設定
curl -fsSL https://code-server.dev/install.sh | sh
sudo systemctl start code-server@$USER
sudo systemctl enable code-server@$USER
## アドオンのインストール
code-server --install-extension MS-CEINTL.vscode-language-pack-ja
code-server --install-extension oderwat.indent-rainbow
code-server --install-extension PKief.material-icon-theme

## ユーザ設定
mkdir -p ~/.local/share/code-server/User/
```

</details>

### code-server 設定

設定ファイル

`~/.local/share/code-server/User/settings.json`

```json
(TBA)
```

`~/.config/code-server/config.yaml`

* default だとローカルホスト (127.0.0.1) でのみ listen しているので変更する
* パスワード設定

```text
$ cat .config/code-server/config.yaml
bind-addr: 0.0.0.0:8080
auth: password
password: (password string)
cert: false
```

設定変更したら再起動

```sh
systemctl restart code-server@$USER
```

## リポジトリのクローン

```sh
git clone https://github.com/infra-handson/network-training.git
cd network-training
```

## Composeファイルのバージョンと警告メッセージ

:warning: docker-compose でマルチステージビルドによる使い分けをするため、compose ファイルのバージョンを 3 系に変更しました。その際、CPU/Memory の上限設定を `deploy` セクションの内容に置き換えています。これは swarm mode のときに使用されるものなので、通常の docker-compose では `--compatibility` オプションをつけて実行する必要があります。(参照: [Compatibility Mode | Compose file versions and upgrading | Docker Documentation](https://docs.docker.com/compose/compose-file/compose-versioning/#compatibility-mode))

```text
WARNING: Some services (lab) use the 'deploy' key, which will be ignored. Compose does not support 'deploy' configuration - use `docker stack deploy` to deploy to a swarm.
```

## 演習コンテナイメージを用意する

### イメージのダウンロード(pull)

利用するだけの場合はダウンロード (pull) で問題ありません。

ダウンロード (pull) する場合、compose ファイルの `build` 設定をコメントアウトしてください。

```sh
# cd ~/network-training
docker-compose pull
```

### イメージのビルド

<details>

<summary>開発時 (イメージの中身の変更)</summary>

ビルドする前に compose ファイルの `build` 設定のコメントを外してください。

```sh
# cd ~/network-training
docker-compose build
```

ビルドが終わると、ベースになる mininet コンテナイメージと、ビルドされたものとで、3 つの image があるはずです。

* orzohmygodorz/mininet (base)
* ghcr.io/infra-handson/network-training (built)

</details>

### イメージのプッシュ

<details>

<summary>開発時 (更新したイメージをコンテナレジストリにアップロード)</summary>

- ref: - [個人アクセストークンを使用する - GitHub Docs](https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- ref: [Working with the Container registry - GitHub Docs](https://docs.github.com/ja/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- ref: [GitHub Container Registry(ghcr.io)にDockerイメージをpushする手順 - Qiita](https://qiita.com/zembutsu/items/1effae6c39ceae3c3d0a)

```sh
cat ghcr-pat.txt | docker login ghcr.io -u <username> --password-stdin

docker push ghcr.io/infra-handson/network-training:latest
```

<details>

<summary>Obsoleted (for Gitlab)</summary>

:warning: 二要素認証 (2FA) 有効にしている場合は `read_registry`+`write_registry` 権限をもつアクセストークンでログインが必要。

- ref: [Gitlabの2段階認証下でコンテナレジストリにPushする方法 | codit](https://www.codit.work/notes/p8deveys7r07s5nmwfa8/)
- ref: [Docker Registry Login with 2FA - How to Use GitLab - GitLab Forum](https://forum.gitlab.com/t/docker-registry-login-with-2fa/6719)

```sh
docker login registry.gitlab.com
# docker login registry.gitlab.com -u ユーザー名 -p アクセストークン

docker push registry.gitlab.com/corestate55/network_practice:latest
```

</details>

</details>

## 演習コンテナを起動する

:warning: docker-compose で `--compatibility` オプションがない場合、警告メッセージ `WARNING: Some services (lab) use the 'deploy' key, which will be ignored. Compose does not support 'deploy' configuration` が表示されます。コンテナ起動時にこのメッセージが表示されている場合、CPU/Memory 上限設定が無視されているので、いったん止めてからオプションをつけて再起動させてください。

:warning: セキュリティ面の注意事項

* 演習コンテナは特権モードで起動します。(compose ファイル内のオプションで指定してあります)。コンテナが特権モードで動く (コンテナ内では root が使える) ため、不正利用された場合に機能制限ができません。

```sh
# cd ~/network-training
docker-compose --compatibility up -d
```

## 演習環境を閉じる

全ての演習が終わったら、(docker host 側で) 演習コンテナを停止させます。

```sh
# cd ~/network-training
docker-compose down
```

## (Optional) 演習コンテナの消費リソースログを取る

<details>

<summary>コンテナリソースログを取る</summary>

[rec_docker_stats.sh](/rec_docker_stats.sh) を実行すると、日付ベースの適当なログファイルを作って docker stats の結果を CSV で保存します。

```sh
# cd ~/network-training
./rec_docker_stats.sh
```

</details>

## (Optional) Mininet で xterm コマンドを使用したい場合

<details>

<summary>Mininet で xterm コマンドを使う</summary>

Linux VM (docker ホスト) に X window system がある場合、Mininet 内部から `xterm` コマンドを使って、仮想ノード上の端末を開くことができます。

ローカルで xterm を使う場合は compose ファイル内の `DISPLAY` 環境変数のコメントを外してください。

X アプリケーションの接続を許可するため (docker ホスト側で) `xhost` コマンドを実行します。

```sh
xhost +
```

`xterm` のフォントが小さい場合、以下のフォント設定を `~/.Xresources` に追記または編集します。

```text
xterm*faceName: Monospace
xterm*faceSize: 14
```

編集してから、`xrdb` コマンドを実行します。

```sh
xrdb -merge ~/.Xresources
```

</details>

<!-- FOOTER -->

---

Previous << [README](/README.md) >> [Next](../common/make_exercise.md)
<!-- /FOOTER -->
