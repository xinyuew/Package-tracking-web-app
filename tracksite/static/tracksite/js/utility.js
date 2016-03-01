function simple_validate(num) {
    if (!num.match(/^[a-zA-Z0-9]+/)) {
        $('#myModal').modal('show');
        return false;
    }

    if (num.length == 0) {
        return false;
    } else if (num.length > 30) {
        $('#myModal').modal('show');
        return false;
    } else if (num.length < 12) {
        $('#myModal').modal('show');
        return false;
    }

    return true;
}

function agreeAddRoommate() {
    $('#roommate-modal-agree').modal('show');
    var request_username = $('#request_username');
    var target_username = $('#target_username');

    $.post("/tracksite/add_as_roommate", {
        request_username: request_username.val(),
        target_username: target_username.val()
    });
}

function rejectAddRoommate() {
    $('#roommate-modal-reject').modal('show');
}

function closeAddRoommateConfirm() {
    document.location.href = "/tracksite/profile"
}

function removeRoommate() {
    var user_id = parseInt($(this).attr('user-id'));
    var panel = $("#roommate-panel" + user_id);
    var modal = $("#remove-roommate-modal");
    $.post("/tracksite/remove_roommate/" + user_id).done(function () {
        var count = parseInt($('#roomate-count-id').html());
        count--;
        $('#roomate-count-id').html(count);
        panel.remove();
        modal.modal('show');
    });
}


function deletePackages() {
    var track_id = parseInt($(this).attr('track-id'));
    var panel = $("#track-panel-" + track_id);
    $.post("/tracksite/delete_track/" + track_id)
        .done(function () {
            var count = parseInt($("#user-info-package-count").html());
            count--;
            $("#user-info-package-count").html(count);
            panel.remove();
        });
}

function background_check_delivery() {
    if ($('.badge').data('bs.popover')) {
        return;
    }

    var badge = $('.badge');
    $.getJSON("/tracksite/check_delivery", function (data) {
        var len = 0;
        var html_content = "";
        $.each(data, function (key, val) {
            html_content += key + "<br>";
            len++;
        });

        badge.html(len);
        if (len > 0) {
            badge.attr("style", "background-color: orangered");
        } else {
            badge.attr("style", "background-color: darkgrey");
        }
    });
}

$(document).ready(function () {
    var csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    // check delivery at background
    background_check_delivery();
    window.setInterval(background_check_delivery, 2*60*1000);

    // bind validation to submit event
    var key = 'queried';
    $('#query_form').submit(function () {
        //event.preventDefault();
        var track = $.trim($("input[name='track_num']").val());

        if (!simple_validate(track)) {
            $("input[name='track_num']").val('');
            return false;
        }

        var history = Cookies.getJSON(key);
        if (history != undefined) {
            history[key].push(track);
            $.unique(history[key]);
            if (history[key].length > 5) {
                history[key].reverse();
                history[key].pop();
                history[key].reverse();
            }
        } else {
            history = {queried: [track]};
        }

        Cookies.set(key, history);
    });

    // udpate history panel
    var entries = Cookies.getJSON(key);
    if (entries == undefined) {
        $('#history-panel').hide();
    } else {
        var list = $('#history-list');
        var i;
        for (i = 0; i < entries[key].length; i++) {
            var html = '<p><a href="/tracksite/query/' + entries[key][i] + '">' + entries[key][i] + '</a></p>';
            list.append(html);
        }
    }

    // tooltip for add icon
    $('#add-it').tooltip();
    $('#add-it').click(function () {
        event.preventDefault();
        var tnum = $('#tnum').attr('value');
        $("input[name='track_num']").val(tnum);

        var old = $('#query_form').attr("action")
        $('#query_form').attr("action", '/tracksite/add_track');
        $('#query_form').submit();

        // reset form attributes
        $('#query_form').attr("action", old);
        $("input[name='track_num']").val('');
    });

    // add button for user homepage
    $('#addbtn').click(function () {
        event.preventDefault();
        var old = $('#query_form').attr("action");
        $('#query_form').attr("action", '/tracksite/add_track');
        $('#query_form').submit();
        $('#query_form').attr("action", old);
    });

    // add roommate
    $('#aggree-add-roommate').click(agreeAddRoommate);
    $('#reject-add-roommate').click(rejectAddRoommate);
    $('#close-add-roommate-confirm').click(closeAddRoommateConfirm);

    // delete package from user's timeline
    $('.glyphicon, .glyphicon-remove-sign, .delete-package').tooltip();
    $('.glyphicon, .glyphicon-remove-sign, .delete-package').click(deletePackages);

    // remove roommate
    $('#manage-roommates').tooltip();
    $('.remove-btn, .btn-primary, .btn, .btn-sm').click(removeRoommate);

    $('#package-number').tooltip();

    // find shipment service provider near user
    $('#prof-location').tooltip();
    $('#prof-location').click(function () {
        event.preventDefault();
        var query_string = "UPS OR FedEx near ";
        query_string += $(this).html();
        query_string = query_string.replace(/ /g, "+");
        var url = "http://maps.google.com/?q=" + query_string;
        window.open(url);
        return false;
    });

    // badge
    $('.badge').click(function () {
        event.preventDefault();
        if ($(this).data('bs.popover')) {
            $(this).popover("destroy");
            return;
        }

        var badge = $('.badge');
        $.getJSON("/tracksite/check_delivery", function (data) {
            var len = 0;
            var html_content = "";
            $.each(data, function (key, val) {
                html_content += "<a href='/tracksite/query/" + key + "'>" + key + "</a><br>";
                html_content += "Est delivery @ " + val + "<br><hr style='margin:3px;'>";
                len++;
            });

            badge.html(len);
            if (len > 0) {
                badge.attr("style", "background-color: orangered");
                badge.popover({
                    trigger: "manual",
                    container: "body",
                    placement: "bottom",
                    title: "Upcoming Delivery within 12 hours",
                    html: true,
                    content: html_content
                });
            } else {
                badge.attr("style", "background-color: darkgrey");
                badge.popover({
                    trigger: "manual",
                    container: "body",
                    placement: "bottom",
                    title: "Upcoming Delivery within 12 hours",
                    content: "No packages"
                });
            }

            badge.popover("show");
        });
    });
});