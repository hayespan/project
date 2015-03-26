$(function( ){  
    // 需要初始化才能访问
    if (localStorage["_csrf_token"] == undefined) { 
        window.location.href = "/m/locations";
    }

    $(".btn-decrease").on('click', function() { 
        var $input = $(this).closest(".item-count").find(".input-number");
        var num = parseInt($input.val());
        if (isNaN(num)) {   
            num = 1;
        }
        if (num > 1) {  
            $input.val(num - 1);
        }
    });

    $(".btn-increase").on('click', function() { 
        var $input = $(this).closest(".item-count").find(".input-number");
        var num = parseInt($input.val());
        if (isNaN(num)) {   
            num = 1;
        }
        if (num < 9999) {  
            $input.val(num + 1);
        }
    });

    $(".input-number").on('change', function() { 
        if ($(this).val() == "" || $(this).val() == "0" || isNaN($(this).val())) {
            $(this).val(1); // 输入非法时恢复默认数字
        }
    });

    $(".btn-put-in").on('click', function() {
        var product_id = this.id;
        var $input = $(this).closest(".product-item").find(".input-number");
        $.post("/cart/insert", 
            {csrf_token: localStorage["_csrf_token"], product_id: product_id, quantity: $input.val()},
                function(data) {
                    if (data.code == 0) {   
                    } else if (data.code == 2 || data.code == 3) {    
                        window.location.href = "/m/locations";
                    }
            }, "json");
    });

});