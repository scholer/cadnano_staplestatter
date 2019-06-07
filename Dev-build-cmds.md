


## Before publishing:

1. Re-generate `USAGE.html`, if you have updated `USAGE.md`:
    * We use `markdown_strict` format, with the `smart` extensions disabled 
    (because the smart extension generate weird ligatures for e.g. quotation marks).

```
pandoc --from markdown_strict-smart -o USAGE.html USAGE.md 
```





