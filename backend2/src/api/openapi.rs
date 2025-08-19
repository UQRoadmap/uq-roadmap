/// Most of this is yoinked from a great guide:
/// https://apatisandor.hu/blog/production-ready-openapi/
/// It goes into plenty more details for extending this further, including security stuff.
use utoipa::OpenApi;

#[derive(OpenApi)]
#[openapi(
    paths(
        crate::api::get_course_by_pair
    ),
    components(
        schemas(
            crate::db::course::Course
        ),
    ),
    tags(
        (name = "course", description = "Related to courses"),
    ),
    servers(
        (url = "/", description = "Local Server"),
    ),
)]
pub struct ApiDoc;
