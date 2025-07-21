# 🖼️ Cum să încarci imagini în AI Photo Editor

## 🎯 **3 Modalități de încărcare a imaginilor:**

### 1. **📁 Butonul "Încarcă Imagine"**
- Apasă butonul din toolbar
- Selectează imaginea din file dialog
- ✅ Metoda cea mai simplă

### 2. **⌨️ Copiază și Lipește (Ctrl+V)**
- În Windows Explorer, fă click dreapta pe o imagine
- Selectează "Copy as path" sau "Copiază calea"
- În aplicație apasă `Ctrl+V`
- ✅ Foarte rapid pentru imagini din sistemul de fișiere

### 3. **🖱️ Butonul "Paste Path"**
- Copiază path-ul unei imagini în clipboard
- Apasă butonul "Paste Path (Ctrl+V)" din toolbar
- ✅ Alternativă la shortcut-ul de keyboard

## 🔧 **De ce nu funcționează drag & drop classic?**

Drag & drop-ul tradițional are probleme de compatibilitate între:
- `customtkinter` (tema modernă)
- `tkinterdnd2` (biblioteca de drag & drop)
- Windows WSL (mediul de dezvoltare)

## 💡 **Tips pentru încărcare rapidă:**

### Pentru Windows:
```
1. Navighează la o imagine în Explorer
2. Shift + Click dreapta → "Copy as path"
3. În aplicație: Ctrl+V
```

### Pentru Linux/WSL:
```
1. ls /path/to/image.jpg
2. Selectează și copiază path-ul complet
3. În aplicație: Ctrl+V
```

## 🎨 **Formate suportate:**
- ✅ PNG (cu transparență)
- ✅ JPEG/JPG
- ✅ GIF (static și animat)
- ✅ BMP
- ✅ TIFF
- ✅ WEBP

## 🚀 **Workflow recomandat:**
1. **Copiază path-ul** imaginii din file manager
2. **Ctrl+V** în aplicație
3. **Testează funcțiile AI** (Analyze Image funcționează perfect)
4. **Salvează rezultatul** cu butonul Save

Această soluție este mai robustă și funcționează consistent în toate mediile!
