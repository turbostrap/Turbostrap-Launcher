import customtkinter as ctk
import subprocess
import threading
import psutil
import os
import sys
import json
import winreg
import webbrowser
import urllib.request
import zipfile
import tempfile
from pathlib import Path
from tkinter import messagebox, colorchooser, Canvas
from PIL import Image, ImageTk
import requests
from io import BytesIO
import ctypes
import pystray
from pystray import MenuItem as TrayItem

def open_roblox_folder():
    path = get_roblox_install_path()
    if path and os.path.exists(path):
        subprocess.Popen(f'explorer "{path}"')
    else:
        from tkinter import messagebox
        messagebox.showerror("Error", "Roblox is not installed.")


def get_roblox_install_path():
    local_appdata = os.getenv("LOCALAPPDATA")
    if not local_appdata:
        return None

    path = os.path.join(local_appdata, "TurboStrap")
    return path if os.path.exists(path) else None


def get_folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total


def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def get_install_size():
    path = get_roblox_install_path()
    if not path:
        return "Not Installed"

    return format_size(get_folder_size(path))
 
 
 
 
def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def init_app_icon():
    try:
        myappid = u"com.capde.turbostraplauncher.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass



FONT_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts"
REQUIRED_FONTS = {
    "BebasNeue-Regular.ttf":        "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
    "Barlow-Regular.ttf":           "https://github.com/google/fonts/raw/main/ofl/barlow/Barlow-Regular.ttf",
    "Barlow-Bold.ttf":              "https://github.com/google/fonts/raw/main/ofl/barlow/Barlow-Bold.ttf",
    "Barlow-SemiBold.ttf":          "https://github.com/google/fonts/raw/main/ofl/barlow/Barlow-SemiBold.ttf",
    "Barlow-Italic.ttf":            "https://github.com/google/fonts/raw/main/ofl/barlow/Barlow-Italic.ttf",
    "BarlowCondensed-Regular.ttf":  "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-Regular.ttf",
    "BarlowCondensed-Bold.ttf":     "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-Bold.ttf",
    "BarlowCondensed-SemiBold.ttf": "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-SemiBold.ttf",
}

def _register_font(path):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, Path(path).stem, 0, winreg.REG_SZ, str(path))
        winreg.CloseKey(key)
    except:
        pass

def _download_font(filename, url):
    dest = FONT_DIR / filename
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r, open(dest, "wb") as f:
        f.write(r.read())
    _register_font(dest)

def _check_fonts_installed():
    return [f for f in REQUIRED_FONTS if not (FONT_DIR / f).exists()]

def bootstrap_fonts():
    missing = _check_fonts_installed()
    if not missing:
        return

    import tkinter as tk
    root = tk.Tk()
    root.withdraw()

    splash = tk.Toplevel(root)
    splash.title("TurboStrap")
    splash.configure(bg="#080808")
    splash.resizable(False, False)
    splash.overrideredirect(True)
    
    

    W, H = 380, 420
    splash.update_idletasks()
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    x = (sw - W) // 2
    y = (sh - H) // 2
    splash.geometry(f"{W}x{H}+{x}+{y}")
    splash.update_idletasks()

    outer = tk.Canvas(splash, width=W, height=H, bg="#080808", highlightthickness=0)
    outer.pack(fill="both", expand=True)

    for x in range(0, W, 24):
        outer.create_line(x, 0, x, H, fill="#1a1a1a", width=1)
    for y in range(0, H, 24):
        outer.create_line(0, y, W, y, fill="#1a1a1a", width=1)

    cx, cy = W // 2, H // 2
    card_w, card_h = 300, 320
    card_x1 = cx - card_w // 2
    card_y1 = cy - card_h // 2
    card_x2 = cx + card_w // 2
    card_y2 = cy + card_h // 2
    outer.create_rectangle(card_x1, card_y1, card_x2, card_y2,
        fill="#0d0d0d", outline="#2a2a2a", width=1)

    for x in range(card_x1, card_x2, 20):
        outer.create_line(x, card_y1, x, card_y2, fill="#141414", width=1)
    for y in range(card_y1, card_y2, 20):
        outer.create_line(card_x1, y, card_x2, y, fill="#141414", width=1)

    logo_cx, logo_cy = cx, card_y1 + 105
    logo_r = 55
    try:
        _bs_img = Image.open(resource_path("turbostrap.png")).resize(
            (logo_r * 2, logo_r * 2), Image.LANCZOS)
        _bs_photo = ImageTk.PhotoImage(_bs_img)
        outer.create_image(logo_cx, logo_cy, anchor="center", image=_bs_photo)
        outer._bs_photo = _bs_photo
    except Exception:
        outer.create_oval(
            logo_cx - logo_r, logo_cy - logo_r,
            logo_cx + logo_r, logo_cy + logo_r,
            fill="#111", outline="#222", width=2)
        outer.create_text(logo_cx, logo_cy, text="CE",
            font=("Consolas", 28, "bold"), fill="#c41213")

    ring_r = logo_r + 10
    ring_bbox = [logo_cx - ring_r, logo_cy - ring_r,
                 logo_cx + ring_r, logo_cy + ring_r]
    outer.create_oval(*ring_bbox, outline="#222", width=3)
    arc = outer.create_arc(*ring_bbox, start=90, extent=0,
        outline="#c41213", width=3, style="arc")

    outer.create_text(cx, logo_cy + 80, text="TurboStrap",
        font=("Consolas", 20, "bold"), fill="#f5f5f5")
    outer.create_text(cx, logo_cy + 106, text="v1.0.0",
        font=("Consolas", 11), fill="#555")

    status_var = tk.StringVar(value="Checking fonts...")
    status_lbl = tk.Label(splash, textvariable=status_var,
        font=("Consolas", 10), fg="#666", bg="#0d0d0d", wraplength=260)
    outer.create_window(cx, card_y2 - 30, window=status_lbl)
    splash.update()

    total = len(missing)
    _done = [0]
    _angle = [0.0]
    _spinning = [True]

    def _spin():
        if _spinning[0]:
            _angle[0] = (_angle[0] - 4) % 360
            progress_extent = int((_done[0] / max(total, 1)) * 360)
            start = (_angle[0] + 90) % 360
            outer.itemconfig(arc, start=start, extent=max(20, progress_extent), outline="#c41213")
            splash.after(16, _spin)

    def _install():
        FONT_DIR.mkdir(parents=True, exist_ok=True)
        for i, filename in enumerate(missing):
            url = REQUIRED_FONTS[filename]
            name = filename.replace(".ttf", "").replace("-", " ")
            status_var.set(f"Installing {name}...")
            splash.update()
            try:
                _download_font(filename, url)
            except:
                status_var.set(f"Skipped {filename}")
            _done[0] = i + 1

        outer.itemconfig(arc, extent=359, outline="#00c850", start=90)
        status_var.set("All tasks completed")
        status_lbl.configure(fg="#00c850")
        _spinning[0] = False
        splash.after(900, lambda: (splash.destroy(), root.destroy()))

    _spin()
    splash.after(100, _install)
    root.mainloop()

bootstrap_fonts()



APP_VERSION = "1.2"
CONFIG_PATH = Path(os.getenv("APPDATA")) / "TurboStrap" / "config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

VERSION_URL = "https://fr.lowkey.nichesite.org/version.txt"

def check_for_update():
    try:
        resp = requests.get(VERSION_URL, timeout=5)
        resp.raise_for_status()
        latest = resp.text.strip()
        return latest if latest != APP_VERSION else None
    except Exception:
        return None
        
DEFAULT_CONFIG = {
    "fps_limit": 144,
    "fps_unlock": True,
    "memory_optimise": True,
    "launch_flags": "",
    "accent_color": "#c41213",
    "roblox_path": "",
    "auto_update": True,
}

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


TS_RBLX_BASE    = Path(os.getenv("LOCALAPPDATA")) / "TurboStrap" / "RblxVersions"
TS_VERSION_FILE = Path(os.getenv("LOCALAPPDATA")) / "TurboStrap" / "current_version.txt"

CDN_VERSION_URL = "https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer"
CDN_BASE        = "https://setup.rbxcdn.com"


ROBLOX_LAUNCH_URI = "roblox-player:1+launchmode:App"

_SKIP_PACKAGES = {
    "RobloxStudio.zip",
    "LibrariesQt5.zip",
}


