# Twitter Conversation Scraper

このアプリケーションはTwitterの3ターン以上の日本語の会話を会話をスクレイピングするアプリケーションです。

DBにはsqlite3を採用しています。

## Usage

step1

まず,secretsという名前のファイルを以下のように作成してください。
フォーマットは
```
BEARER_TOKEN=<YOUR BEARER TOKEN>
ACCESS_TOKEN=<ACCESS TOKEN>
ACCESS_TOKEN_SECRET=<ACCESS TOKEN SECRET>
API_KEY=<API KEY>
API_KEY_SECRET=<API KEY SECRET>
```

step2

```commandline
python TwitterDialogueCrawler.py 
```
を実行してください。本日の日付(JST)の前日からスクレイピングが始まります。

step3 

会話の抜き出し　または　対話の抜き出し　を行ないます。

Twitter のデータは木構造になっています。

本アプリ中のデータベース中のデータは木構造のデータで、ひとつ前のデータがTweetの発言者以外の条件で保存しています。
そのため、複数人でのreplyのチェーンが発生する可能性があります。

複数人の会話について、考慮せずに抜き出すのが、

```commandline
python extract.py --type=conversation
```

2人だけの対話データのみ取り出すのが

```commandline
python extract.py --type=dialogue
```
となっています。

## chips

#### スクレイピング対象の単語を変更したい場合

Known_words.txt を変更してください。

デフォルトでは,　知っているの頻度が 1.9 以上　かつ　話すの頻度が 1.3　以上の1880単語を抜き出しています。

また、独断と偏見により以下の20単語を追加しています。

>マンガ,映画,趣味,小説,ラブコメ,ラノベ,スマホ,恋人,彼女,彼氏,2次元,リア充,Twitter,YouTube,Netflix,オタク,アイドル,コスプレ,クイズ,雑学

単語の頻度について詳しくは[この論文]()を参考にしてください。

#### 以前に作成したデータベース中のデータよりも新しいデータをスクレイピングしたい場合。

デフォルトでは以前にスクレイピングした内容よりも、過去に戻ってスクレイピングしています。

未来に向かってスクレイピングしたい場合は

```commandline
python TwitterDialogueCrawler.py --recursive=False
```
としてください。

#### テーブルを消去して、初めからスクレイピングしたい場合

```commandline
python TwitterDialogueCrawler.py --drop_table=True
```
としてください。