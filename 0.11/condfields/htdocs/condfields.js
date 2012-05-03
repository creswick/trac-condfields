// var condfields = {};


// #for type, fields in condfields.types.iteritems()
// condfields['$type'] = {};
// #for field, val in fields.iteritems()
// condfields['$type']['$field'] = ${val and 'true' or 'false'};
// #end
// #end

// console.log(mode);
console.log(condfields);

// var ok_view_fields = [];
// #for field, val in enumerate(condfields.ok_view_fields)
// ok_view_fields[$field] = '$val';
// #end

// var ok_new_fields = [];
// #for field, val in enumerate(condfields.ok_new_fields)
// ok_new_fields[$field] = '$val';
// #end

$(function() {
    if(mode == 'view'){
        ok_fields = ok_view_fields;
    } else {
        ok_fields = ok_new_fields;
    }

    var field_data = {};
    for(var i=0;i<ok_fields.length;i++) {
        var field = ok_fields[i];
        if(mode == 'view' && field == 'owner') continue;

        field_data[field] = {
            label: $('label[for=\'field-'+field+'\']').parents('th').html(),
            input: $('#field-'+field).parents('td').html()
        };
    }

    function set_type(t) {

        var col = 1;
        var table = '';
        var values = [];
        for(var i=0;i<ok_fields.length;i++) {
          var field = ok_fields[i];
          if(mode == 'view' && field == 'owner') continue;
          if(condfields[t][field] == 0) continue;

          if(col == 1) {
		        table += '<tr><th class="col1">';
		        table += field_data[field].label + '</th>';
		        table += '<td class="col1">' + field_data[field].input + '</td>';
          } else {
            table += '<th class="col2">';
		        table += field_data[field].label + '</th>';
		        table += '<td class="col2">' + field_data[field].input + '</td>';
          }

	        if(col == 1){
		        col = 2;
          } else {
            table += '</tr>';
            col = 1;
          }

          // Copy out the value
          values.push({field:field,value:$('#field-'+field).val()});
        }

        if(mode == 'new') {
            //$('#properties tbody').html(table);
            var n=0;
            $('#properties tbody tr').each(
              function() {
                if(n > 3) {
                  $(this).remove();
                }
                n += 1;
              });
            $('#properties tbody').append(table);
        } else {
            var n=0;
            $('#properties tbody tr').each(function() {
                if(n > 3) {
                    $(this).remove()
                }
                n += 1;
            });
            $('#properties tbody').append(table);
        }

        // Restore the previous values
        for(var i=0;i<values.length;i++) {
            $('#field-'+values[i].field).val(values[i].value);
        }
    }

    function set_header_type(t) {
        // Make a dict so I can check containment
        ok_fields_dict = {};
        for(var i=0;i<ok_fields.length;i++) {
            ok_fields_dict[ok_fields[i]] = 1;
        }

        var elms = [[]];
        $('table.properties tr').each(function() {
            $(this).children().each(function() {
                var attr = {TH: 'id', TD: 'headers'}[this.nodeName];
                if($(this).attr(attr) != null && condfields[t][$(this).attr(attr).substring(2)] == 1) {
                    elms[0].push(this);
                    if(elms[0].length == 4) {
                        var tmp = $('<tr></tr>');
                        $.each(elms[0], function(i, e) {
                            tmp.append(e);
                        });
                        elms[0] = tmp;
                        elms.unshift([]);
                    }
                }
            });
        });
        if(elms[0].length == 0) {
            elms.shift();
        } else {
            var tmp = $('<tr></tr>');
            $.each(elms[0], function(i, e) {
                tmp.append(e);
            });
            elms[0] = tmp;
        }
        elms.reverse();
        $('table.properties').empty();
        $.each(elms, function(i, row) {
            $('table.properties').append(row);
        });
    }

    if(mode == 'view') {
        var status_re = /\(\w+ ([^:]+)(: \w+)?\)/;
        var re_results = status_re.exec($('span.status').text());
        set_header_type(re_results[1]);
    }

    set_type($('#field-type').val());

    $('#field-type').change(function() {
        set_type($(this).val());
    });
});
