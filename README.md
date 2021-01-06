# FilesUpload
文件上传腾讯云或FTP 服务器

## 上传腾讯云
腾讯对象存储COS配置：
详见：https://cloud.tencent.com/document/product/436/7751
> cos_app_id
> cos_secret_id
> cos_secret_key
> cos_region
> cos_scheme
> cos_bucket

调用：
```
files = request.files.getlist('files')
   
uploader = FilesUpload('tengxun')
uploadeds = uploader.files_upload(files)
```

## 上传ftp
配置：
> upload_api  : ftp服务器地址
> ftp_username
> ftp_password


调用：
```
files = request.files.getlist('files')
   
uploader = FilesUpload('ftp')
uploadeds = uploader.files_upload(files)
```
