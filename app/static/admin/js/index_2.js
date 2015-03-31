window.onload = initPage();

// initialize the page
function initPage() {
    pluginsOn();
    logout();

    document.getElementById("build1").onclick = list_buildings;
    document.getElementById("build2").onclick = list_buildings;
    document.getElementById("build3").onclick = list_buildings;
    document.getElementById("li_all").onclick = showTotal;
}

// bootstrap tab plugins
function pluginsOn() {
    $("#myTab a").click(function (e) {
        e.preventDefault();
        $(this).tab("show");
    });

    $(function () { $("#myModal").modal({
        keyboard: true
    })});
}

function logout() {
    var data = "csrf_token=" + window.localStorage.getItem("token");
    document.getElementById("logout").onclick = function() {
        $.ajax({
            type: "POST",
            url: "/admin/logout",
            data: data,
            success: function(msg){
                code = msg.code;
                if (code == 0) {
                    window.location.href = "/admin/login";
                    window.localStorage.removeItem("token");
                } else {
                    errorCode(code);
                }
            }
        });
    };
}


function isArray(arg) {
    if (typeof arg == "object") {
        var criteria = arg.constructor.toString.match(/array/i);
        return criteria != null;
    }
    return false;
}

function clearTables(text) {
    var tables = document.getElementById(text);
    while (tables.firstChild) {
        tables.removeChild(tables.firstChild);
    }
}

/**
 * Four get info functions with ajax post
 */
function showOrders(id) {
    var buildId = id;
    if (buildId == '楼栋') return;
    var url = "/admin/level2/query";
    var data = "csrf_token=" + window.localStorage.getItem("token") + "&" + "get_order_list=" + buildId;

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg){
            code = msg.code;
            if (code == 0) {
                clearTables("orders_table_body");
                InsertOrdersContent(msg);
            } else {
                errorCode(code);
            }
        }
    });
    
}

function showReplenishment(id) {
    var buildId = id;
    if (buildId == '楼栋') return;
    var url = "/admin/level2/query";
    var data = "csrf_token=" + window.localStorage.getItem("token") + "&" + "get_inventory_list=" + buildId;

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg){
            code = msg.code;
            if (code == 0) {
                clearTables("replenishment_table_body");
                InsertRepleContent(msg, buildId);
            } else {
                errorCode(code);
            }
        }
    });
}

function showTotal() {
    var url = "/admin/level2/query";
    var data = "csrf_token=" + window.localStorage.getItem("token") + "&" + "get_total_sales=-1";

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg){
            code = msg.code;
            if (code == 0) {
                clearTables("total_table_body");
                InsertTotalContent(msg);
            } else {
                errorCode(code);
            }
        }
    });

}

function showEvery(id) {
    var buildId = id;
    var url = "/admin/level2/query";
    var data = "csrf_token=" + window.localStorage.getItem("token") + "&" + "get_total_sales=" + buildId;

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg) {
            code = msg.code;
            if (code == 0) {
                clearTables("every_table_body");
                InsertEveryContent(msg);
            } else {
                errorCode(code);
            }
        }
    });
}

/**
 * Four insert functions.
 */
function InsertOrdersContent(json) {
    var ordersDetails = json.data.orders;
    var tableContainer = document.getElementById("orders_table_body");


    var orders = json.data.orders;
    var tableContainer = document.getElementById("orders_table_body");
    for (var i = 0; i < orders.length; ++i) {
        var tr = document.createElement("tr");
        tableContainer.appendChild(tr);
        for (var property = 0; property < 4; ++property) {
            var td = document.createElement("td");
            var text;
            switch (property) {
                case 0:
                    var unixTimestamp = new Date(orders[i]["released_time"] * 1000);
                    text = document.createTextNode(unixTimestamp.toLocaleString());
                    break;
                case 1:
                    var list = document.createElement("ul");
                    list.setAttribute("style", "list-style: none; padding: 0;");
                    for (var info in orders[i]["receiver_info"]) {
                        var li = document.createElement("li");
                        var pre;
                        if (info == "name") pre = "姓名：";
                        else if (info == "location") pre = "地址：";
                        else if (info == "phone") pre = "电话：";
                        li.appendChild(document.createTextNode(pre + orders[i]["receiver_info"][info]));
                        list.appendChild(li);
                    }
                    text = list;
                    break;
                case 2:
                    text = document.createTextNode(orders[i]["money"] + "元");
                    break;
                case 3:
                    if (orders[i]["status"] == "uncompleted") text = document.createTextNode("未完成");
                    else if (orders[i]["status"] == "completed") text = document.createTextNode("已完成");
                    else if (orders[i]["status"] == "cancelled") text = document.createTextNode("已取消");
                    break;
            }
            td.appendChild(text);
            tr.appendChild(td);
        }
    }

}

