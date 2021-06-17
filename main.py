import json

from tkinter import Tk, Label, StringVar, Entry, Button

import os
from dotenv import load_dotenv

load_dotenv()
password = os.getenv("PASS")

with open("data.json", "r") as f:
    data = json.load(f)

with open("playoffs.json", "r") as f:
    playoff = json.load(f)


def main():
    win = Tk()

    index = 1

    win.columnconfigure(0, minsize=10)
    win.columnconfigure(2, minsize=10)
    win.columnconfigure(8, minsize=10)

    win.rowconfigure(0, minsize=10)

    for i in data:
        Label(win, text=i).grid(row=index, column=1)
        Button(win, text="Table", command=lambda i=i: table(i)).grid(row=index,
                                                                     column=3)
        Button(win, text="Fixtures",
               command=lambda i=i: fixtures(i)).grid(row=index, column=5)

        Button(win, text="Add Score",
               command=lambda i=i: login(i)).grid(row=index, column=7)

        win.rowconfigure(index + 1, minsize=10)

        index += 2

    Label(win, text="Playoffs").grid(row=index, column=1)
    Button(win, text="Fixtures", command=playoffs).grid(row=index, column=5)
    Button(win, text="Generate", command=gen_login).grid(row=index, column=3)

    win.mainloop()


def table(group):
    win = Tk()
    table = data[group]["Table"]

    index = 2

    ind = 2
    for i in table[0][list(table[0])[0]]:
        Label(win, text=i).grid(row=index - 1, column=ind)
        ind += 1

    for i in table:
        ind = 2
        Label(win, text=list(i)[0]).grid(row=index, column=1)
        for j in i[list(i)[0]]:
            Label(win, text=i[list(i)[0]][j]).grid(row=index, column=ind)
            ind += 1

        index += 1

    win.mainloop()


def fixtures(group):
    win = Tk()
    fixtures = data[group]["Fixtures"]

    index = 2

    for i in fixtures:
        ind = 1
        scores = []

        for j in fixtures[i]["Teams"]:
            Label(win, text=j).grid(row=index, column=ind)
            score = fixtures[i]["Teams"][j]
            if score == None:
                if ind == 1:
                    score = "N"
                else:
                    score = "A"

            scores.append(score)

            ind += 2

        date = []
        for j in fixtures[i]["Date"]:
            date.append(str(j))

        text = f"{scores[0]} V {scores[1]}\n{' '.join(date)}\n{fixtures[i]['Venue']}"

        Label(win, text=text).grid(row=index, column=2)

        index += 1

    win.mainloop()


def add_score(group, gameid, teams):
    game = data[group]["Fixtures"][gameid]

    scr = Tk()
    team1 = StringVar(scr)
    team2 = StringVar(scr)

    Label(scr, text=teams[0]).grid(row=1, column=2)
    Entry(scr, textvariable=team1).grid(row=2, column=2)

    Label(scr, text=teams[1]).grid(row=1, column=4)
    Entry(scr, textvariable=team2).grid(row=2, column=4)

    Button(scr,
           text="Submit",
           command=lambda: add(group, game, teams, team1, team2, scr)).grid(
               row=2, column=3)

    scr.mainloop()


def add(group, fixture, teams, t1, t2, win):
    win.destroy()
    table = data[group]["Table"]

    for i in table:
        for j in i:
            if j == teams[0]:
                team1 = i[j]
            elif j == teams[1]:
                team2 = i[j]

    score1 = int(t1.get())
    score2 = int(t2.get())

    fixture["Teams"][teams[0]] = score1
    fixture["Teams"][teams[1]] = score2

    team1["Played"] += 1
    team2["Played"] += 1

    if score1 > score2:
        team1["Won"] += 1
        team1["PF"] += score1
        team1["PA"] += score2
        team1["PD"] = team1["PF"] - team1["PA"]
        team1["Points"] += 3

        team2["Lost"] += 1
        team2["PF"] += score2
        team2["PA"] += score1
        team2["PD"] = team2["PF"] - team2["PA"]
        team2["Points"] += 0

    elif score1 == score2:
        team1["Draw"] += 1
        team1["PF"] += score1
        team1["PA"] += score2
        team1["PD"] = team1["PF"] - team1["PA"]
        team1["Points"] += 1

        team2["Draw"] += 1
        team2["PF"] += score2
        team2["PA"] += score1
        team2["PD"] = team2["PF"] - team2["PA"]
        team2["Points"] += 1

    elif score1 < score2:
        team1["Lost"] += 1
        team1["PF"] += score1
        team1["PA"] += score2
        team1["PD"] = team1["PF"] - team1["PA"]
        team1["Points"] += 0

        team2["Won"] += 1
        team2["PF"] += score2
        team2["PA"] += score1
        team2["PD"] = team2["PF"] - team2["PA"]
        team2["Points"] += 3

    table_ord = []

    for i in range(4):
        max_points = 0
        max_team = ""
        first = False
        for j in range(len(table)):
            if table[j][list(table[j])[0]]["Points"] > max_points:
                max_points = table[j][list(table[j])[0]]["Points"]
                max_team = j
                first = True

            elif table[j][list(table[j])[0]]["Points"] == max_points:

                if not first:
                    max_team = j
                    first = True

                if table[j][list(table[j])[0]]["PD"] > table[max_team][list(table[max_team])[0]]["PD"]:
                    max_team = j
                    first = True

        table_ord.append(table[max_team])
        del table[max_team]

    data[group]["Table"] = table_ord

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)


