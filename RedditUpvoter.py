import urllib.request
import urllib.parse
import json
import time
import datetime
import argparse
import sys

def getJSON(url, args : dict, header):
    binaryArgs = None
    if args != None:
        binaryArgs = bytes(urllib.parse.urlencode(args), "UTF8")
    req = urllib.request.Request(url, binaryArgs, header)
    rep = urllib.request.urlopen(req)
    res = str(rep.read(), "UTF8")
    return json.loads(res)

def upvoteAll(user, passwd, userToUpvote):
    # data used for login
    loginData = {
        'user' : user,
        'passwd' : passwd,
        'api_type': 'json'
    }
    # header
    header = {
        'User-Agent' : 'secret santa contracted auto voter 1.0 by /u/gwiazdorrr',
    }

    # login
    print("INFO: logging in as " + user + "...")
    session = getJSON("http://www.reddit.com/api/login/" + user, loginData, header)

    # update header, save user
    header['Cookie'] = "reddit_session=" + session["json"]["data"]["cookie"]
    user = session["json"]["data"]["modhash"]

    # get target user data
    print("INFO: getting user {0} data...".format(userToUpvote))
    time.sleep(2);
    userHistory = getJSON("http://www.reddit.com/user/" + userToUpvote + "/.json?sort=new&limit=100", None, header)

    if "kind" not in userHistory or userHistory["kind"] != "Listing":
        raise Exception("Unexpected kind");

    for entry in userHistory["data"]["children"]:
        data = entry["data"]
        createdOn = datetime.datetime.fromtimestamp(data["created"]);
        name = data["name"]
        if entry["kind"] == "t3":
            title = data["title"]
            type = "link";
        elif entry["kind"] == "t1":
            title = data["link_title"]
            type = "comment";
        else:
            print("WARNING: Unknown entry type: {0} (name: {1}), ignoring".format(entry["kind"], name))
            continue
       
        if data["likes"]:
            print("INFO: already upvoted {1}: {0} {3} from {2}...".format(type, name, createdOn, title.encode('ascii', 'ignore')))
        else:
            print("INFO: upvoting {1}: {0} {3} from {2}...".format(type, name, createdOn, title.encode('ascii', 'ignore')))
            time.sleep(2);
            upvoteData = {
                'id' : name,
                'dir' : 1,
                'uh' : user
            }
            upvote = getJSON("http://www.reddit.com/api/vote", upvoteData, header)
            try:
                if upvote:
                    print("WARNING: Failed to upvote {0} ({1})".format(name))
                    print("\t" + upvote)
            except Exception as ex:
                print("WARNING: Failed on {0}".format(name) + ex)


def main():
    parser = argparse.ArgumentParser(description="Upvotes selected user's activity")
    parser.add_argument("user")
    parser.add_argument("passwd")
    parser.add_argument("target")

    args = parser.parse_args();
    upvoteAll(args.user, args.passwd, args.target);
 
if __name__ == "__main__":
     main()