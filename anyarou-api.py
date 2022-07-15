import typing as t
from flask import Flask, request
import subprocess

# перед запуском сервера файлу должны быть предоставлены права
# $ chmod +X anyarou-api.py
# а также должен быть установлен screen
# вместе с апи, в папке должны находиться файлы
# key.txt, pid.txt, shell-скрипт для запуска бота

KEY = ''

# запустить Аняру
def start(*, full_output: bool = False) -> t.Tuple[bool, str]:
    # читаем ид процесса (если 0, то процесса нет, значит бот не запущен)
    with open('pid.txt', encoding='utf-8') as f:
        pid = f.read().replace('\n', '')

    # если бот уже в сети то ниче делать не нужно
    if pid != '0':
        return False, f'Bot already is online - {pid}'

    # открываем процесс
    # используется шелл, т.к. в линуксе пайтон всегда запущен
    # и может быть конфликт в айди процессов
    # внутри anyarou.sh команда python startup.py
    proc = subprocess.Popen(
        ('screen', '-dmS', 'anyarou', 'sh', 'anyarou.sh'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    startup_out, startup_err = proc.communicate()

    if proc.returncode != 0:
        return False, startup_err.decode('utf-8')

    # здесь спрашиваем ид процесса у системы
    # чтобы его записать в файл
    pidof = subprocess.run(('pidof', '-s', 'sh'), stdout=subprocess.PIPE)
    pid = pidof.stdout.decode('utf-8')

    with open('pid.txt', 'w', encoding='utf-8') as f:
        f.write(pid)

    out = f'Bot online - {pid}'
    # full_output для полного вывода того что произошло при старте
    if full_output:
        out = startup_out.decode('utf-8') + '\n' + out

    return True, out

# оффнуть Аняру
def stop() -> t.Tuple[bool, str]:
    with open('pid.txt', encoding='utf-8') as f:
        pid = f.read().replace('\n', '')
        end_at = int(pid) + 10 # это надо тк та фигня сверху будет изменяться

    if pid == '0':
        return False, 'Bot already is offline'

    ret = (True, 'Bot succesfully terminated')

    # пытаемся найти процесс и стопнуть
    while True:
        kill = subprocess.run(('kill', pid), stderr=subprocess.PIPE)
        if kill.returncode == 0:
            # если процесс получилось стопнуть закрываем цикл
            break
        killerr = kill.stderr.decode('utf-8')
        pid = str(int(pid) + 1)
        if int(pid) > end_at:
            # ну а если не получилось то пусть
            # сам подключается к вдске и стопает балбес
            # или делает запрос к эндпоинту выполнения команд
            ret = (False, 'Tried to kill process 10 times but no process was found in this range\n'\
                            f'{killerr}\n'\
                            'Setting pid to 0')
            break

    with open('pid.txt', 'w', encoding='utf-8') as f:
        f.write('0')

    return ret


# -----------------------------
app = Flask(__name__)

# аче
@app.route('/')
def index():
    return 'тебе че тут надо'

# жиденько покакал
@app.route('...')
def main_route():
    if request.args.get('key') != KEY:
        # отправить домой если пытается чето сделать без ключа
        return 'Key is required'
    method = request.args.get('method')

    if method in ('run', 'start'):
        _, out = start(full_output=True)
        return out

    elif method in ('stop', 'shutdown'):
        _, out = stop()
        return out

    elif method == 'restart':
        completed, stop_out = stop()
        if not completed:
            return stop_out
        completed, start_out = start()
        return f'{stop_out}\n{start_out}' if completed else start_out

    elif method == 'status':
        with open('pid.txt', encoding='utf-8') as f:
            pid = f.read().replace('\n', '')
        return f'Bot online - {pid}' if pid != '0' else 'Bot offline'

    elif method in ('update', 'upgrade'):
        update = subprocess.run(
            ('pip3.9', 'install', '-r', 'requirements.txt', '--upgrade'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if update.returncode == 0:
            return update.stdout.decode('utf-8')
        return update.stderr.decode('utf-8')

    elif method == 'screens':
        screenls = subprocess.run(
            ('screen', '-ls'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if screenls.returncode == 0:
            return screenls.stdout.decode('utf-8')

        return screenls.stderr.decode('utf-8')

    else:
        return 'Invalid method'

if __name__ == '__main__':
    # в файле key.txt должен быть ключ, без которого запросы
    # будут бессмысленны
    with open('key.txt', encoding='utf-8') as f:
        KEY = f.read().replace('\n', '')
    app.run(host='0.0.0.0')
