
# Pythonで簡単なGUIを作れる
import tkinter as tk
import math
from tkinter.constants import N
root = None
canvas = None
import random
import sys
sys.setrecursionlimit(1000)

bomb_list = []
blank_list = []
number_list = []
open_not_bomb_list = [] #bomb以外のセルをオープンした時にカウントしていく
status_list = [] #二次元配列 bomb、number、blank
expansion_blank_list = [] #あるセルを起点に、８方向のセルでblankのセルの座標をリスト化する

check_open_flags = {} #セルが開かれたらTrue
check_set_cell_flags = {} #blank, bomb, numberの、いずれかのセルをセットしたらTrue
finish_flag = {} #勝ちまたは負けになったらTrue
finish_flag['confirm'] = False
check_blue_flags = {} #blue flagをチェック

# 四角の長さ 1個当たり
SQUARE_LENGTH = 30
# 半径
RADIUS = SQUARE_LENGTH / 2 - 5 
# ポジション
POSITION = {"x": 8,  "y": 8}
# ボーダーの広さ
BORDER_WIDTH = 2
# 四角の数 合計20個
NUMBER = 20
# 30 * 20 + 2 * 20 = 600 + 40 = 640
LENGTH = SQUARE_LENGTH * NUMBER + BORDER_WIDTH * NUMBER

# 【Python】Tkinterのcanvasを使ってみる
# https://qiita.com/nnahito/items/2ab3ad0f3adacc3314e6
def create_canvas():
  # 窓を作る
  root = tk.Tk()  
  # 窓の大きさを設定 (LENGTH 640 + POSITION["x"] 8 * 2) × (LENGTH 640 + POSITION["y"] 8 * 2)
  # → 656 × 656 root.geometry(f"""{656}x{656}""")と同じ
  root.geometry(f"""{LENGTH + POSITION["x"] * 2}x{LENGTH + POSITION["y"] * 2}""")
  root.title("マインスイーパー")
    
  # Canvasの作成  第１引数のrootは決まった書き方？ 上に変数あり
  # width = 648  height = 648  canvas = tk.Canvas(root, width=(64800), height=(648)) 64800でも表示変わらず
  canvas = tk.Canvas(root, width=(LENGTH + POSITION["x"]), height=(LENGTH + POSITION["y"]))
  #キャンバスバインド canvas.place(x=100, y=100)にすると、上、左にに余白ができる
  canvas.place(x=0, y=0)

  return root, canvas

def set_field():
  # 3. キャンバスに図形を描画する https://daeudaeu.com/tkinter_canvas_draw/#create_rectangle
  # fill=で色を設定 width=で枠線の太さを設定 8, 8, 648, 648 → 8だけxは左端、yは上に余白ができる　648は縦横の画面の大きさ
  # canvas.create_rectangle(8, 8, 648, 648, fill='#999', width=BORDER_WIDTH)
  # canvas.create_rectangle(POSITION["x"], POSITION["y"], LENGTH + POSITION["x"], LENGTH + POSITION["y"], fill='#aaa', width=BORDER_WIDTH)
  canvas.create_rectangle(POSITION["x"], POSITION["y"], LENGTH + POSITION["x"], 
                          LENGTH + POSITION["y"], fill='#aaa', width=BORDER_WIDTH)
  # 19回繰り返す →20回ではなく、19回線を引けば良い for i in range(0):
  for i in range(NUMBER - 1):
    # i = 0  x = 8 + 30 * (0 + 1) + (2 * 0) + 2 = 38 + 2 = 40   # i = 1  x = 8 + 30 * (1 + 1) + (2 * 1) + 2 = 68 + 4 = 72
    # i = 2  x = 8 + 30 * (2 + 1) + (2 * 2) + 2 = 98 + 6 = 104   # i = 18 x = 8 + 30 * (18 + 1) + (2 * 18) + 2 = 578 + 38 = 616 
    # POSITION["x"]： 左端の余白 SQUARE_LENGTH * (i + 1)：スクウェアの数を計算し、線を引く箇所を右にずらす 
    # BORDER_WIDTH * iの数を計算し、線を引く箇所を右にずらす BORDER_WIDTHでラインを引く位置を計算
    #  x、y それぞれの値を代入
    x = POSITION["x"] + SQUARE_LENGTH * (i + 1) + BORDER_WIDTH * i + BORDER_WIDTH
    y = POSITION["y"] + SQUARE_LENGTH * (i + 1) + BORDER_WIDTH * i + BORDER_WIDTH
    # 直線を描く、多角形を描く # Ⅹ座標（始点）, Ｙ座標（始点）, Ⅹ座標（終点）, Ｙ座標（終点)  
    # 縦のライン #  40, 8, 40, 648  → 72, 8. 72, 648 → 104, 8, 104, 8
    canvas.create_line(x, POSITION["y"], x, LENGTH + POSITION["y"], width=BORDER_WIDTH)
    # 横のライン # 8, 40, 648, 40
    canvas.create_line(POSITION["x"], y, LENGTH + POSITION["x"], y, width=BORDER_WIDTH)

