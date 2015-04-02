jquery = require("jquery")

# $state = jquery(".state")
$cartQuantity = jquery(".state .amount")
$mask = jquery(".mask")
$notification = jquery(".notification")

insertStrategy =
    "0": "添加成功"
    "1": "error: 无效的参数"
    "2": "error: invalid token"
    "3": "亲，请先选择学校楼栋喔"
    "-1": "亲，请先清除购物车中的冲突商品喔"
    "-2": "Oops!商品不存在"

common =
    url: "#{location.protocol}//#{location.host}"
    csrf_token: null
    init: ->
        if localStorage.csrf_token
            @csrf_token = localStorage.csrf_token
            common.initHeader()
        # initFooter()

    showMask: ->
        $mask.fadeIn()

    hideMask: ->
        $mask.fadeOut()

    notify: (msg)->
        $notification.show()
        $notification.text(msg)
        setTimeout (->
            $notification.fadeOut()
        ), 1000

    getSchools: (callback) ->
        jquery.ajax
            url: common.url + "/location/school_list"
            type: 'GET'
            success: (res) ->
                if res.code is 0
                    callback?(res)

    getBuildings: (school_id, callback) ->
        jquery.ajax
            url: common.url + "/location/#{school_id}/building_list"
            type: 'GET'
            success: (res) ->
                if res.code is 0
                    callback?(res)

    changeLocation: (building_id, callback)->
        jquery.ajax
            url: common.url + "/user/choose_location"
            type: 'POST'
            data:
                building_id: building_id
            success: (res)->
                if res.code is 0
                    callback?(res)

    addToCart: (id, amount, callback)->
        jquery.ajax
            url: common.url + "/cart/insert"
            type: "POST"
            data:
                csrf_token: localStorage.csrf_token
                product_id: id
                quantity: amount
            success: (res)->
                common.notify(insertStrategy[res.code])
                if res.code is 0
                    callback?(res)

    initHeader: ->
        jquery.ajax
            url: common.url + "/cart/cnt"
            type: "POST"
            data:
                csrf_token: localStorage.csrf_token
            success: (res)->
                if res.code is 0
                    $cartQuantity.text(res.data)

module.exports = common