PACKAGE_DIRS = {
    "RobloxApp.zip":                "",
    "redist.zip":                   "",
    "Libraries.zip":                "",
    "WebView2RuntimeInstaller.zip": "WebView2RuntimeInstaller",
    "shaders.zip":                  "shaders",
    "ssl.zip":                      "ssl",
    "content-avatar.zip":           "content/avatar",
    "content-configs.zip":          "content/configs",
    "content-fonts.zip":            "content/fonts",
    "content-sky.zip":              "content/sky",
    "content-sounds.zip":           "content/sounds",
    "content-textures2.zip":        "content/textures",
    "content-models.zip":           "content/models",
    "content-textures3.zip":        "PlatformContent/pc/textures",
    "content-terrain.zip":          "PlatformContent/pc/terrain",
    "content-platform-fonts.zip":   "PlatformContent/pc/fonts",
    "extracontent-luapackages.zip": "ExtraContent/LuaPackages",
    "extracontent-translations.zip":"ExtraContent/translations",
    "extracontent-models.zip":      "ExtraContent/models",
    "extracontent-textures.zip":    "ExtraContent/textures",
    "extracontent-places.zip":      "ExtraContent/places",
}


def get_latest_roblox_version():
    try:
        resp = requests.get(CDN_VERSION_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("clientVersionUpload") or data.get("version") or ""
    except Exception:
        return None

def get_installed_version():
    if TS_VERSION_FILE.exists():
        return TS_VERSION_FILE.read_text().strip()
    return ""

def get_installed_exe():
    """Return path to RobloxPlayerBeta.exe if the managed install exists."""
    ver = get_installed_version()
    if not ver:
        return None
    exe = TS_RBLX_BASE / ver / "RobloxPlayerBeta.exe"
    return str(exe) if exe.exists() else None

def find_roblox(cfg=None):
    return get_installed_exe()


def _parse_manifest(text):
    packages = []
    lines = [l.strip() for l in text.splitlines()]
    i = 1 if lines and not lines[0].endswith(".zip") else 0
    while i < len(lines):
        line = lines[i]
        if line.endswith(".zip"):
            if line not in _SKIP_PACKAGES:
                packages.append(line)
            i += 4
        else:
            i += 1
    return packages


def download_roblox(version_hash, progress_cb=None, status_cb=None):
    dest_dir = TS_RBLX_BASE / version_hash
    dest_dir.mkdir(parents=True, exist_ok=True)


    manifest_url = f"{CDN_BASE}/{version_hash}-rbxPkgManifest.txt"
    if status_cb:
        status_cb(f"Fetching manifest for {version_hash}...")
    try:
        resp = requests.get(manifest_url, timeout=15)
        resp.raise_for_status()
        packages = _parse_manifest(resp.text)
    except Exception as e:
        if status_cb:
            status_cb(f"✗ Manifest fetch failed: {e}")
        return False

    if not packages:
        if status_cb:
            status_cb("✗ No packages found in manifest")
        return False

    if status_cb:
        status_cb(f"Found {len(packages)} packages to download")


    total = len(packages)
    for i, pkg in enumerate(packages):
        url      = f"{CDN_BASE}/{version_hash}-{pkg}"
        zip_path = dest_dir / pkg

        marker = dest_dir / f".done_{pkg}"
        if marker.exists():
            if progress_cb:
                progress_cb(((i + 1) / total) * 100)
            if status_cb:
                status_cb(f"Skipping {pkg} (already extracted)")
            continue

        if status_cb:
            status_cb(f"[{i+1}/{total}]  Downloading  {pkg}")

        try:
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=131072):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_cb and total_size:
                                overall = ((i + downloaded / total_size) / total) * 100
                                progress_cb(overall)
        except Exception as e:
            if status_cb:
                status_cb(f"✗ Download failed ({pkg}): {e}")
            continue


        subfolder = PACKAGE_DIRS.get(pkg, "")
        extract_to = (dest_dir / subfolder) if subfolder else dest_dir
        extract_to.mkdir(parents=True, exist_ok=True)

        if status_cb:
            status_cb(f"[{i+1}/{total}]  Extracting   {pkg} → /{subfolder or ''}")
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_to)
            zip_path.unlink()
            marker.touch()
        except Exception as e:
            if status_cb:
                status_cb(f"✗ Extract failed ({pkg}): {e}")
            if zip_path.exists():
                zip_path.unlink(missing_ok=True)
            continue


    app_settings = dest_dir / "AppSettings.xml"
    if not app_settings.exists():
        app_settings.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\r\n'
            '<Settings>\r\n'
            '  <ContentFolder>content</ContentFolder>\r\n'
            '  <BaseUrl>http://www.roblox.com</BaseUrl>\r\n'
            '</Settings>\r\n'
        )
        if status_cb:
            status_cb("✓ Wrote AppSettings.xml")


    exe_path = dest_dir / "RobloxPlayerBeta.exe"
    if not exe_path.exists():
        all_exes = list(dest_dir.rglob("*.exe"))
        if status_cb:
            status_cb("✗ RobloxPlayerBeta.exe not found at install root!")
            for e in all_exes:
                status_cb(f"  Found: {e.relative_to(dest_dir)}  ({e.stat().st_size:,} bytes)")
        return False

    if status_cb:
        status_cb(f"✓ RobloxPlayerBeta.exe  ({exe_path.stat().st_size:,} bytes)")


    TS_VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    TS_VERSION_FILE.write_text(version_hash)

    if status_cb:
        status_cb(f"✓ Roblox {version_hash} ready")
    if progress_cb:
        progress_cb(100)
    return True



ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG      = "#050505"
CARD_BG = "#0a0a0a"
BORDER  = "#1a1a1a"
TEXT    = "#e0e0e0"
MUTED   = "#999999"
ACCENT  = "#c41213"


FFLAGS_LEGACY_FRM_QUALITY_LABELS = frozenset({
    "Voxel (Level 21)", "ShadowMap (Level 20)", "Future (Level 19)",
})



