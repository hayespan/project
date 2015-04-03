jquery = require("jquery")
ko = require("knockout")
common = require("./common.coffee")

vm =
    contactInfo:
        name: ko.observable("")
        phone: ko.observable("")
        addr: ko.observable("")
    is_all_checked: ko.observable(false)

$settleBtn = jquery(".settle-btn")
$contactInfoConfirm = jquery(".contact-info-confirm")
$contactInfoChange = jquery(".contact-info-change")
$confirmBtn = jquery(".confirm-btn")
$changeBtn = jquery(".change-btn")
$cancelBtn = jquery(".cancel-btn")
$saveBtn = jquery(".save-btn")
$mask = jquery('.mask')
originalContactInfo = {}

window.onload = ->
    common.init()
    getCartObjs()
    getContactInfo()
    initBtns()

getCartObjs = ->
    jquery.ajax
        url: common.url + "/cart/"
        type: "POST"
        data:
            csrf_token: localStorage.csrf_token
        success: (res)->
            if res.code is 0
                bindCartObjs res.data
            else
                common.tokenNotify()

getContactInfo = ->
    jquery.ajax
        url: common.url + "/user/contact_info"
        type: "POST"
        data:
            csrf_token: localStorage.csrf_token
        success: (res)->
            originalContactInfo = res.data
            bindContactInfo res.data if res.code is 0
            if res.code != 0
                common.tokenNotify()

initBtns = ->
    $mask.click (e)->
        d = e.target
        while  d != null and d.className != 'mask-box-container'
            d = d.parentNode
        unless d != null and d.className == 'mask-box-container'
            $cancelBtn.click()
            $contactInfoChange.hide()
            $contactInfoConfirm.hide()
            common.hideMask()

    $settleBtn.click ->
        if vm.checkedProductsLength() < 1
            common.notify '请选择商品'
        else
            common.showMask()
            $contactInfoConfirm.show()

    $cancelBtn.click ->
        vm.contactInfo.name(originalContactInfo.name)
        vm.contactInfo.phone(originalContactInfo.phone)
        vm.contactInfo.addr(originalContactInfo.addr)
        $contactInfoChange.hide()
        $contactInfoConfirm.show()

    $saveBtn.click ->
        originalContactInfo.name = vm.contactInfo.name()
        originalContactInfo.phone = vm.contactInfo.phone()
        originalContactInfo.addr = vm.contactInfo.addr()
        $contactInfoChange.hide()
        $contactInfoConfirm.show()

    $changeBtn.click ->
        $contactInfoConfirm.hide()
        $contactInfoChange.show()

    settleStrategy =
        "0": "成功下单"
        "1": "信息输入不正确，请重新输入"
        "-1": " 存在无效商品，请刷新页面后再试"
        "-2": " 存在无效商品，请刷新页面后再试"
        "2": "请重新选择位置后再试"
        "3": "请重新选择位置后再试"

    $confirmBtn.click ->
        if vm.checkedProductsLength() < 1
            common.notify '请选择商品'
        else
            jquery.ajax
                url: common.url + "/order/create"
                type: "POST"
                data:
                    csrf_token: localStorage.csrf_token
                    product_ids: getCheckedProductIds()
                    name: vm.contactInfo.name()
                    phone: vm.contactInfo.phone()
                    addr: vm.contactInfo.addr()
                success: (res) =>
                    console.log res
                    common.notify(settleStrategy[res.code])
                    $contactInfoConfirm.hide()
                    window.location.reload()


bindCartObjs = (objs)->
    for obj in objs
        # let necessary property of obj observable
        obj['is_checked'] = ko.observable(false)
        obj.quantity = ko.observable(obj.quantity)
        obj.filename = "/static/img/" + obj.filename
        injectProperties obj
    vm.cartObjs = ko.observableArray(objs)
    ko.applyBindings(vm)

injectProperties = (obj)->
    obj.setQuantity = ->
        strategy =
            "1": "无效的输入，请重新输入"
            "-3": "该商品不存在，请刷新页面后再试"
            "-2": " 该商品已失效，请刷新页面后再试"
            "2": "请重新选择位置后再试"
            "3": "请重新选择位置后再试"
        quantity = parseInt(@quantity())
        if quantity and quantity > 0
            @quantity(quantity)
        else
            @quantity(1)
            common.notify("请输入正整数");
            return
        jquery.ajax
            url: common.url + '/cart/set_quantity'
            type: "POST"
            data:
                csrf_token: localStorage.csrf_token
                product_id: @product_id
                quantity: @quantity()
            success: (res) ->
                common.notify(strategy[res.code])

    obj.validStatus = -> @is_valid ? '' : 'unvalid'
    obj.removeSelf = -> @deleteHandler('/cart/delete')
    obj.add = -> @quantityHandler('/cart/add')
    obj.reduce = -> @quantityHandler('/cart/sub')
    obj.quantityHandler = quantityHandler
    obj.deleteHandler = deleteHandler
    obj.totalPrice = ko.pureComputed ->
        @quantity() * @price
    , obj
    obj.formattedPrice = ko.pureComputed ->
        "￥" + @totalPrice()
    , obj

deleteHandler = (suffix) ->
    strategy =
        "2": "请重新选择位置后再试"
        "3": "请重新选择位置后再试"
    jquery.ajax
        url: common.url + suffix
        type: "POST"
        data:
            csrf_token: localStorage.csrf_token
            product_id: @product_id
        success: (res) =>
            if res.code is 0
                vm.cartObjs.remove @
                common.initHeader()
            else
                common.notify(strategy[res.code])


quantityHandler = (suffix)->
    strategy =
        "-3": "该商品不存在，请刷新页面后再试"
        "-2": " 该商品已失效，请刷新页面后再试"
        "2": "请重新选择位置后再试"
        "3": "请重新选择位置后再试"
    jquery.ajax
        url: common.url + suffix
        type: "POST"
        data:
            csrf_token: localStorage.csrf_token
            product_id: @product_id
        success: (res) =>
            if res.code is 0
                @quantity(res.data) if res.data > 0
            else
                common.notify(strategy[res.code])


bindContactInfo = (info)->
    props = ['name', 'phone', 'addr']
    for prop in props
        vm.contactInfo[prop](info[prop])

getCheckedProducts = ->
    vm.cartObjs().filter (cart_obj)->
        cart_obj if cart_obj.is_checked() and cart_obj.is_valid

getCheckedProductIds = ->
    productIdsArray = getCheckedProducts().map (valid_cart_obj) ->
        valid_cart_obj.product_id
    return productIdsArray.join(',')

vm.deleteCheckedProducts = ->
    checked_cart_obj.removeSelf() for checked_cart_obj in getCheckedProducts()

vm.checkAllProducts = ->
    vm.is_all_checked(!vm.is_all_checked())
    cart_obj.is_checked(vm.is_all_checked()) for cart_obj in vm.cartObjs()

vm.deleteInvalidProducts = ->
    cart_obj.removeSelf() for cart_obj in vm.cartObjs() when not cart_obj.is_valid

vm.checkedProductsLength = ko.pureComputed ->
    getCheckedProducts().length

vm.checkedProductsTotal = ko.pureComputed ->
    total = 0
    total += checkedProduct.totalPrice() for checkedProduct in getCheckedProducts()
    return "￥" + total

vm.cartObjsLength = ko.pureComputed ->
    vm.cartObjs().length
