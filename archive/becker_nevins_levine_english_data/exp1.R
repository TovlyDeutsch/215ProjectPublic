source("chart_maker.R")
source("mer-utils.txt")
exp1 = read.csv("exp1.csv")
meta1 = read.csv("exp1meta.csv")

exp1$shape_group = factor(exp1$shape_group, levels=c("P","_P","P_"))





# descriptive stats:
with(subset(exp1, type=="stim"), aggregate(rating.pl, list(shape_group), mean ))
with(subset(exp1, type=="stim"), aggregate(rating.pl, list(heavy), mean ))
with(subset(exp1, type=="stim"), aggregate(rating.pl, list(heavy ,shape_group), mean ))
with(subset(exp1, type=="stim"), aggregate(rating.pl, list(complex), mean ))
with(subset(exp1, type=="stim"), aggregate(rating.pl, list(complex ,shape_group), mean ))




# results  by item 
items = with(subset(exp1, type=="stim"), aggregate(rating.pl, list(item), mean));
colnames(items) = c("item", "voice")
items = merge(items, unique(exp1[,c("item","shape_group")]))
quartz.fnc(cwidth=12,cheight=6,cname="r.exp1.items.pdf")
par(family=myfont,ps=pointsize,mar=c(5,10,2,1),mfrow=c(1,1));
plot(c(1,2,3),c(1,7,7), type="n", xlim=c(.6,3.4), xaxt="n", xlab="", yaxt="n", ylab="", cex.lab=2); 
axis(1, at=1:3, cex.axis=1.7, c("monosyllable", "iamb", "trochee")); 
axis(2, at=c(1,7),  c("faithful","voiced"), cex.axis=2, xpd=F, tick=F, las=1,line=3); 
axis(2, at=seq(1,7,1),  paste(seq(1,7,1),"",sep=""), cex.axis=1.7, xpd=F, las=1); 
jamount=.3;
text(jitter(rep(1, nrow(subset(items, shape_group=="P"))), amount=jamount), subset(items, shape_group=="P")$voice, label= subset(items, shape_group=="P")$item, cex=1.4);
text(jitter(rep(2, nrow(subset(items, shape_group=="_P"))), amount=jamount), subset(items, shape_group=="_P")$voice, label= subset(items, shape_group=="_P")$item, cex=1.4);
text(jitter(rep(3, nrow(subset(items, shape_group=="P_"))), amount=jamount), subset(items, shape_group=="P_")$voice, label= subset(items, shape_group=="P_")$item, cex=1.4);
if (chartmode=="pdf") {dev.off()}





# items: voiciness vs. freq
items = with(subset(exp1, type=="stim"), aggregate(rating.pl, list(item[drop=T]), mean));
colnames(items) = c("item", "rating")
freq = with(subset(exp1, type=="stim"), aggregate(freq, list(item[drop=T]), mean));
colnames(freq) = c("item", "freq")
items = merge(items, freq)
items = merge(items, unique(exp1[,c("item","shape_group")]))
items = merge(items, unique(exp1[,c("item","place")]))
items = merge(items, unique(exp1[,c("item","heavy")]))
items = items[order(items$rating),]
with(items, aggregate(freq, list(shape_group), mean))
t.test(items[items$shape_group=="P",]$freq, items[items$shape_group!="P",]$freq)
#
quartz.fnc(cwidth=12,cheight=6,cname="r.english.freq.pdf")
par(family=myfont,ps=pointsize,mar=c(5,10,2,1),mfrow=c(1,1));
plot(rating ~ freq, data=items, type="n", xlab="(log) token frequency", ylab="", yaxt="n", cex.axis=1.8, cex.lab=2);text(items $rating ~ items $freq, label= items $item, cex=1); 
#axis(2, at=c(1,7), c("voiceless","voiced"), cex.axis=2); axis(2, at=2:6, rep("",5))
axis(2, at=c(1,7),  c("faithful","voiced"), cex.axis=2, xpd=F, tick=F, las=1,line=3); 
axis(2, at=seq(1,7,1),  paste(seq(1,7,1),"",sep=""), cex.axis=1.7, xpd=F, las=1); 
lines(lowess(items $rating ~ items $freq))
if (chartmode=="pdf") {dev.off()}
#
quartz.fnc(cwidth=8,cheight=6,cname="r.english.freq.otherway.pdf")
par(family=myfont,ps=pointsize,mar=c(5,5,2,1),mfrow=c(1,1));
items$fitted = fitted(lm(freq ~ poly(rating,2), data= items))
plot(freq ~ rating, data= items, xaxt="n", xlab="", type="n", cex.axis=1.8,  ylab="(log) token frequency", cex.lab=2, xlim=c(.95,7.05)); axis(1, at=c(1,7), c("voiceless","voiced"), cex.axis=2); text(items $freq ~ items $rating, label= items $item, cex=1);
lines(items $fitted ~ items $rating)
if (chartmode=="pdf") {dev.off()}




# BAR PLOT
library(plotrix)
p = with(subset(exp1, type=="stim"), aggregate(rating.pl, list(shape_group), mean))
names(p)=c("shape","voicing")
p$voicing = p$voicing-1
p$up   = p$voicing + with(subset(exp1, type=="stim"), aggregate(rating.pl, list(shape_group), std.error))$x*1.96
p$down = p$voicing - with(subset(exp1, type=="stim"), aggregate(rating.pl, list(shape_group), std.error))$x*1.96
quartz.fnc(cwidth=8,cheight=6,cname="r.exp1.barplot.pdf")
par(family=myfont,ps=pointsize,mar=c(5,10,2,1),mfrow=c(1,1));
barplot(p$voicing, ylim=c(0,6),  names.arg=c("mono","iamb", "trochee"), cex.names=2, ylab="", cex.lab=2, col="gray90", yaxt="n");
axis(2, at=c(0,6),  c("faithful","voiced"), cex.axis=2, xpd=F, tick=F, las=1,line=3); 
axis(2, at=seq(0,6,1),  paste(seq(1,7,1),"",sep=""), cex.axis=1.7, xpd=F, las=1); 
x=c(.5+.2,1.5+.4,2.5+.6);arrows(x,p$down,x,p$up, angle=90, length=.3, code=3)
if (chartmode=="pdf") {dev.off()}








### regressions
library(lme4)
exp1 = subset(exp1, type=="stim")
exp1$c.place = scale(as.numeric(exp1$place))
exp1$c.complex = scale(as.numeric(exp1$complex))
exp1$c.heavy = scale(as.numeric(exp1$heavy))
exp1$c.freq = scale(exp1$freq)
# helmert
exp1$c.shape1 = scale(ifelse(exp1$shape_group=="P" ,-1/2,
+                     ifelse(exp1$shape_group =="_P",1/2,0)))
exp1$c.shape2 = scale(ifelse(exp1$shape_group=="P" ,-1/3, 
+                     ifelse(exp1$shape_group =="_P",-1/3,2/3)))


lmer1 = lmer(rating.pl ~ c.heavy + c.shape1 + c.shape2 +
+ (1 + c.heavy + c.shape1 + c.shape2|item) + (1 + c.heavy + c.shape1 + c.shape2|participant), data=exp1)

kappa.mer(lmer1);max(vif.mer(lmer1));maxcorr.mer(lmer1)















































