#[derive(Debug, serde::Serialize, serde::Deserialize, Clone)]
pub struct AppInfo {
    pub id: String,
    pub name: String,
    pub exec: String,
    pub icon: Option<String>,
    pub icon_path: Option<String>,
    pub comment: Option<String>,
}
