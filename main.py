import winrm

ps_script_1 = r"""Copy-Item \\192.168.13.1\share\Deeva\CONFIG_v0.{s} C:\\Users\\nano_user
""".format(s="swn")

ps_script_2 = r"""& D:\{SWAN}_sochi\swanrun.bat CONFIG_v0
""".format(SWAN="SWAN")

ps_script_3 = r"""Copy-Item  C:\\Users\\{nano_user}\\results\\HSign_v0.dat \\192.168.13.1\share\Deeva
""".format(nano_user="nano_user")
script = ps_script_1 + ps_script_2 + ps_script_3
s = winrm.Session('192.168.13.125', auth=('nano_user', 'uit2Zqhj4c'))
r1 = s.run_ps(script)

out = r1.std_out
# s.run_ps(ps_script_3)
print(out)
print('end')
