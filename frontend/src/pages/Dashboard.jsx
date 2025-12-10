import React, {useEffect, useState} from 'react';
import CameraView from './CameraView';
import { Link } from 'react-router-dom';

export default function Dashboard(){
  const [cams,setCams]=useState([]);
  const token = localStorage.getItem('token');

  useEffect(()=>{
    fetch('/api/cameras',{headers:{'Authorization': `Bearer ${token}`}})
      .then(r=>r.json()).then(setCams)
      .catch(()=>setCams([]));
  },[]);

  return (
    <div style={{padding:20}}>
      <h1>Dashboard</h1>
      {!token && <p><Link to='/login'>Faça login</Link> para ver câmeras e abrir portões.</p>}
      {cams.map(c=> <CameraView key={c.id} camera={c} token={token} />)}
    </div>
  );
}
