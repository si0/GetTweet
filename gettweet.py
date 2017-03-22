from urllib.request import urlopen
import tweepy
import config
import os
import requests
import re


# twitterdevelopertool認証
CONSUMER_KEY = config.authkey["CON_KEY"]
CONSUMER_SECRET = config.authkey["CON_SEC"]
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
ACCESS_TOKEN = config.authkey["ACC_TOK"]
ACCESS_SECRET = config.authkey["ACC_SEC"]
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# APIの作成
api = tweepy.API(auth)


def getPics(user_id):
    # ユーザーの存在確認
    try:
        api.get_user(user_id)

    except tweepy.error.TweepError as e:
        if e.response.status_code == 404:
            return "exists_user"

    except:
        return "error"

    # 保存先フォルダがない場合は作成
    if not os.path.isdir("./img"):
        os.mkdir("img")
    if not os.path.isdir("./img/" + user_id):
        os.mkdir("img/" + user_id)

    file_number = 1 # ファイル名のカウント

    for result in tweepy.Cursor(api.user_timeline, id=user_id).items():
        # リツイートの場合は画像を取得しない
        if hasattr(result, "retweeted_status"):
            continue

        # 画像付きツイートの判定
        if "media" in result.entities:
            # 画像の数(1ツイート内)の取得
            media_len = len(result.extended_entities["media"])

            # ツイート内の画像を保存
            for n in range(media_len):
                # 画像URLの取得
                media_url = result.extended_entities["media"][n]["media_url"]
                # 拡張子の取得
                extension = ".%s" % media_url.split("/")[-1].split(".")[-1]
                # 元サイズの画像URLへ切り替え
                media_url = "%s:orig" % media_url
                # ファイル名の設定
                file_name = user_id + "_" + str(file_number) + extension
                file_number += 1
                # 画像の保存
                download(media_url, user_id, file_name)


def getTweet(user_id, keyword_arg):
    # 検索に一致したツイート内容のリスト
    result_list = []

    # ツイート情報の取得
    result = tweepy.Cursor(api.user_timeline, id=user_id).items()

    # 大文字小文字のどちらも検索可能にする
    keyword = re.compile(keyword_arg, re.IGNORECASE)

    for row in result:
        # キーワードのツイートを判定する
        if re.search(keyword, row.text):
            # リストに追加
            result_list.append({
                "text": row.text,
                "created_at": row.created_at
                })

    print("######################################")
    print("検索が完了しました")
    print("######################################\n")

    # 取得した検索結果の表示
    for row in result_list:
        print("ツイート    : %s" % row["text"])
        print("日時(UTC+0) : %s" % row["created_at"])
        print("---------------------------------------\n")


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
