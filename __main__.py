#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from yaohaocheck import *
import time

phone=os.getenv("phone", "userphone")
pwd=os.getenv("pwd", "123456")
ding_token=os.getenv("ding_token", "11111")

if __name__ == '__main__':
    yaohao = yaohaocheck(phone, pwd, ding_token)
    count = 0
    checkRes = yaohao.check_apply_status()
    while count < 10 and not checkRes:
        print(phone + " login fail, retry")
        count += 1
        time.sleep(1)
        checkRes = yaohao.check_apply_status()

