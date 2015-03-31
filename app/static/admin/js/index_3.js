window.onload = initPage();

// initialize the page
function initPage() {

	// bootstrap plugins initilization
    pluginsOn();
    refreshPerMin();
    bindingFuncWithQuery();
    //showTable(); //testing
    logout();  //enable the logout ajax
}

//binding the onclick function with the tabs
function bindingFuncWithQuery() {
	var query_orders = document.getElementById("query_orders");
	var query_items = document.getElementById("query_items");

	query_orders.onclick = function() {
		
		var url = "/admin/level3/query";   //set the url to get all orders
		var data = "csrf_token=" + window.localStorage.getItem("token") + "&get_order_list=1";

		$.ajax({
   			type: "POST",
   			url: url,
   			data: data,
   			success: function(msg){
      			code = msg.code;
      			if (code == 0) {
      				clearTablesContent();
      				insertIntoOrderTable(msg.data.orders)
    			} else {
    				errorCode(code);
    			}
   			}
		});
	}

	query_items.onclick = function() {
		var url = "/admin/level3/query";   //set the url to get all inventory
		var data = "csrf_token=" + window.localStorage.getItem("token") + "&get_inventory_list=1";

		$.ajax({
   			type: "POST",
   			url: url,
   			data: data,
   			success: function(msg){
      			code = msg.code;
      			if (code == 0) {
      				clearTablesContent();
      				insertIntoItemTable(msg.data.inventory);
    			} else {
    				errorCode(code);
    			}
   			}
		});
	}
}

function logout() {
	document.getElementById("logout").onclick = function() {
		var url = "/admin/logout";
		var data = "csrf_token="+window.localStorage.getItem("token");

  		$.ajax({
   			type: "POST",
   			url: url,
   			data: data,
   			success: function(msg){
      			code = msg.code;
      			if (code == 0) {
      			window.location.href="/admin/login"; 
    			} else {
    				errorCode(code);
    			}
   			}
		});

	}
}

function pluginsOn() {
	// bootstrap tab plugins
	$("#myTab a").click(function (e) {
        e.preventDefault();
        $(this).tab("show");
    });

    //boostrap modal plugins
    $("#deleteOrderBtn").modal({
    	show: false
    });

    $("#finishOrderBtn").modal({
    	show: false
    });
}

//refresh the page per minute
function refreshPerMin() {
	refresh();
	setTimeout(refreshPerMin, 60*1000);
}

//refresh the page
function refresh() {
	//create a request
	var url = "/admin/level3/query";   //set the url to get all orders 
	var data = "csrf_token=" + window.localStorage.getItem("token") + "&get_order_list=1&get_inventory_list=1";
	
  	$.ajax({
   			type: "POST",
   			url: url,
   			data: data,
   			success: function(msg){
      			code = msg.code;

      			if (code == 0) {
      				showTable(msg.data);
    			} else {
    				errorCode(code);
            	}
   			}
		});
}

function errorCode(code) {
	if (code == 1) {
		alert("输入内容非法");
	} else if (code == 2) {
		alert("用户已离线，请重新登陆");
        window.location.href = "/admin/login"
	} else if (code == -2) {
		alert("请登陆");
        window.location.href = "/admin/login"
	} else if (code == -10) {
		alert("非三级管理员（楼管）");
	} else if (code == -6) {
		alert("管理员还没有被分配管理楼栋");
	} else if (code == -11) {
		alert("订单不存在");
	} else if (code == -12) {
		alert("订单已经完成或取消，不能重复操作");
	} else if (code == -27) {
		alert("交易密码错误，请重新输入（4位数字）");
	}
}

function showTable(data) {
    // code == 0
    clearTablesContent(); //clear the former body content in tables
    InsertTablesContent(data);  //insert the new body contents in tables
}

function clearTablesContent() {
	var tables = document.getElementsByTagName("tbody");

	for (var i = 0; i < tables.length; i++) {
		while (tables[i].firstChild) {
			tables[i].removeChild(tables[i].firstChild);
		}
	}
}

