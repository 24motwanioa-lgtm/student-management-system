const modal=document.getElementById('modal'), form=document.getElementById('studentForm');
function showAdd(){form.action='/add';form.reset();document.getElementById('modalTitle').textContent='Add student';modal.classList.add('open');}
function showEdit(roll,name,branch,semester,cgpa,attendance){form.action='/update/'+roll;form.elements.roll.value=roll;form.elements.name.value=name;form.elements.branch.value=branch;form.elements.semester.value=semester;form.elements.cgpa.value=cgpa;form.elements.attendance.value=attendance;document.getElementById('modalTitle').textContent='Update student';modal.classList.add('open');}
function hideModal(){modal.classList.remove('open');}
modal.addEventListener('click',e=>{if(e.target===modal)hideModal()});
document.addEventListener('keydown',e=>{if(e.key==='Escape')hideModal()});
document.getElementById('topic').addEventListener('change',()=>{document.getElementById('xField').style.display=document.getElementById('topic').value==='polynomial'?'block':'none'});
async function runOperation(){
 const btn=document.querySelector('.controls .primary');btn.disabled=true;btn.textContent='Processing…';
 try{
  const r=await fetch('/api/dsa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic:document.getElementById('topic').value,values:document.getElementById('values').value,x:document.getElementById('polyX').value})});
  const d=await r.json();if(!r.ok)throw new Error(d.error||'The operation failed');
  document.getElementById('resultTitle').textContent=d.title;
  const v=document.getElementById('visual');v.innerHTML='';
  (d.structure||[]).forEach(item=>{const el=document.createElement('span');el.textContent=Array.isArray(item)?'['+item.join(', ')+']':item;v.appendChild(el)});
  document.getElementById('operation').textContent=d.operation;
  const st=document.getElementById('steps');st.innerHTML='';(d.steps||[]).forEach((x,i)=>{const p=document.createElement('p');p.textContent=(i+1)+'. '+x;st.appendChild(p)});
 }catch(e){document.getElementById('operation').textContent=e.message}
 finally{btn.disabled=false;btn.textContent='▶ Run operation'}
}
