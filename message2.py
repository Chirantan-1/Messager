from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'secret_key'

names = [["A", "1234"], ["B", "2345"], ["C", "3456"], ["D", "4567"]]

d = {j[0]: i for i, j in enumerate(names)}
m = [[] for _ in names]

unread = [[0 for _ in names] for _ in names]

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
            return render_template(
                "message.html", 
                user=user, 
                messages=[], 
                n=list(zip([_[0] for _ in names], unread[user_index])), 
                e1="Invalid User"
            )

        check_user = request.form.get("check_user")
        if check_user in d:
            check_user_index = d[check_user]
            unread[user_index][check_user_index] = 0
            
            messages = sorted(
                [[msg[1], msg[2], "r"] for msg in m[user_index] if msg[0] == check_user] +
                [[msg[1], msg[2], "s"] for msg in m[check_user_index] if msg[0] == user],
                key=lambda x: x[1]
            )
            return render_template(
                "message.html", 
                user=user, 
                messages=enumerate(messages), 
                n=list(zip([_[0] for _ in names], unread[user_index]))
            )
        elif check_user:
            return render_template(
                "message.html", 
                user=user, 
                messages=[], 
                n=list(zip([_[0] for _ in names], unread[user_index])), 
                e2="Invalid User"
            )

        return redirect(url_for('mess'))
    
    return render_template(
        "message.html", 
        user=user, 
        messages=[], 
        n=list(zip([_[0] for _ in names], unread[user_index]))
    )

@app.route("/relogin", methods=["POST"])
def relogin():
    session.pop('user', None)
    return redirect(url_for('main'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