def set_item(kind, x, y):
  # center_x = 8 + 2 * 「1」 + 2 / 2 + 30 * 「1」 + 30 / 2 = 8 + 2 + 1 + 30 + 15 = 56
  # POSITION["x"]の"x"と、xは異なる
  # center_y = 8 + 2 * 「3」 + 2 / 2 + 30 * 「3」 + 30 / 2 = 8 + 6 + 1 + 90 + 15 = 120 
  center_x = POSITION["x"] + BORDER_WIDTH * x + BORDER_WIDTH / 2 + SQUARE_LENGTH * x + SQUARE_LENGTH / 2
  center_y = POSITION["y"] + BORDER_WIDTH * y + BORDER_WIDTH / 2 + SQUARE_LENGTH * y + SQUARE_LENGTH / 2

  # 長方形を描画する 第１、第２引数は左端、yは上に余白ができる　第３、第４は縦横の画面の大きさ
  # 56 - 15 = 41, 120 - 15 = 105, 56 + 15 = 71, 120 + 25 = 135 　縦横30ずつ
  # x1 と y1 は描画する長方形の左上の座標、x2 と y2 は描画する長方形の右下の座標になります。
  # create_rectangle を実行することで、(x1, y1) – (x2 – 1, y2 – 1) の座標に長方形が描画されることになります。
  # 実際には (x2, y2) は長方形に含まれないところが注意点ですね。
  # 41, 105, 70, 134 #fff 白
  canvas.create_rectangle(center_x - SQUARE_LENGTH / 2, center_y - SQUARE_LENGTH / 2, 
                          center_x + SQUARE_LENGTH / 2, center_y + SQUARE_LENGTH / 2, fill="#fff", width=0)

  if kind != None:
    if kind == "choice_bomb":
    # キャンバスに円を描く f00 赤 https://natu-ym.com/python-canvas-arc-oval/
    # 56 - 10, 120 - 10, 56 + 10, 120 + 10 
    # 46, 110, 66, 130 widthはゼロ
      canvas.create_rectangle(center_x - SQUARE_LENGTH/2, center_y - SQUARE_LENGTH/2, center_x + SQUARE_LENGTH/2, 
                              center_y + SQUARE_LENGTH/2, fill="#000")
                      
    elif kind == "bomb":
      # キャンバスに円を描く f00 赤 https://natu-ym.com/python-canvas-arc-oval/
      # 56 - 10, 120 - 10, 56 + 10, 120 + 10 
      # 46, 110, 66, 130 widthはゼロ
      canvas.create_oval(center_x - RADIUS, center_y - RADIUS, center_x + RADIUS, center_y + RADIUS,  
                         fill="#f00", width=0)
    elif kind == "flag":
      # キャンバスに円を描く f00 赤 https://natu-ym.com/python-canvas-arc-oval/
      # 56 - 10, 120 - 10, 56 + 10, 120 + 10 
      # 46, 110, 66, 130 widthはゼロ
      canvas.create_oval(center_x - RADIUS, center_y - RADIUS, center_x + RADIUS, center_y + RADIUS, 
                         fill="#00f", width=0)
    elif kind == "grey":
      canvas.create_rectangle(center_x - SQUARE_LENGTH / 2, center_y - SQUARE_LENGTH / 2, 
                          center_x + SQUARE_LENGTH / 2, center_y + SQUARE_LENGTH / 2, fill="#aaa", width=0)
    else:
      # オブジェクト名.create_text(座標, オプション)
      canvas.create_text(center_x, center_y, text=kind, justify="center", font=("", 25), tag="count_text")

