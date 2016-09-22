PROGRAM MainGrib

  IMPLICIT NONE

  ! ************** DECLARATIONS *****************

  INTEGER nprx, npry, nprz
  INTEGER, DIMENSION(20) :: LEVPR
  REAL, DIMENSION(232) :: ylev

  REAL :: WPLON, SPLAT, spcnprx, spcnpry

  CHARACTER(LEN=50) :: fprefix
  CHARACTER(LEN=128) :: ifnpress 

  NAMELIST/data_prep/nprx,npry,nprz,levpr,wplon,splat, &
    &      spcnprx,spcnpry,fprefix,ifnpress,ylev

  INTEGER, PARAMETER :: maxfiles=2000

  CHARACTER(LEN=128), DIMENSION(maxfiles) :: fnames
  INTEGER :: nfile

  INTEGER :: i

  ! ************** PROCEDURE BODY ***************


  !-----------------------------------------------------------------
  !        Read input DPREP namelists
  !-----------------------------------------------------------------

      !! open(1,file='PREP_IN-T213',status='old')
      open(1,file='PREP_IN',status='old')
      read(1,data_prep)
      close(1)

  !-----------------------------------------------------------------
  !        Getting GRIB file names
  !-----------------------------------------------------------------

  CALL GRIB_filelist(fnames,nfile,fprefix)

  !-----------------------------------------------------------------
  !        Read pressure data from GRIB files
  !-----------------------------------------------------------------


  DO i = 1, nfile
      CALL MakeDP(i,fnames(i),nprx,npry,nprz,5  &
          &    ,splat,wplon,spcnprx,spcnpry,levpr,ylev,ifnpress)
  ENDDO

END PROGRAM MainGrib
!
! ******************************************************************
!
SUBROUTINE MakeDP(nfile,fname,nx,ny,nz,nvar,splat,wplon,spcnprx,spcnpry &
   &             ,levpr,ylev,ifnpress)

  IMPLICIT NONE

  ! *************** DUMMY ARGUMENTS ************
  INTEGER,INTENT(IN) :: nfile
  CHARACTER(LEN=128), INTENT(IN) :: fname
  INTEGER, INTENT(IN) :: nx,ny,nz,nvar
  REAL, INTENT(IN) :: splat, wplon, spcnprx, spcnpry
  INTEGER, INTENT(IN), DIMENSION(nz) :: levpr
  REAL, INTENT(IN), DIMENSION(ny) :: ylev
  CHARACTER(LEN=*),INTENT(IN) :: ifnpress 

  ! ************** DECLARATIONS *****************


  REAL :: elon, tnlat
  INTEGER :: iyear, imonth, idate, ihour, ivar, level, nlat, nlon

  CHARACTER(LEN=32)  :: fnamesout
  CHARACTER(LEN=200) :: command
  INTEGER, DIMENSION(8) :: header 
  CHARACTER(LEN=80) :: locfn 

  REAL, DIMENSION(nx,ny,nz,nvar) :: p
  REAL, DIMENSION(nx,ny-1,nz,nvar) :: pLin

  REAL, DIMENSION(nx,ny,5) :: pisfc  !manter compatibilidade com o dprep 

  INTEGER :: nc, aux, DIAMES(12)
  INTEGER :: i,j,k,l,ih
  
  DATA DIAMES /31,28,31,30,31,30,31,31,30,31,30,31/

  ! ************** PROCEDURE BODY ***************

  !--------------------------------------------------
  ! Convert each grb file to txt file
  !--------------------------------------------------

  PRINT 81
