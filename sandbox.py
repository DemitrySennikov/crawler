# Песочница - поле для экспериментов
# Пишу какой-нибудь короткий код, чтобы проверить, как работает та или иная питонская штука

import urllib.robotparser as rob
from urllib.parse import urlparse

b = urlparse("https://ru.wikipedia.org/wiki/Гауссов_интеграл")
a = rob.RobotFileParser()
a.set_url(b.scheme + "://" + b.netloc + "/robots.txt")
a.read()
print(a.can_fetch("*", "https://ru.wikipedia.org/wiki/"))
