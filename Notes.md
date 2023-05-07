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


