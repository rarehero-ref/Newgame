# -*- coding: utf-8 -*-
import time
import sys
import random

def yoz(matn, tezlik=0.03):
    """Harflarni ketma-ket chiqarish"""
    for h in matn:
        sys.stdout.write(h)
        sys.stdout.flush()
        time.sleep(tezlik)
    print("")

def boshlash():
    yoz("🏰 Siz qadimiy va sirli 'Xazinalar G'ori' oldidasiz.")
    time.sleep(1)
    yoz("Afsonaga ko'ra, g'or ichida ulkan boyliklar yashiringan.")
    time.sleep(1)
    yoz("Sizning vazifangiz - xazinani topish va tirik qolish!")
    print("-" * 40)

def oyin():
    player = {
        "joy": "kirish",
        "inventar": [],
        "hp": 100
    }

    xonalar = {
        "kirish": {
            "tavsif": "Siz g'or kirishidasiz. Shimolda yo'lak ko'rinmoqda.",
            "chiqishlar": {"shimol": "yolak"},
            "buyum": None
        },
        "yolak": {
            "tavsif": "Tor yo'lak. Sharqda eshik, g'arbda kichik xona.",
            "chiqishlar": {"sharq": "xazina", "g'arb": "kichik_xona", "janub": "kirish"},
            "buyum": None
        },
        "kichik_xona": {
            "tavsif": "Chang bosgan xona. Burchakda eski sandiq bor.",
            "chiqishlar": {"sharq": "yolak"},
            "buyum": "mash'al"
        },
        "xazina": {
            "tavsif": "Qulfli temir eshik. Uni ochish uchun kalit kerak.",
            "chiqishlar": {"g'arb": "yolak"},
            "buyum": "kalit"
        }
    }

    game_over = False
    while not game_over and player["hp"] > 0:
        xona = xonalar[player["joy"]]
        yoz(xona["tavsif"])
        if xona["buyum"] and xona["buyum"] not in player["inventar"]:
            yoz(f"Yerda {xona['buyum']}ni ko'rdingiz.")

        buyruq = input("\n👉 Buyruq kiriting (bor/olish/inventar/chiqish): ").lower().split()
        if not buyruq: 
            continue

        if buyruq[0] in ["bor", "yur"]:
            if len(buyruq) < 2:
                yoz("Qayerga borishni ayting!")
                continue
            yon = buyruq[1]
            if yon in xona["chiqishlar"]:
                yangi = xona["chiqishlar"][yon]
                if yangi == "xazina" and "kalit" not in player["inventar"]:
                    yoz("🚪 Eshik qulflangan! Avval kalit kerak.")
                else:
                    player["joy"] = yangi
                    if player["joy"] == "xazina":
                        yoz("🎉 Siz xazina xonasiga kirdingiz va g'alaba qozondingiz!")
                        game_over = True
            else:
                yoz("Bu tomonda yo'l yo'q.")

        elif buyruq[0] == "olish":
            if len(buyruq) < 2:
                yoz("Nimani olishni ayting!")
                continue
            buyum = buyruq[1]
            if xona["buyum"] == buyum:
                player["inventar"].append(buyum)
                xona["buyum"] = None
                yoz(f"✅ Siz {buyum}ni oldingiz.")
                if buyum == "mash'al":
                    yoz("Mash'al yordamida yo'lakdan kalitni ko'rdingiz!")
                    xonalar["yolak"]["buyum"] = "kalit"
            else:
                yoz("Bu yerda bunday buyum yo'q.")

        elif buyruq[0] == "inventar":
            if player["inventar"]:
                yoz("🎒 Sizda: " + ", ".join(player["inventar"]))
            else:
                yoz("Inventar bo'sh.")

        elif buyruq[0] in ["chiqish", "exit"]:
            yoz("O'yin tugadi.")
            game_over = True

        else:
            yoz("Noto'g'ri buyruq.")

    if player["hp"] <= 0:
        yoz("💀 Siz halok bo'ldingiz!")

if __name__ == "__main__":
    boshlash()
    oyin()
