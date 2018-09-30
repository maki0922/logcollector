logcollector
=====

# Overview

## Description
かゆい設定が出来るログ収集ツール。  
予め定義したノード情報と収集対象のログ情報を元にログを収集する。  
いくつか各利用パターンを考えた機能を具備させた。 
※ansibleでやればええやん！というのはもっと後に気づいた。  

## Functions
機能は大きく分けて以下の3つに分類して実装している  

### Multiple Node Select 
収集する対象のノードを指定する方式は以下の３種から選択を行える。  

<details>
  <summary>
    Detailes. Click This Link.
  </summary>
  <div>

#### 1. select node on command line
コマンドライン上から複数のnodeを指定できる。

#### 2. select node group
複数のノードをグループ定義することにより、対象のグループのみ指定できる。

#### 3. select list file
対象ノードのリストファイル指定して実行することができる。

  </div>
</details>

### Multiple ssh connection Type
ssh/scpによる接続する方法は以下の３種類から選択が行える。  

<details>
  <summary>
    Detailes. Click This Link.
  </summary>
  <div>

#### 1. no password connection
鍵交換を行なっているノードは設定ファイルにパスワード設定不要  

#### 2. connect by using password
従来のパスワードを用いた接続が行える。  

#### 3. connect by using select id_rsa file
指定した秘密鍵ファイルを用いた接続が行える。

  </div>
</details>

### Multiple collection Type
ログの取得方法は以下の2つ選択することができる。  

<details>
  <summary>
    Detailes. Click This Link.
  </summary>
  <div>

#### 1. select generation
ログローテートされているログに対し指定した世代までの取得が行える。  

#### 2. select time range
年月日の範囲を指定してログを取得することができる。  

  </div>
</details>

# Installation
以下の条件で動作確認を行なっている。  

## Requirement
- Python 2.7.15
- Paramiko 

## Install
- `git clone https://github.com/maki0922/logcollecter`
- `pip install -r requirements.txt`
- `cd logcollector` 
- `edit collect.ini`
- `edit nodedef.yml`
- `edit loggdef.yml`

# Fast Start
1. Set [Configration.](#Configuration)
2. Run [Command.](#Commands)

# Commands
`$ python logcollector.py [select Node option] [select log option]`

## Select node options
対象のノードを選択します。

- `-n` : ノード名を指定してください。複数指定もできます
- `-grp` : 対象のノードに設定したグループを指定してください。
- `-l` : 対象のノードを記述したリストファイルを指定してください。

<details>
  <summary>
    Examples. Click This Link.
  </summary>
  <div>

### multiple node select by commandline
`$ python logcollector.py -n webserver01 webserver02`

### group select
`$ python logcollector.py -grp websv`

### use node list file
`$ python logcollector.py -l nodelist.txt`

  </div>
</details>

## Select Log options
任意オプションです。指定しない場合は設定した世代までのログを取得します。

- `-g` : 取得対象のログの世代を指定できます。
- `-t` : 指定した年月日の範囲のログを取得します。<br> yyymmdd形式で選択してください。

<details>
  <summary>
    Examples. Click This Link.
  </summary>
  <div>

### select generation num
`$ python logcollector.py -g 2`

### use node list file
`$ python logcollector.py -t 20180101 20180102`

  </div>
</details>

# Configuration
設定ファイルは以下の3ファイル存在する。  

## collect.ini file
本ツールの基本的な設定ファイルです。
基本的にこの設定使ってください。

<details>
  <summary>
    Detailes. Click This Link.
  </summary>
  <div>

|Section|Key|Type|Description|
|----|----|----|----|
|GENERAL|file_generation|int|世代ファイル指定の取得時のデフォルト値|
|GENERAL|node_config_path|string|ノード情報の定義ファイル|
|GENERAL|log_config_path|string|収集対象ログの定義ファイル|
|GENERAL|log_dir|string|ツールログ出力パス(FullPath)|
|GENERAL|local_dir|string|収集したログの配置場所(FullPath)|
|GENERAL|remote_outdir|string|リモート側のログアーカイブファイルの作成場所|
|GENERAL|use_sudo|string|収集先ノードのコマンド実行時に`sudo`を用いる場合`yes`にする|
|SSH|default_port|int|接続先Port番号(ノード情報にPort番号がない場合使用される)|

  </div>
</details>

## nodedef.yml file
ノード情報定義するファイル。
nodes attribute配下に１ノードに対して以下の様に定義する。
```
nodes:
    webserver01:
      ip: 10.10.10.10
      ssh:
        user: azuki
        pass: azuki
        port: 22
        private_key: /Users/azuki/.ssh/id_rsa
      group:
        - websv
        - dbsv
      log:
        - os-ubuntu
        - syslog
```
#### 1ノードの最小設定は以下である。
```
nodes:
    webserver01:
      log:
        - os-ubuntu
        - syslog
```
<details>
  <summary>
    Setting Detailes. Click This Link.
  </summary>
  <div>

|Section|Key|Type|Description|
|----|----|----|----|
|-|ip|option|指定したIPへssh接続させたい場合は設定する。<br> 設定しない場合は、/etc/hostsに記述されているhostnameを宛先にする。|
|ssh|user|option|ssh接続するユーザを設定する。<br> 設定しない場合は、ツール実行時のユーザを使用して接続。|
|ssh|pass|option|ssh接続するユーザのパスワードを設定する。<br> 設定しない場合は接続先をNoPass設定要。|
|ssh|port|option|ssh接続先のport番号を指定する。<br>設定しない場合はデフォルト値を使用する。|
|ssh|private_key|option|ssh接続する際に秘密鍵を指定する際にはフルパスで設定する。|
|-|group|option|ノード種別を定義します。<br>ツール実行時にグループ指定する際に使用されます。|
|-|log|require|取得対象のログgroupを設定します。<br>設定するログgroupはlogdef.ymlに記述されて要る必要があります。|

  </div>
</details>

## logdef.yml file
取得するログファイルを定義するファイルです。
log_list attribute配下にログgroupを定義する。
定義したgroupに対して取得対象のログのフルパスを設定する。

```
log_list:
  os-ubuntu:
    path:
      -  /var/log/syslog
      -  /var/log/dmesg
  syslog:
    path:
      -  /var/log/system.log
      -  /var/log/syslog
      -  /var/log/dmesg
```

## YAMLファイルの記述の勧め
nodedef.yamlを多量のノード定義する際、yamlのAncherとAliasを使用しましょう。

# Function Restriction

## ssh connection Priolity
nodedef.ymlで複数の設定がされている場合の優先度。
ここら辺はParamiko library 依存です。
1. 指定したprivate_keyを使用した接続(接続できない場合はエラー）
2. `~/.ssh/id_rsa`ファイルを用いたログイン(失敗したらuser/pass接続を試みます）
3. user/passを用いた接続(接続失敗時はエラー)

# Log & Archive

## Remote Archive
デフォルト設定ではリモート側の「/tmp」配下に「<hostname>\_<yyyymmdd>.tar.gz」ファイルが生成されます。
転送完了後には対象ファイルは削除されます

## Local Archive
デフォルト設定ではリモート側の「/tmp」に「yyyymmdd」ディレクトリを生成します。
生成したディレクトリ配下にリモート側で生成されたArchiveをscpにて取得します。

## Tool Log
デフォルト設定では


# Reference
- [logging](https://qiita.com/knknkn1162/items/87b1153c212b27bd52b4)
- [logging](https://qiita.com/toriwasa/items/fa8371c3b98aa993a2fc)
- [set Class](https://blog1.erp2py.com/2012/02/pythonset.html)
