


## Before publishing:

1. Re-generate `USAGE.html`, if you have updated `USAGE.md`:
    * We use `markdown_strict` format, with the `smart` extensions disabled 
    (because the smart extension generate weird ligatures for e.g. quotation marks).
    * Markdown variants: 
        * markdown_strict (Markdown.pl)
        * markdown_mmd (MultiMarkdown)
        * markdown_phpextra (PHP Markdown Extra)
        * gfm (GitHub-Flavored Markdown)
        * markdown_github (deprecated GitHub-Flavored Markdown)
    * See https://pandoc.org/MANUAL.html#markdown-variants for different markdown variants.

```
pandoc --from markdown_strict-smart -o USAGE.html USAGE.md 
```





## Python 2-to-3 conversion:

```

"C:\Program Files\Git\usr\bin\find.exe" . -name "*.py" -exec "futurize --stage1 mypackage/*.py {}" ;

```