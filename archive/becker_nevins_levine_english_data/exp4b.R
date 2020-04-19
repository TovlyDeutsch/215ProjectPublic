source("chart_maker.R")
source("mer-utils.txt")
exp4b = read.csv("exp4b.csv")
exp4b$group = factor(exp4b$group, levels=c("trochee","iamb"))
exp4b$shape = factor(exp4b$shape, levels=c("trochee","iamb"))

exp4b = subset(exp4b, view=="test.ejs" & vowel!="a")
exp4b$opposite = exp4b$group != exp4b$shape


exp4bm = subset(exp4b, responseShapeMatch)



prop.table(xtabs(~ responseShapeMatch, data=exp4b))
prop.table(xtabs(~ success, data=exp4b))
prop.table(xtabs(~ success2, data=exp4b))



# BAR PLOT
library(plotrix)
p = with(exp4b, aggregate(success2, list(group, shape), mean))
names(p)=c("group", "shape","umlaut")
p$up   = p$umlaut + with(exp4b, aggregate(success2, list(group, shape), std.error))$x*1.96
p$down = p$umlaut - with(exp4b, aggregate(success2, list(group, shape), std.error))$x*1.96
quartz.fnc(cwidth=12,cheight=6,cname="r.exp4b.barplot.pdf")
par(family=myfont,ps=pointsize,mar=c(5,4,3,1),mfrow=c(1,2), oma=c(0,4,0,0))
barplot(p[p$group=="trochee",]$umlaut, ylim=c(0,.52), yaxt="n", main="Trochaic training group", cex.main=2, names.arg=c("trochee","iamb"), cex.names=2, ylab="", cex.lab=2, col="gray90");
axis(2, at=.25, "application of umlaut", tick=F, line=5, cex.axis=2, xpd=T)
axis(2, at=seq(0,.5,.1),  paste(seq(0,.5,.1)*100,"%",sep=""), cex.axis=1.7, xpd=F, las=1); x=c(.7,1.9);arrows(x,p[p$group=="trochee",]$down,x,p[p$group=="trochee",]$up, angle=90, length=.3, code=3)
barplot(p[p$group=="iamb",]$umlaut, ylim=c(0,.52), yaxt="n", main="Iambic training group", cex.main=2, names.arg=c("trochee","iamb"), cex.names=2, col="gray90");
axis(2, at=seq(0,.5,.1),  paste(seq(0,.5,.1)*100,"%",sep=""), cex.axis=1.7, xpd=F, las=1); x=c(.7,1.9); arrows(x,p[p$group=="iamb",]$down,x,p[p$group=="iamb",]$up, angle=90, length=.3, code=3)
if (chartmode=="pdf") {dev.off()}







troc = xtabs(success2 ~ userCode[drop=T] + opposite, data=subset(exp4b,group=="trochee"))
iamb = xtabs(success2 ~ userCode[drop=T] + opposite, data=subset(exp4b,group=="iamb"))

t.test(troc[,1],troc[,2], paired=T)
t.test(iamb[,1], iamb[,2], paired=T)
t.test(iamb[,1]-iamb[,2], troc[,1]-troc[,2])



library(lme4)
exp4b$c.group = scale(as.numeric(exp4b$group))
exp4b$c.opposite = scale(as.numeric(exp4b$opposite))

lmer4b = lmer(success2 ~ c.group*c.opposite + (1+c.group*c.opposite|userCode) + (1+c.group*c.opposite|IPA), family="binomial", data=exp4b)

kappa.mer(lmer4b);max(vif.mer(lmer4b));maxcorr.mer(lmer4b)





# good responses only

exp4bm$c.group = scale(as.numeric(exp4bm$group))
exp4bm$c.opposite = scale(as.numeric(exp4bm$opposite))

lmer4bm = lmer(success2 ~ c.group*c.opposite + (1+c.group*c.opposite|userCode) + (1+c.group*c.opposite|IPA), family="binomial", data=exp4bm)

kappa.mer(lmer4bm);max(vif.mer(lmer4bm));maxcorr.mer(lmer4bm)



































