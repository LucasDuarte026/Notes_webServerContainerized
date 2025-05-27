#!/bin/bash
# wait-for-it.sh

# Versão do wait-for-it.sh para esperar por um serviço TCP.
# Uso: ./wait-for-it.sh host:port [-t timeout] [-- command args]

# Definir valores padrão
TIMEOUT=15
QUIET=0
COMMAND=""
HOST=""
PORT=""

# Função para exibir a ajuda
usage() {
  echo "Usage: $0 host:port [-t timeout] [-- command args]"
  echo "  -t TIMEOUT    Timeout em segundos, padrão: 15"
  echo "  -q            Modo silencioso (não imprime mensagens de status)"
  echo "  -- COMMAND    Comando a ser executado após o serviço estar pronto"
  exit 1
}

# Analisar os argumentos
while [ "$#" -gt 0 ]; do
  case "$1" in
    *:*)
      HOST=$(echo "$1" | cut -d: -f1)
      PORT=$(echo "$1" | cut -d: -f2)
      shift
      ;;
    -t)
      TIMEOUT="$2"
      if ! [[ "$TIMEOUT" =~ ^[0-9]+$ ]]; then
        echo "Erro: O timeout deve ser um número inteiro."
        usage
      fi
      shift 2
      ;;
    -q)
      QUIET=1
      shift
      ;;
    --)
      shift
      COMMAND="$@"
      break
      ;;
    *)
      usage
      ;;
  esac
done

if [ -z "$HOST" ] || [ -z "$PORT" ]; then
  usage
fi

# Mensagem de espera
if [ "$QUIET" -eq 0 ]; then
  echo "Aguardando $HOST:$PORT..."
fi

# Loop de tentativa de conexão
START_TIME=$(date +%s)
while :; do
  (echo > /dev/tcp/"$HOST"/"$PORT") >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    if [ "$QUIET" -eq 0 ]; then
      echo "$HOST:$PORT está disponível!"
    fi
    break
  fi

  CURRENT_TIME=$(date +%s)
  ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

  if [ "$ELAPSED_TIME" -ge "$TIMEOUT" ]; then
    echo "Erro: Tempo limite de $TIMEOUT segundos excedido para $HOST:$PORT"
    exit 1
  fi

  if [ "$QUIET" -eq 0 ]; then
    echo "Ainda aguardando $HOST:$PORT... ($ELAPSED_TIME/$TIMEOUT s)"
  fi
  sleep 1
done

# Executar comando se especificado
if [ -n "$COMMAND" ]; then
  if [ "$QUIET" -eq 0 ]; then
    echo "Executando comando: $COMMAND"
  fi
  exec $COMMAND
fi

exit 0