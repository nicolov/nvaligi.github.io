(TeX-add-style-hook
 "fgraph_singlemarker"
 (lambda ()
   (TeX-run-style-hooks
    "latex2e"
    "standalone"
    "standalone10"
    "pgfplots"))
 :latex)