//insert the table content into the suitable table container
// text type: json
function InsertTablesContent(data) {
	//json mode
	var orders = data.orders;
	var items = data.inventory;

	insertIntoOrderTable(orders);
	insertIntoItemTable(items);
	
}

//create td array
function createKeyArray(array) {
	var keyArray = []; // create an empty Array for keys

	for (var i = 0; i < array.length; i++) {
		keyArray[array[i]] = i;
	}

	return keyArray;
}

// insert into the orders table
function insertIntoOrderTable(orders) {
	var tableContainer = document.getElementById("orders_table_body");

	for (var k = 0; k < orders.length; k++) {
		var tr = document.createElement("tr");
		var orderKeys = createKeyArray(["number", "details", "receiver_info", "status", "timedelta"]);  //create keyss except the one for buttons
		var tdsArray = [];

		tableContainer.appendChild(tr);

		//create a tds Array
		for (var i = 0; i < 5; i++) {  				// bad-code !!!!
			var td = document.createElement("td");
			tdsArray.push(td);
		}

		for (var property in orders[k]) {
			/*   abandon
			*if (property == "number" || property == "details" || property == "receiver_info" || property == "status" || property == "timedelta") {
			*	var td = document.createElement("td");
			*	tr.appendChild(td);
			*}
			*/

			if (property == "number") {
				var textNode = document.createTextNode(orders[k]["number"]);
				tdsArray[orderKeys["number"]].appendChild(textNode);       //orderKeys get the index through the key
			} else if (property == "details") {
                for (var i = 0; i < orders[k][property].length; i++) { 
                    var ul = document.createElement("ul");
					tdsArray[orderKeys["details"]].appendChild(ul);
					for (var s_porperty in orders[k][property][i]) {
						var li = document.createElement("li");
						var text = "";
						ul.appendChild(li);

						if (s_porperty == "name") {
							text = "名称："+orders[k][property][i][s_porperty];
						} else if (s_porperty == "price") {
							text = "价格："+orders[k][property][i][s_porperty];
						} else if (s_porperty == "quantity") {
							text = "数量："+orders[k][property][i][s_porperty];
						}

						var textNode = document.createTextNode(text);
						li.appendChild(textNode);
					}

                    var br = null;
                    if (i != orders[k][property].length-1) {
                        br = document.createElement("br");
                    }
                    if (br != null) {
                        ul.appendChild(br);
                    }
				}	
			} else if (property == "receiver_info") {
				var ul = document.createElement("ul");
				tdsArray[orderKeys["receiver_info"]].appendChild(ul);

				for (var s_porperty in orders[k][property]) {
					var li = document.createElement("li");
					var text = "";
					ul.appendChild(li);

					if (s_porperty == "name") {
						text = "姓名："+orders[k][property][s_porperty];
					} else if (s_porperty == "location") {
						text = "住址："+orders[k][property][s_porperty];
					} else if (s_porperty == "phone") {
						text = "电话："+orders[k][property][s_porperty];
					}

					var textNode = document.createTextNode(text);
					li.appendChild(textNode);
				}	
			} else if (property == "status") {
				var text = "";
                var className1 = "";
                var spanNode1 = document.createElement("span");
				var spanNode2 = null;

                if (orders[k][property] == "completed") {
					text = "已完成";
                    className1 = "finished";
				} else if (orders[k][property] == "uncompleted") {
					text = "未完成";
                    className1 = "still";
				} else if (orders[k][property] == "cancelled") {
					text = "已取消";
                    className1 = "cancelled";
				}
                
                spanNode1.appendChild(document.createTextNode(text));
                spanNode1.className = className1;

				if (orders[k]["timeout"]) {
                    spanNode2 = document.createElement("span");
					text = "超时";
                    var className2 = "overtime";
                    spanNode2.appendChild(document.createTextNode(text));
                    spanNode2.className = className2;
				}

                if (spanNode2 != null) {
                    var node = tdsArray[orderKeys["status"]];
                    node.appendChild(spanNode1);
                    node.appendChild(document.createTextNode('('));
                    node.appendChild(spanNode2);
                    node.appendChild(document.createTextNode(')'));
                } else {
				    tdsArray[orderKeys["status"]].appendChild(spanNode1);
                }
            }
             else if (property == "timedelta") {
				var text = "";
				var currentTime = new Date();
				var deadline = new Date((orders[k]["released_time"]+orders[k]["timedelta"])*1000);
                var restTime = new Date(deadline-currentTime);

				text = deadline-currentTime>0 ? [restTime.getUTCHours(), restTime.getUTCMinutes(), restTime.getUTCSeconds()].join(":") :0;
				
				var textNode = document.createTextNode(text);
				tdsArray[orderKeys["timedelta"]].appendChild(textNode);
			}
		}

		//add all tds in tdsArray into the table
		for (var i = 0; i < tdsArray.length; i++) {
			tr.appendChild(tdsArray[i]);
		}
       
        var td = document.createElement("td");
		tr.appendChild(td);
        if (orders[k]["status"] != "cancelled" && orders[k]["status"] != "completed") {
		//add operation button into the chart:   
		    var completeOrderBtn = createBtn("completeOrderBtn");
		    var deleteOrderBtn = createBtn("deleteOrderBtn");

		    td.appendChild(completeOrderBtn);
		    td.appendChild(deleteOrderBtn);
        }
    }
}

