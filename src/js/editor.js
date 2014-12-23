var POST_EDITOR;

$(function () {
    var textArea = $('#post_editor')[0];
    POST_EDITOR = CodeMirror.fromTextArea(textArea, {
        mode: 'markdown',
        lineWrapping: true,
    });

    $('#save-button').on('click', function () {
        var markdown = POST_EDITOR.getValue();
        var post_slug = window.location.pathname;
        $.post('/edit' + post_slug, { text: markdown }, function (response) {
            $('.post').empty().append(response);
            MathJax.Hub.Typeset();
        });
        return false;
    });
});
