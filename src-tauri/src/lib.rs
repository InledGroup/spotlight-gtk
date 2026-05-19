pub mod domain;
pub mod application;
pub mod infrastructure;

use crate::domain::app::AppInfo;
use crate::application::use_cases::{SearchApps, LaunchApp};
use crate::infrastructure::linux_repository::{LinuxAppRepository, LinuxAppLauncher};

#[tauri::command]
fn get_apps() -> Vec<AppInfo> {
    let repo = LinuxAppRepository;
    let use_case = SearchApps { repo: &repo };
    use_case.execute()
}

#[tauri::command]
fn launch_app(app: AppInfo) -> Result<(), String> {
    let launcher = LinuxAppLauncher;
    let use_case = LaunchApp { launcher: &launcher };
    use_case.execute(app)
}

#[tauri::command]
fn hide_window(window: tauri::Window) {
    window.hide().unwrap();
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_log::Builder::default().build())
    .invoke_handler(tauri::generate_handler![get_apps, launch_app, hide_window])
    .setup(|_app| {
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
