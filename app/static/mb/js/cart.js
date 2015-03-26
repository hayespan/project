
$(function() {  
    // 需要初始化才能访问
    if (localStorage["_csrf_token"] == undefined) { 
        window.location.href = "/m/locations";
    }

    // 字符串格式化函数
    var stringFormat = function() {
        if (arguments.length == 1)
            return null;
        var str = arguments[0];
        for ( var i = 1; i < arguments.length; i++) {
            var re = new RegExp('\\{' + (i - 1) + '\\}', 'gm');
            str = str.replace(re, arguments[i]);
        }
        return str;
    };

    $.post("/cart/list/", 
            {csrf_token: localStorage["_csrf_token"]},
            function(data) {
                if (data.code == 0) {
                    for (var i = 0 ; i < data.data.length ; i++) {
                        var html_content = "";
                        if (data.data[i].is_valid == true) {
                            html_content = 
                                "<div id={0} class=\"item-valid\">" +
                                    "<div class=\"radio not-checked\"></div>" +
                                    "<img src=\"/static/img/{1}\" class=\"item-pic\" alt=\"picture\">" +
                                    "<div class=\"item-detail\">" +
                                        "<p>{2}</p>" +
                                        "<p class=\"item-price\">￥{3}</p>" +
                                        "<div class=\"item-count\">" +
                                            "<span class=\"float-left\">数量：</span>" +
                                            "<div class=\"btn-decrease\">-</div>" +
                                            "<input default=\"{4}\" value=\"{4}\" type=\"text\" maxlength=\"4\" pattern=\"[0-9]\" class=\"input-number\"/>" +
                                            "<div class=\"btn-increase\">+</div>" +
                                        "</div>" +
                                    "</div>" +
                                "</div>";
                        } else {    
                            html_content = 
                                "<div id={0} class=\"item-invalid\">" +
                                    "<div class=\"text-invalid\">失效</div>" +
                                    "<img src=\"/static/img/{1}\" class=\"item-pic\" alt=\"picture\">" +
                                    "<div class=\"item-detail\">" +
                                        "<p>{2}</p>" +
                                        "<p class=\"item-price\">￥{3}</p>"+
                                        "<p>数量：{4}</p>" +
                                    "</div>" +
                                "</div>";
                        }
                        var html_format_str = stringFormat(
                                                    html_content,
                                                    data.data[i].product_id, 
                                                    data.data[i].filename, 
                                                    data.data[i].name, 
                                                    data.data[i].price.toFixed(2), 
                                                    data.data[i].quantity);
                        $(".item-container").append(html_format_str);
                    }
                    bindEvent(); // 给商品条目绑定事件
                } else if (data.code == 2) {    
                    window.location.href = "/m/locations";
                }
            },
        "json");


    function bindEvent() {  
        // 商品单选按钮点击
        $(".item-container > * > .radio").on("click", function() {  
            $(this).toggleClass("not-checked").toggleClass("checked");
            calculateTotalPrice(); // 重新计算价格
            changeBtnStatus();
        });

        // 点击全选按钮
        $(".check-all > .radio").on("click", function() {
            $(this).toggleClass("not-checked").toggleClass("checked");

            if ($(this).hasClass("not-checked")) {
                $(".item-container > * > .radio").removeClass("checked");
                $(".item-container > * > .radio").addClass("not-checked");
            } else {    
                $(".item-container > * > .radio").removeClass("not-checked");
                $(".item-container > * > .radio").addClass("checked");
            }
            calculateTotalPrice(); // 重新计算价格
            changeBtnStatus();
        });

        $(".btn-decrease").on("click", function() {   
            var item = $(this).closest(".item-valid");
            if (parseInt(item.find(".input-number").val()) > 1) {   
                var product_id = item.attr("id");
                $.post("/cart/sub", 
                        {csrf_token: localStorage["_csrf_token"], product_id: product_id},
                        function(data) {
                            if (data.code == 0) {   
                                item.find(".input-number").val(data.data);
                                calculateTotalPrice();  // 重新计算价格
                                changeBtnStatus();
                            } else if (data.code == 2) {    
                                window.location.href = "/m/locations";
                            }
                        }, "json");
            }
        });

        $(".btn-increase").on("click", function() {   
            var item = $(this).closest(".item-valid");
            if (parseInt(item.find(".input-number").val()) < 9999) {   
                var product_id = item.attr("id");
                $.post("/cart/add", 
                        {csrf_token: localStorage["_csrf_token"], product_id: product_id},
                        function(data) {
                            if (data.code == 0) {   
                                item.find(".input-number").val(data.data);
                                calculateTotalPrice();  // 重新计算价格
                                changeBtnStatus();
                            } else if (data.code == 2) {    
                                window.location.href = "/m/locations";
                            }
                        }, "json");
            }
        });

        $(".input-number").change(function() {
            if ($(this).val() == "" || $(this).val() == "0" || isNaN($(this).val())) {
                $(this).val($(this).attr("default")); // 输入非法时恢复默认数字
            }
            var item = $(this).closest(".item-valid");
            var product_id = item.attr("id");
            $.post("/cart/set_quantity", 
                        {csrf_token: localStorage["_csrf_token"], product_id: product_id, quantity: $(this).val()},
                        function(data) {
                            if (data.code == 0) {   
                                item.find(".input-number").val(data.data);
                                calculateTotalPrice();  // 重新计算价格
                                changeBtnStatus();
                            } else if (data.code == 2) {    
                                window.location.href = "/m/locations";
                            }
                        }, "json");
        });
    }

    function changeBtnStatus() {    
        $(".input-number").each(function() {
            if ($(this).val() <= 1) {   
                $(this).prev().addClass("btn-disabled");
                $(this).next().removeClass("btn-disabled");
            } else if ($(this).val() >= 9999) { 
                $(this).prev().removeClass("btn-disabled");
                $(this).next().addClass("btn-disabled");
            } else {    
                $(this).prev().removeClass("btn-disabled");
                $(this).next().removeClass("btn-disabled");
            }
        });
        if (parseFloat($(".total-price > * > .text-red").html().substring(1)) > 0) { 
            $(".pay-btn").addClass("pay-btn-active");
        } else {    
            $(".pay-btn").removeClass("pay-btn-active");
        }
    }

    // 计算总价格
    function calculateTotalPrice() {    
        var total_price = 0.00;
        var goods_count = 0;
        $(".item-valid").each(function() {
            if ($(this).find(".radio").hasClass("checked")) {
                var each_price = parseFloat($(this).find(".item-price").html().substring(1));
                var input = $(this).find(".input-number");
                var count = parseInt(input.val());
                goods_count += count;
                total_price += each_price * count;
            }
        });
        $(".total-price").find(".text-red").html("￥"+total_price.toFixed(2));
        $(".total-price").find(".goods-count").html(goods_count);
    }

    // 清除选中项目
    $("#delete-items").on("click", function() {   
        $(".item-valid").each(function() {
            if ($(this).children().hasClass("checked")) {    
                var product_id = $(this).attr("id");
                var obj = $(this);
                $.post("/cart/delete", 
                        {csrf_token: localStorage["_csrf_token"], product_id: product_id},
                        function(data) {
                            if (data.code == 0) {   
                                obj.remove();
                                calculateTotalPrice();  // 重新计算价格
                                changeBtnStatus();
                            } else if (data.code == 2) {    
                                window.location.href = "/m/locations";
                            }
                        }, "json");
            }
        });
    });

    $("#clear-invalid").on("click", function() {   
        $(".item-invalid").each(function() {
            var product_id = $(this).attr("id");
            var obj = $(this);
            $.post("/cart/delete", 
                    {csrf_token: localStorage["_csrf_token"], product_id: product_id},
                    function(data) {
                        if (data.code == 0) {   
                            obj.remove();
                        } else if (data.code == 2) {    
                            window.location.href = "/m/locations";
                        }
                    }, "json");
        });
    });

    $(".pay-btn").on("click", function() {    
        if ($(this).hasClass("pay-btn-active")) {   
            $(".modal-set-info").show();
        }
    });

    $("#order-cancel").on("click", function() {   
        $(".modal").hide();
    });

    $("#order-save").on("click", function() { 
        $(".modal-confirm").show();
        $(".modal-set-info").hide();
        $("#c-name").val($("#name").val());
        $("#c-phone").val($("#phone").val());
        $("#c-addr").val($("#addr").val());
    });

    $("#order-modify").on("click", function() {   
        $(".modal-set-info").show();
        $(".modal-confirm").hide();
    });

    $("#order-submit").on("click", function() { 
        var product_ids = "";
        $(".item-valid").each(function() {
            if ($(this).find(".radio").hasClass("checked")) {
                var product_id = $(this).attr("id");
                product_ids += product_id + ",";
            }
        });
        $.post("/order/create",
                {csrf_token: localStorage["_csrf_token"], product_ids: product_ids, name: $("#name").val(), phone: $("#phone").val(), addr: $("#addr").val()},
                function(data) {
                    if (data.code == 0) {   
                        window.location.href = "/m/order";
                    } else if (data.code < 0) { 
                        location.reload();
                    } else if (data.code == 2) {    
                        window.location.href = "/m/locations";
                    }
                }, "json");
    });

});
