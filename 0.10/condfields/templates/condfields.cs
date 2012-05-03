var condfields = {};
<?cs each:type = condfields.types ?>
condfields['<?cs name:type ?>'] = {};
<?cs each:field = type ?>
condfields['<?cs name:type ?>']['<?cs name:field ?>'] = <?cs var:field ?>;
<?cs /each ?>
<?cs /each ?>

var ok_fields = [];
<?cs each:field = condfields.ok_fields ?>
ok_fields[<?cs name:field ?>] = '<?cs var:field ?>';
<?cs /each ?>

$(function() {
    var mode = '<?cs var:condfields.mode ?>';
    
    var field_data = {};
    for(var i=0;i<ok_fields.length;i++) {
        var field = ok_fields[i];
        if(mode == 'view' && field == 'owner') continue;
        field_data[field] = {
            label: $('label[@for='+field+']').parents('th').html(),
            input: $('#'+field).parents('td').html()
        }
    }
    //console.log(field_data);
    //console.log(mode);
    
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
            } else {
                table += '<th class="col2">'
            }
            
            table += field_data[field].label + '</th><td>' + field_data[field].input + '</td>'
            
            if(col == 1) {
                col = 2;
            } else {
                table += '</tr>'
                col = 1;
            }

            // Copy out the value
            values.push({field:field,value:$('#'+field).val()});

        }
        
        <?cs if:condfields.mode == 'new' ?>
        $('#properties tbody').html(table);
        <?cs else ?>
        var n=0;
        $('#properties tbody tr').each(function() {
            if(n > 3) {
                $(this).remove()
            }
            n += 1;
        })
        $('#properties tbody').append(table);
        <?cs /if ?>
        
        // Restore the previous values
        for(var i=0;i<values.length;i++) {
            $('#'+values[i].field).val(values[i].value);
        }
    }
    
    function set_header_type(t) {
        // Make a dict so I can check containment
        ok_fields_dict = {}
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
    
    set_type($('#type').val());
    
    $('#type').change(function() {
        set_type($(this).val());
    })
});