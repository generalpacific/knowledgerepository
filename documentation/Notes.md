# AWS Lambda Layers
* (Lambda layer)[https://docs.aws.amazon.com/lambda/latest/dg/invocation-layers.html]  is a .zip file archive that can contain additional code or other content. A layer can contain libraries, a custom runtime, data, or configuration files. Use layers to reduce deployment package size and to promote code sharing and separation of responsibilities so that you can iterate faster on writing business logic.
## Updating Layer for python lambda

```
mkdir <newdir>
cd <newdir>
mkdir python
pip3 install <python library> -t python
zip -r newlayer.zip python/
```

### Useful commands

```
python3.10 -m pip install --upgrade pip
arch  -x86_64 pip3.10 install requests -t python --upgrade --platform manylinux2014_x86_64 --only-binary=:all:
arch  -x86_64 pip3.10 install openai -t python --upgrade --platform manylinux2014_x86_64 --only-binary=:all:
arch  -x86_64 pip3.10 install boto3 -t python --upgrade --platform manylinux2014_x86_64 --only-binary=:all:
arch  -x86_64 pip3.10 install datetime -t python --upgrade --platform manylinux2014_x86_64 --only-binary=:all:
zip -r newlayer.zip python/

```

# APi Gateway
* Use lambda proxy integration to pass the parameters from the api

## Makeing API gateway return binary data
* Set the binary type to "\*/\*" in the API settings policy. 
* See the stack overflow: https://stackoverflow.com/questions/35804042/aws-api-gateway-and-lambda-to-return-image

# Lambda Layer
* Install all dependencies needed in the lambda to the new layer to avoid any
  conflict in dependencies between lambda default dependencies 
  and the new layer.

