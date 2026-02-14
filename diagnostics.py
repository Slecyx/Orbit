from manager import OrbitManager
import sys

def debug():
    print("ORBIT Diagnostik Başlatılıyor...")
    manager = OrbitManager()
    print("Uygulamalar taranıyor (bu biraz zaman alabilir)...")
    apps = manager.refresh_apps()
    
    if not apps:
        print("KRİTİK HATA: Hiç uygulama bulunamadı!")
        return

    print(f"Başarılı! Toplam {len(apps)} uygulama bulundu.")
    
    # Kaynaklara göre sayalım
    counts = {}
    for app in apps:
        counts[app.source.value] = counts.get(app.source.value, 0) + 1
    
    for source, count in counts.items():
        print(f" - {source}: {count} uygulama")

    print("\nÖrnek Uygulamalar:")
    for app in apps[:5]:
        print(f" [{app.source.value}] {app.name} ({app.id})")

if __name__ == "__main__":
    debug()
