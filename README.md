# PROJET-COMPILATION
Le projet du cours de Théorie des langages et compilations dispensé à l'ENSSAT (Lannion)

## Comment utiliser le compilateur

Pour compiler et exécuter un fichier .nno, il faut effectuer la commande suivante:

```shell
make TARGET=tests/nnp/correct1.nno
```

Si en plus de compiler et d'exécuter vous voulez voir l'état de la pile à chaque instructions du code objet, vous pouvez utiliser la commande suivante:

```shell
make TARGET=tests/nna/correct1.nno ARGS=-d
```