from fast_tmp.amis_app import AmisAPI
from fast_tmp.conf import settings
from {{cookiecutter.project_slug}}.apps.api.routes.hello_fast_tmp import hello_fast_tmp_router
{{cookiecutter.project_slug}}_app = AmisAPI(
    title="api",
    debug=settings.DEBUG,
)
{{cookiecutter.project_slug}}_app.include_router(hello_fast_tmp_router)