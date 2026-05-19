use std::fs;
use std::path::PathBuf;
use std::process::Command;
use walkdir::WalkDir;
use crate::domain::app::AppInfo;
use crate::application::ports::{AppRepository, AppLauncher};

pub struct LinuxAppRepository;

impl AppRepository for LinuxAppRepository {
    fn get_all_apps(&self) -> Vec<AppInfo> {
        let mut apps = Vec::new();
        let paths = vec![
            PathBuf::from("/usr/share/applications"),
            dirs::home_dir().map(|p| p.join(".local/share/applications")).unwrap_or_default(),
        ];

        for path in paths {
            if !path.exists() { continue; }
            for entry in WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
                if entry.path().extension().map_or(false, |ext| ext == "desktop") {
                    if let Ok(content) = fs::read_to_string(entry.path()) {
                        if let Some(app) = parse_desktop_file(entry.path().to_path_buf(), &content) {
                            apps.push(app);
                        }
                    }
                }
            }
        }
        
        // Remove duplicates by ID (filename)
        apps.sort_by(|a, b| a.id.cmp(&b.id));
        apps.dedup_by(|a, b| a.id == b.id);
        
        apps
    }
}

fn parse_desktop_file(path: PathBuf, content: &str) -> Option<AppInfo> {
    let mut name = None;
    let mut exec = None;
    let mut icon = None;
    let mut comment = None;
    let mut is_no_display = false;

    for line in content.lines() {
        if line.starts_with("NoDisplay=true") {
            is_no_display = true;
        }
        if line.starts_with("Name=") && name.is_none() {
            name = Some(line["Name=".len()..].to_string());
        }
        if line.starts_with("Exec=") && exec.is_none() {
            exec = Some(line["Exec=".len()..].to_string());
        }
        if line.starts_with("Icon=") && icon.is_none() {
            icon = Some(line["Icon=".len()..].to_string());
        }
        if line.starts_with("Comment=") && comment.is_none() {
            comment = Some(line["Comment=".len()..].to_string());
        }
    }

    if is_no_display { return None; }

    if let (Some(n), Some(e)) = (name, exec) {
        // Clean exec (remove %u, %f, etc)
        let clean_exec = e.split_whitespace()
            .filter(|s| !s.starts_with('%'))
            .collect::<Vec<_>>()
            .join(" ");

        Some(AppInfo {
            id: path.file_name()?.to_string_lossy().to_string(),
            name: n,
            exec: clean_exec,
            icon_path: resolve_icon(&icon),
            icon,
            comment,
        })
    } else {
        None
    }
}

fn resolve_icon(icon_name: &Option<String>) -> Option<String> {
    let name = icon_name.as_ref()?;
    if name.is_empty() { return None; }
    
    // If it's already an absolute path and exists
    if name.starts_with('/') {
        if std::path::Path::new(name).exists() {
            return Some(name.clone());
        }
        // Sometimes icons in desktop files have paths but no extension
        let extensions = vec!["png", "svg", "xpm"];
        for ext in extensions {
            let path_with_ext = format!("{}.{}", name, ext);
            if std::path::Path::new(&path_with_ext).exists() {
                return Some(path_with_ext);
            }
        }
    }

    // Common icon themes and paths
    let themes = vec!["hicolor", "Adwaita", "breeze", "Papirus", "ubuntu-mono-dark"];
    let sizes = vec!["scalable", "48x48", "64x64", "128x128", "256x256", "32x32"];
    let categories = vec!["apps", "categories", "devices", "mimetypes"];

    for theme in themes {
        for size in &sizes {
            for category in &categories {
                let base_paths = vec![
                    format!("/usr/share/icons/{}/{}/{}", theme, size, category),
                    format!("/usr/local/share/icons/{}/{}/{}", theme, size, category),
                    dirs::home_dir().map(|p| p.join(format!(".local/share/icons/{}/{}/{}", theme, size, category)).to_string_lossy().to_string()).unwrap_or_default(),
                ];

                for base in base_paths {
                    if base.is_empty() { continue; }
                    let extensions = vec!["png", "svg", "xpm"];
                    for ext in extensions {
                        let path = format!("{}/{}.{}", base, name, ext);
                        if std::path::Path::new(&path).exists() {
                            return Some(path);
                        }
                    }
                }
            }
        }
    }
    
    // Last resort: check pixmaps directly
    let pixmap_bases = vec!["/usr/share/pixmaps", "/usr/local/share/pixmaps"];
    for base in pixmap_bases {
        let extensions = vec!["png", "svg", "xpm", "jpg"];
        for ext in extensions {
            let path = format!("{}/{}.{}", base, name, ext);
            if std::path::Path::new(&path).exists() {
                return Some(path);
            }
        }
    }

    None
}

pub struct LinuxAppLauncher;

impl AppLauncher for LinuxAppLauncher {
    fn launch(&self, app: &AppInfo) -> Result<(), String> {
        Command::new("sh")
            .arg("-c")
            .arg(format!("{} &", app.exec))
            .spawn()
            .map_err(|e| e.to_string())?;
        Ok(())
    }
}
