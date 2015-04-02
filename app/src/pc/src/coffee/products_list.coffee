jquery = require("jquery")
ko = require("knockout")
common = require("./common.coffee")

$cat1 = jquery(".kind")
$cat2 = jquery(".cat2")
$locationWord = jquery(".location-word")
$chooseLocationBtn = jquery(".choose-location-btn")
$schoolsBox = jquery(".schools-box")
$buildingsBox = jquery(".buildings-box")

applied = false

vm =
    schools: ko.observableArray([])
    buildings: ko.observableArray([])
    location: ko.observable('')
    currentCat1Id: ko.observable(0)

window.onload = ->
    common.init()
    cat1_id = getUrlParameter 'cat1'
    cat2_id = getUrlParameter 'cat2'
    getProducts getData(cat1_id, cat2_id)
    initCat1Btn()
    initCat2Btn()
    vm.location($locationWord.text())
    initChooseLocationBtn()
    initLocations()
    vm.location($locationWord.text())
    unless localStorage.csrf_token
        $chooseLocationBtn.click()

initChooseLocationBtn = ->
    $chooseLocationBtn.click ->
        common.showMask()
        $schoolsBox.show()

initLocations = ->
    common.getSchools (res) ->
        bindSchools res.data

bindSchools = (schools) ->
    for school in schools
        school.choose = ->
            common.getBuildings @id, (res) =>
                $schoolsBox.hide()
                bindBuildings @name, res.data
                # vm.buildings(res.data)
                $buildingsBox.show()
    vm.schools schools

bindBuildings = (school_name, buildings) ->
    for building in buildings
        building.choose = ->
            common.changeLocation @id, (res) =>
                common.initHeader()
                common.hideMask()
                $buildingsBox.hide()
                vm.location school_name + @name
                localStorage.csrf_token = res.data._csrf_token
    vm.buildings buildings

getData = (cat1_id, cat2_id) ->
    if cat1_id
        if cat2_id
            data =
                cat1_id: cat1_id
                cat2_id: cat2_id
        else
            data =
                cat1_id: cat1_id
    else if cat2_id
        data =
            cat2_id: cat2_id
    else
        data = {}

getProducts = (data) ->
    jquery.ajax
        url: common.url + "/product/list"
        type: 'POST'
        data: data
        success: (res) ->
            if res.code is 0
                bindProducts res.data.products
                if res.data['current_cat1']
                    vm.currentCat1Id res.data['current_cat1'].id
                else
                    vm.currentCat1Id -1

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

getUrlParameter = (sParam) ->
    sPageURL = window.location.search.substring 1
    sURLVariables = sPageURL.split '&'
    for sURLVariable in sURLVariables
        sParameterName = sURLVariable.split '='
        if sParameterName[0] == sParam
            return sParameterName[1]

initCat1Btn = ->
    $cat1.click (e) ->
        cat1 = e.target
        data =
            cat1_id: cat1.dataset.cat1
        getProducts data

initCat2Btn = ->
    $cat2.click (e) ->
        cat2 = e.target
        data =
            cat2_id: cat2.dataset.cat2
        getProducts data