FFLAG_CATEGORIES = {
    "Rendering": {
        "renderer": {
            "type": "dropdown",
            "label": "Graphics Renderer",
            "desc": "Choose your graphics backend (mutually exclusive)",
            "options": {
                "Vulkan": {
                    "FFlagDebugGraphicsDisableDirect3D11": "True",
                    "FFlagDebugGraphicsPreferVulkan": "True",
                },
                "OpenGL": {
                    "FFlagDebugGraphicsDisableDirect3D11": "True",
                    "FFlagDebugGraphicsPreferOpenGL": "True",
                },
                "Direct3D 11": {"FFlagDebugGraphicsPreferD3D11": "True"},
                "Auto (Roblox Default)": {}
            },
            "default": "Auto (Roblox Default)"
        },
        "lighting_quality": {
            "type": "dropdown",
            "label": "Graphics quality (FRM override)",
            "desc": "DFIntDebugFRMQualityLevelOverride maps to Roblox's internal 1–21 bar "
                    "(low ≈ 1–6, high ≈ 7–21). Prefer Auto so the in-game graphics slider is used.",
            "options": {
                "Auto": {},
                "Low": {"DFIntDebugFRMQualityLevelOverride": "3"},
                "Medium": {"DFIntDebugFRMQualityLevelOverride": "10"},
                "High": {"DFIntDebugFRMQualityLevelOverride": "21"},
            },
            "default": "Auto"
        },
        "disable_post_fx": {
            "type": "toggle",
            "label": "Disable Post-Processing",
            "desc": "Turn off bloom, depth of field, and other post effects",
            "flags": {"FFlagDisablePostFx": "True"}
        },
        "texture_quality": {
            "type": "dropdown",
            "label": "Texture Quality",
            "desc": "Control texture resolution",
            "options": {
                "High (Level 3)": {"DFIntTextureQualityOverride": "3"},
                "Medium (Level 2)": {"DFIntTextureQualityOverride": "2"},
                "Low (Level 1)": {"DFIntTextureQualityOverride": "1"},
                "Auto": {}
            },
            "default": "Auto"
        },
        "disable_vsync": {
            "type": "toggle",
            "label": "Disable V-Sync",
            "desc": "Turn off vertical sync (may cause screen tearing)",
            "flags": {"DFIntTaskSchedulerTargetFps": "9999"}
        },
    },
    "Performance": {
        "fps_unlock": {
            "type": "toggle",
            "label": "Unlock FPS Cap",
            "desc": "Remove Roblox's 60 FPS limit",
            "flags": {
                "FFlagTaskSchedulerLimitTargetFpsTo2402": "False",
                "DFIntTaskSchedulerTargetFps": "240"
            }
        },
        "memory_optimization": {
            "type": "toggle",
            "label": "Memory Optimization",
            "desc": "Reduce memory usage and improve stability",
            "flags": {
                "FIntMeshContentProviderCacheSize": "268435456",
                "DFFlagVideoCaptureServiceEnabled": "False"
            }
        },
        "thread_count": {
            "type": "dropdown",
            "label": "Render Thread Count",
            "desc": "Number of threads for rendering",
            "options": {
                "1 Thread": {"FIntRenderLocalLightFadeInMs": "1"},
                "2 Threads": {"FIntRenderLocalLightFadeInMs": "2"},
                "4 Threads": {"FIntRenderLocalLightFadeInMs": "4"},
                "Auto": {}
            },
            "default": "Auto"
        },
        "network_optimization": {
            "type": "toggle",
            "label": "Network Optimization",
            "desc": "Reduce network overhead and improve ping",
            "flags": {"DFIntConnectionMTUSize": "900"}
        },
    },
    "Physics": {
        "physics_fps": {
            "type": "dropdown",
            "label": "Physics FPS",
            "desc": "Physics simulation rate",
            "options": {
                "240 FPS": {"DFIntS61PhysicsFPSBucket10": "240"},
                "120 FPS": {"DFIntS61PhysicsFPSBucket10": "120"},
                "60 FPS (Default)": {},
            },
            "default": "60 FPS (Default)"
        },
        "reduce_motion_blur": {
            "type": "toggle",
            "label": "Reduce Motion Blur",
            "desc": "Minimize motion blur effects",
            "flags": {"FIntCameraShakeMultiplier": "0"}
        },
    },
    "UI/UX": {
        "disable_telemetry": {
            "type": "toggle",
            "label": "Disable Analytics/Telemetry",
            "desc": "Stop Roblox from collecting usage data",
            "flags": {
                "FFlagDebugDisableTelemetryEphemeralCounter": "True",
                "FFlagDebugDisableTelemetryEphemeralStat": "True",
                "FFlagDebugDisableTelemetryEventIngest": "True",
                "FFlagDebugDisableTelemetryPoint": "True",
                "FFlagDebugDisableTelemetryV2Counter": "True",
                "FFlagDebugDisableTelemetryV2Event": "True",
                "FFlagDebugDisableTelemetryV2Stat": "True"
            }
        },
        "font_size": {
            "type": "dropdown",
            "label": "UI Font Size",
            "desc": "Adjust in-game UI text size",
            "options": {
                "Large": {"FIntFontSizePadding": "2"},
                "Normal": {},
                "Small": {"FIntFontSizePadding": "-2"},
            },
            "default": "Normal"
        },
        "disable_captures": {
            "type": "toggle",
            "label": "Disable Captures",
            "desc": "Turn off Roblox Captures feature",
            "flags": {
                "FFlagEnableCapturesHotkeyExperiment_v4": "False",
                "DFFlagVideoCaptureServiceEnabled": "False"
            }
        },
    },
    "Debug": {
        "show_fps": {
            "type": "toggle",
            "label": "Show FPS Counter",
            "desc": "Display FPS in top-right corner",
            "flags": {"FFlagDebugDisplayFPS": "True"}
        },
        "verbose_logging": {
            "type": "toggle",
            "label": "Verbose Logging",
            "desc": "Enable detailed console logs",
            "flags": {
                "FIntDefaultClientCoreScriptStackTracingProbability": "100",
                "DFFlagDebugEnableNewScriptProfiler": "True"
            }
        },
        "crash_reporter": {
            "type": "toggle",
            "label": "Disable Crash Reporter",
            "desc": "Turn off automatic crash reporting",
            "flags": {
                "DFFlagCrashReportingEnabled": "False",
                "DFFlagCrashUploadToBacktraceEnabled": "False"
            }
        },
    },
    "Experimental": {
        "future_lighting": {
            "type": "toggle",
            "label": "Force Future Lighting",
            "desc": "Enable Future lighting technology (may be buggy)",
            "flags": {
                "FFlagDebugForceFutureIsBrightPhase2": "True",
                "FFlagDebugForceFutureIsBrightPhase3": "True"
            }
        },
        "new_terrain": {
            "type": "toggle",
            "label": "New Terrain System",
            "desc": "Use experimental terrain rendering",
            "flags": {
                "FFlagDebugRenderForceTechnologyVoxel": "False",
                "FFlagDebugEnableNewTerrainSystem": "True"
            }
        },
        "http_cache": {
            "type": "toggle",
            "label": "Aggressive HTTP Caching",
            "desc": "Cache more assets to reduce downloads",
            "flags": {
                "DFIntHttpCacheCleanMaxFilesPerCycle": "2000000",
                "DFIntHttpCacheCleanMinFilesToKeep": "2000000"
            }
        },
    }
}



FFLAGS_PATH = Path(os.getenv("APPDATA")) / "TurboStrap" / "fflags.json"

def load_fflags():
    data = {}
    if FFLAGS_PATH.exists():
        try:
            with open(FFLAGS_PATH) as f:
                data = json.load(f)
        except Exception:
            pass
    lk = "Rendering.lighting_quality"
    if data.get(lk) in FFLAGS_LEGACY_FRM_QUALITY_LABELS:
        data[lk] = "Auto"
        try:
            save_fflags(data)
        except Exception:
            pass
    return data

