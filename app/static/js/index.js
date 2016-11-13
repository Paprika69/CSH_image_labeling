$(function(){

    $("#condition_form").submit(function(e){
        // prevent the default submit event
        e.preventDefault();

        var num = $("input[name='num']").val();
        if(num === ""){
            alert("please fill the Number of Images");
            $("input[name='num']").focus();
            return false;
        }
        $.post('/api/metadata/query', $("#condition_form").serialize(), function(data){
            // empty the div content
            $("#img_list").empty();
            //update stat_bar
            $("#stat_bar").html(data.stat);
            // read the template
            var tpl = $("#tpl").val();
            // for cycle
            for(var i=0; i<data.data.length; i++){
                var tpl2 = tpl;
                var record = data.data[i];

                var segmentType = "None";
                if(record.segmentCharacteristics != undefined && record.segmentCharacteristics.segmentType != undefined){
                    segmentType = record.segmentCharacteristics.segmentType;
                    if(segmentType == "word"){
                        segmentType = segmentType + ":" + record.segmentCharacteristics.label;
                    }
                }

                tpl2 = tpl2.replace('{img}', record.anonymizedImageFile).replace('{id}', record._id).replace('{id}', record._id).replace('{segmentType}', segmentType);
                $("#img_list").append(tpl2);
            }

            $("#condition_form").hide();
            $("#content").show();
        });


    });

    $("#cancel").click(function(){
        $("#content").show();
        $("#condition_form").hide();
    });

    $("#switch").click(function(){
        $("#content").hide();
        $("#condition_form").show();
    });

    $("#partialWord, #multiLine, #nonText, #word, #words").click(function(){
        var checkedList = $("#img_list input[type=checkbox]:checked");
        if(checkedList.length < 0){
            alert("please select the iamges, can not be empty.");
            return;
        }

        var segmentType = $(this).attr('id');
        var label = $("#label").val();

        var id = [];
        for(var i=0;i<checkedList.length;i++){
            id.push(checkedList[i].value);
        }
        var data = {
            id:id,
            segmentType: segmentType
        };

        // if segment type is transcribe, check the input text if has a word
        if(segmentType == 'word' && label.trim().length == 0){
            alert('please input a word');
            return;
        }

        // if segment type is a word, set label
        if(segmentType == 'word'){
            data.label = label;
        }


        // now submit the checkedList to server via ajax
        $.post('/api/metadata/label', data, function(result){
            alert(result.message);
            // action is successful, we will update the page
            if(result.success){
                // update the images key feature
                for(var i=0;i<checkedList.length;i++){
                    var el = checkedList.eq(i);
                    // update segment type
                    var text = segmentType;
                    if(segmentType == "word"){
                        text = segmentType + ":" + label;
                    }
                    el.parents('.responsive').find('.segmentType').text(text);
                    // remove checked
                    el.prop('checked', false);
                }
            }
        });
    });
 });