def set_bomb():
  count = 0
  for i in range(20):
    status_list.append([]) #iを通過するたびに、リスト[]を追加していく
    for j in range(20):
      hit = random.randint(0, 30)
      if hit == 1:
        count += 1
        status_list[i].append('bomb') #インデックスはiが正しい。appendで最後に追加していく
        bomb_list.append([i, j])
        check_set_cell_flags[i, j] = True
      else:
        status_list[i].append('')
  print('爆弾の数' + str(count))

def cnofirm_set_number_list(i, j, k):
  eight_confirm_list = [[i-1, j-1], [i, j-1], [i+1, j-1], [i-1, j], [i+1, j], [i-1, j+1], [i, j+1], [i+1, j+1]]
  return eight_confirm_list[k]

def set_number():
  for i in range(20):
    for j in range(20):
      if [i, j] not in bomb_list:
        number = 0
        for k in range(8):
          eight_confirm_list = cnofirm_set_number_list(i, j, k)
          if eight_confirm_list in bomb_list: # bombが周りにある場合、numberを1つ増やす
            number += 1
        if check_set_cell_flags[i, j] == False:
          if number >= 1 and number <= 8:
            status_list[i][j] = number
            number_list.append([i, j])
            check_set_cell_flags[i, j] = True

def set_blank():
  for i in range(20):
    for j in range(20):
      if [i, j] not in bomb_list and [i, j] not in number_list:
        if check_set_cell_flags[i, j] == False:
          blank_list.append([i, j])

def set_cells():
  set_bomb()
  set_number()
  set_blank()

def open_all_bomb(x, y):
  for i in bomb_list:
    if i[0] == x and i[1] == y:
      pass
    else:
      set_item("bomb", i[0], i[1])
      check_open_flags[x, y] = True
 
def lose():
  print('負け')
  finish_flag['confirm'] = True
  print('finish_flag[\'confirm\']')
  print(finish_flag['confirm'])
  choice_continue_or_end()

def open_bomb(x, y):
  for i in range(len(bomb_list)):
    number_x = bomb_list[i][0]
    number_y = bomb_list[i][1]
    if check_open_flags[x, y] == False:
      if number_x == x and number_y == y:
        set_item("choice_bomb", x, y)
        check_open_flags[x, y] = True
        open_all_bomb(x, y)
        lose()

def expansion_blank(x, y):
  arount_list = [[x-1, y-1], [x, y-1], [x+1, y-1], [x-1, y], [x+1, y], [x-1, y+1], [x, y+1], [x+1, y+1]]
  for i in range(8):
    arount_cell = arount_list[i]
    number1 = arount_cell[0]
    number2 = arount_cell[1]
    if [number1, number2] in blank_list:
      blank_list.append([number1, number2])  
  for i in range(len(blank_list)):
    x = blank_list[i][0]
    y = blank_list[i][1]
    if check_open_flags[x, y] == False:
      if [x, y] in blank_list:
        set_item("", x, y)
        check_open_flags[x, y] = True
        if not [x, y] in open_not_bomb_list:
          open_not_bomb_list.append([x, y])
        blank_around_number(x, y)   
        expansion_blank(x, y)

def blank_around_number(x, y):
  around_eight_confirm_list = [[x-1, y-1], [x, y-1], [x+1, y-1], [x-1, y], [x+1, y], [x-1, y+1], [x, y+1], [x+1, y+1]]
  for i in range(8):
    around_eight_confirm_cell = around_eight_confirm_list[i]
    number1 = around_eight_confirm_cell[0]
    number2 = around_eight_confirm_cell[1]
    if [number1, number2] in number_list:
      open_number(number1, number2)

def open_blank(x, y):
  if [x, y] in blank_list:
    if check_open_flags[x, y] == False:
      set_item("", x, y)
      check_open_flags[x, y] = True
    if not [x, y] in open_not_bomb_list:
      open_not_bomb_list.append([x, y])
    expansion_blank(x, y)

