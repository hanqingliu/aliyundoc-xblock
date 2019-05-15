/* Javascript for AliyunDocXBlock. */
function AliyunDocXBlock(runtime, element) {

    if (element.innerHTML) {
        element = $(element);
    }

    $(function ($) {
        /*
        Use `gettext` provided by django-statici18n for static translations

        var gettext = AliyunDocXBlocki18n.gettext;
        */

        /* Here's where you'd do things on page load. */
        element.find('.doc-download-button').on('click', function () {
            var handlerUrl = runtime.handlerUrl(element, 'on_download');
            $.post(handlerUrl, '{}');
        });
    });
}
