
下記を末尾まで解析
他AIが完璧に再現できる仕様書.md保存

# [kawasin73のブログ](https://kawasin73.hatenablog.com/)

 ## 技術記事とかいろんなことをかくブログです

[2025-11-20](https://kawasin73.hatenablog.com/archive/2025/11/20)

# [AI に作らせる株式分析システム](https://kawasin73.hatenablog.com/entry/2025/11/20/224346)

[作ったもの](https://kawasin73.hatenablog.com/archive/category/%E4%BD%9C%E3%81%A3%E3%81%9F%E3%82%82%E3%81%AE) [Python](https://kawasin73.hatenablog.com/archive/category/Python)

１発当てて大儲け。どうも、かわしんです。

X の流行を見るに AI コーディングを流石にやらないといけないと思い、今年の8月から Claude Code Max プランを契約して AI コーディングの題材として日本の上場銘柄解析システムを作らせていました。

[https://x.com/kawasin73/status/1951869172377682136](https://x.com/kawasin73/status/1951869172377682136)

[新しい技術を追わない](https://kawasin73.hatenablog.com/entry/2021/05/15/180054) をポリシーにしている自分としては、ここらがいい感じに整備されてきて[コスパ](https://d.hatena.ne.jp/keyword/%A5%B3%A5%B9%A5%D1)のいい参入タイミングかなと思い使い始めましたが、結果的にはいいタイミングだったと思います。

さて、上場銘柄の[有価証券報告書](https://d.hatena.ne.jp/keyword/%CD%AD%B2%C1%BE%DA%B7%F4%CA%F3%B9%F0%BD%F1)のデータフォーマットである [XBRL](https://d.hatena.ne.jp/keyword/XBRL) のパーサー自体は実は2年前に作っていたのですが、ファイルのダウンロードと解析をするために手元で毎回 [Python](https://d.hatena.ne.jp/keyword/Python) [スクリプト](https://d.hatena.ne.jp/keyword/%A5%B9%A5%AF%A5%EA%A5%D7%A5%C8)を実行しないといけないため、めんどくさくて数ヶ月に1回くらいしか実行して確認していませんでした。それを AI エージェントを使って 1 から作り直して、さらに自動化して便利にしました。

今回はどういうものを作ったかと、どのような思想で作ったかをソフトウェアエンジニアの目線から説明したいと思います。

AI の使い方については別の記事にしますが、僕はほとんど[ソースコード](https://d.hatena.ne.jp/keyword/%A5%BD%A1%BC%A5%B9%A5%B3%A1%BC%A5%C9)を書いておらず、95% 以上は AI が書いてます。

# 作った解析ページ

#### ネットネットバリュー株ランキングページ

![](https://cdn-ak.f.st-hatena.com/images/fotolife/k/kawasin73/20251120/20251120001820.png)

ランキングページ

![](https://cdn-ak.f.st-hatena.com/images/fotolife/k/kawasin73/20251120/20251120001844.png)

ネットネットバリューPBR 推移ページ

この指標は、会社が持っている現金や有価証券など即時現金化が可能な資産から総負債を引いた会社の解散[時価](https://d.hatena.ne.jp/keyword/%BB%FE%B2%C1)値で[時価総額](https://d.hatena.ne.jp/keyword/%BB%FE%B2%C1%C1%ED%B3%DB)を割った PBR に似た指標です。この値が 1 を割れば現金が割引価格で売られている状態になりお得になります。

どの項目を即時現金化可能な資産として選ぶかや、それぞれの割引率などを独自に設定できるようにしています。

また、PBR チャートタブでは、独自に計算した PBR の過去の推移をチャートにして表示しています。これによって最近 PBR の値が小さくなったのかどうかを判別することができます。

#### オニールの成長株発掘ランキングページ

![](https://cdn-ak.f.st-hatena.com/images/fotolife/k/kawasin73/20251120/20251120002857.png)

ランキング一覧ページ

![](https://cdn-ak.f.st-hatena.com/images/fotolife/k/kawasin73/20251120/20251120002927.png)

銘柄詳細ページの上の方

![](https://cdn-ak.f.st-hatena.com/images/fotolife/k/kawasin73/20251120/20251120003002.png)

銘柄詳細ページの下の方

これは、「オニールの成長株発掘法」という本で紹介されているスクリーニング手法を実装したページです。EPS の成長率やリラティブストレングスという株価の推移の指標を元にスクリーニングします。

各銘柄の詳細ページでは、いつ決算が発表されたかのマーカーと、どの[区間](https://d.hatena.ne.jp/keyword/%B6%E8%B4%D6)でシグナルが点灯したかを背景の色を変えることで可視化しています。

ちなみにランキングページから詳細ページまで１枚の HTML でできた SPA です。

#### オニールのマーケットの天井検出ページ

![](https://cdn-ak.f.st-hatena.com/images/fotolife/k/kawasin73/20251120/20251120003622.png)

市場天井検出ツール

これも、「オニールの成長株発掘法」という本で紹介されているマーケットが上昇トレンドから天井をうって下落に転じる前に現れる「分配日」をカウントしていつマーケットが下落するのかを予測するツールです。

シグナルが出た日をマーカーで表示し、注意期間を背景の色を変えることで可視化しています。

ただ、パラメータのチューニングが難しく、[ベイズ](https://d.hatena.ne.jp/keyword/%A5%D9%A5%A4%A5%BA)最適化でパラメータを計算しようとしましたがうまくいきませんでした。

# ソフトウェアエンジニアとしての思想

#### 自動化

毎日のデータのダウンロードや解析[スクリプト](https://d.hatena.ne.jp/keyword/%A5%B9%A5%AF%A5%EA%A5%D7%A5%C8)の実行をやるのはめんどくさいので、とにかく全部自動化するのが目標です。流石に株の売り買いも自動化すると不具合があった時の代償が大きいので自分で判断して売買しますが、勝手に条件を満たす銘柄が見つかったら通知を飛ばしてくれるのが理想です。

#### メンテコストの最小化

個人プロジェクトなので運用の手間をゼロにしたいです。めんどくさいので。24 時間待機するサーバーを持った時点でセキュリティのリスクがあり、ソフトウェアのアップデートなどがめんどくさいです。なので、全部フルマネージドなサービスを使います。

なるべく利用するサービスの数を減らして、メンテナンスをゼロにします。一度作ったらほったらかしにしても動き続ける堅牢なシステムは要素を減らすことで得られます。

# [アーキテクチャ](https://d.hatena.ne.jp/keyword/%A5%A2%A1%BC%A5%AD%A5%C6%A5%AF%A5%C1%A5%E3)

全体の[アーキテクチャ](https://d.hatena.ne.jp/keyword/%A5%A2%A1%BC%A5%AD%A5%C6%A5%AF%A5%C1%A5%E3)はこんな感じです。肝は、全てを [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルで管理し、[Github](https://d.hatena.ne.jp/keyword/Github) Actions の日次バッチで [SQLite](https://d.hatena.ne.jp/keyword/SQLite) を更新して、S3 に置かれた最新の [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルを引き回すことでローカルやブラウザ上での解析の全てに対応していることです。必要なインフラは [AWS](https://d.hatena.ne.jp/keyword/AWS) S3 と [Github](https://d.hatena.ne.jp/keyword/Github) の[リポジトリ](https://d.hatena.ne.jp/keyword/%A5%EA%A5%DD%A5%B8%A5%C8%A5%EA)だけです。

![](https://cdn-ak.f.st-hatena.com/images/fotolife/k/kawasin73/20251120/20251120000759.png)

#### [Github](https://d.hatena.ne.jp/keyword/Github) Actions で日次処理

[Github](https://d.hatena.ne.jp/keyword/Github) Actions には cron のサポートがあって、以下のように設定すると毎日 18 時に CI workflow が実行されます。

on:
  schedule:
    # Run daily at 6:00 PM JST (9:00 AM UTC)
    - cron: "0 9 * * *"
  workflow_dispatch: # Allow manual trigger for testing

毎日以下の処理を行います。

- 最新の [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルをS3 からダウンロード
- その日に更新された株価、[XBRL](https://d.hatena.ne.jp/keyword/XBRL) などのファイルをダウンロード
- ダウンロードしたファイルをパース+正規化して、[SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルに追記
- ダウンロードした生データファイルを S3 に `aws s3 sync`
- 最新の [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルを S3 に上書き保存
- データを解析して必要な通知を行う
- [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルダウンロードリンクや解析 web page リンクを Summary の Web UI に表示

CI の失敗による欠損データを防ぐために、更新するデータは [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイル内の最新の日付以降を取得するようにして、[SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルのアップロードは一番最後に行うようにしています。

日次処理に [Github](https://d.hatena.ne.jp/keyword/Github) Actions を使えばいいというアイディアは [ChatGPT が教えてくれました](https://chatgpt.com/share/691c91ea-8d54-8003-ac12-53f6373020bf)。

[https://x.com/kawasin73/status/1959106840828289471](https://x.com/kawasin73/status/1959106840828289471)

#### S3 に生データと [SQLite](https://d.hatena.ne.jp/keyword/SQLite) データベースファイルを保存

パースロジックを変更したときには全ての [XBRL](https://d.hatena.ne.jp/keyword/XBRL) ファイルに対してパースをし直すので、全ての [XBRL](https://d.hatena.ne.jp/keyword/XBRL) ファイルが手元に必要です。[XBRL](https://d.hatena.ne.jp/keyword/XBRL) ファイルは[金融庁](https://d.hatena.ne.jp/keyword/%B6%E2%CD%BB%C4%A3)が提供する EDINET からダウンロードしますが、過去 10 年分しか提供していません。また、[DoS](https://d.hatena.ne.jp/keyword/DoS) を避けるために 1秒に 1 ファイルをダウンロードするので [XBRL](https://d.hatena.ne.jp/keyword/XBRL) ファイルのダウンロードはできれば一度だけにしたいです。そのため、[Github](https://d.hatena.ne.jp/keyword/Github) Actions でダウンロードした [XBRL](https://d.hatena.ne.jp/keyword/XBRL) ファイルなどの生ファイルは全て S3 にアップロードして永久保存しています。定期的に `aws s3 sync` をして S3 のファイルを手元にダウンロードしてパーサーの改善をしています。

生データファイルは、年毎に tar.gz ファイルにまとめて [Amazon S3](https://d.hatena.ne.jp/keyword/Amazon%20S3) Glacier Deep Archive クラスで保存することでダウンロードコストと保管コストを下げています。

[SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルはバージョニングを有効にして上書きして更新しています。[SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルは時々詳細な分析をするために、ローカルにダウンロードして使います。最初は [Github](https://d.hatena.ne.jp/keyword/Github) Artifacts に保存するようにしていたのですが、ダウンロードが 1MB/s と超低速なので諦めて S3 を使うようにしました。また、presigned URL を [Github](https://d.hatena.ne.jp/keyword/Github) Actions のサマリーに書き込んで、WebUI から簡単にダウンロードすることができるようにしました。[SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルは数百 MB にもなるので [gzip](https://d.hatena.ne.jp/keyword/gzip) バージョンも置いてブラウザから高速でダウンロードできるようにしました。

[https://x.com/kawasin73/status/1963626393285100003](https://x.com/kawasin73/status/1963626393285100003)

#### [Github](https://d.hatena.ne.jp/keyword/Github) Pages で static HTML ファイルで解析ページを提供

最初に紹介した解析ページはそれぞれ [Gemini canvas モードに作ってもらい](https://gemini.google.com/share/2404c421e15e)ました。デフォルトでレスポンシブ対応なので[スマホ](https://d.hatena.ne.jp/keyword/%A5%B9%A5%DE%A5%DB)でも確認できます。Gemini [canvas](https://d.hatena.ne.jp/keyword/canvas) モードすごい。

[CSS](https://d.hatena.ne.jp/keyword/CSS) / [javascript](https://d.hatena.ne.jp/keyword/javascript) が全て入った HTML 1ファイルなのでビルドも必要なく取り回しが楽です。ライブラリとしては [sqlite](https://d.hatena.ne.jp/keyword/sqlite)-wasm でクエリして、解析結果を lightweight-charts で表示しています。他のチャートライブラリも試しましたが、大量のデータやマーカーを描画するとスクロールがカクついて動かなくなるので、ヌルヌル動く lightweight-charts はとてもおすすめです。

毎日 [Github](https://d.hatena.ne.jp/keyword/Github) Actions が最新の S3 の [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルの presigned URL を生成して解析ページのリンク URL のクエリパラメータに含ませています。ページがブラウザで開かれると [javascript](https://d.hatena.ne.jp/keyword/javascript) で [SQLite](https://d.hatena.ne.jp/keyword/SQLite) ファイルを自動でダウンロードしてキャッシュしブラウザ上で動的に解析をします。細かいパラメータ調整もブラウザ内でできるようになっています。また、ローカルにあるデータベースファイルを指定することもできるので解析ページの追加開発も簡単にできます。

データベースも含んだ解析ページの全てが一つ URL にまとまっているので、そのリンクを誰にでも共有することができます。S3 の presigned リンクは 7 日間の有効期限があるので流出しても被害は限定できます。特に認証はしていないので簡単に友人に共有できるのが便利です。

#### [Github](https://d.hatena.ne.jp/keyword/Github) issue を作って通知

毎日解析ページをチェックするのは手間なので、日次バッチで解析を行って新しい銘柄が発見されたら自分に通知して欲しいです。僕は Slack などは使ってないのでメールでの通知方法を検討しました。

ただし、メール配信サービスを使ったり [gmail](https://d.hatena.ne.jp/keyword/gmail) の認証情報の設定をするのは大がかりになって面倒くさいです。そこで [Github](https://d.hatena.ne.jp/keyword/Github) issues を使うことにしました。

新しい銘柄が発見されたら [Github](https://d.hatena.ne.jp/keyword/Github) Actions は新しい [Github](https://d.hatena.ne.jp/keyword/Github) issue を作成します。それによって[リポジトリ](https://d.hatena.ne.jp/keyword/%A5%EA%A5%DD%A5%B8%A5%C8%A5%EA)オーナーの自分にメールが届く仕組みです。メールには issue の文章が表示されるので簡単に確認できます。もし、その銘柄が気に入らなければその理由とともに issue を close すれば、後で確認できるログにもなります。

# まとめ

こんなシステムを設計して実装しましたが、かなり便利になりました。作業は休日や仕事終わりだけで、3ヶ月でここまで来れたので AI ってすごいなと思いました。アイディアはあるけど形にするのが面倒くさいという時に強力な相棒になります。

ただ、効率の良いプログラムや[アーキテクチャ](https://d.hatena.ne.jp/keyword/%A5%A2%A1%BC%A5%AD%A5%C6%A5%AF%A5%C1%A5%E3)は、まだ僕でないと作れないなと思ったので、もう少しはソフトウェアエンジニアとしての旨みのある仕事は残っていきそうです。

AI の使い方や、[XBRL](https://d.hatena.ne.jp/keyword/XBRL) ファイルのパースの手法などについてはまた別の記事で解説したいと思います。

オチとしては、今年の運用成績は[日経平均](https://d.hatena.ne.jp/keyword/%C6%FC%B7%D0%CA%BF%B6%D1)に負けてます。個別株なんかせずに[インデックス投資](https://d.hatena.ne.jp/keyword/%A5%A4%A5%F3%A5%C7%A5%C3%A5%AF%A5%B9%C5%EA%BB%F1)をした方がいいのかもしれない。