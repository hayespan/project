function login() {
    var username = $("#username").val();
    var password = $("#password").val();
    var data = "username=" + username + "&" + "password="+password;
    url = "/admin/login";

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function(msg){
        code = msg.code;
            if (code == 0) {
                window.localStorage.setItem("token", msg.data._csrf_token);
                window.location.href="/admin/index"; 
            } else if (code == 1) {
                alert("数据不符合格式");
            } else if (code == -7) {
                alert("账号不存在");
            } else if (code == -8) {
                alert("密码错误");
            } else if (code == -10) {
                alert("手机端禁止登陆");
            }
        }
    });
}

window.onload = enableEnter();

function enableEnter() {
    var loginForm = $("form")[0];
    $(loginForm).on("keyup keypress", function(e) {
        var code = e.keyCode || e.which; 
        if (code  == 13) {               
                login();
        }
    });
}