def save_fflags(settings):
    with open(FFLAGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def apply_fflags_to_roblox(flags_dict):
    ver = get_installed_version()
    if ver:
        target_dir = TS_RBLX_BASE / ver
        if target_dir.exists():
            return apply_fflags_to_roblox_path(target_dir, flags_dict)
    versions_base = Path(os.getenv("LOCALAPPDATA")) / "Roblox" / "Versions"
    if not versions_base.exists():
        return False
    version_dirs = sorted(versions_base.glob("version-*"), reverse=True)
    if not version_dirs:
        return False
    return apply_fflags_to_roblox_path(version_dirs[0], flags_dict)

def apply_fflags_to_roblox_path(version_dir, flags_dict):
    """Write ClientAppSettings.json, or remove it when there are no overrides so
    in-game graphics settings work again (stale JSON was ignoring the menu)."""
    try:
        settings_dir = Path(version_dir) / "ClientSettings"
        settings_file = settings_dir / "ClientAppSettings.json"
        if not flags_dict:
            if settings_file.exists():
                settings_file.unlink()
            return True
        settings_dir.mkdir(parents=True, exist_ok=True)
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(flags_dict, f, indent=2)
        return True
    except Exception:
        return False

def load_raw_fflags():
    settings = load_fflags()
    merged = {}
    for cat_name, cat_data in FFLAG_CATEGORIES.items():
        for key, data in cat_data.items():
            full_key = f"{cat_name}.{key}"
            val = settings.get(full_key)
            if val is None:
                continue
            if data["type"] == "toggle" and val:
                merged.update(data["flags"])
            elif data["type"] == "dropdown":
                if (
                    full_key == "Rendering.lighting_quality"
                    and val in FFLAGS_LEGACY_FRM_QUALITY_LABELS
                ):
                    continue
                option_flags = data["options"].get(val, {})
                merged.update(option_flags)
    return merged


def lbl(parent, text, font=("Barlow", 13), color=TEXT, **kw):
    return ctk.CTkLabel(parent, text=text, font=font, text_color=color, **kw)

def btn(parent, text, cmd, font=("Barlow SemiBold", 13), **kw):
    kw.setdefault("corner_radius", 6)
    return ctk.CTkButton(parent, text=text, command=cmd, font=font, **kw)

def _darken(hex_color, factor=0.75):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"

def _darken(hex_color, factor=0.75):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"
    
    
class LaunchPage(ctk.CTkFrame):
    def __init__(self, parent, cfg):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.cfg = cfg

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(anchor="w", padx=30, pady=(28, 0))
        lbl(title_frame, "LAUNCH ", font=("Bebas Neue", 42), color=TEXT).pack(side="left")
        lbl(title_frame, "ROBLOX", font=("Bebas Neue", 42), color=ACCENT).pack(side="left")

        lbl(self, "All systems optimised. Ready to go.",
            font=("Barlow", 12), color=MUTED).pack(anchor="w", padx=30, pady=(4, 20))

        cards_row = ctk.CTkFrame(self, fg_color="transparent")
        cards_row.pack(fill="x", padx=30, pady=(0, 16))
        cards_row.columnconfigure((0, 1, 2), weight=1, uniform="col")

        fps_card = ctk.CTkFrame(cards_row, fg_color=CARD_BG, corner_radius=6,
            border_width=1, border_color=BORDER)
        fps_card.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        lbl(fps_card, "FPS UNLOCK", font=("Barlow", 10), color=MUTED).pack(anchor="w", padx=14, pady=(12, 2))
        fps_val   = "ENABLED"  if cfg.get("fps_unlock", True) else "DISABLED"
        fps_color = "#00c850"  if cfg.get("fps_unlock", True) else "#ff4444"
        self.fps_status_lbl = lbl(fps_card, fps_val, font=("Bebas Neue", 22), color=fps_color)
        self.fps_status_lbl.pack(anchor="w", padx=14, pady=(0, 12))

        mem_card = ctk.CTkFrame(cards_row, fg_color=CARD_BG, corner_radius=6,
            border_width=1, border_color=BORDER)
        mem_card.grid(row=0, column=1, padx=6, sticky="nsew")
        lbl(mem_card, "MEMORY OPT", font=("Barlow", 10), color=MUTED).pack(anchor="w", padx=14, pady=(12, 2))
        mem_val   = "READY"   if cfg.get("memory_optimise", True) else "OFF"
        mem_color = "#ff9500" if cfg.get("memory_optimise", True) else MUTED
        self.mem_status_lbl = lbl(mem_card, mem_val, font=("Bebas Neue", 22), color=mem_color)
        self.mem_status_lbl.pack(anchor="w", padx=14, pady=(0, 12))

        ver_card = ctk.CTkFrame(cards_row, fg_color=CARD_BG, corner_radius=6,
            border_width=1, border_color=BORDER)
        ver_card.grid(row=0, column=2, padx=(6, 0), sticky="nsew")
        lbl(ver_card, "ROBLOX BUILD", font=("Barlow", 10), color=MUTED).pack(anchor="w", padx=14, pady=(12, 2))
        installed = get_installed_version()
        ver_short = installed[-8:].upper() if installed else "NONE"
        self.ver_status_lbl = lbl(ver_card, ver_short, font=("Bebas Neue", 22), color=TEXT)
        self.ver_status_lbl.pack(anchor="w", padx=14, pady=(0, 12))

        self.progress_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=6,
            border_width=1, border_color=BORDER)
        self.progress_label = lbl(self.progress_frame, "Checking for updates...",
            font=("Barlow", 11), color=MUTED)
        self.progress_label.pack(anchor="w", padx=16, pady=(12, 4))
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame,
            fg_color=BORDER, progress_color=ACCENT, height=6, corner_radius=3)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 12))

        lbl(self, "CONSOLE", font=("Barlow SemiBold", 11), color=MUTED).pack(
            anchor="w", padx=30, pady=(0, 6))

        self.console = ctk.CTkTextbox(self, fg_color=CARD_BG, corner_radius=6,
            border_width=1, border_color=BORDER,
            font=("Consolas", 11), text_color=MUTED, state="disabled")
        self.console.pack(fill="both", expand=True, padx=30, pady=(0, 16))

        self.launch_btn = btn(self, "▶  LAUNCH ROBLOX", self._on_launch_click,
            font=("Bebas Neue", 22), height=54,
            fg_color=ACCENT, hover_color=_darken(ACCENT))
        self.launch_btn.pack(fill="x", padx=30, pady=(0, 2))

        btn(self, "🗑  WIPE & REDOWNLOAD", self._wipe_and_redownload,
            font=("Barlow SemiBold", 11), height=28,
            fg_color="#222", hover_color="#333").pack(fill="x", padx=30, pady=(0, 2))

        btn(self, "OPEN ROBLOX.COM", lambda: webbrowser.open("https://www.roblox.com"),
            font=("Barlow SemiBold", 12), height=32,
            fg_color=CARD_BG, hover_color=BORDER).pack(fill="x", padx=30, pady=(0, 20))

        self.refresh()

    def _log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def _set_progress(self, value, label=None):
        def _update():
            self.progress_bar.set(value / 100)
            if label:
                self.progress_label.configure(text=label)
        self.after(0, _update)

    def _show_progress(self, show=True):
        def _update():
            if show:
                self.progress_frame.pack(fill="x", padx=30, pady=(0, 10), before=self.console)
            else:
                self.progress_frame.pack_forget()
        self.after(0, _update)

    def refresh(self):
        fps_val   = "ENABLED"  if self.cfg.get("fps_unlock",      True) else "DISABLED"
        fps_col   = "#00c850"  if self.cfg.get("fps_unlock",      True) else "#ff4444"
        mem_val   = "READY"    if self.cfg.get("memory_optimise", True) else "OFF"
        mem_col   = "#ff9500"  if self.cfg.get("memory_optimise", True) else MUTED
        installed = get_installed_version()
        ver_short = installed[-8:].upper() if installed else "NONE"

        self.fps_status_lbl.configure(text=fps_val, text_color=fps_col)
        self.mem_status_lbl.configure(text=mem_val, text_color=mem_col)
        self.ver_status_lbl.configure(text=ver_short)

        ts_exe = get_installed_exe()
        if ts_exe:
            self._log(f"✓ TurboStrap Roblox ready  [{installed}]")
        else:
            self._log("ℹ No TurboStrap Roblox install — click Launch to download")

    def _wipe_and_redownload(self):
        import shutil
        ver = get_installed_version()
        if not ver:
            self._log("Nothing to wipe.")
            return
        if not messagebox.askyesno("Wipe Install",
                f"Delete install ({ver[-8:].upper()}) and redownload?"):
            return
        try:
            shutil.rmtree(TS_RBLX_BASE / ver, ignore_errors=True)
        except Exception as e:
            self._log(f"✗ Wipe failed: {e}")
            return
        if TS_VERSION_FILE.exists():
            TS_VERSION_FILE.unlink(missing_ok=True)
        self._log("✓ Install wiped — click Launch to redownload")
        self.ver_status_lbl.configure(text="NONE")

    def _on_launch_click(self):
        self.launch_btn.configure(state="disabled", text="CHECKING...")
        threading.Thread(target=self._check_and_launch, daemon=True).start()

    def _check_and_launch(self):
        self.after(0, lambda: self._log("Checking for Roblox updates..."))

        latest    = get_latest_roblox_version()
        installed = get_installed_version()
        ts_exe    = get_installed_exe()

        if not latest:
            if ts_exe:
                self.after(0, lambda: self._log("⚠ Couldn't reach CDN — launching existing install"))
                self._do_launch_exe()
            else:
                self.after(0, lambda: messagebox.showerror(
                    "No Internet / No Install",
                    "Could not reach the Roblox update server and no local install was found.\n\n"
                    "Please check your internet connection and try again."))
                self.after(0, lambda: self.launch_btn.configure(
                    state="normal", text="▶  LAUNCH ROBLOX"))
            return

        self.after(0, lambda: self._log(f"Latest:    {latest}"))
        self.after(0, lambda: self._log(f"Installed: {installed if installed else 'none'}"))

        need_download = (latest != installed) or (not ts_exe)

        if need_download:
            label = "Installing Roblox..." if not installed else f"Updating to {latest[-12:]}..."
            self.after(0, lambda: self._log(label))
            self._show_progress(True)
            self.after(0, lambda: self._set_progress(0, label))
            self.after(0, lambda: self.launch_btn.configure(
                text="DOWNLOADING..." if not installed else "UPDATING..."))

            success = download_roblox(
                latest,
                progress_cb=lambda v: self._set_progress(v),
                status_cb=lambda s: self.after(0, lambda m=s: (
                    self._log(m),
                    self._set_progress(self.progress_bar.get() * 100, m)
                ))
            )

            self._show_progress(False)

            if success:
                ver_short = latest[-8:].upper()
                self.after(0, lambda: self.ver_status_lbl.configure(text=ver_short))
                raw = load_raw_fflags()
                apply_fflags_to_roblox_path(TS_RBLX_BASE / latest, raw)
                if raw:
                    self.after(0, lambda: self._log(f"✓ Applied {len(raw)} FFlags"))
                self._do_launch_exe()
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Download Failed",
                    "Roblox failed to download.\n\n"
                    "Click 'WIPE & REDOWNLOAD' then try again.\n"
                    "Check the console for details."))
                self.after(0, lambda: self.launch_btn.configure(
                    state="normal", text="▶  LAUNCH ROBLOX"))
        else:
            self.after(0, lambda: self._log("✓ Already up to date"))
            self._do_launch_exe()

    def _do_launch_exe(self):
        roblox = get_installed_exe()

        if not roblox:
            self.after(0, lambda: messagebox.showerror(
                "TurboStrap",
                "RobloxPlayerBeta.exe not found.\n\n"
                "Click 'WIPE & REDOWNLOAD' to reinstall."))
            self.after(0, lambda: self.launch_btn.configure(
                state="normal", text="▶  LAUNCH ROBLOX"))
            return

        exe_size = Path(roblox).stat().st_size
        self.after(0, lambda: self._log(
            f"Launching: {Path(roblox).name}  ({exe_size:,} bytes)"))
        self.after(0, lambda: self._log(f"URI arg: {ROBLOX_LAUNCH_URI}"))
        self.after(0, lambda: self.launch_btn.configure(text="LAUNCHING..."))

        try:
            apply_fflags_to_roblox(load_raw_fflags())

            proc = subprocess.Popen(
                [roblox, ROBLOX_LAUNCH_URI],
                cwd=str(Path(roblox).parent)
            )
            self.after(0, lambda: self._log("✓ Roblox launched successfully"))
            root = self
            while root is not None:
                if isinstance(root, TurboStrap):
                    self.after(0, lambda r=root: r.go_to_tray(proc))
                    break
                root = getattr(root, "master", None)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Launch Error", str(e)))
            self.after(0, lambda: self._log(f"✗ Launch failed: {e}"))
        finally:
            self.after(0, lambda: self.launch_btn.configure(
                state="normal", text="▶  LAUNCH ROBLOX"))




