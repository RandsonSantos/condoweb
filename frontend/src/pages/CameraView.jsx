import React, {useEffect, useRef} from 'react';
import Hls from 'hls.js';

export default function CameraView({camera, token}){
  const videoRef = useRef(null);

  useEffect(()=>{
    if(!camera) return;
    if(camera.tipo === 'hls' || camera.tipo === 'rtsp'){
      fetch(camera.stream_endpoint, {headers: {'Authorization': `Bearer ${token}`}})
        .then(r=>r.json()).then(data=>{
          const url = data.hls_url || data.stream || data.hls || data.hls_url;
          if(!url) return;
          const full = url.startsWith('http') ? url : `${window.location.origin}${url}`;
          if (Hls.isSupported()) {
            var hls = new Hls();
            hls.loadSource(full);
            hls.attachMedia(videoRef.current);
          } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
            videoRef.current.src = full;
          }
        }).catch(e=>console.error(e));
    }
  },[camera, token]);

  const openGate = async ()=>{
    const resp = await fetch('/api/portao/abrir',{method:'POST', headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`}, body: JSON.stringify({ tipo: camera.porta_tipo, camera_id: camera.id })});
    const data = await resp.json();
    alert(data.msg || JSON.stringify(data));
  };

  return (
    <div style={{border:'1px solid #ddd', padding:10, marginBottom:12, maxWidth:720}}>
      <h3>{camera.nome} ({camera.porta_tipo})</h3>
      {camera.tipo === 'mjpeg' && <img src={camera.stream_endpoint} alt={camera.nome} style={{width:'100%'}} />}
      {(camera.tipo === 'hls' || camera.tipo === 'rtsp') && <div><video ref={videoRef} controls style={{width:'100%'}}/></div>}
      <div style={{marginTop:8}}><button onClick={openGate}>Abrir Portão</button></div>
    </div>
  );
}