//insert into the item table(intervory)
function insertIntoItemTable(items) {
	var tableContainer = document.getElementById("stocks_table_body");

	for (var k = 0; k < items.length; k++) {
		var tr = document.createElement("tr");
		var text;
		var itemKeys = createKeyArray(["name", "description", "quantity"]);  //create the keys array for items
		var tdsArray = [];  //create a tds array for items

		tableContainer.appendChild(tr);

		for (var i = 0 ; i < 3; i++) {      // bad-code
			var td = document.createElement("td");
			tdsArray.push(td);
		}

		for (var property in items[k]) {
			var text = document.createTextNode(items[k][property]);

			if (itemKeys[property] != undefined)   //if itemKeys[property] != undefined
				tdsArray[itemKeys[property]].appendChild(text);
		}

		// insert all the tds in the tdsArray into the tr
		for (var i = 0; i < tdsArray.length; i++)
			tr.appendChild(tdsArray[i])
	}
}


function createBtn(className) {
	var btn = document.createElement("button");
	var text;

	btn.setAttribute("type","button");
	btn.setAttribute("class","btn-xs operationBtn");


	if (className.indexOf("completeOrderBtn") != -1) {
		text = document.createTextNode("完成订单");
	} else {
		text = document.createTextNode("取消订单");
	}

	btn.className += " "+className;
	btn.appendChild(text);

	btn.onclick = operationBtnFunc;
	return btn;
}

function operationBtnFunc() {
	var password = prompt("请输入密码：", "");

	//post password to back-end
	if (password != null && password != "") {
		if (this.className.indexOf("completeOrderBtn") != -1)
			validation(password, this.parentNode.parentNode.firstChild.firstChild.nodeValue, 1);
		if (this.className.indexOf("deleteOrderBtn") != -1)
			validation(password, this.parentNode.parentNode.firstChild.firstChild.nodeValue, 0);
	}
}


function validation(password, order_id, operation) {
	var sendData = "csrf_token="+window.localStorage.getItem("token")+"&ticketid="+order_id;
  	//set the url
  	var url = "/admin/level3/handle_order";  //set the url to change the order status

  	//send different data with different operations
  	if (operation == 1) 
  		sendData += "&handle="+"1"+"&password="+password;
  	if (operation == 0)
  		sendData += "&handle="+"-1"+"&password="+password;

	$.ajax({
   		type: "POST",
   		url: url,
   		data: sendData,
   		success: function(msg){
      		code = msg.code;

      		if (code == 0) {
      			refresh();
    		} else {
    			errorCode(code);
    		}
   		}
	});
}

// for json
function isArray(arg) {
  if (typeof arg == 'object') {
    var criteria = arg.constructor.toString().match(/array/i);
    return (criteria != null);
  }
  return false;
}

