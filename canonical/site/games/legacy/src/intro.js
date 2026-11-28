export function startIntro(){
  const intro=document.getElementById('brandIntro'),app=document.getElementById('app');
  if(!intro||!app)return;
  let timer;function finish(){clearTimeout(timer);intro.hidden=true;app.inert=false;}
  intro.addEventListener('animationend',e=>{if(e.target===intro&&e.animationName==='brand-exit')finish()});
  intro.classList.add('play');timer=setTimeout(finish,3100);
}
