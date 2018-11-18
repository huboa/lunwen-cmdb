import paramiko
import subprocess
import shlex
import re


class connect_ssh_tb(object):

    def __init__(self,ip='',port='22',username='',password=''):
        '''
        用于使用跳板机获取硬件信息
        :param ip:  跳扳机ip
        :param port:  跳板端口
        :param username: 跳板机用户
        :param password:密码
        '''
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    ###连接跳板机
    def ssh_connect(self,command_line):
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        ssh.connect(timeout=1,hostname=self.ip,port=self.port ,username=self.username, password=self.password)

        # # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command_line)
        result = stdout.readlines()

        # 关闭连接
        ssh.close()
        return  result

    ###获取执行命令
    def command_line(self,user,host,command):
        remote_command=('ssh %s@%s %s' % (user,host,command))
        result=self.ssh_connect(remote_command)
        return result
    ###执行dmidecode
    def get_sys_info(self,user,host):

        data_list = self.command_line(user=user, host=host, command="dmidecode")
        if data_list :
            sys_info_dict = self.get_sys_info_dict(data_list)
            sys_info_dict["mem_info"] = self.get_memory_info(data_list)
            sys_info_dict["cpu_info"] = self.get_cpu_info(data_list)
        else:
            return None
        print(sys_info_dict,)
        return  sys_info_dict
    #加工decode 获取系统信息
    def get_sys_info_dict(self,data_list):
        tag = False
        lines = []
        for line in data_list:
            if line.startswith('System Information'): # 如果遍历到System Information 写入新列表
                tag = True
                continue
            if tag:
                if not line.strip():  # 如果遍历到空行，即新的一段信息前，则可以退出循环了
                    break
                else:
                    lines.append(line)
        sys_info = self.get_dmi(lines)
        return sys_info
    def get_dmi(self,list_info):
        dmi_dic = {}
        dmi = {}
        dmi_dic = dict([i.strip().split(":") for i in list_info])
        for k, v in dmi_dic.items():
            dmi_dic[k] = v.strip()

        dmi['Manufacturer'] = dmi_dic['Manufacturer']
        dmi['Product Name'] = dmi_dic['Product Name']
        dmi['Serial Number'] = dmi_dic['Serial Number']
        return dmi

        ###提取内存信息
    def get_memory_info(self, data_list):
        tag = False
        lines = []
        for line in data_list:
            if line.startswith('Memory Device'):  # 如果遍历到System Information 写入新列表
                tag = True
                continue
            if tag:
                if not line.strip():  # 如果遍历到空行，即新的一段信息前，则可以退出循环了
                    tag = False
                    continue
                else:
                    if line.startswith('\tSize:'):  # 如果遍历到Size 写入新列表
                        lines.append(line)
        mem_info = self.phase_memory_info(lines)
        return mem_info
        ###将内存转换成字典并返回
    def phase_memory_info(self, list_info):
        dmi_dic = {}
        all_size=0
        info=''
        all_count=0
        for i in list_info:
           if i in dmi_dic:
                dmi_dic[i] +=1
           else:
                dmi_dic[i]=1
        for n in dmi_dic:
            # print(dmi_dic[n],dmi_dic)
            all_count += dmi_dic[n]
            if n == "\tSize: No Module Installed\n":
                continue
            info += str(int(re.sub("\D", '', n)) // 1024) + "G*" + str(dmi_dic[n]) +" "
            all_size += int(re.sub("\D",'',n))//1024*dmi_dic[n]
        mem_info=info +str(all_size) + "G/"+str(all_count)
        return mem_info
    def get_cpu_info(self,data_list):
        tag = False
        lines = []
        for line in data_list:
            if line.startswith('Processor Information'):  # 如果遍历到System Information 写入新列表
                tag = True
                continue
            if tag:
                if not line.strip():  # 如果遍历到空行，即新的一段信息前，则可以退出循环了
                    tag = False
                    continue
                else:
                    if line.startswith('\tVersion:'):  # 如果遍历写入新列表
                        lines.append(line)
                    if line.startswith('\tThread Count:'):  # 如果遍历写入新列表
                        lines.append(line)
        cpu_info = self.phase_cpu_info(lines)
        return cpu_info
    def phase_cpu_info(self,lines):
        dict={}
        info=''
        for n in lines:
            if n in dict:
                dict[n]+=1
            else:
                dict[n] = 1
        for key in dict:
            # print(key, dict[key])
            dmi_dic = (key.strip().split(": "))
            # print(dmi_dic)
            if dmi_dic[0]=="Version":
                version=str(dmi_dic[1]).replace(' ', '')
            else:
                thread=str(dmi_dic[1])
                info = version+"-"+str(dict[key]) + '*'+thread
        return info
 ####获取系统信息
    def get_os_info(self,user,host,):
        sys_os_dict = {}
        tag = self.command_line(user=user, host=host, command="hostname")
        if  tag:
            sys_os_dict["disk_info"] = str(self.command_line(user=user, host=host,command="fdisk -l |grep Disk |egrep '/dev/sd'|awk '{print $2$3$4}'")).strip().strip("'[]n\\")
            sys_os_dict["hostname"] = str(self.command_line(user=user, host=host, command="hostname")).strip().strip("'[]n\\")
            os_info_list = self.command_line(user=user, host=host,command="cat /etc/issue")
            # print(os_info_list)
            os_info=str(os_info_list[0])
            if os_info.startswith("Ubuntu"):
                sys_os_dict["os_info"] = str(self.command_line(user=user, host=host,command="cat /etc/issue|awk '{print$1\"-\"$2\"-\"$3}'|grep Ubuntu")).strip().strip("'[]n\\")
                sys_os_dict["core_info"] = str(self.command_line(user=user, host=host, command="uname -rm|awk -F '[- ]+' '{print$1\"-\"$2\"-\"$NF}'")).strip().strip("'[]n\\")
            elif os_info.startswith("Citrix"):
                sys_os_dict["os_info"] = str(self.command_line(user=user, host=host,command="cat /etc/redhat-release |awk -F '[ -]+' '{print$1\"-\"$3}'")).strip().strip("'[]n\\")
                sys_os_dict["core_info"] = str(self.command_line(user=user, host=host, command="uname -rm|awk -F '[ -]+' '{print$1\"-\"$NF}'")).strip().strip("'[]n\\")
            else:
                sys_os_dict["os_info"] = str(self.command_line(user=user, host=host,command="cat /etc/redhat-release |awk -F '[ -]+' '{print$1\"-\"$3}'")).strip().strip("'[]n\\")
                sys_os_dict["core_info"] = str(self.command_line(user=user, host=host,command="uname -rm|awk -F '[ -]+' '{print$1\"-\"$NF}'")).strip().strip("'[]n\\")
        return sys_os_dict

    def get_vhost_info(self,user,host,):
        list_info = self.command_line(user=user, host=host,
                                             command="xe vm-list  params=uuid,name-label,power-state,VCPUs-number,memory-static-max,os-version,networks | grep -v '^$'")
        # print(list_info)

        def vhost_dict(list_info,):
            vm_dic = {}

            def dict_format(line, lable,):
                data = line.split(":")[1]
                data = data.strip()
                vm_dic[uuid][lable] = data

            def get_mac(uuid):
                command = ("xe vm-vif-list uuid=%s  params=MAC|grep -v '^$'" % (uuid))
                mac_addr_info = self.command_line(user=user, host=host, command=command)
                for n in mac_addr_info:
                    mac = n.split(': ')[1]
                    mac = mac.strip()
                    if mac:
                        return mac

            def get_vhost_disk_list(uuid):
                command = ("xe vm-disk-list   uuid=%s |grep virtual-size|awk '{print$NF}'" % (uuid))
                vhost_disk_info = self.command_line(user=user, host=host, command=command)
                vhost_disk=''
                for n in vhost_disk_info:
                    n = str(int(int(n)/1024/1024/1024))
                    vhost_disk=vhost_disk + n + "G,"
                if vhost_disk:
                    return vhost_disk
            for line in list_info:
                line = line.strip()
                if line.startswith('uuid'):  # 如果遍历到System Information 写入新列表
                    uuid = line.split(":")[1]
                    uuid = uuid.strip()
                    vm_dic[uuid] = {}
                    continue
                elif line.startswith('name-label'):
                    dict_format(line, lable="name-label")
                    continue
                elif line.startswith('power-state'):
                    dict_format(line, lable='power-state')
                    continue
                elif line.startswith('VCPUs-number'):
                    dict_format(line, lable="VCPUs-number")
                    continue
                elif line.startswith('memory-static-max'):
                    dict_format(line, lable="memory-static-max")
                    mm = vm_dic[uuid]['memory-static-max']
                    vm_dic[uuid]['memory-static-max'] = str(int(int(mm)/1024/1024/1024))+'G'
                    continue
                elif line.startswith("networks"):
                    string_ip=line
                    result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", string_ip)
                    result_list=[]
                    for ip in result:
                        if ip :
                            result_list.append(ip)
                        else:
                            vm_dic[uuid]["networks"] = "no"
                    vm_dic[uuid]["networks"] = str(result_list)
                    continue
                elif line.startswith("os-version"):
                    group = re.search(r'name:(.*?)\(Core\);.+?uname:(.*?);', line, re.M)
                    if group:
                        group.group(1)
                        group.group(2)
                        vm_dic[uuid]["os-version"] =  group.group(1) +  group.group(2)
                    else:
                        vm_dic[uuid]["os-version"] = 'no'
                    continue
            for n in vm_dic:
                vm_dic[n]["MAC"] = get_mac(n)
                vm_dic[n]["DISK"] = get_vhost_disk_list(n)
            return vm_dic
        return vhost_dict(list_info,)




##调试信息
# ####使用说明创建跳扳机连接实例
# # ssh.connect(hostname='10.199.104.63', port=22, username='admin', password='1r ')
# connect_obj = connect_ssh_tb(ip='192.168.50.18',username='root',password='')
# #
# # ####获取信息
# print(connect_obj.get_vhost_info(user='root',host='192.168.51.31'))

# sys_info_dict = connect_obj.get_sys_info(user='root',host='192.168.50.229',)
# print(connect_obj.get_os_info(user='root',host='192.168.50.228'))
# print(sys_info_dict['Manufacturer'])
# print(sys_info_dict['Product Name'])
# print(sys_info_dict['Serial Number'])
