import React, {useState} from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login(){
  const [cpf,setCpf]=useState('');
  const [password,setPassword]=useState('');
  const nav = useNavigate();

  const submit = async (e)=>{
    e.preventDefault();
    const resp = await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cpf,password})});
    const data = await resp.json();
    if(data.access_token){
      localStorage.setItem('token', data.access_token);
      nav('/');
    } else {
      alert(data.msg || 'erro');
    }
  };

  return (
    <div style={{maxWidth:420, margin:'40px auto'}}>
      <h2>Login</h2>
      <form onSubmit={submit}>
        <div><input placeholder='CPF' value={cpf} onChange={e=>setCpf(e.target.value)} /></div>
        <div><input placeholder='Senha' type='password' value={password} onChange={e=>setPassword(e.target.value)} /></div>
        <button>Entrar</button>
      </form>
    </div>
  );
}
