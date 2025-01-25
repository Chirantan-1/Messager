from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'fhgfgyegfygfyegfyegfyufgeufygk'

names = [["A", "1234"], ["B", "2345"], ["C", "3456"], ["D", "4567"]]
d = {"A": 0, "B": 1, "C": 2, "D": 3}
m = [[] for _ in names]

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        if [name, password] in names:
            session['user'] = name
            return redirect(url_for('mess'))
        return render_template("login.html", error="Invalid Username or Password")
    return render_template("login.html")

@app.route("/message", methods=["GET", "POST"])
def mess():
    if 'user' not in session:
        return redirect(url_for('main'))
    user = session['user']
    user_index = d[user]

    if request.method == "POST":
        recipient = request.form.get("user")
        content = request.form.get("cont")
        if recipient in d and content:
            recipient_index = d[recipient]
            m[recipient_index].append([user, content])
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
            print(m)

        check_user = request.form.get("check_user")
        if check_user in d:
            check_user_index = d[check_user]
            messages = [msg[1] for msg in m[user_index] if msg[0] == check_user]
            return render_template("message.html", user=user, messages=messages)

    return render_template("message.html", user=user, messages=[])

@app.route("/relogin", methods=["POST"])
def relogin():
    session.pop('user', None)
    return redirect(url_for('main'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
