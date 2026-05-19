use crate::domain::app::AppInfo;

pub trait AppRepository {
    fn get_all_apps(&self) -> Vec<AppInfo>;
}

pub trait AppLauncher {
    fn launch(&self, app: &AppInfo) -> Result<(), String>;
}