def open_number(x, y):
  if [x, y] in number_list:
    number = status_list[x][y]
    set_item(number, x, y)
    check_open_flags[x, y] = True
    if not [x, y] in open_not_bomb_list:
      open_not_bomb_list.append([x, y])       

def point_to_numbers(event_x, event_y):
    x = math.floor((event_x - POSITION["x"]) / (SQUARE_LENGTH + BORDER_WIDTH))
    y = math.floor((event_y - POSITION["y"]) / (SQUARE_LENGTH + BORDER_WIDTH))
    return x, y

def set_flags():
  for i in range(3):
    x = 0 
    y = 0
    while x < 20:
      while y < 20:
        if i == 0:
          check_open_flags[x, y] = False
        elif i == 1:
          check_set_cell_flags[x, y] = False
        elif i == 2:
          check_blue_flags[x, y] = False
        y += 1
      x += 1
      y = 0
    i += 1
   
def flag_bomb_check():
  blue_flag_list = []
  for i in range(20):
    for j in range(20):
      if check_blue_flags[i, j] == True:
        blue_flag_list.append([i, j])
  blue_flag_list.sort()
  bomb_list.sort()
  if blue_flag_list == bomb_list:
    game_clear()

def set_blue_flag(x, y):
  if check_open_flags[x, y] == False:
    set_item("flag", x, y)
    check_open_flags[x, y] = True  
    check_blue_flags[x, y] = True  
    flag_bomb_check()
  elif check_open_flags[x, y] == True:
    if check_blue_flags[x, y] == True:
      set_item("grey", x, y)
      check_blue_flags[x, y] = False
      check_open_flags[x, y] = False
  
def game_clear():
  print('勝ち')
  finish_flag['confirm'] = True
  choice_continue_or_end()
  
def game_clear_or_not():
  bomb_number = len(bomb_list)
  all_cell_number = NUMBER * NUMBER
  not_bomb_number = all_cell_number - bomb_number
  confirm_number = len(open_not_bomb_list)
  if confirm_number == not_bomb_number:
    game_clear()

def choice_continue_or_end():
  global root
  choice = input('再度ゲームをプレイする場合は「1」を押してください')
  choice_key = int(choice) 
  if choice_key == 1:
    root.destroy()
    finish_flag['confirm'] = False
    play()    
  else:
    print('ゲーム終了')
    root.destroy()

def click1(event):
  x, y = point_to_numbers(event.x, event.y)
  if finish_flag['confirm'] == False:
    open_bomb(x, y)
    open_number(x, y)
    open_blank(x, y)
    game_clear_or_not()

def click2(event):
  x, y = point_to_numbers(event.x, event.y)
  set_blue_flag(x, y)

def reset_list_flags():
  global bomb_list, blank_list, number_list, check_open_flags, check_set_cell_flags
  global open_not_bomb_list, status_list, expansion_blank_list, finish_flag, check_blue_flags
  bomb_list = []
  blank_list = []
  number_list = []
  open_not_bomb_list = [] #bomb以外のセルをオープンした時にカウントしていく
  status_list = [] #二次元配列　bomb、number、blank
  expansion_blank_list = [] #あるセルを起点に、８方向のセルでblankのセルの座標をリスト化する

  check_open_flags = {} #セルが開かれたらTrue
  check_set_cell_flags = {} #blank, bomb, numberの、いずれかのセルをセットしたらTrue
  finish_flag = {} #勝ちまたは負けになったらTrue
  finish_flag['confirm'] = False
  check_blue_flags = {} #blue flagをチェック

def play():
  reset_list_flags()
  global root
  global canvas
  root, canvas = create_canvas()
  set_field()
  set_flags()
  set_cells()

  if finish_flag['confirm'] == False:
    # bind()メソッドはすべてのウィジェットに対してトリガーとなる特定のイベントと実行する関数（コールバック関数）を紐づける
    # https://office54.net/python/tkinter/tkinter-bind-event
    canvas.bind("<Shift-1>", lambda event: click2(event))
    canvas.bind("<Button-1>", lambda event: click1(event))
    
  # この「ループ」は静止画面（GUIアプリの画面）を表示するために永遠と実行される無限ループです。
  # つまりmainloopのおかげでGUIアプリの画面が表示したままになっているということです。
  root.mainloop()

play()