function InsertRepleContent(json, buildId) {

    
    var reples = json.data.inventory;
    var tableContainer = document.getElementById("replenishment_table_body");
    
    for (var i = 0; i < reples.length; ++i) {
        var tr = document.createElement("tr");
        tableContainer.appendChild(tr);
        var td;

        for (var property = 0; property < 5; ++property) {
            var text;
            switch(property) {
                case 0:
                    text = document.createTextNode(reples[i]["id"]);
                    break;
                case 1:
                    text = document.createTextNode(reples[i]["name"]);
                    break;
                case 2:
                    text = document.createTextNode(reples[i]["description"]);
                    break;
                case 3:
                    text = document.createTextNode(reples[i]["price"] + "元");
                    break;
                case 4:
                    text = document.createTextNode(reples[i]["quantity"] + "份");
                    break;
            }
            td = document.createElement("td");
            td.appendChild(text);
            if (property == 0) {
                td.className += 'productId';
            }
            if (property == 2) {
                td.className += 'description';
            }
            if (property == 4) {
                td.className += 'productQuantity';
            }
            tr.appendChild(td);
        }
        td = document.createElement("td");
        td.appendChild(createInput("replenishInput"));
        tr.appendChild(td);
        td = document.createElement("td");
        td.appendChild(createBtn("replenishBtn"), buildId);
        tr.appendChild(td);
    }

}

function InsertTotalContent(json) {
    
    var sales = json.data.total_sales;
    var tableContainer = document.getElementById("total_table_body");
    var tr = document.createElement("tr");
    tableContainer.appendChild(tr);

    for (var property = 0; property < 2; ++property) {
        var td = document.createElement("td");
        var text;
        switch(property) {
            case 0:
                text = document.createTextNode(sales["amount"] + "份");
                break;
            case 1:
                text = document.createTextNode(sales["money"] + "元");
                break;
        }
        td.appendChild(text);
        tr.appendChild(td);
    }
}

function InsertEveryContent(json) {
    
    var sales = json.data.total_sales;
    var tableContainer = document.getElementById("every_table_body");
    var tr = document.createElement("tr");
    tableContainer.appendChild(tr);

    for (var property = 0; property < 2; ++property) {
        var td = document.createElement("td");
        var text;
        switch(property) {
            case 0:
                text = document.createTextNode(sales["amount"] + "份");
                break;
            case 1:
                text = document.createTextNode(sales["money"] + "元");
                break;
        }
        td.appendChild(text);
        tr.appendChild(td);
    }
}

// create a dynamic button
function createBtn(className, buildId) {
    var btn = document.createElement("button");
    var text;

    btn.setAttribute("type","submit");
    btn.setAttribute("class","btn");

    text = document.createTextNode("补货");
    btn.appendChild(text);

    btn.onclick = operationBtnFunc;

    return btn;
}

// create a dynamic input form
function createInput(className) {
    var input = document.createElement("input");

    input.setAttribute("type", "text");
    input.setAttribute("class", "form-control");
    input.setAttribute("name", "amount");
    input.setAttribute("placeholder", "请输入数量");

    return input;
}

