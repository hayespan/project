// choose_school.js
$(function() {  

    $.getJSON("/location/school_list", function(data) {
        if (data['code'] == 0) {
            var school_list = data['data'];
            for (var i = 0 ; i < school_list.length ; i++) {
                var item = $("<li/>").attr({id: school_list[i]["id"], class: "school-list-item"});
                item.html(school_list[i]["name"]);
                item.appendTo(".school-list");
            }
            $(".school-list > .school-list-item").click(get_building);
        }
    });

    function get_building() {   
        $(".building-list > .school-list-item").html($(this).html());
        $.getJSON("/location/" + this.id + "/building_list", function(data) {
            if (data['code'] == 0) {
                $(".school-list-container").hide(); // 隐藏学校列表
                $("#school-banner").hide();
                $("#building-banner").show();
                $(".building-list-container").show(); // 显示楼栋列表
                var building_list = data['data'];
                for (var i = 0 ; i < building_list.length ; i++) {
                    var item = $("<li/>").attr({id: building_list[i]["id"], class: "building-list-item"});
                    item.html(building_list[i]["name"]);
                    item.appendTo(".building-list");
                }
                $(".building-list-item").click(set_building);
            }
        });
    }

    // 完成初始化
    function set_building() {
        $.post("/user/choose_location", {building_id: this.id}, function(data) {    
            if (data["code"] == 0) {    
                localStorage["csrf_token"] = data["data"]["csrf_token"];
                window.location.href="/m/"; 
            }
        }, "json");
    }

    // 返回按钮
    $(".back-btn").click(function() {   
        $(".school-list-container").show(); // 显示学校列表
        $("#school-banner").show();
        $(".building-list-item").remove();
        $("#building-banner").hide();
        $(".building-list-container").hide(); // 显示楼栋列表
    });

});
