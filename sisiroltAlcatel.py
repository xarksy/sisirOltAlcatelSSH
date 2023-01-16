import paramiko
import time
import re
from datetime import datetime
import os
import concurrent.futures

now = datetime.now()
current_dir = os.getcwd()

def connect_ssh():
    host = 'iphostnya'
    username = 'usernya'
    password = 'passwordssh'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Menguhubungkan.... ' + host)
    ssh.connect(host,22,username=username,password=password)    
    remote_conn = ssh.invoke_shell()    

    return ssh, remote_conn


def mengtelnet(remote_conn, ip):
    
    filename_hasilssh = r'hasilsshtemp.txt'
    myfile = os.path.join(current_dir, filename_hasilssh)
    f = open(myfile, "w")

    try:
        remote_conn.send('telnet ' + str(ip) + '\n')
        print('Telnet ' + str(ip))
        output_str = ''
        output = remote_conn.recv(99999)
        output_str = output.decode('utf-8').replace('\x1b','')
        output_str2 = re.sub(r'..(1D)','',output_str)
        # remote_conn.settimeout(3)
        # ===================== waiting login
        i = 0
        while True:
            output_str = ''
            output = remote_conn.recv(99999)
            output_str = output.decode('utf-8').replace('\x1b','')
            output_str2 = re.sub(r'..(1D)','',output_str)
            print(output_str2)
            print('========================================================================= 1')
            i = i + 1
            print('waiting login...',i)
            time.sleep(5)

            if 'Connected' in output_str2 or i == 30:
                # remote_conn.send('\x03')
                # print('exiting...')
                print(output_str2)
                print('========================================================================= 2')
                print('logging in....')
                remote_conn.send('usernya' + '\n')
                remote_conn.send('passwordtelnet' + '\n')
                time.sleep(1)
                while True:
                    output_str = ''
                    output = remote_conn.recv(99999)
                    output_str = output.decode('utf-8').replace('\x1b','')
                    output_str2 = re.sub(r'..(1D)','',output_str)
                    # remote_conn.send('\x03')
                    # time.sleep(1)                    
                    print('cek unprov')
                    time.sleep(1)
                    print(output_str2)
                    print('========================================================================= 3')
                    if 'Welcome to ISAM' in output_str2:
                        print('login sukses................')
                        remote_conn.send('show pon unprov' + '\n')
                        print(output_str2)
                        print('========================================================================= 4')
                        # ===================== waiting uncfg
                        i = 0
                        hasil_list_uncfg = []
                        while True:
                            time.sleep(5)
                            output_v2_str = ''
                            output_v2 = remote_conn.recv(99999)
                            output_v2_str = output_v2.decode('utf-8').replace('\x1b','')
                            output_v2_str2 = re.sub(r'..(1D)','',output_v2_str)
                            i = i + 1
                            print('waiting uncfg...',i)
                            

                            try:
                                uncfgsnnya = re.findall(r'1/1/.*',output_v2_str2)
                                for we in uncfgsnnya:
                                    hem = re.search(r'1/1/\d+/\d+\s*([^\s]+)',we)
                                    if 'ALCL' in hem[0] or 'HWTC' in hem[0] or 'ZTEG' in hem[0] or 'FHTT' in hem[0]:
                                        hostname = re.search(r'GPON.*>', output_v2_str2)
                                        if hem[0] not in hasil_list_uncfg:
                                            wes = ip, hostname[0].replace('>',''), hem[0], datetime.now().strftime('%I:%M:%S:%p %d-%m-%Y')
                                            hasil_list_uncfg.append(wes)
                            except Exception as e:
                                print(e)
                                pass

                            if 'unprovision-onu count' in output_v2_str2 or i == 60:
                                # ==================================================================== ngerekap
                                # f.write(str(ip) + ' ' + str(datetime.now()) + '\n')
                                # print('didalam proses................................................')
                                print(hasil_list_uncfg)
                                
                                hasil = output_v2_str2
                                # olahdataya(hasil)
                                f.write(hasil + '\n')
                                # ====================================================================
                                # print(output_v2_str2)
                                print('========================================================================= 5')
                                try:
                                    jumlah_unprov = re.search(r'unprovision-onu count : \d+',output_v2_str2)
                                    print('unprovision-onu count : ', jumlah_unprov[0])
                                except:
                                    jumlah_prov = re.search(r'interface count : \d+',output_v2_str2)
                                    print('interface count : ', jumlah_prov[0])
                                remote_conn.send('logout' + '\n')
                                print("logged out")                                
                                while True:
                                    output_v2_str = ''
                                    output_v2 = remote_conn.recv(99999)
                                    output_v2_str = output_v2.decode('utf-8').replace('\x1b','')
                                    output_v2_str2 = re.sub(r'..(1D)','',output_v2_str)
                                    print('masuk looping sini sukses....')
                                    print(output_v2_str2)
                                    print('========================================================================= 6')
                                    if 'Connection closed' in output_v2_str2:
                                        print('break dari looping sukses')
                                        print('break 1')  
                                        break
                                print('break 2')
                                break

                        time.sleep(5)
                        print('break 3')  
                        break
                        
                    else:
                        remote_conn.send('logout' + '\n')
                        remote_conn.send('\x03')
                        print('exiting from logging...')
                        while True:
                            output_v2_str = ''
                            output_v2 = remote_conn.recv(99999)
                            output_v2_str = output_v2.decode('utf-8').replace('\x1b','')
                            output_v2_str2 = re.sub(r'..(1D)','',output_v2_str)
                            print('masuk looping exit sini....')
                            print(output_v2_str2)
                            print('========================================================================= 7')
                            if 'Connection closed' in output_v2_str2:
                                print('break 4')
                                break
                        print('break 5')
                        break

                print('break 6')
                time.sleep(5)
                # f.close()
                break
            
            elif ('Trying') in output_str:
                remote_conn.send('\x03')
                print('exiting...')
                print('break 7 dari trying')
                time.sleep(5)
                break

        # remote_conn.send('logout' + '\n')
        f.close()
        return hasil,jumlah_unprov[0]
        

    except Exception as e:
        print(e)
    

