// 大的图片广告
// 根据图片创建id,按钮元素等，实际开发建议使用JSON数据类似

$(function() {  
    var htmlAdBtn = '';
    $("#AdSlide img").each(function(index, image) {
        var id = "adImage" + index;
        htmlAdBtn = htmlAdBtn + '<a href="javascript:" class="rb_ad_btn_a" data-rel="'+ id +'">'+ (index + 1) +'</a>';
        image.id = id;
    });
    $("#AdBtn").html(htmlAdBtn).find("a").powerSwitch({
        eventType: "hover",
        classAdd: "active",
        animation: "fade",
        autoTime: 5000,
        onSwitch: function(image) {
            if (!image.attr("src")) {
                image.attr("src", image.attr("data-src"));  
            }
        }
    }).eq(0).trigger("mouseover");


    $(".cat1").on("click", function() {   
        var item = $(this).closest(".list-item");
        var cat2 = item.children(".cat2");
        cat2.toggle();
        $(this).find(".arrow").toggleClass("arrow-bottom");
        $(this).find(".arrow").toggleClass("arrow-fold");
    });

    changeBadgeStatus();
    
    function changeBadgeStatus() {
        $.post("/cart/cnt",
            {csrf_token: localStorage["csrf_token"]},
            function(data) {    
                if (data.code == 0) {   
                    if (data.data > 0) {    // 为0则不显示气泡
                        $(".badge").html(data.data).show();
                    } else if (data.data == 0) {    
                        $(".badge").hide();
                    }
                }
            }, "json");
    }


});