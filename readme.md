目前后端分为7个模块，分别是管理员、位置、用户、分类、商品、购物车、订单。接下来会随着编码进行更新。
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
input:
csrf_token: str
username: str
password: str
name: str // real name (optional)
contact_info: str // phone num, etc (optional)
----
ouput:
```
{
     'code': x,
     'data': 'msg'
}
```
----
local errno:
0
1
-1 username exists.




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
#### file
```
id
filename
```

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

----
#### promotion
```
id
pic_id -> file.id
```

6. Cart Module
----
#### cart
```
user_id -> user.id
product_id -> product.id
building_id -> building.id
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

#### order_snapshot
```
order_id -> order.id
snapshot_id -> snapshot.id
quantity
```

----
Global errno:

1  Invalid arguments.
