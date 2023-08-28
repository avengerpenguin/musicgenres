#!/bin/sh

echo 'digraph g {' >all.dot
echo 'node [shape=circle]' >>all.dot
cat Music/*.md | grep 'URL=' | sort | uniq >>all.dot
cat Music/*.md | grep '\->' | sort | uniq >>all.dot
echo '}' >>all.dot
dot -Tpng all.dot >all.png && open all.png
