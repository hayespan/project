$(function() { 
    // 需要初始化才能访问
    if (localStorage["_csrf_token"] == undefined) { 
        window.location.href = "/m/locations";
    }

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

});
