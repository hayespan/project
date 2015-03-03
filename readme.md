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