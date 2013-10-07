#!/bin/bash

readme_fn="README.md"

cat description.md >"$readme_fn"

printf "\n## get_comment_text.py\n\n" >>"$readme_fn"
./get_comment_text.py -h | sed 's/^/    /' >>"$readme_fn"

printf "\n## word_frequency.py\n\n" >>"$readme_fn"
./word_frequency.py -h | sed 's/^/    /' >>"$readme_fn"

echo '' >>"$readme_fn"
cat nltk-required-packages.md >>"$readme_fn"

