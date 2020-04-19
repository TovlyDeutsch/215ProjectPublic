source("chart_maker.R")
source("mer-utils.txt")
exp2 = read.csv("exp2.csv")
meta2 = read.csv("exp2meta.csv")
exp2$shape = factor(exp2$shape, levels=c("mono","iamb","trochee"))




# descriptive
with(subset(exp2, type=="stim"), aggregate(rating1, list(shape), mean))
with(subset(exp2, type=="stim"), aggregate(rating1, list(weight), mean))
with(subset(exp2, type=="stim"), aggregate(rating1, list(weight,shape), mean))



# by item chart
items = with(subset(exp2, type=="stim"), aggregate(rating1, list(item), mean));
colnames(items) = c("item","voice")
items = items[order(items$voice),]; 
items = merge(items, unique(exp2[,c("item","shape")]))
items = merge(items, unique(exp2[,c("item","IPA")]))
#
quartz.fnc(cwidth=12,cheight=6,cname="r.exp2.byitem.pdf")
par(family=myfont,ps=pointsize,mar=c(5,10,2,1),mfrow=c(1,1));
plot(c(1,2,3),c(1,7,7), type="n", xlim=c(.6,3.4), xaxt="n", xlab="", yaxt="n", ylab="", cex.lab=2); 
axis(2, at=c(1,7),  c("faithful","voiced"), cex.axis=2, xpd=F, tick=F, las=1,line=3); 
axis(2, at=seq(1,7,1),  paste(seq(1,7,1),"",sep=""), cex.axis=1.7, xpd=F, las=1); 
axis(1, at=1:3, cex.axis=1.7, c("monosyllable", "iamb", "trochee")); jamount=.3;
text(jitter(rep(1, nrow(subset(items, shape=="mono"))), amount=jamount), subset(items, shape=="mono")$voice, label= subset(items, shape=="mono")$IPA, cex=1.4);
text(jitter(rep(2, nrow(subset(items, shape=="iamb"))), amount=jamount),subset(items, shape=="iamb")$voice, label= subset(items, shape=="iamb")$IPA, cex=1.4);
text(jitter(rep(3, nrow(subset(items, shape=="trochee"))), amount=jamount),subset(items, shape=="trochee")$voice, label= subset(items, shape=="trochee")$IPA, cex=1.4)
if (chartmode=="pdf") {dev.off()}



# BAR PLOT
library(plotrix)
p = with(subset(exp2, type=="stim"), aggregate(rating1, list(shape), mean))
names(p)=c("shape","voicing")
p$voicing = p$voicing-1
p$up   = p$voicing + with(subset(exp2, type=="stim"), aggregate(rating1, list(shape), std.error))$x*1.96
p$down = p$voicing - with(subset(exp2, type=="stim"), aggregate(rating1, list(shape), std.error))$x*1.96
quartz.fnc(cwidth=8,cheight=6,cname="r.exp2.barplot.pdf")
par(family=myfont,ps=pointsize,mar=c(5,10,2,1),mfrow=c(1,1));
barplot(p$voicing, ylim=c(0,6),  names.arg=c("mono","iamb", "trochee"), cex.names=2, ylab="", cex.lab=2, col="gray90", yaxt="n");
axis(2, at=c(0,6),  c("faithful","voiced"), cex.axis=2, xpd=F, tick=F, las=1,line=3); 
axis(2, at=seq(0,6,1),  paste(seq(1,7,1),"",sep=""), cex.axis=1.7, xpd=F, las=1); 
x=c(.5+.2,1.5+.4,2.5+.6);arrows(x,p$down,x,p$up, angle=90, length=.3, code=3)
if (chartmode=="pdf") {dev.off()}


### regression
library(lme4)
exp2 = subset(exp2, type=="stim")
exp2$c.place = scale(as.numeric(exp2$place))
exp2$c.weight = scale(as.numeric(exp2$weight))

exp2$c.shape1 = scale(ifelse(exp2$shape=="mono",-1/2,ifelse(exp2$shape =="iamb",1/2,0)))
exp2$c.shape2 = scale(ifelse(exp2$shape=="mono",-1/3,ifelse(exp2$shape =="iamb",-1/3,2/3)))


#lmer2.p = lmer(rating1 ~ (c.shape1+c.shape2)*c.weight+c.place + (1|item) + (1+(c.shape1+c.shape2)*c.weight+c.place |participant), data=exp2)

#lmer2.i = lmer(rating1 ~ (c.shape1+c.shape2)*c.weight+c.place + (1+c.shape1+c.shape2+c.weight|item) + (1+c.shape1+c.shape2+c.weight|participant), data=exp2)
kappa.mer(lmer2.i);max(vif.mer(lmer2.i));maxcorr.mer(lmer2.i)


lmer2.p = lmer(rating1 ~ (c.shape1+c.shape2)*c.weight+c.place + (1+(c.shape1+c.shape2)*c.weight|item) + (1+(c.shape1+c.shape2)*c.weight|participant), data=exp2)
kappa.mer(lmer2.p);max(vif.mer(lmer2.p));maxcorr.mer(lmer2.p)




































