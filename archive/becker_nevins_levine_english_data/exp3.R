source("chart_maker.R")
source("mer-utils.txt")
exp3 = read.csv("exp3.csv")
exp3$shape = factor(exp3$shape, levels=c("mono","iamb"))
exp3$group = factor(exp3$group, levels=c("mono","iamb"))


exp3 = subset(exp3, experiment_phase=="testing" & consonant != "W")
exp3v = subset(exp3, response!="")
exp3m = subset(exp3, match)


#descriptive
# how many responses had -ni?
length(grep("ni$", exp3$plural_response))/length(exp3$plural_response)
xtabs(voiced ~ group + opposite, data= exp3)
xtabs(voiced ~ group + opposite, data= exp3)/xtabs(~ group + opposite, data=exp3)




# BAR PLOT
library(plotrix)
p = with(exp3, aggregate(voiced, list(group, shape), mean))
names(p)=c("group", "shape","voicing")
p$up   = p$voicing + with(exp3, aggregate(voiced, list(group, shape), std.error))$x*1.96
p$down = p$voicing - with(exp3, aggregate(voiced, list(group, shape), std.error))$x*1.96
quartz.fnc(cwidth=12,cheight=6,cname="r.exp3.barplot.pdf")
par(family=myfont,ps=pointsize,mar=c(5,4,3,1),mfrow=c(1,2), oma=c(0,4,0,0))
barplot(p[p$group=="mono",]$voicing, ylim=c(0,.651), yaxt="n", main="Monosyllabic training group", cex.main=2, names.arg=c("mono","iamb"), cex.names=2, ylab="", cex.lab=2, col="gray90");
axis(2, at=.3, "application of voicing", tick=F, line=5, cex.axis=2, xpd=T)
axis(2, at=seq(0,.6,.2),  paste(seq(0,.6,.2)*100,"%",sep=""), cex.axis=1.7, xpd=F, las=1); x=c(.7,1.9);arrows(x,p[p$group=="mono",]$down,x,p[p$group=="mono",]$up, angle=90, length=.3, code=3)
barplot(p[p$group=="iamb",]$voicing, ylim=c(0,.651), yaxt="n", main="Iambic training group", cex.main=2, names.arg=c("mono","iamb"), cex.names=2, col="gray90");
axis(2, at=seq(0,.6,.2),  paste(seq(0,.6,.2)*100,"%",sep=""), cex.axis=1.7, xpd=F, las=1); x=c(.7,1.9); arrows(x,p[p$group=="iamb",]$down,x,p[p$group=="iamb",]$up, angle=90, length=.3, code=3)
if (chartmode=="pdf") {dev.off()}






#boxplot(mono[,1]-mono[,2],iamb[,2]-iamb[,1])


# regression
library(lme4)
exp3$c.group = scale(as.numeric(exp3$group))
exp3$c.opposite = scale(as.numeric(exp3$opposite))
exp3v$c.group = scale(as.numeric(exp3v$group))
exp3v$c.opposite = scale(as.numeric(exp3v$opposite))
exp3m$c.group = scale(as.numeric(exp3m$group))
exp3m$c.opposite = scale(as.numeric(exp3m$opposite))




# all data points
lmer3 = lmer(voiced ~ c.group*c.opposite + (1+c.group*c.opposite | participant.code) + (1+c.group*c.opposite|IPA), family="binomial", data=exp3) 

kappa.mer(lmer3);
max(vif.mer(lmer3));
maxcorr.mer(lmer3)

# valid data points
lmer3v = lmer(voiced ~ c.group*c.opposite + (1+c.group*c.opposite|participant.code) + (1+c.group*c.opposite|IPA), family="binomial", data=exp3v)

kappa.mer(lmer3v);
max(vif.mer(lmer3v));
maxcorr.mer(lmer3v)

# matching data points
lmer3m = lmer(voiced ~ c.group*c.opposite + (1+c.group*c.opposite|participant.code) + (1+c.group*c.opposite|IPA), family="binomial", data=exp3m)

kappa.mer(lmer3m);
max(vif.mer(lmer3m));
maxcorr.mer(lmer3m)







































