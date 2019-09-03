import winrm
import shutil
import os

transfer_folder = '\\\\192.168.13.1\\share\share_with_blades\\125'

config_name = "CONFIG_v1"

swan_remote_path = 'C:\\Users\\nano_user'

ps_script_1 = r"""Copy-Item %s\%s.swn %s
""" % (transfer_folder, config_name, swan_remote_path)

ps_script_2 = r"""& %s\swanrun.bat %s\\%s
""" % (swan_remote_path, swan_remote_path, config_name)

swan_remote_path_results = '%s\\results' % swan_remote_path
result_name = 'HSign_v0.dat'
ps_script_3 = r"""Copy-Item  %s\\%s %s
""" % (swan_remote_path_results, result_name, transfer_folder)
script = ps_script_1 + ps_script_2 + ps_script_3

s = winrm.Session('192.168.13.125', auth=('nano_user', 'uit2Zqhj4c'))
r1 = s.run_ps(script)

out = r1.std_out
# s.run_ps(ps_script_3)
print(out)
print('end')