class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent, cfg, refresh_cb):
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        self.cfg = cfg
        self.refresh_cb = refresh_cb

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        lbl(scroll, "Settings", font=("Bebas Neue", 28)).pack(anchor="w", pady=(0, 20))

        
        card1 = ctk.CTkFrame(
            scroll,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=BORDER
        )
        card1.pack(fill="x", pady=10)

        lbl(card1, "Performance", font=("Barlow SemiBold", 16)).pack(
            anchor="w", padx=20, pady=(15, 10)
        )

        self.fps_unlock_var = ctk.BooleanVar(value=cfg.get("fps_unlock", True))
        ctk.CTkSwitch(
            card1,
            text="Unlock FPS Cap",
            variable=self.fps_unlock_var,
            onvalue=True,
            offvalue=False,
            progress_color=ACCENT,
            button_color=TEXT,
            fg_color=BORDER,
            font=("Barlow", 13)
        ).pack(anchor="w", padx=20, pady=5)

        self.mem_opt_var = ctk.BooleanVar(value=cfg.get("memory_optimise", True))
        ctk.CTkSwitch(
            card1,
            text="Memory Optimization",
            variable=self.mem_opt_var,
            onvalue=True,
            offvalue=False,
            progress_color=ACCENT,
            button_color=TEXT,
            fg_color=BORDER,
            font=("Barlow", 13)
        ).pack(anchor="w", padx=20, pady=(5, 15))

        btn(
            scroll,
            "📂 Open Roblox Folder",
            open_roblox_folder,
            width=200,
            fg_color=ACCENT,
           hover_color=_darken(ACCENT)
        ).pack(pady=10)

       
        self.install_size_lbl = lbl(
            scroll,
            f"Install Size: {get_install_size()}",
            font=("Barlow", 12),
            color="white"
        )
        self.install_size_lbl.pack(anchor="w", padx=315, pady=0)


    def _save(self):
        self.cfg["fps_unlock"] = self.fps_unlock_var.get()
        self.cfg["memory_optimise"] = self.mem_opt_var.get()
        save_config(self.cfg)
        messagebox.showinfo("TurboStrap", "Settings saved!")
        self.refresh_cb()

class LogsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        lbl(self, "Logs", font=("Bebas Neue", 28)).pack(anchor="w", padx=20, pady=20)
        self.log_box = ctk.CTkTextbox(self, fg_color=CARD_BG, corner_radius=8,
            border_width=1, border_color=BORDER, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_box.insert("1.0", "TurboStrap Logs\n" + "=" * 50 + "\n\n")
        self.log_box.insert("end", "✓ Launcher initialized\n")
        self.log_box.insert("end", "✓ Configuration loaded\n")
        self.log_box.insert("end", "✓ FFlags system ready\n")


class AboutPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=8,
            border_width=1, border_color=BORDER)
        card.pack(pady=40, padx=40, fill="both", expand=True)
        lbl(card, "TurboStrap", font=("Bebas Neue", 36)).pack(pady=(40, 10))
        lbl(card, f"Version {APP_VERSION}", font=("Barlow", 14), color=MUTED).pack()
        lbl(card, "Enhanced Roblox Launcher", font=("Barlow", 13), color=MUTED).pack(pady=(5, 30))
        lbl(card, "Features:", font=("Barlow SemiBold", 15)).pack(pady=(20, 10))
        for feat in [
            "✓ FPS Unlock & Performance Optimization",
            "✓ Advanced FFlags Management",
            "✓ System Resource Monitoring",
            "✓ Custom Accent Colors",
            "✓ Minimize to Tray"
        ]:
            lbl(card, feat, font=("Barlow", 12), color=TEXT).pack(pady=2)
class ThemePage(ctk.CTkFrame):
    def __init__(self, parent, cfg, refresh_cb):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.cfg = cfg
        self.refresh_cb = refresh_cb

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        title_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        title_frame.pack(anchor="w", pady=(0, 20))
        lbl(title_frame, "THEME ", font=("Bebas Neue", 42), color=TEXT).pack(side="left")
        lbl(title_frame, "EDITOR", font=("Bebas Neue", 42), color=ACCENT).pack(side="left")
        lbl(scroll, "Customise the look of TurboStrap.",
            font=("Barlow", 12), color=MUTED).pack(anchor="w", pady=(0, 20))

    
        accent_card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=8,
            border_width=1, border_color=BORDER)
        accent_card.pack(fill="x", pady=10)

        lbl(accent_card, "Accent Colour", font=("Barlow SemiBold", 16)).pack(
            anchor="w", padx=20, pady=(15, 4))
        lbl(accent_card, "Changes the primary accent colour throughout the app. Restart to apply everywhere.",
            font=("Barlow", 11), color=MUTED, wraplength=560, justify="left").pack(
            anchor="w", padx=20, pady=(0, 14))

        preview_row = ctk.CTkFrame(accent_card, fg_color="transparent")
        preview_row.pack(fill="x", padx=20, pady=(0, 6))

        self._swatch = ctk.CTkFrame(preview_row, width=48, height=48,
            corner_radius=8, fg_color=cfg.get("accent_color", ACCENT))
        self._swatch.pack(side="left", padx=(0, 14))
        self._swatch.pack_propagate(False)

        info_col = ctk.CTkFrame(preview_row, fg_color="transparent")
        info_col.pack(side="left")
        lbl(info_col, "Current colour", font=("Barlow", 10), color=MUTED).pack(anchor="w")
        self._hex_lbl = lbl(info_col, cfg.get("accent_color", ACCENT).upper(),
            font=("Consolas", 15), color=TEXT)
        self._hex_lbl.pack(anchor="w")
        self._hover_lbl = lbl(info_col,
            f"Hover: {_darken(cfg.get('accent_color', ACCENT)).upper()}",
            font=("Consolas", 11), color=MUTED)
        self._hover_lbl.pack(anchor="w")

        btn_row = ctk.CTkFrame(accent_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(10, 18))
        btn(btn_row, "🎨  Pick Colour", self._pick_accent,
            width=140, fg_color=ACCENT, hover_color=_darken(ACCENT)).pack(side="left", padx=(0, 8))
        btn(btn_row, "↺  Reset to Default", self._reset_accent,
            width=160, fg_color="#333", hover_color="#444").pack(side="left")

    
        presets_card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=8,
            border_width=1, border_color=BORDER)
        presets_card.pack(fill="x", pady=10)

        lbl(presets_card, "Colour Presets", font=("Barlow SemiBold", 16)).pack(
            anchor="w", padx=20, pady=(15, 4))
        lbl(presets_card, "Click a preset to instantly apply it.",
            font=("Barlow", 11), color=MUTED).pack(anchor="w", padx=20, pady=(0, 14))

        presets_grid = ctk.CTkFrame(presets_card, fg_color="transparent")
        presets_grid.pack(fill="x", padx=20, pady=(0, 18))

        self._presets = [
            ("TurboRed",    "#c41213"),
            ("Flame",       "#ff3c00"),
            ("Cobalt",      "#1e6fff"),
            ("Emerald",     "#00c850"),
            ("Violet",      "#8b5cf6"),
            ("Gold",        "#f59e0b"),
            ("Cyan",        "#06b6d4"),
            ("Rose",        "#f43f5e"),
        ]

        for i, (name, color) in enumerate(self._presets):
            col = i % 4
            row = i // 4
            cell = ctk.CTkFrame(presets_grid, fg_color="transparent")
            cell.grid(row=row, column=col, padx=8, pady=8, sticky="w")
            swatch = ctk.CTkFrame(cell, width=32, height=32,
                corner_radius=6, fg_color=color, cursor="hand2")
            swatch.pack()
            swatch.pack_propagate(False)
            swatch.bind("<Button-1>", lambda e, c=color: self._apply_accent(c))
            lbl(cell, name, font=("Barlow", 10), color=MUTED).pack(pady=(4, 0))

      
        save_card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=8,
            border_width=1, border_color=BORDER)
        save_card.pack(fill="x", pady=10)
        lbl(save_card, "Changes are previewed live but require a restart to apply everywhere.",
            font=("Barlow", 11), color=MUTED, wraplength=560, justify="left").pack(
            anchor="w", padx=20, pady=(15, 10))
        btn(save_card, "💾  Save Theme", self._save,
            width=180, fg_color=ACCENT, hover_color=_darken(ACCENT)).pack(
            anchor="w", padx=20, pady=(0, 18))

    def _pick_accent(self):
        current = self.cfg.get("accent_color", ACCENT)
        result = colorchooser.askcolor(color=current, title="Pick Accent Colour")
        if result and result[1]:
            self._apply_accent(result[1].lower())

    def _reset_accent(self):
        self._apply_accent("#c41213")

    def _apply_accent(self, color):
        global ACCENT
        ACCENT = color
        self.cfg["accent_color"] = color
        self._swatch.configure(fg_color=color)
        self._hex_lbl.configure(text=color.upper())
        self._hover_lbl.configure(text=f"Hover: {_darken(color).upper()}")

    def _save(self):
        global ACCENT
        ACCENT = self.cfg.get("accent_color", ACCENT)
        save_config(self.cfg)
        messagebox.showinfo("TurboStrap", "Theme applied!")
        self.refresh_cb()

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, nav_cb):
        super().__init__(parent, fg_color=BG, corner_radius=0, width=220)
        self.nav_cb = nav_cb
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(20, 10))
        lbl(logo_frame, "TurboStrap", font=("Barlow SemiBold", 14)).pack()

        
        

        
        
        for text, page in [
            ("🚀 LAUNCH",     "LAUNCH"),
            ("⚙️  SETTINGS",  "SETTINGS"),
            ("🔧 FAST FLAGS", "FFLAGS"),
            ("🛠  CUSTOM FLAGS", "CUSTOM"),
            ("🎨 THEME",      "THEME"),
            ("📊 LOGS",       "LOGS"),
            ("ℹ️  ABOUT",     "ABOUT"),
        ]:
            ctk.CTkButton(self, text=text, command=lambda p=page: nav_cb(p),
                font=("Barlow SemiBold", 13), fg_color="transparent",
                hover_color=BORDER, anchor="w", height=40).pack(fill="x", padx=10, pady=2)


