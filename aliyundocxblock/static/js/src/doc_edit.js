function docXBlockInitEdit(runtime, element) {
    $(element).find('.action-cancel').bind('click', function () {
        runtime.notify('cancel', {});
    });

    $(element).find('.action-save').bind('click', function () {
        var data = {
            'display_name': $('#doc_edit_display_name').val(),
            url: $('#doc_edit_url').val(),
            'allow_download': $('#doc_edit_allow_download').val(),
            'source_text': $('#doc_edit_source_text').val()
        };

        runtime.notify('save', { state: 'start' });

        var handlerUrl = runtime.handlerUrl(element, 'save_doc');
        $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
            if (response.result === 'success') {
                runtime.notify('save', { state: 'end' });
            }
            else {
                runtime.notify('error', { msg: response.message });
            }
        });
    });
}
