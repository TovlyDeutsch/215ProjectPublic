source("chart_maker.R")
source("mer-utils.txt")
exp4a = read.csv("exp4a.csv")
exp4a$group = factor(exp4a$group, levels=c("trochee","iamb"))
exp4a$shape = factor(exp4a$shape, levels=c("trochee","iamb"))

exp4a = subset(exp4a, experiment_phase=="testing" & vowel!="a")
exp4a$opposite = exp4a$group != exp4a$shape
exp4am = subset(exp4a, responseShapeMatch)


# descriptive
xtabs(success2 ~ group + opposite, data=exp4a)
xtabs(success2 ~ group + opposite, data=exp4a)/xtabs(~ group + opposite, data=exp4a)

with(exp4a, aggregate(success2, list(group, opposite), mean))


# t-tests
troc = xtabs(success2 ~ participant.code[drop=T] + opposite, data=subset(exp4a,group=="trochee"))
iamb = xtabs(success2 ~ participant.code[drop=T] + opposite, data=subset(exp4a,group=="iamb"))
t.test(troc[,1], iamb[,1])
t.test(troc[,2], iamb[,2])
t.test(troc[,1]-troc[,2], iamb[,1]-iamb[,2])





# BAR PLOT
library(plotrix)
p = with(exp4a, aggregate(success2, list(group, shape), mean))
names(p)=c("group", "shape","umlaut")
p$up   = p$umlaut + with(exp4a, aggregate(success2, list(group, shape), std.error))$x*1.96
p$down = p$umlaut - with(exp4a, aggregate(success2, list(group, shape), std.error))$x*1.96
quartz.fnc(cwidth=12,cheight=6,cname="r.exp4a.barplot.pdf")
par(family=myfont,ps=pointsize,mar=c(5,4,3,1),mfrow=c(1,2), oma=c(0,4,0,0))
barplot(p[p$group=="trochee",]$umlaut, ylim=c(0,.52), yaxt="n", main="Trochaic training group", cex.main=2, names.arg=c("trochee","iamb"), cex.names=2, ylab="", cex.lab=2, col="gray90");
axis(2, at=.25, "application of umlaut", tick=F, line=5, cex.axis=2, xpd=T)
axis(2, at=seq(0,.5,.1),  paste(seq(0,.5,.1)*100,"%",sep=""), cex.axis=1.7, xpd=F, las=1); x=c(.7,1.9);arrows(x,p[p$group=="trochee",]$down,x,p[p$group=="trochee",]$up, angle=90, length=.3, code=3)
barplot(p[p$group=="iamb",]$umlaut, ylim=c(0,.52), yaxt="n", main="Iambic training group", cex.main=2, names.arg=c("trochee","iamb"), cex.names=2, col="gray90");
axis(2, at=seq(0,.5,.1),  paste(seq(0,.5,.1)*100,"%",sep=""), cex.axis=1.7, xpd=F, las=1); x=c(.7,1.9); arrows(x,p[p$group=="iamb",]$down,x,p[p$group=="iamb",]$up, angle=90, length=.3, code=3)
if (chartmode=="pdf") {dev.off()}





# regressions
library(lme4)
exp4a$c.group = scale(as.numeric(exp4a$group)-1, scale=F)
exp4a$c.opposite = scale(as.numeric(exp4a$opposite), scale=F)



lmer4 = lmer(success2 ~ c.group*c.opposite + (1+c.group*c.opposite| participant.code) + (1|IPA), family="binomial", data=exp4a)

kappa.mer(lmer4);
max(vif.mer(lmer4));
maxcorr.mer(lmer4)


# just the good responses
exp4am$c.group = scale(as.numeric(exp4am$group))
exp4am$c.opposite = scale(as.numeric(exp4am$opposite))

lmer4m = lmer(success ~ c.group * c.opposite + (1| participant.code) + (1|IPA), family="binomial", data= exp4am)

kappa.mer(lmer4m);
max(vif.mer(lmer4m));
maxcorr.mer(lmer4m)


































