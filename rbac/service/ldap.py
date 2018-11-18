"""
官方文档
http://ldap3.readthedocs.io/connection.html
"""

from ldap3 import Connection, Server, ANONYMOUS, SIMPLE, SYNC, ASYNC

ldapurl='ldap://10.10.30.206:389'
BaseDN='dc=mtime,dc=com' #ldap_authuser在连接到LDAP的时候不会用到baseDN，在验证其他用户的时候才需要使用
UserDN='shengchong.zhao@mtime.com'
all_DN='%s,%s'%(BaseDN,UserDN)
server = Server(ldapurl)
conn = Connection(server,all_DN,password='admin2018+',read_only=True)
print(conn,type(conn))
print(conn.authentication)
print(conn.bind())
# # -*- coding: UTF-8 -*-
# import sys
# sys.setdefaultencoding('utf-8')
#
# import ldap3,logging,time
# logfile = 'd:\\a.txt'
# # logging.basicConfig(filename=logfile,level=logging.INFO)
# # logging.basicConfig(format='%(time.asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# logging.basicConfig(level=logging.INFO,
#                     #format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', #返回值：Thu, 26 May 2016 15:09:31 t11.py[line:92] INFO
#                     format='%(asctime)s %(levelname)s %(message)s',
#                     #datefmt='%a, %d %b %Y %H:%M:%S',
#                     #datefmt='%Y/%m/%d %I:%M:%S %p', #返回2016/05/26 03:12:56 PM
#                     datefmt='%Y-%m-%d %H:%M:%S', #返回2016/05/26 03:12:56 PM
#                     filename=logfile#,
#                     #filemode='a' #默认为a
#                    )
# #logging输出结果：
#2016-05-26 15:22:29 INFO liu1 valid passed.
#2016-05-26 15:22:37 INFO liu1 valid passed.
#
#
# class ldapc:
#     def __init__(self,ldap_path,baseDN,domainname,ldap_authuser,ldap_authpass):
#         self.baseDN = baseDN
#         self.ldap_error = None
#         ldap_authduser = '%s\%s' %(domainname,ldap_authuser)
#         self.l=ldap3.BASE
#         self.l=ldap3.initialize(ldap_path)
#         self.l.protocol_version = ldap3.VERSION3
#         try:
#             self.l.simple_bind_s(ldap_authduser,ldap_authpass)
#         except(ldap3.LDAPError,err):
#             self.ldap_error = 'Connect to %s failed, Error:%s.' %(ldap_path,err.message['desc'])
#             print(self.ldap_error)
#         # finally:
#         #     self.l.unbind_s()
#         #     del self.l
#
#     def search_users(self,username): #模糊查找，返回一个list，使用search_s()
#         if self.ldap_error is None:
#             try:
#                 searchScope = ldap3.SCOPE_SUBTREE
#                 searchFiltername = "sAMAccountName" #通过samaccountname查找用户
#                 retrieveAttributes = None
#                 searchFilter = '(' + searchFiltername + "=" + username +'*)'
#                 ldap_result =self.l.search_s(self.baseDN, searchScope, searchFilter, retrieveAttributes)
#                 if len(ldap_result) == 0: #ldap_result is a list.
#                     return "%s doesn't exist." %username
#                 else:
#                     # result_type, result_data = self.l.result(ldap_result, 0)
#                     # return result_type, ldap_result
#                     return ldap_result
#             except(ldap3.LDAPError,err):
#                 return err
#
#     def search_user(self,username): #精确查找，返回值为list，使用search()
#         if self.ldap_error is None:
#             try:
#                 searchScope = ldap3.SCOPE_SUBTREE
#                 searchFiltername = "sAMAccountName" #通过samaccountname查找用户
#                 retrieveAttributes = None
#                 searchFilter = '(' + searchFiltername + "=" + username +')'
#                 ldap_result_id =self.l.search(self.baseDN, searchScope, searchFilter, retrieveAttributes)
#                 result_type, result_data = self.l.result(ldap_result_id, 0)
#                 if result_type == ldap3.RES_SEARCH_ENTRY:
#                     return result_data
#                 else:
#                     return "%s doesn't exist." %username
#             except (ldap3.LDAPError,err):
#                 return err
#
#     def search_userDN(self,username): #精确查找，最后返回该用户的DN值
#         if self.ldap_error is None:
#             try:
#                 searchScope = ldap3.SCOPE_SUBTREE
#                 searchFiltername = "sAMAccountName" #通过samaccountname查找用户
#                 retrieveAttributes = None
#                 searchFilter = '(' + searchFiltername + "=" + username +')'
#                 ldap_result_id =self.l.search(self.baseDN, searchScope, searchFilter, retrieveAttributes)
#                 result_type, result_data = self.l.result(ldap_result_id, 0)
#                 if result_type == ldap3.RES_SEARCH_ENTRY:
#                     return result_data[0][0] #list第一个值为用户的DN，第二个值是一个dict，包含了用户属性信息
#                 else:
#                     return "%s doesn't exist." %username
#             except(ldap3.LDAPError,err):
#                 return err
#
#     def valid_user(self,username,userpassword): #验证用户密码是否正确
#         if self.ldap_error is None:
#             target_user = self.search_userDN(username) #使用前面定义的search_userDN函数获取用户的DN
#             if target_user.find("doesn't exist") == -1:
#                 try:
#                     self.l.simple_bind_s(target_user,userpassword)
#                     logging.info('%s valid passed.\r'%(username)) #logging会自动在每行log后面添加"\000"换行，windows下未自动换行
#                     return True
#                 except(ldap3.LDAPError,err):
#                     return err
#             else:
#                 return target_user
#
#     def update_pass(self,username,oldpassword,newpassword): #####未测试#########
#         if self.ldap_error is None:
#             target_user = self.search_userDN(username)
#             if target_user.find("doesn't exist") == -1:
#                 try:
#                     self.l.simple_bind_s(target_user,oldpassword)
#                     self.l.passwd_s(target_user,oldpassword,newpassword)
#                     return 'Change password success.'
#                 # except (ldap3.e,):
#                 #     return err
#             else:
#                 return target_user


#
# ldap_authuser='liu1'
# ldap_authpass='pass'
# domainname='uu'
# ldappath='ldap://10.10.30.206:389'
#
# BaseDN='dc=mtime,dc=com' #ldap_authuser在连接到LDAP的时候不会用到baseDN，在验证其他用户的时候才需要使用
# UserDN='username@mtime.com'
# username = 'liu1' #要查找/验证的用户
# p=ldapc(ldappath,baseDN,domainname,ldap_authuser,ldap_authpass)
# print p.valid_user('Lily','lpass') #调用valid_user()方法验证用户是否为合法用户