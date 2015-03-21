function logout() {
    var data = "_csrf_token=" + window.localStorage.getItem("token");
    document.getElementById("logout").onclick = function() {
        $.ajax({
            type: "POST",
            url: "/admin/logout",
            data: token,
            success: function(msg){
                code = msg.code;
                if (code == 0) {
                } else {
                    errorCode(code);
                }
            }
        });
    };
}
