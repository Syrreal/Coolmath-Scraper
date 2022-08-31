import requests
import re
import time


def parse(page):
    games = {}
    page = page.text
    populardiv = page.find('popularcategoryhome')
    if populardiv != -1:
        page = page[populardiv:]
        gameitems = page.find('game-item')
        if gameitems != -1:
            page = page[:page.find('dtp-hide')]
            gameindeces = [_.start() for _ in re.finditer('game-item', page)]
            startindex = 0
            frames = []
            for index in gameindeces:
                if gameindeces.index(index) % 2 == 0:
                    startindex = index
                else:
                    frames.append(page[startindex:index])
            for frame in frames:
                x = frame.find('title=')
                newframe = frame[x+7:]
                y = newframe.find('"')
                title = newframe[:y]
                games[f'{frames.index(frame)+1}.'] = title
    return games


# return false if dicts are the same
def comparedicts(new, old):
    if new:
        if old:
            i = 1
            different = False
            if old == new:
                print('Dicts are not different')
                print("games ----")
                for key in new:
                    print(f'{key}  {new.get(key)}')
                return different
            print("-----old----------new-----")
            diff_list = []
            while i <= 32:
                index = f'{i}.'
                print(f'{index} {old.get(index)}  ---  {new.get(index)}')
                if new.get(f'{index}') != old.get(f'{index}'):
                    different = True
                    diff_list.append(i)
                i += 1
            if diff_list:
                print(f'Changed indices ---- ')
                for index in diff_list:
                    print(f'{index}', end=', ')
                print('\n')
            return different
        else:
            print("old games is not loaded ---")
            print("games ----")
            for key in new:
                print(f'{key}  {new.get(key)}')
            return True

    else:
        print("New games could not be loaded in 'comparedicts'")
    return False


def retrieveolddict():
    oldgames = {}
    index = 0
    try:
        open('oldgames.txt', 'r')
    except FileNotFoundError:
        print('"oldgames.txt" does not exist -- skipping retrieval of oldgames dict')
        return {}
    with open('oldgames.txt', 'r') as f:
        for line in f:
            if index > 31:
                return oldgames
            stripped_line = line.strip('\n')
            oldgames[f'{index + 1}.'] = stripped_line
            index += 1
        return oldgames


def commitnewdict(newdict):
    templine = 0
    with open('oldgames.txt', 'r') as f:
        for i in range(0, 32):
            f.readline()
        templine = f.readline()
    with open('oldgames.txt', 'w') as f:
        for key in newdict:
            f.write(newdict.get(key))
            f.write('\n')
        f.write(templine)


# calculates time since the list has changed using epoch time
# converts the difference in epoch time to days and hours
# returns a list with 2 components [days, hours]
def gettime(changed):
    newtime = int(time.time())
    oldtime = 0
    templist = []
    with open('oldgames.txt', 'r') as f:
        templist = [f.readline() for line in range(0, 32)]
        oldtime = int(f.readline())
    timediff = []
    timediff.append(int((newtime - oldtime) / 86400))
    timediff.append(int(((newtime - oldtime) / 3600) - (timediff[0]*24)))
    if changed:
        with open('oldgames.txt', 'w') as f:
            f.writelines(templist)
            f.write(f'{newtime}')
    return timediff


def main():
    games = {}

    coolmathlink = "https://www.coolmathgames.com"

    page = requests.get(coolmathlink)
    if page.status_code == 200:
        games = parse(page)
    else:
        print(f'Page request failed with code: {page.status_code}')

    oldgames = retrieveolddict()

    changed = False
    if comparedicts(games, oldgames):
        print('Dicts were different, committing new list to file')
        commitnewdict(games)
        changed = True

    timechange = gettime(changed)
    print(f'TIME SINCE LAST CHANGE -- {timechange[0]} DAYS {timechange[1]} HOURS')


if __name__ == "__main__":
    main()
