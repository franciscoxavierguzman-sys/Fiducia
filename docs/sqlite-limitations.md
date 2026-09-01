# Limitaciones de SQLite

SQLite es adecuado para el prototipo local de FIDUCIA, pruebas y demostracion controlada.

Limitaciones:

- ejecucion single-node;
- concurrencia de escritura limitada;
- ausencia de alta disponibilidad;
- backups manuales;
- sin replicacion nativa;
- bloqueos posibles si hay escrituras simultaneas extensas;
- no representa arquitectura productiva financiera.

Ruta futura recomendada: PostgreSQL con migraciones formales, backups automatizados, control de conexiones y monitoreo.
