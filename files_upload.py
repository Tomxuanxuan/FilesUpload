#!/usr/bin/env python
# encoding: utf-8
"""
@author: tx
@File    : files_upload.py
@desc    : 文件上传
"""
import os
import uuid
from ftplib import FTP
from ftplib import error_perm
import socket

from datetime import datetime
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client



class FilesUpload:
    def __init__(self, upload_key, bufsize=1024):
        self.bufsize = bufsize
        self.upload_key = upload_key    # tengxun 腾讯云   ftp ftp上传

    def files_upload(self, files):
        _uploads = []
        if self.upload_key == "tengxun":
            _uploads = self.tengxun_cos_upload(files)
        elif self.upload_key == "ftp":
            _uploads = self.ftp_file_upload(files)
        return _uploads

    # 腾讯上传
    def cos_config(self):
        """公共配置 相关参数需要进行配置，或从数据库进行获取"""
        token = None
        config = CosConfig(
            Region='cos_region',
            Secret_id='cos_secret_id',
            Secret_key='cos_secret_key',
            Timeout=1200,  # 20分钟
            Token=token
        )  # 获取配置对象
        return config

    def tengxun_cos_upload(self, files):
        _uploads = []
        config = self.cos_config()
        client = CosS3Client(config)
        if isinstance(files, list):
            for file in files:
                _upload = self.rebuild_file(client, file)
                # print(response)
                # {'ETag': '"9987668b99a448119e71234b9a40dbe7"', 'Connection': 'keep-alive', 'Server': 'tencent-cos', 'Date': 'Tue, 24 Mar 2020 13:04:20 GMT', 'x-cos-request-id': 'NWU3YTA1NTRfMzA5ZDA4MDlfNDk0N18zMmJmNDRm', 'Content-Length': '0'}
                _uploads.append(_upload)
        else:
            _uploads.append(self.rebuild_file(client, files))
        return _uploads  # 返回列表

    def rebuild_file(self, client, file):
        _upload = {}  # 在里面定义，每次都可以刷新，不然返回的结果都一样
        # file字典格式content_length=0,content_type='image/jpeg',filename='***.jpg',mimetype='image/jpeg',name='file',stream
        today = datetime.strftime(datetime.now(), '%Y%m%d')
        uuid_str = uuid.uuid4().hex
        upload_name = file.filename
        file_suffix = os.path.splitext(upload_name)[1]
        file_type = file.mimetype
        save_name = uuid_str + file_suffix
        file_path = 'app/%s/%s/%s' % (today, save_name)  # app/appId/年-月-日/filename
        blob = file.read()
        file_size = len(blob)  
        _upload['uploadName'] = upload_name
        _upload['saveName'] = save_name
        _upload['fileSuffix'] = file_suffix
        _upload['fileType'] = file_type
        _upload['filePath'] = file_path
        _upload['fileUrl'] = 'http://xxx.com' + file_path
        _upload['fileSize'] = file_size
        response = client.put_object(
            Bucket='cos_bucket',
            Body=blob,  # 上传的文件对象
            Key=file_path,  # 带路径的文件名，无须/开头
            CacheControl='no-cache'
        )
        return _upload

    # ftp 上传
    def ftpconnect(self, host, port, username, password):
        ftp = FTP()
        # ftp.set_debuglevel(2)         #打开调试级别2，显示详细信息
        ftp.encoding = 'utf-8'  # 解决中文编码问题，默认是latin-1
        try:
            ftp.connect(host, port)  # 连接
            ftp.login(username, password)  # 登录，如果匿名登录则用空串代替即可
            print(ftp.getwelcome())  # 打印欢迎信息
        except (socket.error, socket.gaierror):  # ftp 连接错误
            print("ERROR: 连接服务器出错 [{0}:{1}]".format(host, port))
            return None
        except error_perm:  # 用户登录认证错误
            print("ERROR: 身份认证错误 ")
            return None
        return ftp

    def ftp_file_upload(self, files):
        _uploads = []
        host = 'upload_api'
        port = 21
        username = 'ftp_username'
        password = 'ftp_password'

        ftp = self.ftpconnect(host, port, username, password)

        # 创建files_test目录
        file_list = ftp.nlst()
        if 'files_test' not in file_list:
            res = ftp.mkd(self.app_id)

        # 进入目录
        ftp.cwd('files_test')

        # 上传文件
        if isinstance(files, list):

            for file in files:
                _uploads.append(self.ftpstorbinary(ftp, file))
        else:
            _uploads.append(self.ftpstorbinary(ftp, files))

        return _uploads

    def ftpstorbinary(self, ftp, file):
        _upload = {}
        # 重命名
        uuid_str = uuid.uuid4().hex
        upload_name = file.filename
        file_suffix = os.path.splitext(upload_name)[1]
        save_name = uuid_str + file_suffix
        file_type = file.mimetype
        file_path = '{0}/{1}'.format(self.app_id, save_name)
        file_url = '{0}/{1}'.format(self.upload_api, file_path)
        file_size = 0

        res = ftp.storbinary('STOR ' + save_name, file, self.bufsize)  # 上传文件
        # 226 Transfer complete.
        if res.find('226') != -1:
            print('ftp 文件上传完成', upload_name)
        ftp.set_debuglevel(0)

        _upload['uploadName'] = upload_name
        _upload['saveName'] = save_name
        _upload['fileSuffix'] = file_suffix
        _upload['fileType'] = file_type
        _upload['filePath'] = file_path
        _upload['fileUrl'] = file_url
        _upload['fileSize'] = file_size

        return _upload





