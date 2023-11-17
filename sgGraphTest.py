import PySimpleGUI as psg
graph=psg.Graph(canvas_size=(700,300), graph_bottom_left=(0, 0), graph_top_right=(700,300),
 background_color='red', enable_events=True, drag_submits=True, key='graph')
layout = [[graph], [psg.Button('LEFT'), psg.Button('RIGHT'), psg.Button('UP'), psg.Button('DOWN')]]
window = psg.Window('Graph test', layout, finalize=True)
x1,y1 = 350,150
circle = graph.draw_circle((x1,y1), 10, fill_color='black', line_color='white')
rectangle = graph.draw_rectangle((50,50), (650,250), line_color='purple')
while True:
   event, values = window.read()
   if event == psg.WIN_CLOSED:
      break
   if event == 'RIGHT':
      graph.MoveFigure(circle, 10, 0)
   if event == 'LEFT':
      graph.MoveFigure(circle, -10,0)
   if event == 'UP':
      graph.MoveFigure(circle, 0, 10)
   if event == 'DOWN':
      graph.MoveFigure(circle, 0,-10)
   if event=="graph+UP":
      x2,y2= values['graph']
      graph.MoveFigure(circle, x2-x1, y2-y1)
      x1,y1=x2,y2
window.close()