def olahdataya(inputnya):
    hasil_list_uncfg = []
    uncfgsnnya = re.findall(r'1/1/.*',inputnya)
    print('done telnet')
    for we in uncfgsnnya:
        hem = re.search(r'1/1/\d+/\d+\s*([^\s]+)',we)
        if 'ALCL' in hem[0] or 'HWTC' in hem[0] or 'ZTEG' in hem[0] or 'FHTT' in hem[0]:
            hostname = re.search(r'GPON.*>', inputnya)
            wes = wow, hostname[0].replace('>',''), re.sub(' +',' ',hem[0]), datetime.now().strftime('%I:%M:%S:%p %d-%m-%Y')
            hasil_list_uncfg.append(wes)
    print('---------------------- hasil olah data')
    print(hasil_list_uncfg)

    return hasil_list_uncfg
# ============================================================================================== data


# =========================================================================================== starting

start = datetime.now()


cobaya = connect_ssh()
list_ipnya = ['172.23.225.111']
current_dir = os.getcwd()
# filename_hasilssh = r'hasiluncfgALU ' + datetime.today().strftime('%Y-%m-%d') + '.txt'
# myfile = os.path.join(current_dir, filename_hasilssh)
# f = open(myfile, "wb")

hasil_list_uncfg = []
filename_hasilssh = r'hasilsshtemp.txt'
rekaptotal = r'rekaptotaluncfg.txt'
myfile = os.path.join(current_dir, filename_hasilssh)
filetotal = os.path.join(current_dir, rekaptotal)

for wow in list_ipnya:
    output_str2 = mengtelnet(cobaya[1],wow)
    try:
        print(output_str2[0])    
        f = open(myfile, "r")
        baca = f.read()
        w = open(filetotal, "a")
        w.write(str(wow) + ' ' + str(output_str2[1]) + ' ' + str(datetime.now()) + '\n')
    except:
        pass
    
    try:
        uncfgsnnya = re.findall(r'1/1/.*',baca)
        print('done telnet')
        for we in uncfgsnnya:
            hem = re.search(r'1/1/\d+/\d+\s*([^\s]+)',we)			
            if 'ALCL' in hem[0] or 'HWTC' in hem[0] or 'ZTEG' in hem[0] or 'FHTT' in hem[0]:
                hostname = re.search(r'GPON.*>', baca)
                wes = wow, hostname[0].replace('>',''), re.sub(' +',' ',hem[0]), datetime.now().strftime('%I:%M:%S:%p %d-%m-%Y')
                hasil_list_uncfg.append(wes)
            
    except Exception as e:
        print(e)
        pass
    # f.close()

w.write('==============================================\n')
w.close()
cobaya[0].close()

# checking if the directory demo_folder2 
if not os.path.isdir("rekapanALU"):
    
    os.makedirs("rekapanALU")

    
filename_hasilssh = r'rekapanALU/ALU ' + datetime.today().strftime('%Y_%m_%d-%I_%M_%p') + '.txt'
myfile = os.path.join(current_dir, filename_hasilssh)
z = open(myfile, "w")
for we in hasil_list_uncfg:
    we = ' '.join(we)
    z.write(we + '\n')
z.close() 


current_dir = os.getcwd()
filename_ALU = r'hasiluncfgALU.txt'
folder_alu = os.path.join(current_dir, filename_ALU)
z = open(folder_alu, "w")
x = open(myfile, "r")
y = x.read()
z.write(y)
x.close()
z.close()


finish = datetime.now()
print(finish-start)
