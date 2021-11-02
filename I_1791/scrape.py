import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm


##########################################################################
# THIS SHOULD SERVE ONLY FOR PRELIMINARY TEXT PROCESSING                 #
# CORRECTIONS BY HAND WERE NECESSARY TO GENERATE THE FINAL .tex DOCUMENT #
##########################################################################


numerator_regex = re.compile(r"\d+\)")

full_text = r"""
\documentclass{book}
\usepackage[utf8]{inputenc}
\usepackage[polish]{babel}
\usepackage{polski}
\begin{document}
"""

for chapter in tqdm(range(12)):
    addr=f"http://libr.sejm.gov.pl/tek01/txt/kpol/1791-r{chapter}.html"
    response = requests.get(addr)
    soup = BeautifulSoup(response.content, parser="html.parser")
    sec_title = soup.find("h2").text.strip().replace("\n", " ")
    full_text += f"\n\section*{{{sec_title}}}" 
    footnotes = soup.findAll(lambda tag: tag.name=="a" and "name" in tag.attrs and tag.attrs["name"].startswith("p"))
    footnote_contents = {f.attrs["name"]: numerator_regex.sub("", f.text) for f in footnotes}
    pars = soup.findAll("p") 
    if len(pars) > 1:
        for par in pars:
            a_s = par.findAll("a")
            for a in a_s:
                footnote_number = a.get("href").lstrip("#")
                replaced = f"\\footnote{{{footnote_contents[footnote_number]}}}"
                a.replaceWith(replaced)
            par_text = par.text.replace("\n", ' ')
            full_text += f"\n\n{par_text}"
    else:
        # some text is not contained within <p>
        pass
    

full_text += "\n\end{document}"

with open("main.tex", "w") as f:
    f.write(full_text)
