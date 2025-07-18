# coding=utf-8
# 需要安装 [sudo]gem install terminal-notifier
# The notifier function
'''
Description:
Author: itgoyo
E-mail: itgoyo@gmail.com
Github: itgoyo
'''
import os

def notify(title, subtitle, message,appIcon):
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    i = '-contentImage {!r}'.format(appIcon)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s,i])))


# # Calling the function
# notify(title    = '订阅价格变化',
#     subtitle = '价格',
#     message  = '⚡️⚡️订阅价格变化⚡️⚡️',
#     appIcon = 'https://img.qlchat.com/qlLive/admin/BX31GN25-3MYD-77L3-1670913090514-FXIC2795ZRMI.JPG')

