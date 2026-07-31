import json

# Simple rule-based game HTML generator. Produces a single-file HTML + JS playable prototype.

def generate_game_html(spec: dict) -> str:
    import html as _html
    title = spec.get('title') or spec.get('genre','Mini Game')
    player_color = spec.get('player_color','#4f46e5')
    enemy_color = spec.get('enemy_color','#ef4444')
    theme = spec.get('theme','')
    instructions = spec.get('instructions','Use arrow keys to move, space to shoot.')

    template = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>__TITLE__</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <style>
    html,body { height:100%; margin:0; background:#0b1220; color:#e6eef8; font-family:Inter,Segoe UI,Arial; }
    #game { display:block; margin:24px auto; background:#111; border:6px solid #222; max-width:900px; }
    .hud { text-align:center; padding:8px; }
    .btn { background:#2b6cb0; color:white; padding:8px 12px; border-radius:6px; cursor:pointer; border:none; }
  </style>
</head>
<body>
  <div style="max-width:960px;margin:12px auto;text-align:center;">
    <h1>__TITLE__</h1>
    <p style="opacity:0.8">__THEME__</p>
    <div class="hud">__INSTRUCTIONS__</div>
    <canvas id="game" width="800" height="480"></canvas>
    <div class="hud"><button id="restart" class="btn">Restart</button></div>
  </div>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

let keys = {};
window.addEventListener('keydown', e=>keys[e.code]=true);
window.addEventListener('keyup', e=>keys[e.code]=false);

actionStart();

function actionStart(){
  let player = {x:W/2,y:H-60,w:28,h:28,spd:5,color:'__PLAYER_COLOR__'};
  let bullets = [];
  let enemies = [];
  let score = 0;
  let gameOver = false;

  function spawnEnemy(){
    const x = Math.random()*(W-40)+20;
    enemies.push({x,y:0+20,w:28,h:28,spd:1.2+Math.random()*1.2,color:'__ENEMY_COLOR__'});
  }
  for(let i=0;i<6;i++) spawnEnemy();

  document.getElementById('restart').onclick = ()=>{ enemies=[]; bullets=[]; score=0; gameOver=false; player.x=W/2; for(let i=0;i<6;i++) spawnEnemy(); }

  function update(){
    if(gameOver) return;
    // input
    if(keys['ArrowLeft'] || keys['KeyA']) player.x -= player.spd;
    if(keys['ArrowRight'] || keys['KeyD']) player.x += player.spd;
    if(keys['Space']){
      if(!keys._fired){ bullets.push({x:player.x, y:player.y-12, w:6,h:12,spd:8}); keys._fired=true; }
    } else keys._fired=false;

    // bounds
    player.x = Math.max(16, Math.min(W-16, player.x));

    // update bullets
    for(let b of bullets) b.y -= b.spd;
    bullets = bullets.filter(b=>b.y+ b.h > 0);

    // update enemies
    for(let e of enemies){ e.y += e.spd; if(Math.random()<0.004) e.x += (Math.random()-0.5)*20; }
    // collisions
    for(let i=enemies.length-1;i>=0;i--){
      const e = enemies[i];
      // hit by bullet
      for(let j=bullets.length-1;j>=0;j--){
        const b = bullets[j];
        if(b.x > e.x - e.w && b.x < e.x + e.w && b.y > e.y - e.h && b.y < e.y + e.h){
          enemies.splice(i,1); bullets.splice(j,1); score += 10; spawnEnemy(); break;
        }
      }
      // hit player or bottom
      if(Math.abs(e.x-player.x) < 28 && Math.abs(e.y-player.y) < 28){ gameOver = true; }
      if(e.y > H+40){ enemies.splice(i,1); spawnEnemy(); score -= 2; }
    }
  }

  function render(){
    ctx.clearRect(0,0,W,H);
    // background grid
    ctx.fillStyle = '#071025'; ctx.fillRect(0,0,W,H);
    // player
    ctx.fillStyle = player.color; ctx.beginPath(); ctx.arc(player.x, player.y, 14,0,Math.PI*2); ctx.fill();
    // bullets
    for(let b of bullets){ ctx.fillStyle='#fff'; ctx.fillRect(b.x-3,b.y-12,b.w,b.h); }
    // enemies
    for(let e of enemies){ ctx.fillStyle=e.color; ctx.fillRect(e.x-14,e.y-14,e.w,e.h); }

    // HUD
    ctx.fillStyle='#e6eef8'; ctx.font='18px sans-serif'; ctx.fillText('Score: '+score, 12, 26);
    if(gameOver){ ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(0,H/2-40,W,90); ctx.fillStyle='#fff'; ctx.font='28px sans-serif'; ctx.fillText('Game Over - Refresh or Restart', W/2-220, H/2+10); }
  }

  function loop(){ update(); render(); if(!gameOver) requestAnimationFrame(loop); }
  requestAnimationFrame(loop);
}
</script>
</body>
</html>'''

    # safe replacements
    safe_title = _html.escape(str(title))
    safe_theme = _html.escape(str(theme))
    safe_instructions = _html.escape(str(instructions))
    html = template.replace('__TITLE__', safe_title).replace('__PLAYER_COLOR__', player_color).replace('__ENEMY_COLOR__', enemy_color).replace('__THEME__', safe_theme).replace('__INSTRUCTIONS__', safe_instructions)
    return html
