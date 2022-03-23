! PROGRAM SIVINPUT. Fortran-77. For generating input deck to
! Sivells nozzle design code (AEDC-TR-78-63).
!
! emailed back ‘From moen Wed Nov 25 12:00:09 1992’ after use by him.
!
! this program writes an input file in the correct format for
! sivells code; sps 6-27-90
! modified 9-30-92 for the square nozzle work with streamlines sps
! modified to produce starting streamlines on nozzle wall.
! mod sps 11-30-92 to make mp=5
! mod 11-30 sps to allow choices of IN, XC, IX
! add header info. 1-16-95, this is the current version used by Alcenius
! for his MS thesis and square nozzle computations (see appendix of
! Alcenius MS thesis).

character*10 title
character*20 sivfile

write (*,*) ’enter a rootname to write sivells input file:’
read (*,10) sivfile
title = sivfile
ileng = index(sivfile,’ ’) -1
sivfile(ileng+1:ileng+4) = ’.inp’
write (*,*) ’opening file-’,sivfile,’-for output’
open(unit=2,file=sivfile,status=’new’)

write (*,*) ’enter title of run (10 characters): ’
read (*,20) title
write (*,*) ’enter jd (-1=2D, 0=axisym): ’
read (*,*) jd
write (2,30) title,jd
write (*,*) ’enter sfoa:’
read (*,*) sfoa
sfoa=0. !use 3rd or 4th degree distribution
gam = 1.40
ar = 1716.563
zo=1
! following three used in bl computations, not used here
ro=1
visc=1
vism=1

xbl=1000. !gives values at evenly spaced intervals
write (2,40) gam,ar,zo,ro,visc,vism,sfoa,xbl

write (*,*) ’enter etad,rc,bmach,cmc: ’

read (*,*) etad,rc,bmach,cmc
xc=0. !so 4th degree distribution, change?
write (*,*) ’enter xc, in: ’
read (*,*) xc,in
write (*,*) ’xc,in= ’,xc,in
fmach=0. !this sets distribution, change?
sf = 0. !nozzle throat radius = 1.0
pp = 0. !coordinates given relative to throat
write (2,50) etad,rc,fmach,bmach,cmc,sf,pp,xc
write (*,*) ’enter mt,nt,ix,in,md,nd,nf,mp,jc,lr,nx:’
read (*,*) mt,nt,ix,in,md,nd,nf,mp,jc,lr,nx
mt=61 !pts on char. EG, max 125
nt=31 !pts on axis IE, max 149-LR
write (*,*) ’enter ix: ’
read (*,*) ix
ix=0 !is 3rd deriv matched? change?
in=10 !use Mach no. distrib on BC, makes 2nd deriv match rad. flow change?
iq=0 !calls for complete contour
md=61 !pts on char. AB, max about 125, odd
nd=15 !pts on axis BC, max about 150,
! changed from 49 to 15 sps 7-2-90
write (*,*) ’enter -1 for smoothing, 1 for no smoothing: ’
read (*,*) ismooth
nf=ismooth*81 !pts on characteristic CD. Neg calls for smoothing
mp=5 !pts on GA, conical section, if Fmach ne Bmach
jc=0 !if not 0, used to print intermediate characteristics
lr=31 !pts on throat char., - prints out transonic soln
nx=13 !spacing of pts on axis upstream, this no. recc.
mq=0 !pts downstream of D
jb=-1 !neg for no BL computation
jx=1 !pos calls for streamlines
it=0 !jack points, not used
write (2,60) mt,nt,ix,in,iq,md,nd,nf,mp,mq,jb,jx,jc, it,lr,nx

if (ismooth .eq. -1) then
noup=10 !smoothing parameters, arbitrary
nodo=10
npct=90
write (2,70) noup,npct,nodo
    end if

! gives streamline distribution that corresponds
! to the half wall for conversion to a square nozzle.
! note that the number of streamlines requested will
! be reduced by one because Sivells automatically
! calculates the wall streamline. Sivells output
! will have the actual number of streamlines requested.
! (moen 10-92)
!
write (*,*) ’How many streamlines along halfwall?’
read (*,*) nstream
nstream=nstream-1
dx=1.0/(float(nstream)*sqrt(2.0))
ycnt=1.0/sqrt(2.0)
do 100 istream = 0,nstream-1
etadstr = etad*sqrt((istream*dx)**2+ycnt**2) !see btm page 59
qm = sqrt((istream*dx)**2+ycnt**2)
xj = 1 !look for more streamlines
write (2,90) etadstr,qm,xj
if (ismooth .eq. -1) then
write (2,70) noup,npct,nodo !must have for each!!
end if

continue

close(2)
stop
format(a20)
format(a10)
format(1x,a10,2x,i2)
format(8(1x,f9.3))
format(8(1x,f9.3))
format(1x,i4,15(i5))
format(1x,i4,2(i5))
format(3(1x,f9.4),1x)
end