getwd()
library(rmarkdown)
rmarkdown:::convert_ipynb(input='Codigos_Python.ipynb',
                        output = xfun::with_ext('Codigos_Python.ipynb', "Rmd"))
