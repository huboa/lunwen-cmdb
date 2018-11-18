print("加载stark文件")

from stark.service import v1
from rbac import models
from app01 import models as amodels
from django.shortcuts import HttpResponse,render,redirect
from django.conf.urls import url
from django.forms import ModelForm
from django.forms import fields
from django.utils.safestring import mark_safe
from django.urls import reverse
from rbac.service.init_permissions import reset_permission
from utils.server_hardware_info import connect_ssh_tb
from utils.zabbix_api import Zabbix
import requests
##注册说明
# 将models中的UserInfo类注册到【某个地方】
"""
_registry = {
    models.UserInfo: StarkConfig(models.UserInfo),
    models.Role: StarkConfig(models.Role),
}

/stark/app01/userinfo/，执行 StarkConfig(models.UserInfo).changelist_view()
/stark/app01/userinfo/add/，执行 StarkConfig(models.UserInfo).add_view()


/stark/app01/role/，执行 StarkConfig(models.Role).changelist_view()
/stark/app01/role/add/，执行 StarkConfig(models.Role).add_view()


for k,v in _registry.items():
    print(v.mcls)

"""

####劫持说明
"""
_registry = {
    models.UserInfo: UserInfoConfig(models.UserInfo),
    models.Role: StarkConfig(models.UserInfo),
    models.Group: StarkConfig(models.UserInfo),
}

/stark/app01/userinfo/，执行 UserInfoConfig(models.UserInfo).changelist_view()
/stark/app01/userinfo/add/，执行 UserInfoConfig(models.UserInfo).add_view()

/stark/app01/role/，执行 StarkConfig(models.Role).changelist_view()
/stark/app01/role/add/，执行 StarkConfig(models.Role).add_view()

"""


####用户表单form 表单
class UserInfoModelForm(ModelForm):
    xx = fields.CharField()
    class Meta:
        model = models.UserInfo
        fields = "__all__"

###主机表单表单form 表单
class HostModelForm(ModelForm):
        class Meta:
            model = amodels.Host
            fields = "__all__"
            # fields = ["idc", "remoteip", "host_ip"]
            required = True
            labels = {
                "sn": "主机SN号",
                "remoteip": "带外IP",
                'host_ip': '主机IP',
            }
            error_messages = {
                "idc": {
                    "required": "不能为空"
                },
                "sn": {
                    "required": "不能为空"
                },
                "remoteip": {
                    "required": "不能为空"
                }
            }

##用户类#角色类劫持角色配置类
class UserInfoConfig(v1.StarkConfig):   ####可以劫持父类 中的 任何数据 只要添加

    def logout_url(self,is_header=False,row=None):   ###添加显示字段
        if is_header:
            return '注销'
        return  mark_safe('<a href=/stark/rbac/userinfo/%s/logout/>注销</a> '%(row.id))

    def display_gender(self, is_header=False, row=None):
        if is_header:
            return '性别'
        # if row.gender == 1:
        #     return '男'
        # else:
        #     return '女'
        return row.get_gender_display()

    def display_status(self, is_header=False, row=None):
        if is_header:
            return '状态'
        return row.get_status_display()

    def display_dp(self, is_header=False, row=None):
        if is_header:
            return '部门'
        return row.id

####显示列表可以添加函数数据库字段和
    list_display = ['id', 'username',display_gender,display_status,display_dp,logout_url]
    search_list = ["username__contains",]
    comb_filter = ['gender','status','dp']
    model_form_cls = UserInfoModelForm  ####劫持form 表单
    # def changelist_view(self,request):
    #     print("劫持页面")
    #     return HttpResponse("特殊页面劫持")
    def extra_url(self):  #######钩子函数配了 会劫持 扩展url 用
        patterns=[
            url(r'^xx$', self.xx),
            url(r'^(\d+)/logout/$', self.logout),
        ]
        return patterns

    ####注销函数
    def logout(self,request,pk):
        user_obj = self.model_class.objects.filter(id=pk).first()
        if user_obj.session_key:
            reset_permission(user_obj,request)
        else:
            user_obj.session_key = None
            user_obj.status = 2
            user_obj.save()
        return redirect(self.get_list_url())

    def xx(self,request):
        return HttpResponse("xx劫持或添加")


