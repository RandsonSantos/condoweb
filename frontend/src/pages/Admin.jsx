import React, {useEffect, useState} from 'react';

export default function Admin(){
  const [moradores, setMoradores] = useState([]);
  const [cameras, setCameras] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(()=>{
    fetch('/api/moradores',{headers:{'Authorization':`Bearer ${token}`}}).then(r=>r.json()).then(setMoradores).catch(()=>{});
    fetch('/api/cameras',{headers:{'Authorization':`Bearer ${token}`}}).then(r=>r.json()).then(setCameras).catch(()=>{});
  },[]);

  return (
    <div style={{padding:20}}>
      <h1>Admin</h1>
      <section>
        <h2>Moradores</h2>
        <ul>{moradores.map(m=> <li key={m.id}>{m.nome} - {m.cpf}</li>)}</ul>
      </section>
      <section>
        <h2>Câmeras</h2>
        <ul>{cameras.map(c=> <li key={c.id}>{c.nome} ({c.tipo}) - {c.url}</li>)}</ul>
      </section>
    </div>
  );
}
