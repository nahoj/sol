all: svg pdf png

svg: sol.en.svg sol.fr.svg

sol.en.svg: sol.py
	./sol.py en > sol.en.svg

sol.fr.svg: sol.py
	./sol.py fr > sol.fr.svg

pdf: sol.en.pdf sol.fr.pdf

%.pdf: %.svg
	inkscape -A $@ $<

png: sol.en.small.png sol.fr.small.png sol.en.large.png sol.fr.large.png

%.small.png: %.svg
	inkscape -e $@ $< -w 1080

%.large.png: %.svg
	inkscape -e $@ $< -w 14142

clean:
	rm -f sol.en.svg sol.fr.svg sol.en.pdf sol.fr.pdf
	rm -f sol.en.small.png sol.fr.small.png sol.en.large.png sol.fr.large.png

.PHONY: all svg pdf png clean
