目前后端分为8个主要模块，分别是管理员、位置、用户、分类、商品、购物车、订单、文件。接下来会随着编码进行更新。
每个模块文档格式如下：

1. 模块名
2. 数据库设计（前端人员不用看，这个是后端看的）
3. api详情列表（ajax的api均为form表单提交，json返回；常规api后期再补上）
4. 错误码（包含局部错误码（<0）与全局错误码（>0），局部错误码须写明错误状态描述，全局错误码不用写明，具体参考附录的全局错误码表；0表示成功状态，一般不会返回提示信息，但某些api可能会返回具体数据；）
5. 具体api文档在__非管理页__、__管理页__ issue中。

环境安装：

python2.7, pip

pip install -r requirements.txt

然后新建project/instance/文件夹，创建两个文件`__init__.py`, `config.py`

`config.py`内容如下：

```
# -*- coding: utf-8 -*-
# config for db/key, etc -- private & personal
DEBUG = True
SECRET_KEY = 'your own scret key'
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@ip/dbname'
```

