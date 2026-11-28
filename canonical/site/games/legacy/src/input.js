import {W,H,maps,project,clamp} from './data.js';
// Coordinates follow the rendered image, including object-fit letterboxing.
export function fieldPoint(rect,clientX,clientY){const scale=Math.min(rect.width/W,rect.height/H);if(!Number.isFinite(scale)||scale<=0)return null;const x=(clientX-rect.left-(rect.width-W*scale)/2)/scale,y=(clientY-rect.top-(rect.height-H*scale)/2)/scale;return Number.isFinite(x)&&Number.isFinite(y)&&x>=0&&x<=W&&y>=0&&y<=H?{x,y}:null}
export function padAt(mi,p,radius=20){if(!p)return -1;let best=radius,i=-1;maps[mi].pads.forEach((q,j)=>{const d=Math.hypot(p.x-q[0],p.y-q[1]);if(d<best){best=d;i=j}});return i}
export function routePoint(mi,p){if(!p)return null;const points=maps[mi].paths.flatMap(r=>r.segments.map(s=>project(s,p.x,p.y)));points.sort((a,b)=>Math.hypot(a.x-p.x,a.y-p.y)-Math.hypot(b.x-p.x,b.y-p.y));return{x:clamp(points[0].x,12,443),y:points[0].y}}
export function releaseTarget(mi,mode,start,end){if(!start||!end)return null;if(mode==='move')return routePoint(mi,end);if(mode==='meteor')return end;const i=padAt(mi,start);return i>=0&&i===padAt(mi,end)?{pad:i}:null}
