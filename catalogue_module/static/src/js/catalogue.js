odoo.define('catalogue_module.catalogue', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.OnlineAppointment = publicWidget.Widget.extend({
        selector: '.submit_catalogue',

        events: {
            'click .submit_catalog': 'submit_conditions',
            'click .add_product': 'add_products',
            'click .delete_line': 'delete_line',
        },

        submit_conditions: function (e) {
            e.preventDefault();
            let form = document.querySelector('form');

            let qty = document.getElementsByClassName('quantities');
            let qty_add = document.getElementsByClassName('qty_add');

            let error_value = document.getElementsByClassName('error_value');
            let can_submit = true;
            for (let i = 0; i < qty.length; i++){
                if (parseInt(qty_add[i].value) > parseInt(qty[i].value)){
                    can_submit = false;
                    error_value[i].style = "display: block;"
                }
                else{
                    error_value[i].style = "display: none;"
                }
            }
            if (can_submit){
                form.submit();
            }
        },

        delete_line: function (e) {
            e.preventDefault();
            let parentRow = e.currentTarget.parentElement.parentNode;
            parentRow.remove();
        },

        add_products: function (e) {
            e.preventDefault();

            let catalogue_id = document.getElementById('catalogue_id');
            let products = document.getElementsByClassName('product_template_id');
            let productValues = [];

            for (let i = 0; i < products.length; i++) {
                productValues.push(products[i].value);
            }
            $.ajax({
                url: '/website/catalogue/available/products',
                data: {
                    catalogue_id: catalogue_id.value,
                    products: JSON.stringify(productValues),
                },
                dataType: 'json',
                success: function(data) {
                    if (data.length == 0){
                        return
                    }
                    let print_btn = document.getElementsByClassName('print_btn');
                    if (print_btn.length > 0){
                        print_btn[0].remove();
                    }

                    let table = document.getElementsByClassName('table');
                    let newRow = table[0].insertRow(-1);

                    let cell0 = newRow.insertCell(0);
                    let cell1 = newRow.insertCell(1);
                    let cell2 = newRow.insertCell(2);
                    let cell3 = newRow.insertCell(3);
                    let cell4 = newRow.insertCell(4);
                    let cell5 = newRow.insertCell(5);
                    let cell6 = newRow.insertCell(6);

                    cell0.style = "padding-left: 10px; border-bottom: solid #d9d9d9 1px;"
                    cell1.style = cell2.style = cell3.style = cell4.style = cell5.style = cell6.style = "border-bottom: solid #d9d9d9 1px;"

                    let selectElement = document.createElement('select');
                    selectElement.classList.add('form-select', 'product_template_id');

                    let div_product_name = document.createElement('div');
                    div_product_name.classList.add('product-name');

                    let input_qty_add = document.createElement('input');
                    input_qty_add.classList.add('form-control', 'qty_add');
                    input_qty_add.type = 'number';

                    let error_value = document.createElement('div');
                    error_value.classList.add('error_value');
                    error_value.innerHTML = `<span class="text-danger">Quantity Unavailable.</span>`
                    error_value.style= "display: none;";

                    let input_max_qty = document.createElement('input');
                    input_max_qty.classList.add('form-control', 'quantities');
                    input_max_qty.type = 'number';
                    input_max_qty.setAttribute("readonly", "readonly");
                    input_max_qty.style= "background: white; border: 0px;";
                    input_max_qty.disabled = true;

                    let input_price_unit = document.createElement('input');
                    input_price_unit.classList.add('form-control', 'price_unit');
                    input_price_unit.type = 'number';


                    let input_subtotal = document.createElement('input');
                    input_subtotal.classList.add('form-control', 'product-subtotal');
                    input_subtotal.type = 'number';
                    input_subtotal.setAttribute("readonly", "readonly");
                    input_subtotal.style= "background: white; border: 0px;";
                    input_subtotal.disabled = true;

                    let div_delete_parent = document.createElement('div');
                    div_delete_parent.classList.add('btn', 'btn-danger', 'delete_line');
                    div_delete_parent.textContent = 'Delete'



                    data.forEach(function(product) {
                        let optionElement = document.createElement('option');
                        optionElement.value = product.product_id;
                        optionElement.text = product.product_name;
                        selectElement.appendChild(optionElement);
                        let product_name = (product.product_id).toString() + '-product_template_id';
                        selectElement.setAttribute("name", product_name);

                        div_product_name.textContent = product.product_name;

                        input_qty_add.value = product.max_qty;
                        let qty_add = (product.product_id).toString() + '-product_uom_qty"';
                        input_qty_add.setAttribute("name", qty_add);
                        input_qty_add.max = parseFloat(product.max_qty);
                        input_qty_add.min = 1;

                        input_max_qty.value = product.max_qty;

                        input_price_unit.value = product.price_unit;
                        let price_name = (product.product_id).toString() + '-price_unit';
                        input_price_unit.setAttribute("name", price_name);
                        input_price_unit.min = 1;

                        input_subtotal.value = parseFloat(product.max_qty) * parseFloat(product.price_unit)
                    });

                    cell0.appendChild(selectElement);
                    cell1.appendChild(div_product_name);
                    cell2.appendChild(input_qty_add);
                    cell2.appendChild(error_value);
                    cell3.appendChild(input_max_qty);
                    cell4.appendChild(input_price_unit);
                    cell5.appendChild(input_subtotal);
                    cell6.appendChild(div_delete_parent);

                },
                error: function (error) {
                    console.log(`Error ${error}`);
                }
            });


        },



    })
});
