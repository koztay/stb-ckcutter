

function setPrice() {
        var price = $(".variation_select option:selected").attr("data-price");

        var sale_price = $(".variation_select option:selected").attr("data-sale-price");
        if (sale_price != "" && sale_price != "None" && sale_price != null) {
            $("#price").html(sale_price + " ,-₺ " + "<del class='og-price'>" + price + " ,-₺ " + "</del>");
        } else {
            $("#price").html(price+ " ,-₺ ");
        }
    }

setPrice();

$(".variation_select").change(function () {
    console.log("set_Price çalıştı.")
    setPrice();

    // var img = $(".variation_select option:selected").attr("data-img")
    // $("img").attr("src", img);

});


// quick view modal
$('#quick-view-modal').on('show.bs.modal', function (event) {

    var button = $(event.relatedTarget); // Button that triggered the modal
    var title = button.data('title'); // Extract info from data-* attributes
    var description = button.data('description');
    var price = button.data('price');
    var saleprice = button.data('saleprice');
    var url = button.data('url');
    var imagehd = button.data('imagehd');
    var imagesd = button.data('imagesd');
    var imagemedium = button.data('imagemedium');
    var imagemicro = button.data('imagemicro');
    var category = button.data('category');
    var category_url = button.data('category_url');
    var variation_set = button.data('variation_set');

    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or
    // other methods instead.

    var modal = $(this);
    modal.find('.modal-product-title').text(title);
    modal.find(".modal-product-description").text(description);
    modal.find('.view-product-details').attr("href", url);
    modal.find('.simpleLens-big-image').attr("src", imagemedium);
    modal.find('.simpleLens-lens-image').attr('data-lens-image', imagehd);
    //modal.find('.simpleLens-thumbnail-wrapper').attr('data-lens-image', imagemedium);
    //modal.find('.simpleLens-thumbnail-wrapper').attr('data-big-image', imagemedium);
    //modal.find('.simpleLens-thumbnail-wrapper').attr('src', imagemedium);
    modal.find('.category-url').attr("href", category_url);
    modal.find(".category-url").text(category);

    var $el = modal.find('.variation_select');
    $el.empty(); // remove old options
    $.each(variation_set, function(key,value) {
    //          console.log(value.fields.pk)
    $el.append($("<option></option>")
        .attr("value", value.pk).text(value.fields.title)
        .attr("data-price", value.fields.price)
        .attr("data-sale-price", value.fields.sale_price || "None"));

    });

    if (saleprice > 0){

        var element = modal.find('.aa-product-view-price');
        element.text('');
        var spansale = document.createElement("span");
        var nodesale = document.createTextNode(saleprice + ' ,-₺ ');
        spansale.appendChild(nodesale);
        element[0].appendChild(spansale);

        var spanprice = document.createElement("span");
        var del = document.createElement("del");
        var nodeprice = document.createTextNode(price + ' ,-₺ ');
        del.appendChild(nodeprice);
        spanprice.appendChild(del);
        element[0].appendChild(spanprice);

    }else{
        //console.log("burası çalışmamalı");
        modal.find('.aa-product-view-price').text(price + ' ,-₺ ');
    }

});
