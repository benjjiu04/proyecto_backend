
try{
  if (Get-Command -Name py -errorAction SilentlyContinue){
    py -m pip install -r ./requirements.txt
  }

  elseif (Get-Command -Name python -errorAction SilentlyContinue){
    python -m pip install -r ../requirements.txt
  }

}catch{
  echo "las librerias necesarias no pudieron ser instaladas."
}

echo "las librerias necesarias fueron instaladas correctamente!"