### 物理机配置
class HostConfig(v1.StarkConfig):
    ####批量执行功能函数视图
    def pk_del(self, request, action):
        pk_list = request.POST.getlist("pk")
        print(pk_list, "批量删除")
        for n in pk_list:
            amodels.Host.objects.filter(id=n).delete()
            print(n, "批量删除")
    def pk_update(self, request, action):
        pk_list = request.POST.getlist("pk")
        print(pk_list, "批量更新")
        for nid in pk_list:
            self.updatefunc(request,nid)

    def update_url(self, is_header=False, row=None):  ###添加显示字段
        if is_header:
            return '更新host'
        return mark_safe('<a href=/stark/app01/host/%s/updateinfo/>更新SYS</a> ' % (row.id))

    def update_vhost_url(self, is_header=False, row=None):  ###添加显示字段
        if is_header:
            return '更新Vhost'
        return mark_safe('<a href=/stark/app01/host/%s/updatevhost/>更新Vhost</a> ' % (row.id))

    list_display = ['id', 'idc','sn','hostname','host_ip',"Hosys","Hcore",'manufacturer','product_name',"Hcpu","Hmemory","Hdisk",'remoteip',"HotherIp","Hother",update_vhost_url,update_url]
    search_list = ["sn__contains", 'remoteip__contains','hostname__contains','manufacturer__contains','product_name__contains',"host_ip__contains","Hosys__contains"]
    comb_filter = ['idc', ]
    ####批量执行清单
    # action_list = [{"name":"批量删除","func_name":"pk_del"},{"name":"批量更新","func_name":"pk_update"}]
    action_list = [ {"name": "批量更新", "func_name": "pk_update"}]
    model_form_cls = HostModelForm ####劫持form 表单


    def extra_url(self):  #######钩子函数配了 会劫持 扩展url
        patterns = [
            url(r'^(\d+)/updateinfo/$', self.updatefunc),
            url(r'^(\d+)/updatevhost/$', self.update_vhost),
        ]
        return patterns

    def updatefunc(self,request,nid):
        """
        更新宿主机硬件和 系统信息
        :param request:
        :param nid:
        :return:
        """
        try:
            host = amodels.Host.objects.get(id=nid)
            tb_obj = amodels.TBServer.objects.get(Tidc=host.idc_id)
            connect_obj = connect_ssh_tb(ip=tb_obj.Tip, username=tb_obj.Tuser, password=tb_obj.Tpassword)
        except:
            return redirect(self.get_list_url())
        sys_info_dict = connect_obj.get_sys_info(user='root',host=host.host_ip,)
        sys_os_info_dict = connect_obj.get_os_info(user='root',host=host.host_ip,)
        if sys_info_dict:
            host.manufacturer=sys_info_dict['Manufacturer']
            host.sn=sys_info_dict['Serial Number']
            host.product_name=sys_info_dict['Product Name']
            host.Hmemory=sys_info_dict["mem_info"]
            host.Hcpu = sys_info_dict["cpu_info"]
            host.save()
        if sys_os_info_dict:
            host.Hdisk = sys_os_info_dict["disk_info"]
            host.hostname = sys_os_info_dict["hostname"]
            host.Hosys = sys_os_info_dict["os_info"]
            host.Hcore = sys_os_info_dict["core_info"]
            host.save()
        return redirect(self.get_list_url())
    def update_vhost(self,request,nid):
        """
        从宿主机更新虚拟机硬件信息
        :param request:
        :param nid:
        :return:
        """
        try:
            host = amodels.Host.objects.get(id=nid)
            tb_obj = amodels.TBServer.objects.get(Tidc=host.idc_id)
            connect_obj = connect_ssh_tb(ip=tb_obj.Tip, username=tb_obj.Tuser, password=tb_obj.Tpassword)
            vhost_info = connect_obj.get_vhost_info('root', host.host_ip)
        except:
            return redirect(self.get_list_url())
        vhost_models_obj = amodels.Vhost.objects
        print(vhost_info)
        for n in  vhost_info:
            V = vhost_models_obj.filter(uuid=n)
            if  V:
                vhost = vhost_models_obj.get(uuid=n)
                vhost.VCPUs = vhost_info[n]['VCPUs-number']
                vhost.Vname = vhost_info[n]['name-label']
                vhost.Vmem = vhost_info[n]['memory-static-max']
                vhost.Vdisk = vhost_info[n]['DISK']
                vhost.Vmac = vhost_info[n]['MAC']
                vhost.Vstatus = vhost_info[n]['power-state']
                vhost.Vnetworks = vhost_info[n]['networks']
                vhost.Vos = vhost_info[n]['os-version']
                vhost.Host_id = nid

                vhost.save()
            else:
                vhost_models_obj.create(Vname=vhost_info[n]['name-label'],
                                        VCPUs=vhost_info[n]['VCPUs-number'],
                                        Vmem=vhost_info[n]['memory-static-max'],
                                        Vdisk=vhost_info[n]['DISK'],
                                        Vmac=vhost_info[n]['MAC'],
                                        Vstatus=vhost_info[n]['power-state'],
                                        Vnetworks=vhost_info[n]['networks'],
                                        Host_id=nid,
                                        uuid=n,
                                        Vos=vhost_info[n]['os-version'],
                                        )
        return redirect(self.get_list_url())



