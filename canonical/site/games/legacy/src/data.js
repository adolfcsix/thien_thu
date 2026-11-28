export const W=480; export const H=288;
export const maps=[
 {name:'Hắc Mộc cổ lâm',short:'Hắc Mộc',gold:340,colors:['#344f38','#4c6948','#6d8757','#b99b6e'],routes:[[[-14,72],[92,72],[92,193],[218,193],[218,75],[352,75],[352,224],[458,224]]],pads:[[42,31],[43,128],[145,33],[149,126],[45,219],[148,243],[270,137],[281,33],[307,196],[403,132],[411,266],[263,252]]},
 {name:'Băng Hà hiểm lộ',short:'Băng Hà',gold:360,colors:['#7595a2','#a1bec6','#d2e2df','#d2c9b1'],routes:[[[-14,218],[125,218],[125,150],[350,150],[350,60],[458,60]]],pads:[[50,176],[64,261],[167,257],[166,107],[315,102],[315,199],[405,113],[406,29],[397,198],[155,32],[319,252],[450,182]]},
 {name:'Hỏa Vực song môn',short:'Hỏa Vực',gold:400,colors:['#493638','#725243','#a16b4b','#bf9069'],routes:[[[-14,65],[110,65],[110,150],[340,150],[340,230],[458,230]],[[-14,238],[110,238],[110,150],[340,150],[340,230],[458,230]]],pads:[[45,27],[43,115],[47,185],[47,265],[165,72],[165,207],[254,97],[254,210],[383,107],[390,183],[300,267],[435,270]]}
];
export const towers=[
 {name:'Cung thủ',cost:80,d:20,r:83,rate:.62,v:265,col:'#cbe29d',branches:[['Liên Xạ','Bắn liên tục',120,'#a5ed9b',1.05,1,.46],['Thần Tiễn','Xuyên giáp, tầm xa',135,'#ffdb85',2.65,1.38,1.3]]},
 {name:'Pháp sư',cost:120,d:38,r:79,rate:1.2,v:160,col:'#c9b0ff',branches:[['Lôi Pháp','Sét lan 3 mục tiêu',175,'#e5c6ff',1.65,1.12,.85],['Viêm Pháp','Thiêu đốt 3 giây',165,'#ff9d62',1.5,1.05,1]]},
 {name:'Băng tháp',cost:100,d:12,r:73,rate:.84,v:215,col:'#91e4ff',branches:[['Bão Tuyết','Làm chậm diện rộng',145,'#c9f4ff',1.4,1.13,.9],['Hàn Ngục','Khống chế mạnh',150,'#78b4ff',2.1,1.22,.85]]},
 {name:'Pháo đài',cost:150,d:76,r:94,rate:1.85,v:135,col:'#f0b77a',branches:[['Cự Pháo','Vụ nổ lớn',210,'#ff9e66',1.65,1.12,1.05],['Diệt Thành','Chuyên hạ boss',225,'#f5dfa6',2.9,1.23,1.1]]}
];
export const heroes=[{name:'Vệ Thần',role:'Kiếm sĩ',hp:340,d:40,r:30,rate:.65,sp:75,col:'#d3be8b',skill:'Kiếm trận',cd:18,desc:'Chặn một quái thường; tuyệt kỹ diện rộng và hồi 25% HP.'},{name:'Nguyệt Linh',role:'Cung thủ',hp:220,d:34,r:105,rate:.47,sp:100,col:'#c3de9b',skill:'Vũ tiễn',cd:20,desc:'Tấn công từ xa; tuyệt kỹ xuyên giáp tối đa 8 mục tiêu.'},{name:'Huyền Sư',role:'Pháp sư',hp:200,d:54,r:88,rate:1.05,sp:70,col:'#c7b1ff',skill:'Tinh vân',cd:22,desc:'Đánh lan; tuyệt kỹ làm chậm quái 4 giây.'}];
export const mobs={grunt:[1,33,15,12,'#86ad67'],fast:[.67,56,13,10,'#d09a63'],armor:[2.1,21,25,22,'#98aeb9'],elite:[3.1,28,36,31,'#b093cb'],boss:[10,16,140,54,'#bd5b4c']};
export const techs=[['Ngân khố','+40 vàng khởi đầu'],['Binh khí','+8% sát thương trụ'],['Công sự','+2 sinh lực thành'],['Học viện','+10% sát thương tướng'],['Linh thuật','−8% hồi chiêu thần thuật'],['Chiến lợi phẩm','+6% vàng hạ quái']];
export const gears=[['Vũ khí tinh luyện','+25% sát thương',90],['Giáp hộ mệnh','+50 HP, giảm 12% sát thương',85],['Ấn linh lực','−12% hồi chiêu tuyệt kỹ',100]];
export const waveNames=['Tiên phong','Bầy săn','Thiết giáp','Kỵ binh','Hộ vệ','Quân đoàn','Tinh nhuệ','Binh đoàn thép','Đêm tận thế','Chúa tể'];
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
for(const m of maps)m.paths=m.routes.map(points=>{let len=0;const segments=points.slice(1).map((b,i)=>{const a=points[i],l=Math.hypot(b[0]-a[0],b[1]-a[1]),s=len;len+=l;return{a,b,l,s}});return{points,segments,len}});
export function pos(p,d){const s=p.segments.find(s=>d<=s.s+s.l)||p.segments.at(-1),t=clamp((d-s.s)/s.l,0,1);return{x:s.a[0]+(s.b[0]-s.a[0])*t,y:s.a[1]+(s.b[1]-s.a[1])*t,dx:Math.sign(s.b[0]-s.a[0])}}
export function project(s,x,y){const dx=s.b[0]-s.a[0],dy=s.b[1]-s.a[1],t=clamp(((x-s.a[0])*dx+(y-s.a[1])*dy)/s.l**2,0,1);return{x:s.a[0]+dx*t,y:s.a[1]+dy*t}}
