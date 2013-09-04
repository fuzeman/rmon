import HTMLParser
import pprint
import datetime
from flask import Flask, render_template
from rlib import Reddit

app = Flask(__name__)
reddit = Reddit()
comment_cache = {}
h = HTMLParser.HTMLParser()


@app.route('/')
def home():
    return 'Hello World'


@app.route('/u/<username>/<limit>')
@app.route('/u/<username>', defaults={'limit': 25})
def user(username, limit):
    limit = int(limit)
    if limit > 50:
        limit = 50

    user = reddit.get_user(username)

    comments = []

    for comment in user.get_comments():
        full_comment = get_full_comment(comment)

        #pprint.pprint(comment.__dict__)
        #pprint.pprint(full_comment.__dict__)
        if full_comment:
            comments.append(create_comment_model(comment, full_comment))

        if len(comments) >= limit:
            break

    return render_template('user.html', request_detail={
        'username': username,
        'limit': limit
    }, user=user, comments=comments)


def create_comment_model(comment, full_comment):
    comment_model = create_reply_model(full_comment)

    comment_model.update({
        'body_html': h.unescape(full_comment.body_html),
        'link_title': comment.link_title
    })

    pprint.pprint(comment_model)

    return comment_model


def create_reply_model(full_comment):
    model = {
        'author': full_comment.author,
        'body_html': h.unescape(full_comment.body_html),
        'permalink': full_comment.permalink,
        'replies': []
    }

    for reply in full_comment.replies:
        model['replies'].append(create_reply_model(reply))

    return model


def get_full_comment(comment):
    if comment.id in comment_cache:
        cc = comment_cache[comment.id]

        if (datetime.datetime.now() - cc['date']).total_seconds() < 1 * 60 * 60:
            return cc['object']

    full_comment = reddit.get_comment(comment.subreddit, comment.link_id, comment.id)
    comment_cache[comment.id] = {
        'date': datetime.datetime.now(),
        'object': full_comment
    }

    return full_comment


if __name__ == '__main__':
    app.run(debug=True, port=5001)