class VhostConfig(v1.StarkConfig):
    ####批量执行功能函数视图

    list_display = []
    search_list = ["uuid__contains","Vname__contains","Vstatus__contains","Vnetworks__contains","Vos__contains",]
###权限类
class PermissionsConfig(v1.StarkConfig):
    list_display = ['id','title','url','code','group','gmid']
    search_list = ["title__contains",'url__contains', 'code__contains',]

###监控zabbix
class ZabbixConfig(v1.StarkConfig):
    def display_status(self, is_header=False, row=None):
        if is_header:
            return '状态'
        return row.get_Zstatus_display()

    def conntest_url(self, is_header=False, row=None):  ###添加显示字段
        if is_header:
            return '测试连接'
        return mark_safe('<a href=/stark/app01/zabbix/%s/conntest/>测试连接</a> ' % (row.id))

    list_display = ['id', 'Zidc',"Zname",'Zip',"Zapi","Zadmin","ZabbixPassword",display_status,"Ztoken", conntest_url]

    def extra_url(self):  #######钩子函数配了 会劫持 扩展url
        patterns = [
            url(r'^(\d+)/conntest/$', self.conn_test),
        ]
        return patterns

    def conn_test(self, request, nid):

        Zabbix_obj = amodels.Zabbix.objects.get(id=nid)
        obj = Zabbix(url=Zabbix_obj.Zapi, user=Zabbix_obj.Zadmin, password=Zabbix_obj.ZabbixPassword)
        token= obj.get_token()
        if token:
            Zabbix_obj.Zstatus=2
            Zabbix_obj.Ztoken=token
        else:
            Zabbix_obj.Zstatus=1
        Zabbix_obj.save()
        return redirect(self.get_list_url())
class ZabbixTempConfig(v1.StarkConfig):
    action_list = [{"name": "同步zabbix_temp", "func_name": "rsyntemp"}]
    def rsyntemp(self,request,action):
        Zabbix_obj = amodels.Zabbix.objects.filter(Zstatus=2)
        for z in Zabbix_obj:
            zid=z.id
            Zabbix_obj = amodels.Zabbix.objects.get(id=zid)
            obj=Zabbix(url=Zabbix_obj.Zapi, user=Zabbix_obj.Zadmin, password=Zabbix_obj.ZabbixPassword)
            temp_dic=obj.get_template_list()
            for n in temp_dic["result"]:
                Temp_obj=amodels.ZabbixTemplate.objects
                T=Temp_obj.filter(Tzabbix_id=int(zid),Tid=int(n['templateid']))
                if not T:
                    Tobj=T.create(Tzabbix_id=int(zid),Tid=int(n['templateid']),Tname=n['name'])
                    Tobj.save()



#注册mode表 待生成url
v1.site.registry(models.UserInfo,UserInfoConfig)
v1.site.registry(models.Role)
# v1.site.registry(models.Ldap)

v1.site.registry(models.Permissions,PermissionsConfig)
v1.site.registry(models.PermissionGroup)
v1.site.registry(models.Menu)

v1.site.registry(amodels.IDC)
v1.site.registry(amodels.Cabinet)
v1.site.registry(amodels.Host,HostConfig)
# v1.site.registry(amodels.Vhost,VhostConfig)
#
# v1.site.registry(amodels.TBServer)
#
# v1.site.registry(amodels.Zabbix,ZabbixConfig)
# v1.site.registry(amodels.ZabbixTemplate,ZabbixTempConfig)



