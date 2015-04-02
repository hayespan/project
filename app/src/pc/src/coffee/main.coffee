jquery = require("jquery")
ko = require("knockout")
common = require("./common.coffee")
$locationWord = jquery(".location-word")
$chooseLocationBtn = jquery(".choose-location-btn")
$schoolsBox = jquery(".schools-box")
$buildingsBox = jquery(".buildings-box")
$hotProductsList = jquery(".hot-products-list")
$productCounts = jquery(".product-count")
$mask = jquery(".mask")

applied = false

vm =
    schools: ko.observableArray([])
    buildings: ko.observableArray([])
    location: ko.observable('')

window.onload = ->
    vm.location($locationWord.text())
    common.init()
    getProducts()
    initChooseLocationBtn()
    initLocation()
    unless common.csrf_token
        $chooseLocationBtn.click()

initChooseLocationBtn = ->
    if localStorage.csrf_token
        $mask.click (e)->
            d = e.target
            while  d != null and d.className != 'mask-box-container'
                d = d.parentNode
            unless d != null and d.className == 'mask-box-container'
                $schoolsBox.hide()
                $buildingsBox.hide()
                common.hideMask()

    $chooseLocationBtn.click ->
        common.showMask()
        $schoolsBox.show()

initLocation = ->
    common.getSchools (res) ->
        bindSchools res.data

bindSchools = (schools) ->
    for school in schools
        school.choose = ->
            common.getBuildings @id, (res) =>
                $schoolsBox.hide()
                bindBuildings @name, res.data
                $buildingsBox.show()
    vm.schools schools

bindBuildings = (school_name, buildings) ->
    strategy =
        "0": "定位成功"
        "1": "error: 无效的参数"
        "-1": "error: 建筑物不存在"
    for building in buildings
        building.choose = ->
            common.changeLocation @id, (res) =>
                common.initHeader()
                common.hideMask()
                $buildingsBox.hide()
                vm.location(school_name + @name)
                localStorage.csrf_token = res.data._csrf_token
                getProducts()
                common.notify(strategy[res.code])
    vm.buildings(buildings)

getProducts = ->
    jquery.ajax
        url: common.url + "/product/hot"
        type: 'POST'
        success: (res) ->
            if res.code is 0
                bindProducts res.data

bindProducts = (products) ->
    for product in products
        product.filename = "/static/img/" + product.filename
        product.setAmount = ->
            amount = parseInt(@amount())
            if amount and amount > 0
                @amount(amount)
            else
                @amount(1)
                common.notify("请输入正整数");

        product.formattedPrice = "￥ " + product.price
        product.amount = ko.observable 1
        product.amountIsNumber = ko.observable true
        product.isOverflow = ko.pureComputed ->
            return @amount() > @quantity
        , product
        product.add = -> @amount @amount() + 1
        product.reduce = ->
            if @amount() > 1
                @amount @amount() - 1
        product.addToCart = ->
            common.addToCart @id, @amount(), ->
                common.initHeader()
                return

    unless applied
        vm.products = ko.observableArray products
        ko.applyBindings vm
        applied = true
    else
        vm.products products
