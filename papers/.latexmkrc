# pdfLaTeX + biber; aux files go to ./build
$pdf_mode = 1;
$bibtex_use = 2;
$out_dir = 'build';
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$xelatex  = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$lualatex = 'lualatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$biber = 'biber %O %S';
