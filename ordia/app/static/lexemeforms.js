// functions to interact with https://tools.wmflabs.org/lexeme-forms

function lexemeTemplatesByLang(templates_response) {
    var templates_by_language = {};
    for (var key in templates_response) {
        var template_data = templates_response[key];
        var language = template_data['language_code'];
        var label = template_data['label'];
        if (! (language in templates_by_language) ) {
             templates_by_language[language] = {};
        }
        templates_by_language[language][key] = label;
    }
    return templates_by_language;
}

function lexemeTemplateSelection(language, lexeme, element) {
    var templates_api_url = "https://tools.wmflabs.org/lexeme-forms/api/v1/template/";
    var templates_prefix = "https://tools.wmflabs.org/lexeme-forms/template/";
    
    $.getJSON(templates_api_url, function(response) {
        var templates_by_language = lexemeTemplatesByLang(response);
        var use_templates = templates_by_language[language];
        for (var key in use_templates) {
            $(element).append('<a href="' +
			      templates_prefix +
			      key +
			      '?form_representation=' +
			      lexeme +
			      '"><button type="button" class="btn btn-secondary">' +
			      use_templates[key] +
			      '</button></a> ');
        }
    });
}
