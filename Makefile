all: svg pdf png

svg: sol.bare.svg sol.en.svg sol.fr.svg

sol.bare.svg: sol.py
	./sol.py '' > $@

sol.en.svg: sol.py
	./sol.py en > $@

sol.fr.svg: sol.py
	./sol.py fr > $@

pdf: sol.bare.pdf sol.en.pdf sol.fr.pdf

%.pdf: %.svg
	inkscape -A $@ $<

png: sol.bare.small.png sol.en.small.png sol.fr.small.png
png: sol.bare.large.png sol.en.large.png sol.fr.large.png

%.small.png: %.svg
	inkscape -e $@ $< -w 1080

%.large.png: %.svg
	inkscape -e $@ $< -w 14400

clean:
	rm -f sol.bare.svg sol.en.svg sol.fr.svg
	rm -f sol.bare.pdf sol.en.pdf sol.fr.pdf
	rm -f sol.bare.small.png sol.en.small.png sol.fr.small.png
	rm -f sol.bare.large.png sol.en.large.png sol.fr.large.png

.PHONY: all svg pdf png clean
