
class fixed_config():
    def __init__(self):
        self.New_Port="Port 22222"
        self.UserName="safe_account"
        self.UserPass="root@userpass"
        self.Lock_users = ['listen', 'gdm', 'webservd','nobody', 'nobody4', 'noaccess']
        self.Initial_dir="/etc/._initialbak/"
