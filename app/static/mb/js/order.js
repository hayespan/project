$(function() { 
    // 需要初始化才能访问
    if (localStorage["_csrf_token"] == undefined) { 
        window.location.href = "/m/locations";
    }

    changeBadgeStatus();

    $("#all-order-btn").click(function() {
        $(".list-top-item").removeClass("list-top-item-active");
        $(this).addClass("list-top-item-active");
        $(".coming-order").show();
        $(".finish-order").show();
    });

    $("#coming-order-btn").click(function() {
        $(".list-top-item").removeClass("list-top-item-active");
        $(this).addClass("list-top-item-active");
        $(".coming-order").show();
        $(".finish-order").hide();
    });

    $("#finish-order-btn").click(function() {
        $(".list-top-item").removeClass("list-top-item-active");
        $(this).addClass("list-top-item-active");
        $(".coming-order").hide();
        $(".finish-order").show();
    });

    function changeBadgeStatus() {
        $.post("/cart/cnt",
            {csrf_token: localStorage["_csrf_token"]},
            function(data) {    
                if (data.code == 0) {   
                    if (data.data > 0) {    // 为0则不显示气泡
                        $(".badge").html(data.data).show();
                    }
                }
            }, "json");
    }

});
