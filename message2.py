from flask import Flask, render_template, request, session, redirect, url_for
import time

app = Flask(__name__)
app.secret_key = 'key'

names = [["A", "1234"], ["B", "2345"], ["C", "3456"], ["D", "4567"], ["admin", "123"]]

def rebuild_dicts():
    global d, m, unread
    d = {j[0]: i for i, j in enumerate(names)}
    m = [[] for _ in names]
    unread = [[0 for _ in names] for _ in names]

rebuild_dicts()

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        if [name, password] in names:
            session['user'] = name
            return redirect(url_for('admin' if name == "admin" else 'mess'))
        return render_template("login.html", error="Invalid Username or Password")
    return render_template("login.html")

@app.route("/message", methods=["GET", "POST"])
def mess():
    if 'user' not in session or session['user'] == "admin":
        return redirect(url_for('main'))
    user = session['user']
    if user not in d:
        session.pop('user', None)
        return redirect(url_for('main'))
    user_index = d[user]

    if request.method == "POST":
        recipient = request.form.get("user")
        content = request.form.get("cont")
        if recipient == user:
            return redirect(url_for('mess'))
        if recipient in d and content:
            if len(content) < 110:
                recipient_index = d[recipient]
                if not any(msg[0] == user and msg[1] == content for msg in m[recipient_index]):
                    m[recipient_index].append([user, content, time.time()])
                    unread[recipient_index][user_index] = 1
                max_count = 10
                seen = {}
                result = []
                for item in reversed(m[recipient_index]):
                    char = item[0]
                    if seen.get(char, 0) < max_count:
                        result.append(item)
                        seen[char] = seen.get(char, 0) + 1
                result.reverse()
                m[recipient_index] = result
            return redirect(url_for('mess'))
        elif recipient:
            return render_template("message.html", user=user, messages=[], n=list(zip([_[0] for _ in names], unread[user_index])), e1="Invalid User")

        check_user = request.form.get("check_user")
        if check_user in d:
            check_user_index = d[check_user]
            unread[user_index][check_user_index] = 0
            messages = sorted(
                [[msg[1], msg[2], "r"] for msg in m[user_index] if msg[0] == check_user] +
                [[msg[1], msg[2], "s"] for msg in m[check_user_index] if msg[0] == user],
                key=lambda x: x[1]
            )
            return render_template("message.html", user=user, messages=enumerate(messages), n=list(zip([_[0] for _ in names], unread[user_index])))
        elif check_user:
            return render_template("message.html", user=user, messages=[], n=list(zip([_[0] for _ in names], unread[user_index])), e2="Invalid User")

    return render_template("message.html", user=user, messages=[], n=list(zip([_[0] for _ in names], unread[user_index])))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if 'user' not in session or session['user'] != "admin":
        return redirect(url_for('main'))

    messages = []
    if request.method == "POST":
        check_user = request.form.get("check_user")
        if check_user in d:
            i = d[check_user]
            for j, _ in enumerate(names):
                r_msgs = [[msg[1], msg[2], "r"] for msg in m[i] if msg[0] == names[j][0]]
                s_msgs = [[msg[1], msg[2], "s"] for msg in m[j] if msg[0] == check_user]
                messages = sorted(r_msgs + s_msgs, key=lambda x: x[1])
        elif check_user:
            return render_template("admin.html", messages=[], n=names, e2="Invalid User")

        target = request.form.get("target")
        new_user = request.form.get("new_user")
        new_pass = request.form.get("new_pass")
        for i, (u, p) in enumerate(names):
            if u == target:
                if new_user: names[i][0] = new_user
                if new_pass: names[i][1] = new_pass
                rebuild_dicts()
                break

        recipient = request.form.get("user")
        content = request.form.get("cont")
        if recipient in d and content:
            sender = "admin"
            recipient_index = d[recipient]
            if not any(msg[0] == sender and msg[1] == content for msg in m[recipient_index]):
                m[recipient_index].append([sender, content, time.time()])
                unread[recipient_index][d[sender]] = 1

    return render_template("admin.html", messages=enumerate(messages), n=names)

@app.route("/relogin", methods=["POST"])
def relogin():
    session.pop('user', None)
    return redirect(url_for('main'))

@app.route("/password", methods=["POST"])
def password():
    if 'user' not in session:
        return redirect(url_for('main'))
    p1 = request.form.get("p1")
    p2 = request.form.get("p2")
    if p1 and p2:
        for i, (n, pw) in enumerate(names):
            if n == session['user'] and pw == p1:
                names[i][1] = p2
                return redirect(url_for('mess'))
        return render_template("password_change.html", error="Invalid Password")
    return render_template("password_change.html")

@app.route("/username", methods=["POST"])
def username():
    if 'user' not in session:
        return redirect(url_for('main'))
    p = request.form.get("p")
    u = request.form.get("u")
    if p and u:
        if any(n[0] == u for n in names):
            return render_template("username_change.html", error="Username already exists")
        for i, (n, pw) in enumerate(names):
            if n == session['user'] and pw == p:
                names[i][0] = u
                session['user'] = u
                rebuild_dicts()
                return redirect(url_for('mess'))
        return render_template("username_change.html", error="Invalid Password")
    return render_template("username_change.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

