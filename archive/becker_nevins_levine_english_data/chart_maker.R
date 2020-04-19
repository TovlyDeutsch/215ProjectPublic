
chartmode = "pdf"
chartmode = "screen"
#myfont = "Doulos SIL"; pointsize=10
myfont = "Linux Biolinum"; pointsize=12
myfont = "Linux Libertine"; pointsize=12
quartz.fnc = function(cwidth,cheight,cname) {
	if(chartmode=="screen") {
		quartz(width=cwidth,height=cheight)
	}
	if(chartmode=="pdf") {
		quartz(width=cwidth,height=cheight,type="pdf",file=cname)
	}
}
