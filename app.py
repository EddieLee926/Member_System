# 載入pymongo套件
import pymongo
# 載入所有Flask套件
from flask import *
from flask import render_template
from flask import redirect

# ----------------------------------------------------------------
# 連線到 MongoDB 雲端資料庫
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://root:root666@cluster0.xo0kjco.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# 把資料放進資料庫中
db = client.member_system  # 選擇操作 XXXX 資料庫，他會幫我們創一個test資料庫

# ----------------------------------------------------------------
# 初始化 Flask 伺服器
# 建立application物件，可以設定靜態檔案的路徑處理
app = Flask(
    __name__,
    static_folder="public",     # 靜態檔案的資料夾名稱，預設是"static"
    static_url_path="/"  # 靜態檔案對應的網址路徑，預設是"/static"
)
# 所有在 static 資料夾底下的檔案，都對應到網址路徑 /static/檔案名稱
app.secret_key = "secretkey"  # 設定session的密鑰

# ----------------------------------------------------------------
# ?????????????????

# 首頁頁面


@app.route("/")
def index():
    return render_template("index.html")


# /member 會員頁面
@app.route("/member")
def member():
    # 要進入會員頁面之前，要先判斷nickname有沒有紀錄在session裡面
    if "nickname" in session:
        return render_template("member.html")
    else:
        return redirect("/")


# /error 錯誤頁面，用「要求字串」帶出錯誤訊息
# /error?msg=錯誤訊息
@app.route("/error")
def error():
    message = request.args.get("msg", "發生錯誤。請聯繫客服")
    return render_template("error.html", message=message)


# /signUp 會員註冊功能，純後端功能
@app.route("/signUp", methods=["POST"])
def signUp():
    # 從前端接收資料
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    # 根據接收到的資料，和資料互動
    collection = db.users  # 選擇操作 XXXX 集合
    # 檢查會員集合中是否有相同 email 的文件資料
    result = collection.find_one({
        "email": email
    })
    if result != None:
        return redirect("/error?msg=信箱已經被註冊過了")
        # 把資料放進資料庫，完成註冊
    else:
        collection.insert_one({
            "nickname": nickname,
            "email": email,
            "password": password
        })
        return redirect("/")


# /signIn 會員登入功能，純後端功能
# 若登入成功，我們在session紀錄會員資訊
# redirect到(路由到) /member 頁面
# 若登入成功，redirect到(路由到) /error?msg=錯誤訊息 頁面
@app.route("/signIn", methods=["POST"])
def signIn():
    # 從前端接收資料
    email = request.form["email"]
    password = request.form["password"]
    # 根據接收到的資料，和資料互動
    collection = db.users  # 選擇操作 XXXX 集合
    # 檢查密碼是否正確
    result = collection.find_one({
        "$and": [
            {"email": email},
            {"password": password}
        ]
    })
    if result == None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
        # 找不到對應的資料，登入失敗，導向到錯誤頁面
    else:
        # 登入成功，在session紀錄會員資訊，導向到會員頁面
        session["nickname"] = result["nickname"]
        return redirect("/member")


# /signOut 會員登出功能，純後端功能
# 若登出成功，我們在session移除會員資訊
# redirect到(路由到) / 頁面
@app.route("/signOut")
def signOut():
    # 移出 session 中的會員資訊
    del session["nickname"]
    return redirect("/")


# 啟動網站伺服器,可透過 port 參數指定阜號
app.run(port=3000)

# 啟動程序:
# python app.py