// judge pure numbers with reg expression
function isDigital(str) {
    if (str.match(/^-?\d+$/) != null) return true;
    return false;
}

// modify quantity
function operationBtnFunc() {
    var amount = this.parentNode.parentNode.getElementsByTagName("input")[0].value;

    if (amount == "" || !isDigital(amount)) {
        alert("请输入数字");
        this.parentNode.parentNode.getElementsByTagName("input")[0].value = "";
    } else {
        var url = "/admin/level2/modify_quantity";
        var building_id = document.getElementById('build2').parentNode.id;
        var product_id = this.parentNode.parentNode.getElementsByClassName("productId")[0].firstChild.nodeValue;
        var data = "csrf_token=" + window.localStorage.getItem("token") + "&" + "building_id=" + building_id + "&" + "product_id=" + product_id + "&" + "quantity=" + parseInt(amount);
        var that = this;
        $.ajax({
            type: "POST",
            url: url,
            data: data,
            success: function(msg) {
                code = msg.code;
                if (code == 0) {
                    that.parentNode.parentNode.getElementsByClassName("productQuantity")[0].firstChild.nodeValue = msg.data + "份";
                } else {
                    errorCode(code);
                }
            }
        });
    }
}

// after choose a building, the button"s text will change. (More friendly)
function buildingChoose() {
    var text = this.innerHTML;
    var buildId = this.id;
    if (this.className.indexOf("tab1") >= 0) {
        document.getElementById("build1").innerHTML = this.innerHTML;
        document.getElementById("build1").parentNode.id = this.id;
        showOrders(buildId);
    } else if (this.className.indexOf("tab2") >= 0) {
        document.getElementById("build2").innerHTML = this.innerHTML;
        document.getElementById("build2").parentNode.id = this.id;
        showReplenishment(buildId);
    } else if (this.className.indexOf("tab3") >= 0) {
        document.getElementById("build3").innerHTML = this.innerHTML;
        document.getElementById("build3").parentNode.id = this.id;
        showEvery(buildId);
    }
}

// get all buildings info with ajax post
function list_buildings() {
    var url = "/admin/level2/query";
    var data = "csrf_token=" + window.localStorage.getItem("token") + "&" + "get_building_list=1";

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg) {
            code = msg.code;
            if (code == 0) {
                clearModals();
                InsertModals(msg);
            } else {
                errorCode(code);
            }
        }
    });

}

// clear all buildings info (buildings info may change)
function clearModals() {
    var btns = $(".modal-body button");
    for (var i = 0; i < btns.length; ++i) {
        btns[i].remove();
    }
}

// insert all buildings in modals
function InsertModals(json) {
    var allBuildings = json.data.buildings;

    var modals = $(".modal-body");
    for (var i = 0; i < modals.length; ++i) {
        for (var build in allBuildings) {
            var buildInfo = allBuildings[build];
            var name = "";
            var bid = "";
            for (var property in buildInfo) {
                if (property == "id") {
                    bid += buildInfo[property];
                } else if (property == "name") {
                    name += buildInfo[property];
                }
            }
            var btn = document.createElement("button");
            modals[i].appendChild(btn);

            btn.setAttribute("type", "button");
            var className = "btn btn-link modalBtn chooseBuild tab" + (i+1);
            // for link style btn
            btn.setAttribute("class", className);
            btn.setAttribute("data-dismiss", "modal");
            btn.id = bid;

            btn.appendChild(document.createTextNode(name));
            btn.onclick = buildingChoose;
        }
    }
}


// judge error code
function errorCode(code) {
    switch(code) {
        case 1:
            alert("输入内容非法");
            break;
        case 2:
            alert("用户已离线，请重新登陆");
            window.location.href = "/admin/login"
            break;
        case -2:
            alert("请登陆");
            window.location.href = "/admin/login"
            break;
        case -9:
            alert("管理员暂且未被分配管理学校");
            break;
        case -10:
            alert("非法操作");
            break;
        case -13:
            alert("商品在当前楼栋没有出售");
    }
}
