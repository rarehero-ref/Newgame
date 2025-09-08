# main.py
# -*- coding: utf-8 -*-
__version__ = "1.0.0"

import random
import time
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

# Minimal Kivy styling with a simple layout
KV = '''
<RootWidget>:
    orientation: 'vertical'
    padding: 8
    spacing: 8

    ScrollView:
        size_hint_y: 0.82
        do_scroll_x: False
        do_scroll_y: True

        Label:
            id: output
            text: root.display_text
            text_size: self.width, None
            size_hint_y: None
            valign: 'top'
            halign: 'left'
            markup: True
            padding: 6, 6
            size: (self.width, self.texture_size[1])

    BoxLayout:
        size_hint_y: 0.10
        spacing: 8

        TextInput:
            id: cmd_input
            multiline: False
            hint_text: "Masalan: bor shimol  yoki olish mash'al"
            on_text_validate: root.on_enter(self.text)
        
        Button:
            text: "Yuborish"
            size_hint_x: 0.28
            on_press: root.on_enter(cmd_input.text)
'''

# Game logic class (text engine)
class GameEngine:
    def __init__(self, output_callback):
        self.output = output_callback
        self.reset_game()

    def reset_game(self):
        # Player state
        self.player = {
            'joylashuv': 'kirish',
            'inventar': [],
            'hp': 20,
            'max_hp': 20,
            'food': 1,
            'achievements': set()
        }

        # Randomize map layout a bit each game
        rooms = {
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
                'buyum': "mash'al"
            },
            'xazina_xonasi': {
                'tavsif': "Siz og'ir, temir eshik oldidasiz. Eshik qulflangan.\nUni ochish uchun 'kalit' kerak.",
                'chiqishlar': {'g\'arb': 'yolak'},
                'buyum': 'kalit'  # Eshikni ochgandan keyin olinadi
            },
            # Qo'shimcha xonalar—tasodifiy qo'shimchalar
            'tuzoq': {
                'tavsif': "Bu xona tuzoqli ko'rinadi. Ehtiyot bo'ling — er osti daryosi tovushi eshitiladi.",
                'chiqishlar': {'sharq': 'yolak'},
                'buyum': None
            },
            'kutubxona': {
                'tavsif': "Eski kitoblar to'la kutubxona. Sahifalar orasida kod yoki jumboq yashiringan bo'lishi mumkin.",
                'chiqishlar': {'g\'arb': 'yolak'},
                'buyum': 'jumboq_qismi'
            }
        }

        # Har safar xaritaga ehtimoliy yangi xonani qo'shamiz
        extra_rooms = ['tuzoq', 'kutubxona']
        if random.random() < 0.7:
            rooms.update({k: rooms[k] for k in extra_rooms})

        self.rooms = rooms
        self.game_over = False
        self.turns = 0

        self.output("[b]Xazinalar G'ori (Kivy) — O'yin boshlandi![/b]\n")
        self.describe_current_room()

    def describe_current_room(self):
        r = self.rooms[self.player['joylashuv']]
        text = r['tavsif']
        # Agar xona buyumga ega bo'lsa va inventarda bo'lmasa
        if r.get('buyum') and r['buyum'] not in self.player['inventar']:
            text += f"\nSiz yerda yotgan [i]{r['buyum']}[/i]ni ko'rdingiz."
        self.output(text)

    def tick(self):
        # Har 5 turganda ozgina tonus pasayishi yoki random hodisa
        self.turns += 1
        if self.turns % 6 == 0:
            if self.player['food'] > 0:
                self.player['food'] -= 1
                self.output("Siz ozginasiga ovqat yeding. (food -1)")
            else:
                self.player['hp'] -= 2
                self.output("Ochlik tufayli sog'lig'ingiz pasaymoqda (-2 HP).")
        if self.player['hp'] <= 0:
            self.output("[color=ff0000]Siz mag'lub bo'ldingiz. O'yin tugadi.[/color]")
            self.game_over = True

    def handle(self, raw_cmd):
        if self.game_over:
            self.output("O'yin tugagan — qayta boshlash uchun 'restart' yozing.")
            return

        cmd = raw_cmd.lower().strip()
        if not cmd:
            self.output("Hech qanday buyruq kiritilmadi.")
            return

        parts = cmd.split()
        verb = parts[0]

        if verb in ['bor', 'yur', 'ket']:
            if len(parts) < 2:
                self.output("Qayerga borishni aniqlang (masalan: 'bor shimol').")
                return
            direction = parts[1]
            cur = self.rooms[self.player['joylashuv']]
            if direction in cur['chiqishlar']:
                dest = cur['chiqishlar'][direction]
                # Agar eshik xazina va kalit yo'q bo'lsa
                if dest == 'xazina_xonasi' and 'kalit' not in self.player['inventar']:
                    self.output("Eshik qulflangan! Avval kalit toping.")
                    if 'mash'al' in self.player['inventar']:
                        self.output("Maslahat: Mash'alingiz bilan devor yoriqlarini tekshiring.")
                    return
                self.player['joylashuv'] = dest
                self.output(f"Siz {direction}ga — {dest}ga bordingiz.")
                # Tasodifiy dushman paydo bo'lishi imkoniyati
                if random.random() < 0.25:
                    self.encounter_enemy()
                else:
                    self.describe_current_room()
            else:
                self.output("Bu yerda shu yo'nalish yo'q.")
        elif verb == 'olish':
            if len(parts) < 2:
                self.output("Nimani olishni aniqlang (masalan: 'olish mash'al').")
                return
            item = " ".join(parts[1:])
            cur = self.rooms[self.player['joylashuv']]
            if cur.get('buyum') == item:
                self.player['inventar'].append(item)
                cur['buyum'] = None
                self.output(f"Siz {item}ni oldingiz.")
                # Maxsus hodisalar
                if item == "mash'al":
                    self.output("Endi qorong'u joylarni ko'ra olasiz! Yo'lakni qayta tekshiring.")
                    # mash'al keyin yolakda kalit paydo bo'lishi mumkin
                    if 'yolak' in self.rooms:
                        self.rooms['yolak']['buyum'] = 'kalit'
                        self.rooms['yolak']['tavsif'] += "\nMash'al yorug'ida devordagi yoriqdan bir narsa yaltiradi."
                if item == 'jumboq_qismi':
                    self.player['achievements'].add('jumboq_topildi')
                    self.output("Siz jumboq bo'lakini topdingiz — yutuq: Jumboq bo'lagi.")
            else:
                self.output("Bu yerda bunday buyum yo'q.")
        elif verb == 'inventar':
            inv = ", ".join(self.player['inventar']) or "bo'sh"
            self.output(f"Sizning inventaringiz: {inv}\nHP: {self.player['hp']}/{self.player['max_hp']}  Food: {self.player['food']}")
        elif verb == 'ich':
            # ich = ovqat
            if 'ovqat' in self.player['inventar']:
                self.player['inventar'].remove('ovqat')
                self.player['food'] += 2
                self.player['hp'] = min(self.player['max_hp'], self.player['hp'] + 3)
                self.output("Siz ovqat yeding: HP +3, food +2")
            else:
                self.output("Sizda ovqat yo'q.")
        elif verb in ['jang', 'urish']:
            # oddiy jang: dushman random qarama-qarshi
            self.start_combat()
        elif verb == 'qidir' or verb == 'tekshir':
            # Tekshirish: mash'al bilan qo'shimcha narsalar ko'rinadi
            if 'mash\'al' in self.player['inventar']:
                # mash'al bilan qo'shimcha topish imkoniyati
                if random.random() < 0.6 and self.rooms[self.player['joylashuv']].get('buyum'):
                    self.output("Mash'al yordamida bir narsani topdingiz!")
                else:
                    # kichik sovg'alar
                    found = random.choice(['ovqat', 'hech narsa', 'eski tangacha'])
                    if found == 'hech narsa':
                        self.output("Qidiruv natijasi: hech narsa topilmadi.")
                    else:
                        if found not in self.player['inventar']:
                            self.player['inventar'].append(found)
                            self.output(f"Siz {found}ni topdingiz va inventarga qo'shdingiz.")
                        else:
                            self.output("Siz shu narsani allaqachon bilasiz.")
            else:
                self.output("Atrof qorong'i — mash'al kerak.")
        elif verb in ['chiqish', 'exit', 'quit']:
            self.output("O'yindan chiqdingiz. Yana kelavering!")
            self.game_over = True
        elif verb == 'restart':
            self.output("O'yin qayta boshlanmoqda...")
            Clock.schedule_once(lambda dt: self.reset_game(), 0.2)
        elif verb == 'yutuqlar':
            ach = ", ".join(self.player['achievements']) or "yo'q"
            self.output(f"Yutuqlaringiz: {ach}")
        else:
            self.output("Buyruq tushunarsiz. Mumkin: bor, olish, inventar, jang, qidir, ich, restart, chiqish")

        # Har harakatdan keyin vaqt o'tadi
        self.tick()

    def encounter_enemy(self):
        # sodda dushman logikasi
        enemy = random.choice([
            {'nom': 'qaroqchi', 'hp': 6, 'damage': 3},
            {'nom': 'ilon', 'hp': 4, 'damage': 2},
            {'nom': "ma'lumotsiz maxluq", 'hp': 5, 'damage': 2}
        ])
        self.output(f"[color=ff3333]Sizga {enemy['nom']} hujum qildi![/color]")
        # Kengaytirilgan jang: so'rov kerak, ammo biz foydalanuvchidan 'jang' buyrug'i kutamiz.
        # Avval qisqacha vaqtincha effekt: o'yinchi avtomatik hujumni boshlaydi
        self.resolve_combat(enemy)

    def start_combat(self):
        # foydalanuvchi 'jang' deb yozganda, biz random dushman yaratamiz
        enemy = random.choice([
            {'nom': 'qaroqchi', 'hp': 6, 'damage': 3},
            {'nom': 'ilon', 'hp': 4, 'damage': 2},
            {'nom': "ma'lumotsiz maxluq", 'hp': 5, 'damage': 2}
        ])
        self.output(f"Siz jangga kirishdingiz: {enemy['nom']} bilan!")
        self.resolve_combat(enemy)

    def resolve_combat(self, enemy):
        # Soddalashtirilgan navbatli jang
        while enemy['hp'] > 0 and self.player['hp'] > 0:
            # O'yinchi hujumi
            player_hit = random.randint(1, 5)
            enemy['hp'] -= player_hit
            self.output(f"Siz {enemy['nom']}ga {player_hit} zarar berdingiz. (dushman HP: {max(0, enemy['hp'])})")
            if enemy['hp'] <= 0:
                self.output(f"[b]{enemy['nom']} mag'lub etildi![/b]")
                # sovrin: ehtimol ovqat yoki tangacha
                loot = random.choice(['ovqat', 'hech narsa', 'eski tangacha'])
                if loot != 'hech narsa':
                    self.player['inventar'].append(loot)
                    self.output(f"Siz {loot} topdingiz.")
                # yutuq texnika
                self.player['achievements'].add(f"{enemy['nom']}_yengildi")
                return
            # Dushman javobi
            self.player['hp'] -= enemy['damage']
            self.output(f"{enemy['nom']} sizga {enemy['damage']} zarar berdi. (HP: {self.player['hp']}/{self.player['max_hp']})")
            if self.player['hp'] <= 0:
                self.output("[color=ff0000]Siz mag'lub bo'ldingiz.[/color]")
                self.game_over = True
                return

    # output_callback: labelga yozadi (bo'sh qatordan keyin qo'shib boradi)
class RootWidget(BoxLayout):
    display_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_string(KV)
        self.engine = GameEngine(self.append_output)
        # kichik intro
        self.append_output("[b]Xush kelibsiz! O'yin boshlandi. Qoidalar: bor, olish, inventar, jang, qidir, ich, restart, chiqish[/b]\n")

    def append_output(self, text):
        # Kivy thread-safe tarzda main threadga chiqarish
        def _do(dt):
            # markup yordamida formatlash
            cur = self.display_text
            if cur:
                self.display_text = cur + "\n\n" + text
            else:
                self.display_text = text
        Clock.schedule_once(_do, 0)

    def on_enter(self, text):
        if not text:
            return
        # labelga buyruq ko'rinishini qo'shamiz
        self.append_output(f"[i]> {text}[/i]")
        self.engine.handle(text)
        # clear input field
        self.ids.cmd_input.text = ""

class AdventureApp(App):
    def build(self):
        Window.soft_input_mode = 'below_target'
        return RootWidget()

if __name__ == '__main__':
    AdventureApp().run()
