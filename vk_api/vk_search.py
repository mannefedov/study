import vk
import os
import time

def main():
    session = vk.AuthSession(app_id=5506677, user_login='manefedov26@gmail.com', user_password=input('enter password: '))
    api = vk.API(session)

    all_users = api.users.search(country=1, city=1083663, count=662, fields='bdate,sex,education,personal', offset=492)

    try:
        os.mkdir('corpus')
    except FileExistsError:
        pass

    os.chdir('corpus')
    meta = open('meta.csv', 'w', encoding='utf-8')
    meta.write('id,sex,bdate,education,lang\n')
    for user in all_users[1:]:
        time.sleep(2)
        posts = api.wall.get(owner_id=user['uid'], filter='owner', count=100)
        try:
            sex = 'None'
            g = user.get('sex')
            if g is not None:
                sex = 'male' if g == 2 else 'female'
            bdate = 'None'
            if user.get('bdate') is not None:
                bdate = user['bdate']
            edu = 'None'
            g = user.get('university')
            if g is not None:
                edu = g
            lang = 'None'
            g = user.get('personal')
            if g is not None and g != [] and g.get('langs') is not None:
                lang = '\,'.join(g.get('langs'))
            meta.write('{},{},{},{},{}\n'.format(user['uid'], sex, bdate, edu, lang))
        except Exception:
            print(user)
            raise
        with open(str(user['uid']) + '.txt', 'w', encoding='utf-8') as dump:
            for p in posts[1:]:
                if len(p['text']) > 1:
                    dump.write(p['text'] + '\n')
    meta.close()

if __name__ == '__main__':
        main()
