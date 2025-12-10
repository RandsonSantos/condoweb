# condoweb (full)

Projeto completo de exemplo para controle de portões com câmera e painel admin.

Conteúdo:
- backend/ : Flask API (auth JWT, morador, veiculo, camera, logs, proxy endpoints)
- frontend/ : React app (login, dashboard, camera view, admin CRUD)
- firmware/ : ESP32 Arduino sketch (POST /open)
- docker-compose.yml : backend, db, nginx (serve HLS), streamer (ffmpeg template)
- README com instruções rápidas
