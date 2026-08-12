from game_generator import generate_game_html
spec={'title':'Abyss Test','genre':'Hole game','instructions':'Move the hole with mouse'}
html=generate_game_html(spec)
print('LEN', len(html))
open('generated_hole_test.html','w',encoding='utf-8').write(html)
print('WROTE generated_hole_test.html')