def score(group):
    fixtures = data[group]["Fixtures"]
    win = Tk()

    index = 2

    for i in fixtures:
        teams = []
        for j in fixtures[i]["Teams"]:
            teams.append(j)
        text = " v ".join(teams)
        Button(
            win,
            text=text,
            command=lambda i=i, teams=teams: add_score(group, i, teams)).grid(row=index, column=1)

        index += 1

    win.mainloop()


def login(group):
    def check(auth):
        if auth.get() == password:
            lgin.destroy()
            score(group)

    lgin = Tk()
    auth = StringVar(lgin)

    Entry(lgin, textvariable=auth).grid(row=1, column=1)
    Button(lgin, text="Submit", command=lambda: check(auth)).grid(row=2, column=1)

    lgin.mainloop()


def playoffs():
    win = Tk()

    Label(win, text="Playoffs").grid(row=1, column=1)

    Button(win, text="Theoretical 16s", command=theoretical16).grid(row=3, column=1)
    Label(win, text="(Games based\non unfinished\nresults)").grid(row=4, column=1)

    Button(win, text="Round of 16", disabled=True).grid(row=6, column=1)

    Button(win, text="Semi Finals", disabled=True).grid(row=8, column=1)

    Button(win, text="Final/3rd Place", disabled=True).grid(row=10, column=1)

    win.mainloop()


def theoretical16(needs_return=False):
    tables = []

    for i in data:
        tables.append(data[i]["Table"])

    adef = "3rd A/D/E/F"

    abc = "3rd A/B/C"

    abcd = "3rd A/B/C/D"

    defz = "3rd D/E/F"

    games = [[0, 1, 1, 1], [0, 0, 2, 1], [2, 0, defz, None], [1, 0, adef, None], [3, 1, 4, 1], [5, 0, abc, None], [3, 0, 5, 1], [4, 0, abcd, None]]

    if needs_return:
        return (games)

    win = Tk()

    index = 1
    for i in games:
        Label(win, text=list(tables[i[0]][i[1]])[0]).grid(row=index, column=1)
        Label(win, text="V").grid(row=index, column=2)

        if i[3] == None:
            Label(win, text=i[2]).grid(row=index, column=3)
        else:
            Label(win, text=list(tables[i[2]][i[3]])[0]).grid(row=index, column=3)

        date = []
        for j in playoff["Round of 16"][str(index)]["Date"]:
            date.append(str(j))

        text = " ".join(date)
        Label(win, text=text).grid(row=index, column=4)
        Label(win, text=playoff["Round of 16"][str(index)]["Venue"]).grid(row=index, column=5)

        index += 1

    win.mainloop()


def generate():
    games = theoretical16(True)
    gamedata = playoff["Round of 16"]

    tables = []

    for i in data:
        tables.append(data[i]["Table"])

    for i in range(len(games)):
        print(tables)
        print(games[i][0])
        print(list(tables[games[i][0]][games[i][1]].keys())[0])
        gamedata[str(i + 1)]["Teams"].update(
            {list(tables[games[i][0]][games[i][1]].keys())[0]: None})

        if games[i][3] == None:
            gamedata[str(i + 1)]["Teams"].update({games[i][2]: None})
        else:
            gamedata[str(i + 1)]["Teams"].update({{
                list(tables[games[i][0]][games[i][1]].keys())[0]:
                None
            }})

    with open("playoffs.json", "w") as f:
        json.dump(data, f, indent=2)

def gen_login():
    def check(auth):
        if auth.get() == password:
            lgin.destroy()
            generate()

    lgin = Tk()
    auth = StringVar(lgin)

    Entry(lgin, textvariable=auth).grid(row=1, column=1)
    Button(lgin, text="Submit", command=lambda: check(auth)).grid(row=2,
                                                                  column=1)

    lgin.mainloop()


if __name__ == "__main__":
    main()