class FFlagsPage(ctk.CTkFrame):
    def __init__(self, parent, cfg):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.cfg = cfg
        self.settings = load_fflags()
        self._active_tab = list(FFLAG_CATEGORIES.keys())[0]

    
        header = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0,
            border_width=1, border_color=BORDER)
        header.pack(fill="x")
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=14)
        lbl(inner, "FAST FLAGS ", font=("Bebas Neue", 28), color=TEXT).pack(side="left")
        lbl(inner, "CONFIGURATION", font=("Bebas Neue", 28), color=ACCENT).pack(side="left")
        btn(inner, "💾 Save & Apply", self._save,
            width=140, fg_color=ACCENT, hover_color=_darken(ACCENT)).pack(side="right", padx=(8, 0))
        btn(inner, "🔄 Reset All", self._reset,
            width=120, fg_color="#2a2a2a", hover_color="#333").pack(side="right")

       
        tab_bar = ctk.CTkFrame(self, fg_color=BG, corner_radius=0,
            border_width=0)
        tab_bar.pack(fill="x")

        
        pill_bg = ctk.CTkFrame(tab_bar, fg_color="#000000", corner_radius=8)
        pill_bg.pack(fill="x", padx=20, pady=10)

        self._tab_buttons = {}
        categories = list(FFLAG_CATEGORIES.keys())
        for i, cat in enumerate(categories):
            is_active = cat == self._active_tab
            tb = ctk.CTkButton(
                pill_bg,
                text=cat,
                font=("Barlow SemiBold", 12),
                fg_color=ACCENT if is_active else "transparent",
                hover_color=_darken(ACCENT) if is_active else "#1e1e1e",
                text_color=TEXT if is_active else MUTED,
                corner_radius=6,
                height=32,
                command=lambda c=cat: self._switch_tab(c),
            )
            tb.pack(side="left", expand=True, fill="x", padx=4, pady=4)
            self._tab_buttons[cat] = tb

       
        self._content_area = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._content_area.pack(fill="both", expand=True, padx=0, pady=0)

        self.widgets = {}
        self._tab_frames = {}
        for category_name, category_data in FFLAG_CATEGORIES.items():
            frame = ctk.CTkScrollableFrame(self._content_area, fg_color="transparent")
            self._tab_frames[category_name] = frame
            for setting_key, setting_data in category_data.items():
                self._render_setting(frame, category_name, setting_key, setting_data)

        self._switch_tab(self._active_tab)

    def _switch_tab(self, name):
        self._active_tab = name
        for cat, frame in self._tab_frames.items():
            frame.pack_forget()
        self._tab_frames[name].pack(fill="both", expand=True, padx=16, pady=(8, 16))
        for cat, tb in self._tab_buttons.items():
            is_active = cat == name
            tb.configure(
                fg_color=ACCENT if is_active else "transparent",
                hover_color=_darken(ACCENT) if is_active else "#1e1e1e",
                text_color=TEXT if is_active else MUTED,
            )

    def _render_setting(self, parent, category, key, data):
        full_key = f"{category}.{key}"
        container = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=8,
            border_width=1, border_color=BORDER)
        container.pack(fill="x", pady=6, padx=4)
        header_row = ctk.CTkFrame(container, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=(12, 4))
        lbl(header_row, data["label"], font=("Barlow SemiBold", 14)).pack(side="left")
        lbl(container, data["desc"], font=("Barlow", 11), color=MUTED,
            wraplength=600, justify="left").pack(anchor="w", padx=15, pady=(0, 10))

        if data["type"] == "toggle":
            saved_value = self.settings.get(full_key, False)
            var = ctk.BooleanVar(value=saved_value)
            self.widgets[full_key] = {"type": "toggle", "var": var, "flags": data["flags"]}
            ctk.CTkSwitch(container, variable=var, text="Enabled",
                onvalue=True, offvalue=False, progress_color=ACCENT,
                button_color=TEXT, fg_color=BORDER,
                font=("Barlow", 12)).pack(anchor="w", padx=15, pady=(0, 12))
        elif data["type"] == "dropdown":
            saved_value = self.settings.get(full_key, data.get("default", list(data["options"].keys())[0]))
            if (
                full_key == "Rendering.lighting_quality"
                and saved_value in FFLAGS_LEGACY_FRM_QUALITY_LABELS
            ):
                saved_value = data.get("default", "Auto")
            if saved_value not in data["options"]:
                saved_value = data.get("default", list(data["options"].keys())[0])
            var = ctk.StringVar(value=saved_value)
            self.widgets[full_key] = {"type": "dropdown", "var": var, "options": data["options"]}
            ctk.CTkOptionMenu(container, variable=var,
                values=list(data["options"].keys()),
                fg_color=BORDER, button_color=ACCENT,
                button_hover_color=_darken(ACCENT),
                dropdown_fg_color=CARD_BG,
                font=("Barlow", 12), width=300).pack(anchor="w", padx=15, pady=(0, 12))

    def _save(self):
        new_settings = {}
        merged_flags = {}
        for key, widget_data in self.widgets.items():
            if widget_data["type"] == "toggle":
                value = widget_data["var"].get()
                new_settings[key] = value
                if value:
                    merged_flags.update(widget_data["flags"])
            elif widget_data["type"] == "dropdown":
                value = widget_data["var"].get()
                new_settings[key] = value
                merged_flags.update(widget_data["options"].get(value, {}))
        save_fflags(new_settings)
        self.settings = new_settings
        success = apply_fflags_to_roblox(merged_flags)
        if success:
            if merged_flags:
                messagebox.showinfo("TurboStrap",
                    f"✓ Applied {len(merged_flags)} fast flags!\n\nRestart Roblox for changes to take effect.")
            else:
                messagebox.showinfo("TurboStrap",
                    "Removed ClientAppSettings overrides.\n\nRestart Roblox so the graphics menu controls quality again.")
        else:
            messagebox.showwarning("TurboStrap",
                "⚠ Settings saved but couldn't find Roblox installation to update ClientAppSettings.")

    def _reset(self):
        if messagebox.askyesno("Reset Flags", "Reset all fast flags to default settings?"):
            self.settings = {}
            save_fflags({})
            for key, widget_data in self.widgets.items():
                if widget_data["type"] == "toggle":
                    widget_data["var"].set(False)
                elif widget_data["type"] == "dropdown":
                    for cat, cat_data in FFLAG_CATEGORIES.items():
                        for setting_key, setting_data in cat_data.items():
                            full_key = f"{cat}.{setting_key}"
                            if full_key == key and "default" in setting_data:
                                widget_data["var"].set(setting_data["default"])
            if apply_fflags_to_roblox({}):
                messagebox.showinfo("TurboStrap",
                    "All flags reset — ClientAppSettings removed.\n\nRestart Roblox to restore normal graphics controls.")
            else:
                messagebox.showinfo("TurboStrap",
                    "All flags reset in TurboStrap. Open Save & Apply once Roblox is installed to clear overrides on disk.")

