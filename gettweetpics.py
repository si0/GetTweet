from urllib.request import urlopen
import tweepy
import config
import os
import requests

def getPics(user_id):
    # TwitterDeveloperTool認証
    CONSUMER_KEY = config.authkey["CON_KEY"]
    CONSUMER_SECRET = config.authkey["CON_SEC"]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    ACCESS_TOKEN = config.authkey["ACC_TOK"]
    ACCESS_SECRET = config.authkey["ACC_SEC"]
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    # APIの作成
    api = tweepy.API(auth)

    try:
        # 全ツイート数を取得
        count = api.get_user(user_id).statuses_count - 1
    except tweepy.error.TweepError:
        print("ユーザーが存在しません。")
        return "exists_user"

    # 保存先フォルダがない場合は作成
    if not os.path.isdir("./img"):
        os.mkdir("img")

    if not os.path.isdir("./img/" + user_id):
        os.mkdir("img/" + user_id)

    tweet_count = 0 # ツイート数のカウント
    tweet_page = 1 # ツイート毎のページ数のカウント
    file_number = 1 # ファイル名のカウント

    # ツイートの取得
    result = api.user_timeline(user_id, count=250, page=1)
    result_len = len(result) - 1

    try:
        for i in range(count):
            # 作業中のページが終了した場合は次のページへ
            if tweet_count > result_len and result_len != 0:
                tweet_count = 0
                tweet_page = tweet_page + 1
                result = api.user_timeline(user_id, count=result_len + 1, page=tweet_page)
                result_len = len(result) - 1

            # リツイートの場合は画像を取得しない
            if hasattr(result[tweet_count], "retweeted_status"):
                tweet_count = tweet_count + 1
                continue

            # 画像付きツイートの判断
            elif "media" in result[tweet_count].entities:
                # 画像の数(1ツイート内)の取得
                media_len = len(result[tweet_count].extended_entities["media"])

                # ツイート内の画像を保存
                for n in range(media_len):
                    # 画像URLの取得
                    media_url = result[tweet_count].extended_entities["media"][n]["media_url"]
                    # 拡張子の取得
                    extension = ".%s" % media_url.split("/")[-1].split(".")[-1]
                    # 元サイズの画像URLへURLの書き換え
                    media_url = "%s:orig" % media_url
                    # ファイル名の設定
                    file_name = user_id + "_" + str(file_number) + extension
                    file_number = file_number + 1
                    # 画像の保存
                    download(media_url, user_id, file_name)

                tweet_count = tweet_count + 1

            else:
                tweet_count = tweet_count + 1

    except IndexError as e:
        print("エラー: " + str(e))
        print("ツイートページ: " + str(tweet_page))
        print("ツイートカウント: " + str(tweet_count))
        print("ツイート総数: " + str(count))
        return "error"


def download(media_url, user_id, file_name):
    # URL先ステータスの取得
    res = requests.get(media_url)
    # URL先に画像があることを確認
    if res.status_code == 200:
        # 画像の保存
        with open("./img/" + user_id + "/" + file_name, 'wb') as f:
            media = urlopen(media_url)
            f.write(media.read())
            f.close()
    else:
        return None
