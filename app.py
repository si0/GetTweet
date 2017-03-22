from flask import Flask, request, render_template, flash, redirect, url_for
from gettweet import getPics
import config
import os


# Configurations
DEBUG = config.flask_config["DEBUG"]
SECRET_KEY = config.flask_config["SECRET_KEY"]

# Flaskオブジェクト
app = Flask(__name__)
app.config.from_object(__name__)


# キャッシュバスター
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route("/")
def show_index():
    return render_template("index.html")


@app.route("/getPics", methods=["POST", "GET"])
def pro_getPics():
    # GETの場合は"/"へリダイレクト
    if request.method == "GET":
        return redirect(url_for("show_index"))

    else:
        # 未記入がある場合は戻る
        if not request.form["user_id"]:
            flash("未記入の項目があります")
            redirect(url_for("show_index"))

        else:
            # POSTされたユーザーIDの取得
            user_id = request.form["user_id"]
            # 画像を収集する
            result = getPics(user_id)

            # zip圧縮が成功した場合は画像をダウンロードできるようにする
            if result == "zip_success":
                # zipのパスを取得する
                zip_path = "./zip/%s.zip" % user_id
                return render_template("index.html", zip_path = zip_path)

            # [エラー]ユーザーが存在しない場合
            if result == "exists_user":
                flash("存在しないユーザーIDです")

            # [エラー]何かしらのエラー
            elif result == "error":
                flash("エラーが発生しました")

    return redirect(url_for("show_index"))


if __name__ == "__main__":
    app.run(threaded=True)