class CustomFlagsPage(ctk.CTkFrame):
    def __init__(self, parent, cfg):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.cfg = cfg
        self._flags = self._load()
        self._selected = set()

       
        header = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0,
            border_width=1, border_color=BORDER)
        header.pack(fill="x")
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=14)
        lbl(inner, "CUSTOM ", font=("Bebas Neue", 28), color=TEXT).pack(side="left")
        lbl(inner, "FLAGS", font=("Bebas Neue", 28), color=ACCENT).pack(side="left")

        
        toolbar = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        toolbar.pack(fill="x", padx=16, pady=(10, 0))

        btn(toolbar, "➕  Add Flag", self._add_flag,
            width=110, fg_color=ACCENT, hover_color=_darken(ACCENT)).pack(side="left", padx=(0, 6))
        btn(toolbar, "🗑  Delete Selected", self._delete_selected,
            width=140, fg_color="#2a2a2a", hover_color="#333").pack(side="left", padx=(0, 6))
        btn(toolbar, "🗑  Delete All", self._delete_all,
            width=110, fg_color="#2a2a2a", hover_color="#333").pack(side="left", padx=(0, 6))
        btn(toolbar, "📥  Import JSON", self._import_json,
            width=120, fg_color="#2a2a2a", hover_color="#333").pack(side="left", padx=(0, 6))
        btn(toolbar, "📤  Export JSON", self._export_json,
            width=120, fg_color="#2a2a2a", hover_color="#333").pack(side="left")

  
        self._count_lbl = lbl(toolbar, f"Total Flags: {len(self._flags)}",
            font=("Barlow", 11), color=MUTED)
        self._count_lbl.pack(side="right", padx=10)

       
        search_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=6,
            border_width=1, border_color=BORDER)
        search_frame.pack(fill="x", padx=16, pady=10)
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *a: self._refresh_list())
        ctk.CTkEntry(search_frame, textvariable=self._search_var,
            placeholder_text="🔍  Search flags...",
            fg_color="transparent", border_width=0,
            font=("Barlow", 12), height=36).pack(fill="x", padx=10)

   
        col_header = ctk.CTkFrame(self, fg_color=BORDER, corner_radius=0)
        col_header.pack(fill="x", padx=16)
        ctk.CTkLabel(col_header, text="", width=30).pack(side="left", padx=(8, 0))
        ctk.CTkLabel(col_header, text="Flag Name", font=("Barlow SemiBold", 12),
            text_color=MUTED, anchor="w").pack(side="left", fill="x", expand=True, padx=8, pady=6)
        ctk.CTkLabel(col_header, text="Value", font=("Barlow SemiBold", 12),
            text_color=MUTED, anchor="w", width=160).pack(side="left", padx=8)
        ctk.CTkLabel(col_header, text="Actions", font=("Barlow SemiBold", 12),
            text_color=MUTED, width=80).pack(side="right", padx=8)

        
        self._list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent",
            corner_radius=0)
        self._list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 0))

      
        apply_bar = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0,
            border_width=1, border_color=BORDER)
        apply_bar.pack(fill="x")
        lbl(apply_bar, "Changes apply on next Roblox launch.",
            font=("Barlow", 11), color=MUTED).pack(side="left", padx=20, pady=12)
        btn(apply_bar, "💾  Save & Apply", self._save_and_apply,
            width=160, fg_color=ACCENT, hover_color=_darken(ACCENT)).pack(
            side="right", padx=20, pady=10)

        self._refresh_list()

    def _load(self):
       
        path = Path(os.getenv("APPDATA")) / "TurboStrap" / "custom_flags.json"
        custom = {}
        if path.exists():
            try:
                with open(path) as f:
                    custom = json.load(f)
            except Exception:
                pass
    
       
        preset = load_raw_fflags()
        merged = {**preset, **custom} 
        return merged
        
        
        
    def _save(self):
      
        preset_keys = set(load_raw_fflags().keys())
        custom_only = {k: v for k, v in self._flags.items() if k not in preset_keys}
        path = Path(os.getenv("APPDATA")) / "TurboStrap" / "custom_flags.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(custom_only, f, indent=2)

    def _refresh_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        query = self._search_var.get().lower().strip()
        filtered = {k: v for k, v in self._flags.items()
                    if query in k.lower() or query in str(v).lower()}

        if not filtered:
            lbl(self._list_frame, "No flags found. Click '➕ Add Flag' to get started.",
                font=("Barlow", 12), color=MUTED).pack(pady=40)
            self._count_lbl.configure(text=f"Total Flags: {len(self._flags)}")
            return

        for flag_name, flag_value in filtered.items():
            row = ctk.CTkFrame(self._list_frame, fg_color=CARD_BG, corner_radius=6,
                border_width=1, border_color=BORDER)
            row.pack(fill="x", pady=3)

            
            var = ctk.BooleanVar(value=flag_name in self._selected)
            def _on_check(v=var, n=flag_name):
                if v.get():
                    self._selected.add(n)
                else:
                    self._selected.discard(n)
            ctk.CTkCheckBox(row, text="", variable=var, command=_on_check,
                width=30, checkbox_width=16, checkbox_height=16,
                fg_color=ACCENT, hover_color=_darken(ACCENT),
                border_color=BORDER).pack(side="left", padx=(10, 0), pady=10)

            
            name_var = ctk.StringVar(value=flag_name)
            name_entry = ctk.CTkEntry(row, textvariable=name_var,
                fg_color="transparent", border_width=0,
                font=("Consolas", 12), text_color=TEXT)
            name_entry.pack(side="left", fill="x", expand=True, padx=8, pady=6)

         
            val_var = ctk.StringVar(value=str(flag_value))
            val_entry = ctk.CTkEntry(row, textvariable=val_var,
                fg_color="transparent", border_width=0,
                font=("Consolas", 12), text_color=ACCENT, width=160)
            val_entry.pack(side="left", padx=8, pady=6)

           
            def _on_edit(event, old=flag_name, nv=name_var, vv=val_var):
                new_name = nv.get().strip()
                new_val  = vv.get().strip()
                if not new_name:
                    return
                if old in self._flags:
                    del self._flags[old]
                self._flags[new_name] = new_val
                self._save()
            name_entry.bind("<FocusOut>", _on_edit)
            val_entry.bind("<FocusOut>", _on_edit)
            name_entry.bind("<Return>", _on_edit)
            val_entry.bind("<Return>", _on_edit)

           
            btn(row, "✕", lambda n=flag_name: self._delete_one(n),
                width=36, height=28, fg_color="#333", hover_color="#c41213",
                font=("Barlow", 11)).pack(side="right", padx=8, pady=6)

        self._count_lbl.configure(text=f"Total Flags: {len(self._flags)}")

    def _add_flag(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Flag")
        dialog.geometry("420x200")
        dialog.configure(fg_color=BG)
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.lift()

        lbl(dialog, "Flag Name", font=("Barlow SemiBold", 13)).pack(anchor="w", padx=20, pady=(16, 2))
        name_entry = ctk.CTkEntry(dialog, font=("Consolas", 12),
            fg_color=CARD_BG, border_color=BORDER, border_width=1, height=34)
        name_entry.pack(fill="x", padx=20)

        lbl(dialog, "Value", font=("Barlow SemiBold", 13)).pack(anchor="w", padx=20, pady=(10, 2))
        val_entry = ctk.CTkEntry(dialog, font=("Consolas", 12),
            fg_color=CARD_BG, border_color=BORDER, border_width=1, height=34)
        val_entry.pack(fill="x", padx=20)

        def _confirm():
            name = name_entry.get().strip()
            val  = val_entry.get().strip()
            if not name:
                return
            self._flags[name] = val
            self._save()
            self._refresh_list()
            dialog.destroy()

        btn(dialog, "Add Flag", _confirm,
            fg_color=ACCENT, hover_color=_darken(ACCENT)).pack(pady=14)
        name_entry.focus()
        val_entry.bind("<Return>", lambda e: _confirm())

    def _delete_one(self, name):
        if name in self._flags:
            del self._flags[name]
            self._selected.discard(name)
            self._save()
            self._refresh_list()

    def _delete_selected(self):
        if not self._selected:
            messagebox.showinfo("TurboStrap", "No flags selected.")
            return
        if messagebox.askyesno("Delete Selected",
                f"Delete {len(self._selected)} selected flag(s)?"):
            for name in list(self._selected):
                self._flags.pop(name, None)
            self._selected.clear()
            self._save()
            self._refresh_list()

    def _delete_all(self):
        if not self._flags:
            return
        if messagebox.askyesno("Delete All", "Delete ALL custom flags?"):
            self._flags.clear()
            self._selected.clear()
            self._save()
            self._refresh_list()

    def _import_json(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Import Flags JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                messagebox.showerror("Import Failed", "JSON must be a flat key-value object.")
                return
            self._flags.update({k: str(v) for k, v in data.items()})
            self._save()
            self._refresh_list()
            messagebox.showinfo("TurboStrap", f"✓ Imported {len(data)} flags.")
        except Exception as e:
            messagebox.showerror("Import Failed", str(e))

    def _export_json(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            title="Export Flags JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump(self._flags, f, indent=2)
            messagebox.showinfo("TurboStrap", f"✓ Exported {len(self._flags)} flags.")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def _save_and_apply(self):
        self._save()
       
        merged = load_raw_fflags()
        merged.update(self._flags)
        success = apply_fflags_to_roblox(merged)
        if success:
            messagebox.showinfo("TurboStrap",
                f"✓ Applied {len(merged)} total flags ({len(self._flags)} custom).\n\n"
                "Restart Roblox for changes to take effect.")
        else:
            messagebox.showwarning("TurboStrap",
                "⚠ Saved but couldn't find Roblox install to write ClientAppSettings.")
def show_splash(master, accent, version):
    import tkinter as tk
    W, H = 520, 280
    splash = tk.Toplevel(master)
    splash.overrideredirect(True)
    splash.configure(bg="#050505")
    splash.resizable(False, False)
    splash.update_idletasks()
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    x = (sw - W) // 2
    y = (sh - H) // 2
    splash.geometry(f"{W}x{H}+{x}+{y}")
    splash.update_idletasks()
    splash.lift()
    splash.attributes("-topmost", True)
    splash.after(200, lambda: splash.attributes("-topmost", False))

    try:
        response = requests.get("https://fr.lowkey.nichesite.org/splash_updated.jpg", timeout=5)
        img = Image.open(BytesIO(response.content)).resize((W, H), Image.LANCZOS)
    except Exception:
        img = Image.new("RGB", (W, H), "#050505")
    bg_photo = ImageTk.PhotoImage(img)

    canvas = Canvas(splash, width=W, height=H,
        highlightthickness=0, borderwidth=0, bg="#050505")
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)
    canvas.bg_photo = bg_photo

    bx, by = W // 2, H // 2 - 40
    try:
        _splash_img = Image.open(resource_path("turbostrap.png")).resize((100, 100), Image.LANCZOS)
        _splash_photo = ImageTk.PhotoImage(_splash_img)
        canvas.create_image(bx, by, anchor="center", image=_splash_photo)
        canvas._splash_photo = _splash_photo
    except Exception:
        size = 80
        canvas.create_rectangle(bx-size//2, by-size//2, bx+size//2, by+size//2, outline=accent, width=2)
        canvas.create_text(bx, by, text="CE", font=("Bebas Neue", 32), fill=accent)
    
    
    
    canvas.create_text(W//2, H//2+30, text="TurboStrap", font=("Bebas Neue", 34), fill="#f5f5f5")
    canvas.create_text(W//2, H//2+58, text="Roblox Launcher", font=("Barlow", 12), fill="#a0a0a0")
    canvas.create_text(W//2, H//2+78, text=f"v{version}", font=("Barlow Condensed", 11), fill="#777777")
    status_text = canvas.create_text(W//2, H-20, text="Checking for updates…",
        font=("Barlow", 9), fill="#dddddd")
    canvas._status_text = status_text

    def _do_version_check():
        new_ver = check_for_update()
        if new_ver:
            canvas.itemconfig(status_text,
                text=f"⚠  v{new_ver} available!",
                fill="#f59e0b")
        else:
            canvas.itemconfig(status_text, text="✓  Up to date", fill="#00c850")

    threading.Thread(target=_do_version_check, daemon=True).start()
    return splash


    
class TurboStrap(ctk.CTk):
    def __init__(self):
        init_app_icon()
        super().__init__()
        self.cfg = load_config()
        self.tray_icon   = None
        self.roblox_proc = None

        self.title("TurboStrap")
        self.geometry("960x620")
        self.minsize(860, 560)
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        global ACCENT
        ACCENT = self.cfg.get("accent_color", ACCENT)
        self.withdraw()
        self._build()
  
        self.splash = show_splash(self, ACCENT, APP_VERSION)
        self.after(3000, self._end_splash)
        self.iconbitmap(resource_path("turbostrap.ico"))

    def _end_splash(self):
        try:
            if self.splash:
                self.splash.destroy()
        except Exception:
            pass
        self.splash = None
        self.update_idletasks()
        w, h = 960, 620
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.deiconify()
        self.lift()
        self.focus_force()
        self.after(500, self._check_update_and_prompt)

    def _check_update_and_prompt(self):
        def _worker():
            new_ver = check_for_update()
            if new_ver:
                self.after(0, lambda v=new_ver: self._show_update_prompt(v))
        threading.Thread(target=_worker, daemon=True).start()

    def _show_update_prompt(self, v):
        self.lift()
        self.focus_force()
        result = messagebox.askyesno(
            "Update Available 🚀",
            f"A new version of TurboStrap is available!\n\n"
            f"  Current version:  v{APP_VERSION}\n"
            f"  Latest version:    v{v}\n\n"
            f"Would you like to download the latest version?"
        )
        if result:
            webbrowser.open("https://github.com/turbostrap/Turbostrap-Launcher/releases")

   

    def _build(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.pages = {
            "LAUNCH":   LaunchPage(self.content, self.cfg),
            "SETTINGS": SettingsPage(self.content, self.cfg, self._refresh),
            "THEME":    ThemePage(self.content, self.cfg, self._rebuild),
            "FFLAGS":   FFlagsPage(self.content, self.cfg),
            "CUSTOM": CustomFlagsPage(self.content, self.cfg),
            "LOGS":     LogsPage(self.content),
            "ABOUT":    AboutPage(self.content),
        }
        self.sidebar = Sidebar(self, self._nav)
        self.sidebar.pack(side="left", fill="y")
        self.divider = ctk.CTkFrame(self, width=1, fg_color="#1a1a1a", corner_radius=0)
        self.divider.pack(side="left", fill="y")
        self.content.pack(side="left", fill="both", expand=True)
        self._show("LAUNCH")

    def _show(self, name):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[name].pack(fill="both", expand=True)

    def _nav(self, name):
        self._show(name)

    def _refresh(self):
        self.pages["LAUNCH"].refresh()
    def _rebuild(self):
        global ACCENT
        ACCENT = self.cfg.get("accent_color", ACCENT)
        for page in self.pages.values():
            page.destroy()
        self.content.destroy()
        self.sidebar.destroy()
        self.divider.destroy()
        self._build()
        self._show("THEME")
    def go_to_tray(self, roblox_proc):
        self.roblox_proc = roblox_proc
        self.withdraw()
        self._create_tray_icon()
        threading.Thread(target=self._wait_for_roblox_exit, daemon=True).start()

    def _wait_for_roblox_exit(self):
        try:
            self.roblox_proc.wait()
        except Exception:
            pass
        self.after(0, self._restore_from_tray)

    def _create_tray_icon(self):
        if self.tray_icon is not None:
            return
        try:
            image = Image.open(resource_path("turbostrap.ico"))
        except Exception:
            image = Image.new("RGB", (32, 32), color=(30, 30, 30))
        menu = (
            TrayItem("Show TurboStrap", lambda icon, item: self._restore_from_tray()),
            TrayItem("Exit",            lambda icon, item: self._exit_from_tray()),
        )
        self.tray_icon = pystray.Icon("TurboStrap", image, "TurboStrap", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_from_tray(self):
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None
        self.deiconify()
        self.focus_force()
        try:
            self.pages["LAUNCH"].launch_btn.configure(state="normal", text="▶  LAUNCH ROBLOX")
        except Exception:
            pass

    def _exit_from_tray(self):
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None
        self.after(0, self.destroy)

    def _on_close(self):
        if self.roblox_proc and self.roblox_proc.poll() is None:
            self.go_to_tray(self.roblox_proc)
        else:
            self.destroy()


if __name__ == "__main__":
    app = TurboStrap()
    app.mainloop()
