# mlst --- Scan contig files against PubMLST typing schemes

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/570)

Singularity container for Torsten Seemann's [MLST](https://github.com/tseemann/mlst)

## Pre-requisite

Install [Singularity](http://singularity.lbl.gov/docs-installation)

## Usage

### Latest version

The following steps are needed to use the image:

1. Pull the image:

```
singularity pull --name mlst shub://phgenomics-singularity/mlst@latest
```
This will command will create a file `mlst.simg`, which is executable.

2. Use the image:
```
./mlst.simg --help
```

### A particular version

```
singularity pull --name mlst shub://phgenomics-singularity/mlst@v2.9
```

## Suggested pattern

1. Create a `singularity` folder:

```
mkdir $HOME/singularity
```

2. Pull the image to the `singularity` folder.

```
singularity pull --name mlst_v2.10 shub://phgenomics-singularity/mlst@v2.10
```

3. Link the image to a folder in your `$PATH` (e.g., `$HOME/bin`)

```
ln -s $HOME/singularity/mlst_v2.10.simg $HOME/bin/mlst
```

Now, when you login again, you should be able to just type:

```
mlst --help
```
