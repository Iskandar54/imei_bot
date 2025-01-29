import subprocess

if __name__ == "__main__":
    database = subprocess.Popen('python database.py')
    api_server = subprocess.Popen('python api_local.py')
    bot = subprocess.Popen('python bot_aio.py')