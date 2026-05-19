use crate::domain::app::AppInfo;
use crate::application::ports::{AppRepository, AppLauncher};

pub struct SearchApps<'a> {
    pub repo: &'a dyn AppRepository,
}

impl<'a> SearchApps<'a> {
    pub fn execute(&self) -> Vec<AppInfo> {
        self.repo.get_all_apps()
    }
}

pub struct LaunchApp<'a> {
    pub launcher: &'a dyn AppLauncher,
}

impl<'a> LaunchApp<'a> {
    pub fn execute(&self, app: AppInfo) -> Result<(), String> {
        self.launcher.launch(&app)
    }
}
