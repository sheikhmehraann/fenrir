# Fenrir

An LK patcher to bypass secure boot checks, spoof lock state, and force boot state to green on MediaTek Dimensity devices.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)

---

## 📱 Supported Devices

| Device | Codename | Platform | Tested |
| :--- | :---: | :---: | :---: |
| **Infinix GT 20 Pro** | `X6871` | Dimensity 8200 (`mt6895`) | Yes 🟢 |
| **Infinix ZERO 40 5G** | `X6861` | Dimensity 8200 (`mt6878`) | Yes 🟢 |
| Nothing Phone (2a) | `Pacman` | Dimensity 7200 Ultra | Yes 🟢 |
| Nothing Phone (2a) Plus | `PacmanPro` | Dimensity 7350 Pro | Yes 🟢 |
| CMF Phone 1 | `Tetris` | Dimensity 7300 | Yes 🟢 |
| Tecno Pova 4 | `LG7n` | Helio G99 | Yes 🟢 |
| Tecno Pova 4 Pro | `LG8n` | Helio G99 | Yes 🟢 |
| Tecno Pova 5 | `LH7n` | Helio G99 | Yes 🟢 |
| itel RS4 | `S666LN` | Helio G99 | Yes 🟢 |
| Redmi K70E / POCO X6 Pro 5G | `duchamp` | Dimensity 8300 Ultra | Yes 🟢 |
| Redmi Turbo 4 / POCO X7 Pro | `rodin` | Dimensity 8400 | Yes 🟢 |
| Redmi Note 11T Pro / POCO X4 GT | `xaga` | Dimensity 8100 | Yes 🟢 |
| Xiaomi 12T | `plato` | Dimensity 8100 Ultra | Yes 🟢 |
| Lenovo IdeaTab Pro 12.7 | `peridotl` | Dimensity 8300 | Yes 🟢 |
| Zinwa Q25 | `Q25` | Dimensity Platform | Yes 🟢 |

---

## 🛠️ Usage

### Prerequisites
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Build
To generate the patched LK image for your target device:

#### On Linux / macOS:
```bash
./build.sh <codename>
```

#### On Windows:
```cmd
python build.py <codename>
```

*(For example, `python build.py X6861` or `python build.py X6871`).*

The patched bootloader image will be saved as `lk.patched` in the root directory.

### Flash
Flash the generated image to both slots via Fastboot:

```bash
fastboot flash lk_a lk.patched
fastboot flash lk_b lk.patched
fastboot reboot
```

Alternatively, use the automated flashing script:
```bash
python flash.py
```

---

## 🔍 How It Works

Fenrir exploits a structural logic vulnerability in MediaTek bootloader implementations. When a device's security configuration (`seccfg`) is unlocked, the MediaTek Preloader skips cryptographic verification of the `bl2_ext` partition.

Because `bl2_ext` executes directly at **EL3** (the highest ARM64 Exception Level), patching `bl2_ext` allows complete takeover of subsequent boot stages (`TEE`, `GenieZone`, `LK`, `Linux Kernel`).

Fenrir applies surgical instruction replacements to disable AVB verification policy checks (`sec_get_vfy_policy`), spoof `ro.boot.verifiedbootstate` to **`green`**, and force `ro.boot.flash.locked = 1` (`LKS_LOCK`) to pass Play Store Integrity & SafetyNet checks natively.

---

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file for details.