81 FORMAT(//,1X,70('-')/  &
       &    ,'  Converting binary Grib file to ASCII Grib file',/  &
       &    ,1X,70('-')//)

  fnamesout=fname(1:28)//'.txt'
  !!command=   &
  !!     &     './grbconv-T213 -i '//fname//' -o '//fnamesout//' -t cona'

  command=   &
       &     './grbconv.x -i '//fname//' -o '//fnamesout//' -t cona'

  CALL system(command)

  !Debug
  !     print *,'comand = ',command
  !Debug

  !--------------------------------------------------
  ! Reading from txt file
  !--------------------------------------------------

  PRINT *,'nFile: ', nfile, '   File: ',fnamesout
  OPEN(10,file=fnamesout,status='unknown',form='formatted')

  CALL Le_Header (10,header)

  ivar = header(1)
  level = header(2)
  iyear = header(3)/10000
  imonth = (header(3) - iyear*10000) /100
  idate = header(3) - (header(3)/100)*100
  ihour = header(4)
  nlon = header(5)
  nlat = header(6)
  write(*,*)'ano=',iyear,' mes=',imonth,' dia=',idate,' hora=',ihour

  ! Hallak - corecao das datas no nome do dp
  aux = ihour / 24
  ihour = MOD(ihour,24)
  IF (MOD(iyear,4) .EQ. 0) DIAMES(2)=29
  DO IH=1,aux
  idate = idate + 1
  IF (idate .GT. DIAMES(imonth)) THEN
  idate=1
  imonth=imonth+1
  IF (imonth .GT. 12) THEN
  imonth=1
  iyear=iyear+1
  ENDIF
  ENDIF
  ENDDO
  write(*,*)'ano0=',iyear,' mes0=',imonth,' dia0=',idate,' hora0=',ihour    
  ! Hallak

  REWIND(10)

  CALL prstage_GRIB(10,nx,ny,nz,nvar,p)

  CLOSE(10)

  !--------------------------------------------------
  ! Linear Interpolation
  !--------------------------------------------------

  CALL interpolate(nx,ny,nz,nvar,p,pLin,SPLAT,spcnpry,ylev,levpr)

  !--------------------------------------------------
  ! Make the DP file
  !--------------------------------------------------

  nc=INDEX(ifnpress,' ')-1

  WRITE(locfn,'(a,i4.4,a1,i2.2,a1,i2.2,a1,i4.4)' )            &
       &       ifnpress(1:nc),iyear,'-',imonth,'-',idate,'-'  &
       &      ,ihour*100

  !Debug
  !    print *,'DP file name =',locfn
  !Debug

  ELON=WPLON+(NX-1)*SPCNPRX
  TNLAT=SPLAT+(NY-2)*SPCNPRY

  IF(elon.GT.360. .OR. tnlat .GT. 90.) THEN
      PRINT*,'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
      PRINT*,'!!! BAD DOMAIN SPECIFICATION   !!'
      PRINT*,'!!! Latitude - ',splat,tnlat
      PRINT*,'!!! Longitude- ',wplon,elon
      PRINT*,'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
      STOP 'bad_domain'
  ENDIF


  OPEN(11,file=locfn,status='unknown',form='formatted')
  REWIND (11)

  CALL pressio_GRIB(11,locfn,pLin,nx,ny,nz,5,pisfc,5, &
       &   iyear,imonth,idate,ihour,wplon,splat,spcnprx,spcnpry, &
       &   elon,tnlat,levpr)

  CLOSE(11)

  !  print *,'Excluindo arquivos ASCII ...'

  command=   &
       &     'rm -f '//fnamesout
  CALL system(command)

END SUBROUTINE MakeDP

!
! ******************************************************************
!
SUBROUTINE GRIB_filelist(fnames,nfile, fprefix)

  IMPLICIT NONE

  ! *************** DUMMY ARGUMENTS ************
  INTEGER, INTENT(INOUT) :: nfile
  CHARACTER(LEN=*), INTENT(OUT), DIMENSION(*) :: fnames
  CHARACTER(LEN=*), INTENT(IN) :: fprefix

  ! ************** DECLARATIONS *****************
  CHARACTER(LEN=128) :: file, command
  INTEGER :: iun, nf

  ! ************** PROCEDURE BODY ***************

  nfile = 0
  PRINT *, 'GRIB_filelist: Checking directory'

  command=   &
       &     'ls -1 '//fprefix//'  >/tmp/RAMS_filelist'
  CALL system(command)
  command=   &
       &     'chmod 777 /tmp/RAMS_filelist'
  CALL system(command)

  !--------------------------------------------------
  !     Open the directory list and read through the files
  !--------------------------------------------------

  iun=98
  OPEN(unit=iun,file='/tmp/RAMS_filelist',status='old',err=15)
  REWIND iun

  DO nf=1,2000
      READ(iun,'(a128)',END=30,err=30) file
      fnames(nf) = file
  ENDDO

30 CONTINUE
  CLOSE(iun)
  command= '/bin/rm -f /tmp/RAMS_filelist'

  CALL system(command)

  !--------------------------------------------------

  nfile=nf-1

  IF (nfile .EQ. 0) THEN
      PRINT *, 'No RAMS files for prefix:',fprefix
  ENDIF

  RETURN 

15 PRINT *, 'RAMS_filelist: Error opening /tmp/RAMS_filelist'
  STOP 'RAMS_filelist-/tmp file error : run again'

  RETURN

END SUBROUTINE GRIB_filelist

! ****************************************

SUBROUTINE Le_Header(iun,head)

  IMPLICIT NONE

  ! *************** DUMMY ARGUMENTS ************
  INTEGER, INTENT(IN) :: iun 
  INTEGER, INTENT(OUT), DIMENSION(8) :: head 

  ! ************** DECLARATIONS *****************

  ! ************** PROCEDURE BODY ***************

  !----------------------------------------------
  !    Read the header of the grib file 
  !----------------------------------------------

  READ(iun,100) head 
100 FORMAT(8I10)

  !  varcode = head(1)
  !  nivel = head(2)
  !  ano = head(3)/10000
  !  mes = (head(3) - ano*10000) /100
  !  dia = head(3) - (head(3)/100)*100
  !  hora = head(4)
  !  nlongitude = head(5)
  !  nlatitude = head(6)

  RETURN

END SUBROUTINE Le_Header

!
! ******************************************************************
!
SUBROUTINE prstage_GRIB(iun,n1,n2,n3,n4,d)

  IMPLICIT NONE

  integer :: teste
  character(len=80) :: string

  ! *************** DUMMY ARGUMENTS ************
  INTEGER, INTENT(IN) :: n1, n2, n3, n4, iun
  REAL, INTENT(OUT), DIMENSION(n1,n2,n3,n4) :: d

  ! ************** DECLARATIONS *****************
  REAL, DIMENSION(n1*n2) :: SeaPress
  INTEGER, DIMENSION(8) :: head
  INTEGER :: i,j,k,l,kk,ih,DIAMES(12)
  INTEGER :: ilvl, ivaria, iano, imes, idia, ihora, aux
  DATA DIAMES /31,28,31,30,31,30,31,31,30,31,30,31/

  ! ************** PROCEDURE BODY ***************

  PRINT 91
91 FORMAT(////,1X,70('*')/  &
       &      ,'  Access coarse resolution pressure data GAMRAMS',/  &
       &      ,1X,70('*')///)

  d= 0.

  kk = n1*n2

  !----------------------------------
  !  Read grib header 
  !----------------------------------

  READ(iun,99) head 
99 FORMAT(8I10)
print*,head 
  !----------------------------------
  !  Read Sea Level Pressure
  !----------------------------------

!  READ(iun,*) (SeaPress(k),k=1,n1*n2)

  READ(iun,'(8ES13.10)') (SeaPress(k),k=1,n1*n2)
  ! print *,'Seapress = ',(SeaPress(k),k=1,n1*n2)

  !Fausto

  PRINT 554
554 FORMAT(/,' GRIB Variable Code',/   &
       &     '    02   =  Pressure reduced to MSL ',/ &
       &     '    33   =  u component of wind ',/ &
       &     '    34   =  v component of wind ',/ &
       &     '    07   =  Geopotential height ',/ &
       &     '    11   =  Temperature ',/ &
       &     '    52   =  Relative Humidity ',//)

  ilvl = head(2)
  ivaria = head(1)
  iano = head(3)/10000
  imes = (head(3) - iano*10000) /100
  idia = head(3) - (head(3)/100)*100
  ihora = head(4)

  ! Hallak - corecao das datas no nome do dp
  aux = ihora / 24
  ihora = MOD(ihora,24)
  IF (MOD(iano,4) .EQ. 0) DIAMES(2)=29
  DO IH=1,aux
  idia = idia + 1
  IF (idia .GT. DIAMES(imes)) THEN
  idia=1
  imes=imes+1
  IF (imes .GT. 12) THEN
  imes=1
  iano=iano+1
  ENDIF
  ENDIF
  ENDDO
  write(*,*)'ano1=',iano,' mes1=',imes,' dia1=',idia,' hora1=',ihora    
  ! Hallak

  PRINT 555,ILVL,IVARIA,IMES,IDIA,IANO,IHORA
555 FORMAT(' Read CPTEC GRIB field  ',2I4,' at ',I2,'/',I2,'/',I4 &
       &       ,I6,' GMT')
  !Fausto


!!!!!!Debug
 ! print *,'SeaPress(1,1)',SeaPress(1)
 ! print *,'SeaPress(2,1)',SeaPress(2)
 ! print *,'SeaPress(9,1)',SeaPress(9)
 ! print *,'SeaPress(49,47)',SeaPress(49*47)
!!!!!!Debug


  !----------------------------------
  ! Reading u, v, t, zgeo, rh
  !----------------------------------
  DO l = 1,n4                  ! variable (1-5)
      DO k = 1,n3               ! level (1-14)
        !!read(iun,*)

        READ(iun,'(8I10)') (head(i),i=1,8)          ! header 
        !!print *, "head=", head
!        READ(iun,*) ((d(i,j,k,l),i=1,n1),j=1,n2)     ! values
        READ(iun,'(8ES13.10)') ((d(i,j,k,l),i=1,n1),j=1,n2)     ! values
        
  !Fausto
        ilvl = head(2)
        ivaria = head(1)
        iano = head(3)/10000
        imes = (head(3) - iano*10000) /100
        idia = head(3) - (head(3)/100)*100
        ihora = head(4)

  ! Hallak - corecao das datas no nome do dp
  aux = ihora / 24
  ihora = MOD(ihora,24)
  IF (MOD(iano,4) .EQ. 0) DIAMES(2)=29
  DO IH=1,aux
  idia = idia + 1
  IF (idia .GT. DIAMES(imes)) THEN
  idia=1
  imes=imes+1
  IF (imes .GT. 12) THEN
  imes=1
  iano=iano+1
  ENDIF
  ENDIF
  ENDDO
!  write(*,*)'ano2=',iano,' mes2=',imes,' dia2=',idia,' hora2=',ihora    
  ! Hallak

        PRINT 556,ILVL,IVARIA,IMES,IDIA,IANO,IHORA
556     FORMAT(' Read CPTEC GRIB field  ',2I4,' at ',I2,'/',I2,'/',I4 &
             &       ,I6,' GMT')
        !Fausto


      ENDDO
  ENDDO

  RETURN

END SUBROUTINE prstage_GRIB
!
! ******************************************************************
!
SUBROUTINE interpolate(n1,n2,n3,n4,d,dLin,splat,spcnpry,ylev,zlev)

  IMPLICIT NONE

  ! *************** DUMMY ARGUMENTS ************
  INTEGER, INTENT(IN) :: n1, n2, n3, n4
  REAL, INTENT(IN), DIMENSION(n1,n2,n3,n4) :: d
  REAL, INTENT(OUT), DIMENSION(n1,n2-1,n3,n4) :: dLin
  REAL, INTENT(IN) :: splat, spcnpry
  REAL, INTENT(IN), DIMENSION(n2) :: ylev
  INTEGER, INTENT(IN), DIMENSION(n3) :: zlev
  

  ! ************** DECLARATIONS *****************

  REAL, DIMENSION(n2-1) :: ylevLinear

  INTEGER :: i,j,k,l
  REAL :: V1, V2, Y1, Y2, aux


  ! ************** PROCEDURE BODY ***************

  !----------------------------------------------------------------------
  ! Fausto
  !
  ! INPUT:
  ! ylev = y coordinate gaussian grid
  ! zlev = level pressure
  ! d = 4d array with the original grib data
  !
  ! OUTPUT:
  ! dLin = 4d array with the interpolated grib data
  !
  ! LOCAL:
  ! ylevLinear = y coordinates of linear grid according splat and spcnpry
  ! V1 = gaussian grib value at x(n),ylev(i)
  ! V2 = gaussian grib value at x(n),ylev(i+1)
  ! Y1 = ylev(i)
  ! Y2 = ylev(i+1)
  !
  ! In grib file the variables follow the sequence: u,v,zgeo,theta,rh
  ! In dp file the variables follow the sequence: u,v,theta,zgeo,rh
  ! 
  !----------------------------------------------------------------------


  DO i = 1, n2-1 
      ylevLinear(i) = SPLAT + (i-1)*spcnpry
  ENDDO

  !Debug
  !  print *,'ylevLin(1) = ',ylevLinear(1)
  !  print *,'ylevLin(2) = ',ylevLinear(2)
  !  print *,'ylevLin(45) = ',ylevLinear(45)
  !  print *,'ylevLin(46) = ',ylevLinear(46)
  !Debug

  DO l = 1, n4              ! var   = 1-5 
      DO k = 1, n3           ! level = 1-14
        DO j = 1, n2-1      ! y = 1-46
           DO i = 1, n1     ! x = 1-49

              V1 = d(i, j  , k, l) 
              V2 = d(i, j+1, k, l)
              Y1 = ylev(j)
              Y2 = ylev(j+1)
              aux = ((V2-V1)*(Y2-ylevLinear(j)))/(Y2-Y1)
!SRF
!	      if(k.eq.1) then
!	       if(j.eq.1) then
!	        if(i.eq.1) print*,v1,v2,aux,v2-aux
!		endif
!		endif
!
              ! Putting the variables in the right form: u,v,theta.zgeo,rh

              IF (l .EQ. 3) dLin(i,j,k,4) = V2 - aux 
              IF (l .EQ. 4) dLin(i,j,k,3) = V2 - aux
              IF ((l .NE. 3) .AND. (l .NE. 4))  &
                   &          dLin(i,j,k,l) = V2 - aux

              !Debug
              !   IF ( j == 1) THEN
              !   print *,'V1 = ',V1
              !   print *,'V2 = ',V2
              !   print *,'dLin(',j,k,l,') = ',dLin(j,k,l)
              !   ENDIF
              !Debug

           ENDDO
        ENDDO
      ENDDO
  ENDDO

  RETURN

END SUBROUTINE interpolate
!
! ******************************************************************
!
SUBROUTINE PRESSIO_GRIB(IUN,IFN,D,n1,n2,n3,n4,ds,ns,  &
     &   iyear,imonth,idate,ihour,wplon,splat,spcnprx,spcnpry, &
     &   elon,tnlat,levpr)

  IMPLICIT NONE

  ! *************** DUMMY ARGUMENTS ************
  INTEGER, INTENT(IN) :: iun, n1, n2, n3, n4, ns
  REAL, INTENT(IN), DIMENSION(n1,n2-1,n3,n4) :: D
  REAL, INTENT(IN), DIMENSION(n1,n2-1,*) :: ds 
  CHARACTER(LEN=*), INTENT(IN) :: IFN
  INTEGER, INTENT(IN) :: iyear,imonth,idate,ihour
  REAL, INTENT(IN) :: wplon,splat,spcnprx,spcnpry,elon,tnlat
  INTEGER, INTENT(IN), DIMENSION(n3) :: levpr 

  ! ************** DECLARATIONS *****************
  INTEGER :: i, j, ij, lv, n, l

  ! ************** PROCEDURE BODY ***************


  PRINT 10, IUN,IFN
10 FORMAT(//,'Writing pressure file on unit ',I2,' .',/  &
       &     ,'  Filename - ',A40)

  WRITE(IUN,900) IYEAR,IMONTH,IDATE,IHOUR,N3,N1,N2-1        &
       &     ,WPLON,SPLAT,SPCNPRX,SPCNPRY,(LEVPR(L),L=1,N3)
900 FORMAT(I9,2I7,I7,3I8,2F9.3,2F8.3,/,(14I6))

  !print *,'Passei aqui' 
  !print *,'n3 = ',n3 
  !print *,'n4 = ',n4 
  !print *,'n1 = ',n1 
  !print *,'n2 = ',n2 

  DO lv=1,n3
     DO n=1,n4
        WRITE(iun,950) ((d(i,j,lv,n),i=1,n1),j=1,n2-1)
!srf        if(lv.eq.1) print*,d(1,1,lv,n)


950     FORMAT(8f10.3)
     ENDDO
  ENDDO

  DO n=1,ns
     WRITE(iun,950) ((ds(i,j,n),i=1,n1),j=1,n2-1) 
  ENDDO

  CLOSE(iun)
  WRITE(*,*)'ELON= ',elon
  WRITE(*,*)'TNLAT= ',tnlat

  PRINT 102,' *****  Pressure file written *************'  &
       &     ,IYEAR,IMONTH,IDATE,IHOUR,WPLON,ELON,SPLAT,TNLAT    &
       &     ,SPCNPRX,SPCNPRY,N1,N2-1,N3,(LEVPR(L),L=1,N3)
102 FORMAT(////,A45,//                                       &
       &     ,7X,' Date (year,month,day,hour)  - ',4I11,/        &
       &     ,7X,' Lon-lat bounds              - ',4F8.3,/       &
       &     ,7X,' Grid spacing (degrees)      - ',2F8.3,/       &
       &     ,7X,' Number of X,Y points        - ',2I5,/         &
       &     ,7X,' Number of pressure levels   - ',I5,/          &
       &     ,7X,' Pressure levels  (mb)       - '/,(32X,14I5))


  RETURN
END SUBROUTINE PRESSIO_GRIB



