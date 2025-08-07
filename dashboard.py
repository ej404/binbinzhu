import os
import sqlite3
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

@app.route('/admin', methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != PASSWORD:
            return "❌ 密码错误", 403
    else:
        return '''
            <form method="post">
                <input type="password" name="password" placeholder="请输入密码">
                <button type="submit">登录</button>
            </form>
        '''

    with sqlite3.connect("transactions.db") as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS records (user_id TEXT, amount TEXT, currency TEXT, raw_text TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        rows = c.execute("SELECT user_id, amount, currency, timestamp FROM records ORDER BY timestamp DESC").fetchall()
    return render_template("dashboard.html", records=rows)
    if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
