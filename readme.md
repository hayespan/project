Admin module
----
#### admin
id
username
password_hash
is_root
name
contact_info


Location Module
----
#### school
id
name
admin_id -> admin.id

#### building
id
name
school_id -> school.id
admin_id -> admin.id

User Module
----
#### user
id
(use `session` to store default location information)

Category Module
----
#### cat1
id 
name

----
#### cat2
id
name
cat1_id -> cat1.id

Product Module
----
#### file
id
filename

----
#### product
id
name
cat2_id -> cat2.id
pic_id -> file.id
description
price

----
#### product_building
product_id -> product.id
building_id -> building.id
quantity
eta(a default value for each order)

----
#### promotion
id
pic_id -> file.id


Cart Module
----
#### cart
user_id -> user.id
product_id -> product.id
building_id -> building.id
is_valid
quantity

Order Module
----
#### order
id
ticketid
user_id -> user.id
building_id -> building,id
room
receiver
phone
status
released_time
eta
password

---
#### order_product
order_id -> order.id
product_id -> product.id
quantity
