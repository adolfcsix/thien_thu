// Rendering cadence is independent of simulation. Never replay time spent hidden.
export function createFrameClock(){let last=null,rendered=null;return {reset(){last=rendered=null},step(now,quality='high'){const dt=last===null?0:Math.max(0,Math.min(.05,(now-last)/1000));last=now;const interval=quality==='low'?1000/30:1000/60;const draw=rendered===null||now-rendered>=interval-1;if(draw)rendered=now;return {dt,draw}}}}
// Avoid identical synchronous writes; failed writes remain retryable.
export function createSaveWriter(storage,key,initial=null){let last=initial;return value=>{try{const raw=JSON.stringify(value);if(raw!==last){storage.setItem(key,raw);last=raw}return true}catch{return false}}}
