import os

def upgrade_forms():
    template_dirs = [
        r"c:\Users\Yves Zigashane\Documents\Projects\accounting_project\src\templates\accounting",
        r"c:\Users\Yves Zigashane\Documents\Projects\accounting_project\src\templates\cashflow",
        r"c:\Users\Yves Zigashane\Documents\Projects\accounting_project\src\templates\budget",
    ]
    
    form_template = """{%% extends 'base.html' %%}
{%% load i18n crispy_forms_tags %%}

{%% block title %%}
{%% trans "Form" %%} | Système de Comptabilité
{%% endblock %%}

{%% block content %%}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card mb-3">
            <div class="card-header bg-light">
                <h5 class="mb-0">
                    {%% if form.instance.pk %%}{%% trans "Edit" %%}{%% else %%}{%% trans "Create" %%}{%% endif %%}
                </h5>
            </div>
            <div class="card-body border-top">
                <form method="post" class="needs-validation">
                    {%% csrf_token %%}
                    <div class="mb-3">
                        {{ form|crispy }}
                    </div>
                    <div class="d-flex justify-content-between mt-4">
                        <a href="javascript:history.back()" class="btn btn-falcon-default btn-sm">
                            <span class="fas fa-arrow-left me-1"></span>{%% trans "Back" %%}
                        </a>
                        <button type="submit" class="btn btn-falcon-primary btn-sm px-4">
                            <span class="fas fa-save me-1"></span>{%% trans "Save" %%}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{%% endblock %%}
"""

    delete_template = """{%% extends 'base.html' %%}
{%% load i18n %%}

{%% block title %%}
{%% trans "Confirm Delete" %%} | Système de Comptabilité
{%% endblock %%}

{%% block content %%}
<div class="row justify-content-center">
    <div class="col-lg-6">
        <div class="card mb-3">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0 text-white">
                    <span class="fas fa-exclamation-triangle me-2"></span>{%% trans "Confirm Deletion" %%}
                </h5>
            </div>
            <div class="card-body border-top text-center py-5">
                <h4 class="mb-3">{%% trans "Are you sure?" %%}</h4>
                <p class="mb-4">{%% trans "You are about to delete this record. This action cannot be undone." %%}</p>
                <form method="post">
                    {%% csrf_token %%}
                    <div class="d-flex justify-content-center gap-2">
                        <a href="javascript:history.back()" class="btn btn-falcon-default">
                            {%% trans "Cancel" %%}
                        </a>
                        <button type="submit" class="btn btn-danger px-4">
                            <span class="fas fa-trash me-1"></span>{%% trans "Yes, Delete" %%}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{%% endblock %%}
"""

    for t_dir in template_dirs:
        for f in os.listdir(t_dir):
            path = os.path.join(t_dir, f)
            if not f.endswith('.html'): continue
            
            size = os.path.getsize(path)
            if size < 600:
                if f.endswith('_form.html'):
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(form_template)
                    print(f"Upgraded {f}")
                elif f.endswith('_confirm_delete.html') or f.endswith('_confirm.html'):
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(delete_template)
                    print(f"Upgraded {f}")

upgrade_forms()
