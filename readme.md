目前后端分为8个模块，分别是管理员、位置、用户、分类、商品、购物车、订单、文件。接下来会随着编码进行更新。
每个模块文档格式如下：

1. 模块名
2. 数据库设计（前端人员不用看，这个是后端看的）
3. api详情列表（ajax的api均为form表单提交，json返回；常规api后期再补上）
4. 错误码（包含局部错误码（<0）与全局错误码（>0），局部错误码须写明错误状态描述，全局错误码不用写明，具体参考附录的全局错误码表；0表示成功状态，一般不会返回提示信息，但某些api可能会返回具体数据；）

最后附录有__全局错误码表__。


1. Admin module
----
#### admin
```
id
username
password_hash
is_root
name
contact_info
```
#####1.1 CreateAdmin (权限要求：root_required)

`POST /admin/create`

----
```
input:
csrf_token: str
username: str
password: str
name: str // real name (optional)
contact_info: str // phone num, etc (optional)
```
----
ouput:
```
{
     'code': x,
     'data': 'msg'
}
```
----
```
local errno:
0
1
-1 username exists.
```



2. Location Module
----
#### school
```
id
name
admin_id -> admin.id
```

#### building
```
id
name
school_id -> school.id
admin_id -> admin.id
```

3. User Module
----
#### user
```
id
(use `session` to store default location information)

```
##### 3.1 create_user
`POST /user/choose_location`

----
```
input:
building_id
```
----
```
ouput:
{
'code': 0,
'data': {'_csrf_token': 'xxx'} // 写localstorage，伴随着用户终身
}
```
----
```
0
1
-1 Building does not exist.
```
----
##### 3.2 get_user_location_Info
`GET /user/location_info`

----
```
ouput:
{
'code': 0,
'data': {
'school': {'id': x, 'name': 'xxx'}, 
'building': {'id': x, 'name': 'xxx'}}
}
```
----
```
0
-1 Location info does not exist.
```
----
##### 3.3 get_contactInfo
`GET /user/contact_info`

----
```
ouput:
{
'code': 0,
'data': {'name': 'xxx', 'phone':'xxx', 'addr': 'xxx'}
}
```
----
```
0
-1 Contact info does not exist.
```


4. Category Module
----
#### cat1
```
id 
name
```

#### cat2
```
id
name
cat1_id -> cat1.id
```

5. Product Module
----

#### product
```
id
name
cat2_id -> cat2.id
pic_id -> file.id
description
price
```

#### product_building
```
product_id -> product.id
building_id -> building.id
quantity
timedelta // a default value for each order
```
#### snapshot
```
id
product_id -> product.id
name
pic_id
cat1_rd
cat2_rd
description
price
released_time
```


6. Cart Module
----
#### cart
```
user_id -> user.id
product_id -> product.id
building_id -> building.id
last_viewed_time
is_valid
quantity
```

7. Order Module
----
#### order
```
id
ticketid
user_id -> user.id
building_id -> building,id
room
receiver
phone
status
released_time
timedelta
password
school_name_rd // 'rd' means 'redundancy'
building_name_rd
```


#### order_snapshot
```
order_id -> order.id
snapshot_id -> snapshot.id
quantity
```

8. File Module
----
#### file
```
id
filename
```
----
#### promotion
```
id
pic_id -> file.id
```

----
Global errno:

1  Invalid arguments.
