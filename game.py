# -*- coding: utf-8 -*-
import time
import sys

def yoz(matn):
    """Harflarni birma-bir, chiroyli chiqarish uchun funksiya"""
    for harf in matn:
        sys.stdout.write(harf)
        sys.stdout.flush()
        time.sleep(0.04)
    print("")

def boshlash():
    """O'yin boshlanishi va tanishtiruv"""
    yoz("Siz qadimiy va sirli 'Xazinalar G\'ori' oldidasiz.")
    time.sleep(1)
    yoz("Afsonalarga ko'ra, bu g'orning ichida bitmas-tuganmas boyliklar yashiringan.")
    time.sleep(1)
    yoz("Sizning maqsadingiz - g'orga kirib, xazinani topish. Olg'a!")
    print("-" * 30)

def oyin():
    """Asosiy o'yin logikasi"""
    
    # O'yinchi holati
    player = {
        'joylashuv': 'kirish',
        'inventar': []
    }

    # G'or xaritasini (xonalar) tuzamiz
    xonalar = {
        'kirish': {
            'tavsif': "Siz g'orning kirish qismidasiz. Ichkaridan salqin havo esmoqda.\nOldinda qorong'u yo'lak ko'rinmoqda. Shimolda yo'lak bor.",
            'chiqishlar': {'shimol': 'yolak'},
            'buyum': None
        },
        'yolak': {
            'tavsif': "Siz uzun va tor yo'lakdasiz. Devorlar nam va silliq.\nSharqda bir eshik ko'rinmoqda, g'arbda esa kichikroq o'tish joyi bor.",
            'chiqishlar': {'sharq': 'xazina_xonasi', 'g\'arb': 'kichik_xona', 'janub': 'kirish'},
            'buyum': None
        },
        'kichik_xona': {
            'tavsif': "Bu kichkina, chang bosgan xona. Burchakda eski sandiq turibdi.\nBu yerda 'mash'al' borga o'xshaydi.",
            'chiqishlar': {'sharq': 'yolak'},
            'buyum': 'mash\'al'
        },
        'xazina_xonasi': {
            'tavsif': "Siz og'ir, temir eshik oldidasiz. Eshik qulflangan.\nUni ochish uchun 'kalit' kerak.",
            'chiqishlar': {'g\'arb': 'yolak'},
            'buyum': 'kalit' # Bu shartli, eshikni ochgandan keyin olinadi
        }
    }

    game_over = False
    while not game_over:
        hozirgi_xona = xonalar[player['joylashuv']]
        
        # Hozirgi joylashuv tavsifi
        yoz(hozirgi_xona['tavsif'])
        time.sleep(1)

        # Xonadagi buyumni tekshirish
        if hozirgi_xona['buyum'] and hozirgi_xona['buyum'] not in player['inventar']:
             yoz(f"Siz yerda yotgan {hozirgi_xona['buyum']}ni ko'rdingiz.")

        # Foydalanuvchi buyrug'ini qabul qilish
        buyruq = input("\nNima qilasiz? (Masalan: 'bor shimol', 'olish mash\'al', 'inventar')\n> ").lower().strip().split()

        if not buyruq:
            yoz("Hech qanday buyruq kiritmadingiz.")
            continue

        harakat = buyruq[0]

        # Harakatni qayta ishlash
        if harakat in ['bor', 'yur', 'ket']:
            if len(buyruq) > 1:
                yonalish = buyruq[1]
                if yonalish in hozirgi_xona['chiqishlar']:
                    # Xazina xonasiga kirish sharti
                    if hozirgi_xona['chiqishlar'][yonalish] == 'xazina_xonasi' and 'kalit' not in player['inventar']:
                        yoz("Eshik qulflangan! Avval kalitni topishingiz kerak.")
                        # Kichik maslahat
                        if 'mash\'al' in player['inventar']:
                            yoz("Maslahat: Mash'alingiz bilan qorong'u joylarni yaxshiroq tekshirib ko'ring...")
                        else:
                            yoz("Atrof juda qorong'i, ba'zi narsalarni ko'rmayotgan bo'lishingiz mumkin.")
                    else:
                        player['joylashuv'] = hozirgi_xona['chiqishlar'][yonalish]
                        if player['joylashuv'] == 'xazina_xonasi':
                            yoz("\nSiz kalit bilan eshikni ochib, xazina xonasiga kirdingiz!")
                            yoz("Xona oltin va qimmatbaho toshlar bilan to'la! Siz g'alaba qozondingiz!")
                            game_over = True
                else:
                    yoz(f"Bu yerda {yonalish}ga yo'l yo'q.")
            else:
                yoz("Qayerga borishni aniq ayting (masalan, 'bor shimol').")
        
        elif harakat == 'olish':
            if len(buyruq) > 1:
                buyum = buyruq[1]
                if hozirgi_xona['buyum'] == buyum:
                    player['inventar'].append(buyum)
                    hozirgi_xona['buyum'] = None # Buyum olingandan keyin xonadan yo'qoladi
                    yoz(f"Siz {buyum}ni oldingiz.")

                    # Kalitni topish sharti
                    if buyum == 'mash\'al':
                        yoz("Endi qorong'u joylarni ham ko'ra olasiz! Yo'lakka qaytib, yaxshilab atrofga qarang.")
                        # Kalitni yo'lakka "joylashtiramiz"
                        xonalar['yolak']['buyum'] = 'kalit'
                        xonalar['yolak']['tavsif'] += "\nMash'al yorug'ida devordagi yoriqdan 'kalit' yaltirab ko'rindi!"

                else:
                    yoz(f"Bu yerda bunday buyum yo'q.")
            else:
                yoz("Nimani olishni aniq ayting (masalan, 'olish mash\'al').")

        elif harakat == 'inventar':
            if player['inventar']:
                yoz("Sizning inventaringiz: " + ", ".join(player['inventar']))
            else:
                yoz("Sizning inventaringiz bo'sh.")
        
        elif harakat in ['chiqish', 'exit']:
            yoz("O'yindan chiqdingiz. Yana qaytib keling!")
            game_over = True
        
        else:
            yoz("Tushunarsiz buyruq. Mumkin bo'lgan buyruqlar: 'bor', 'olish', 'inventar', 'chiqish'.")
        
        print("-" * 30)

if __name__ == "__main__":
    boshlash()
    oyin()

