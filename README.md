
<div align="center">

# 🛰️ ORBIT
## Universal Linux Package Manager
### Evrensel Linux Paket Yöneticisi

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![GTK 4](https://img.shields.io/badge/GTK-4.0-green.svg?style=for-the-badge&logo=gtk&logoColor=white)](https://www.gtk.org/)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://kernel.org)

[English](#english) | [Türkçe](#türkçe)

</div>

---

<a name="english"></a>
## 🇬🇧 English

### Overview
**Orbit** is a modern, unified application store and package manager for Linux systems. It aggregates applications from multiple sources (Flatpak, Snap, Native Package Managers like APT/Pacman/DNF, AppImage) into a single, beautiful interface.

Designed with **GTK4** and **Libadwaita**, Orbit provides a premium user experience that feels at home on GNOME and other modern desktop environments.

### ✨ Key Features
- **Unified Store**: Browse, install, and manage apps from Flatpak, Snap, and system repositories in one place.
- **Smart Search**: Real-time search that queries both local apps and online repositories (Flatpak/Snap) simultaneously.
- **Visual Statistics**: View detailed breakdowns of your installed packages with interactive charts.
- **Batch Operations**: Update or remove multiple applications at once with a single click.
- **Backup & Restore**: Export your installed application list to a JSON file and restore it on another machine.
- **Modern UI**: Features a glassmorphism-inspired design, smooth animations, and a responsive layout.
- **Advanced Filtering**: Filter apps by source (e.g., show only Flatpak), status (installed/updates), or category.
- **AppImage Support**: Automatically detects and manages AppImages from your standard directories.

### 🚀 Installation

#### Prerequisites
Orbit requires Python 3.10+, GTK4, and Libadwaita.

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 python3-pip
```

**Fedora:**
```bash
sudo dnf install python3 python3-gobject gtk4 libadwaita python3-notify2
```

**Arch Linux:**
```bash
sudo pacman -S python python-gobject gtk4 libadwaita python-notify2
```

#### Quick Start
Clone the repository and run the application:

```bash
git clone https://github.com/Slecyx/Orbit.git
cd Orbit
pip install -r requirements.txt
python3 main.py
```

### 🎮 Usage

1.  **Search & Install**: 
    - Type in the search bar to filter installed apps.
    - Press **Enter** to search online repositories (Flatpak/Snap).
    - Click any result and hit **Install**.

2.  **Manage**:
    - Right-click or select an app to view details.
    - Use the **Filter** button in the header to narrow down the list.
    - Go to **Menu > Statistics** to see your system overview.

3.  **Personalize**:
    - Open **Menu > Settings** to change themes (Light/Dark/System) or enable **Compact Mode**.

### 🤝 Contributing
We welcome contributions! Please feel free to submit a Pull Request.

---

<a name="türkçe"></a>
## 🇹🇷 Türkçe

### Genel Bakış
**Orbit**, Linux sistemleri için geliştirilmiş modern ve birleşik bir uygulama mağazası ve paket yöneticisidir. Flatpak, Snap, Yerel Paket Yöneticileri (APT/Pacman/DNF) ve AppImage dahil olmak üzere farklı kaynaklardan gelen uygulamaları tek bir güzel arayüzde toplar.

**GTK4** ve **Libadwaita** ile tasarlanan Orbit, GNOME ve modern masaüstü ortamlarıyla uyumlu, "premium" bir kullanıcı deneyimi sunar.

### ✨ Temel Özellikler
- **Birleşik Mağaza**: Flatpak, Snap ve sistem depolarındaki tüm uygulamaları tek bir yerden arayın, kurun ve yönetin.
- **Akıllı Arama**: Hem kurulu uygulamalarda hem de çevrimiçi depolarda (Flatpak/Snap) aynı anda, gerçek zamanlı arama yapın.
- **Görsel İstatistikler**: Kurulu paketlerinizi interaktif grafiklerle detaylı bir şekilde analiz edin.
- **Toplu İşlemler**: Tek tıkla tüm uygulamaları güncelleyin veya birden fazla uygulamayı aynı anda kaldırın.
- **Yedekleme ve Geri Yükleme**: Kurulu uygulama listenizi JSON formatında dışa aktarın ve başka bir bilgisayarda geri yükleyin.
- **Modern Arayüz**: Glassmorphism efektleri, yumuşak animasyonlar ve duyarlı tasarımıyla göz alıcı bir deneyim.
- **Gelişmiş Filtreleme**: Uygulamaları kaynağına (örn. sadece Flatpak), durumuna (kurulu/güncelleme) veya kategorisine göre filtreleyin.
- **AppImage Desteği**: Standart klasörlerinizdeki AppImage dosyalarını otomatik olarak algılar ve yönetir.

### 🚀 Kurulum

#### Gereksinimler
Orbit; Python 3.10+, GTK4 ve Libadwaita gerektirir.

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 python3-pip
```

**Fedora:**
```bash
sudo dnf install python3 python3-gobject gtk4 libadwaita python3-notify2
```

**Arch Linux:**
```bash
sudo pacman -S python python-gobject gtk4 libadwaita python-notify2
```

#### Hızlı Başlangıç
Depoyu klonlayın ve uygulamayı çalıştırın:

```bash
git clone https://github.com/Slecyx/Orbit.git
cd Orbit
pip install -r requirements.txt
python3 main.py
```

### 🎮 Kullanım

1.  **Arama ve Kurulum**: 
    - Arama çubuğuna yazarak kurulu uygulamaları anında filtreleyin.
    - Mağazalarda arama yapmak için **Enter** tuşuna basın.
    - Bir sonuca tıklayın ve **Install** (Kur) butonuna basın.

2.  **Yönetim**:
    - Detayları görmek için bir uygulamaya tıklayın.
    - Üst çubuktaki **Filtre** butonunu kullanarak listeyi daraltın.
    - Sistem genel görünümü için **Menü > İstatistikler** yolunu izleyin.

3.  **Kişiselleştirme**:
    - Temayı değiştirmek (Açık/Koyu) veya **Kompakt Mod**'u açmak için **Menü > Ayarlar**'a gidin.

### 🤝 Katkıda Bulunma
Katkılarınızı bekliyoruz! Hata bildirmek veya özellik eklemek için Pull Request göndermekten çekinmeyin.

---

<div align="center">

**Developed with ❤️ by [Slecyx](https://github.com/Slecyx)**

2026 © All Rights Reserved

</div>
