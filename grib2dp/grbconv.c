#if defined(__convex__)
#include <sys/malloc.h>
#else
#include <malloc.h>
#endif
#include <string.h>
#if defined (sun)
#include <strings.h>
#endif
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <math.h>

#define INT long
#define REAL float
#define CHAR unsigned char

#define TRUE  1
#define FALSE 0
#define SEEK_CUR 1

#define MAX_LEVELS      80
#define MAX_Longitudes 358
#define MAX_Latitudes  232

#define MAX_DimGP     (MAX_Longitudes * MAX_Latitudes)
#define MAX_NVCT      (MAX_LEVELS * 2 + 2)     

INT         GribEdition;
INT         Grib1Offset;
INT         nvct;
INT         Debug = 0;

static FILE *fp;
static char *ofile;
 
int qu2reg2_(pfield, kpoint, klat, klon, kcode, pmsval, kret)
REAL *pfield, *pmsval;
INT *kpoint, *klat, *klon, *kcode, *kret;
{
   return 0;
} /* qu2reg2_ */

/* usage: readgrib -t type -i infile -o outfile -d debug */
int main(argc, argv)
int argc;
char *argv[];
{
   extern INT  gribdate_();
   extern int  gribin_();

   FILE       *cfile;
   static char yifile[80], yofile[80], yptype[80], ydebug[80];
   static INT  kunit = 11, keof, kret, ksec1[1200], ksec2[32], lens4;
   static INT  i, b, nrec, offset= 0;
   static INT  lt = 0, li = 0, lo = 0, ld = 0;
   static INT  nvar, nlev, hour, ndat, nlat, nlon, centerID, modelID;
   static REAL undef = -9999.9, zero = 0.0;
   static INT  one = 1;
   static INT  mask[MAX_DimGP];
   static REAL Sec4[MAX_DimGP];
   static INT  head[8];

   if (argc == 1) {
      fprintf(stdout,"Type output type [list|cona|conb|conp] : ");
      fscanf (stdin ,"%s",yptype);
      fprintf(stdout,"Type infile name                       : ");
      fscanf (stdin ,"%s",yifile);
      fprintf(stdout,"Type outfile name                      : ");
      fscanf (stdin ,"%s",yofile);
      fprintf(stdout,"Debug info wanted ? [yes|no]           : ");
      fscanf (stdin ,"%s",ydebug);
      if (strcmp(ydebug,"yes") == 0) Debug = 1;
      else                           Debug = 0;
   }  else {
      for (i = 1; i < argc; i += 2) {
          if (strcmp(argv[i],"-t") == 0)
          { lt = 1; strcpy(yptype,argv[i+1]); }
          if (strcmp(argv[i],"-i") == 0)
          { li = 1; strcpy(yifile,argv[i+1]); }
          if (strcmp(argv[i],"-o") == 0)
          { lo = 1; strcpy(yofile,argv[i+1]); }
          if (strcmp(argv[i],"-d") == 0) {
            ld = 1; strcpy(ydebug,argv[i+1]);
            if (strcmp(ydebug,"yes") == 0) Debug = 1;
            else                           Debug = 0;
          }
      }
      if (li == 0 || lo == 0 || lt == 0) {
          printf("readgrib : interactive usage\n");
          printf("readgrib -t type -i infile -o outfile -d debug\n");
      }

      if (lt == 0) {
         fprintf(stdout,"Type output type [list|cona|conb|conp]  : ");
         fscanf (stdin ,"%s",yptype);
      }
      if (li == 0) {
         fprintf(stdout,"Type infile name                   : ");
         fscanf (stdin ,"%s",yifile); li = 1;
      }
      if (lo == 0) {
         fprintf(stdout,"Type outfile name                  : ");
         fscanf (stdin ,"%s",yofile); lo = 1;
      }
   }

   cfile = fopen(yofile,"w");

   if (strcmp(yptype,"list") == 0) {
      fprintf(cfile,"List of contents of %s\n", yifile);
      fprintf(cfile,"      code     level    yymmdd        hh       lon       lat\n");
      fprintf(cfile,"      ----     -----    ------        --       ---       ---\n");
   }

   keof = 0;
   while (1) {
      if (strcmp(yptype,"list") == 0)
         gribin_(&kunit, (REAL *)0, ksec1, ksec2, mask,
                 &lens4, &keof, &kret, yifile, &undef);
      else if (strcmp(yptype,"cona") == 0 ||
          strcmp(yptype,"conb") == 0 || strcmp(yptype,"conp") == 0  )
         gribin_(&kunit, Sec4, ksec1, ksec2, mask,
                 &lens4, &keof, &kret, yifile, &undef);
      else {
         printf("main: output type *%s* not known\n",yptype);
         exit(1);
      }
      if (keof != 0 || kret != 0) break;
      centerID = ksec1[2-1]; modelID = ksec1[3-1];
      nvar = ksec1[6-1]; nlev = ksec1[8-1];
      nlon = ksec2[2-1]; nlat = ksec2[3-1];
      ndat = gribdate_(ksec1);
      hour = ndat % 100;
      ndat = ndat / 100;
      if (strcmp(yptype,"cona") == 0 ||
          strcmp(yptype,"list") == 0  ) {
         if (ksec2[1-1] == 50)
            fprintf(cfile,"%10d%10d%10d%10d%10d%10d%10d%10d\n",
                    nvar,nlev,ndat,hour,lens4,(INT)one,modelID,centerID);
         else
            fprintf(cfile,"%10d%10d%10d%10d%10d%10d%10d%10d\n",
                    nvar,nlev,ndat,hour,nlon,nlat,modelID,centerID);
      }
      if (strcmp(yptype,"cona") == 0) {
         for (i = 0; i < lens4; i++) {
             fprintf(cfile,"%13.6e",Sec4[i]);
             if (((i+1) % 8 == 0)&&(i<(lens4-1))) fprintf(cfile,"\n");
         }
         fprintf(cfile,"\n");
      }
      if (strcmp(yptype,"conp") == 0) {
         fwrite((char *)Sec4,sizeof(REAL),lens4,cfile);
      }
      if (strcmp(yptype,"conb") == 0) {
         head[0] = nvar; head[1] = nlev; head[2] = ndat; head[3] = hour;
         head[4] = nlon; head[5] = nlat; head[6] = modelID; head[7] = centerID;
         if (ksec2[1-1] == 50) {
             head[4] = lens4; head[5] = one;
         }
         fwrite(head        ,sizeof(INT) ,    8,cfile);
         fwrite((char *)Sec4,sizeof(REAL),lens4,cfile);
      }
   }

   if (kret == 0)
      printf("readgrib : NORMAL EXIT\n");
   else
      printf("readgrib : ERROR  EXIT with return code %d\n",kret);
   exit(kret);
}

INT  gribdate_(ksec1)
INT *ksec1;
{
   static INT mtinc, mtave, myref, mtuni, mtran;
   static INT mc, my, mm, md, mh, ay, am;

   if (GribEdition == 1) mc = ksec1[22-1] - 1;
   else                  mc =               0;
   if (mc < 0) mc = 0;
   my = ksec1[10-1];
   myref = my - 1;
   mm = ksec1[11-1];
   md = ksec1[12-1];
   mh = ksec1[13-1];

   if (Debug)
   printf("gribdate : cc %3d yy %3d mm %3d dd %3d hh %3d\n",
                      mc,    my,    mm,    md,    mh);

   mtuni = ksec1[15-1];
   mtinc = ksec1[16-1];
   mtran = ksec1[18-1];
   mtave = ksec1[19-1];
   am = mtave % 100;
   ay = mtave / 100;
   if (mtran == 0) {
      if (mtuni == 1) {mh += mtinc;}
      if (mtuni == 2) {md += mtinc;}
      if (mtuni == 3) {mm += mtinc;}
      if (mtuni == 4) {my += mtinc;}
   }  else {
      if (mtinc != 0) {
         if (mtuni == 0) {mh += mtinc / 60;}
         if (mtuni == 1) {mh += mtinc;}
         if (mtuni == 2) {mh += mtinc * 24;}
         if (mtuni == 3) {mh += mtinc * 720;}
         if (mh >= 24) {mh += -24;}
         md += mh / 24;
         mh %= 24;
         mm += (md - 1) / 30;
         md  = (md - 1) % 30 + 1;
         my += (mm - 1) / 12;
         mm  = (mm - 1) % 12 + 1;
         my -= myref;
      }
   }
   return (mh + md * 100 + mm * 10000 + (my + (mc * 100)) * 1000000);
} /* gribdate_ */


void Abort(errtext)
char *errtext;
{
   fprintf(stderr,errtext);
    printf(       errtext);
    exit(1);
}


REAL decfp(iexp, imant)
INT iexp, imant;
{
   INT   Negative;
   REAL Result;

   Negative = iexp > 127;
   Result   = imant * pow(16.0,(REAL)((iexp & 127)-64)) *
              (1.0 /(1 << 24));
   if (Negative) return(-Result);
   else          return( Result);
}

void ungrib(igrib, sec1, sec2, sec4, mask, rmiss)
CHAR *igrib;
INT sec1[], sec2[], mask[];
REAL *sec4, *rmiss;
{
   INT  dim;
   INT  jlenv,jlenf,lblk,i,m,j;
   INT  ilat1,ilat2;
   INT  ibits,imiss3;
   INT  iexp,imant,iflag,irep,lnil,jscale,imiss;
   INT  masklen,offset;
   INT  ReducedGrid = FALSE, NNV, NPV;
   INT  iwest, ieast, *nvcpr;
   INT  kret, One = 1, nolat, nolng;
   REAL fmin,zscale;

   extern int qu2reg2_();

   igrib += 4;
   igrib += Grib1Offset;
   lblk  = ((*igrib) << 16) + ((*(igrib+1)) << 8) + *(igrib+2);
   igrib += 3;

   offset = 4;
   offset += Grib1Offset;
   offset += lblk;

   /***************************************/
   /* block 1 - product definition block. */
   /***************************************/

   for (i = 0 ; i < lblk - 3 ; i++) sec1[i] = *igrib++ ;
   if (Grib1Offset) sec1[0] = 1;
   else             sec1[0] = 0;
   sec1[18] = (sec1[18] << 8) + sec1[19];
   sec1[19] = 0;

   if (sec1[6] == 100 || sec1[6] == 103 ||
       sec1[6] == 105 || sec1[6] == 107 ||
       sec1[6] == 109 || sec1[6] == 160 )
   {
      sec1[7] = (sec1[7] << 8) + sec1[8];
      sec1[8] = 0;
   }

   /* one time range can occupy two octets. */

   if (sec1[17] == 10)
   {
      sec1[15] = (sec1[15] << 8) + sec1[16];
      sec1[16] = 0 ;
   }

   if (lblk > 28)
   sec1[43] = (sec1[43] << ((sizeof(INT) - 1) * 8)) +
              (sec1[44] << ((sizeof(INT) - 2) * 8)) +
              (sec1[45] << ((sizeof(INT) - 3) * 8)) +
              (sec1[46] << ((sizeof(INT) - 4) * 8));
   sec1[44] = sec1[45] = sec1[46] = 0;

   /*************************************/
   /* block 2 - grid description block. */
   /*************************************/

   if (sec1[4] == 128 || sec1[4] == 192)
   {
      lblk  = *igrib++ << 16;
      lblk += *igrib++ <<  8;
      lblk += *igrib++      ;

      offset += lblk;

/*    length is 32 octets for lat/long, gaussian and spherical */
/*    harmonics . for any data  on hybrid levels the           */
/*    vertical coordinates are added.                          */
/*    For reduced grid data NNV = 0 and NPV != 255              */
/*    number of unused bits at end of block. */
      NNV = *igrib++;

/*    next octet is reserved. */
/*    or is the location of either VCT or PIR */

      NPV = *igrib++;
      
      if (NNV == 0 && NPV != 255 && NPV != 0) ReducedGrid = TRUE;

/*    data representation type. */

      sec2[0] = *igrib++;

/*    lat/longitude grid, gaussian grid and spherical harmonics */
/*    are the only data representations handled.                */

      if (sec2[0] != 0 && sec2[0] != 4 && sec2[0] != 50)
         Abort(" grid description block not yet defined\n");

/*    lat/long or gaussian grid. */

      if (sec2[0] == 0 || sec2[0] == 4)
      {
/*       number of lat/long points. */

         sec2[1]  = *igrib++ << 8;
         sec2[1] += *igrib++;
         sec2[2]  = *igrib++ << 8;
         sec2[2] += *igrib++;

/*       lat/long of origin. */

         ilat1  = *igrib++ << 16;
         ilat1 += *igrib++ <<  8;
         ilat1 += *igrib++      ;
         ilat2  = *igrib++ << 16;
         ilat2 += *igrib++ <<  8;
         ilat2 += *igrib++      ;

/*       if sign bit set to 1 , values are negative. */

         if (ilat1 < 8388608) sec2[3] = ilat1;
         else                 sec2[3] = 8388608 - ilat1;
         if (ilat2 < 8388608) sec2[4] = ilat2;
         else                 sec2[4] = 8388608 - ilat2;

/*       resolution flag. */

         sec2[5] = *igrib++;

/*       lat/long of extreme points. */

         ilat1  = *igrib++ << 16;
         ilat1 += *igrib++ <<  8;
         ilat1 += *igrib++      ;
         ilat2  = *igrib++ << 16;
         ilat2 += *igrib++ <<  8;
         ilat2 += *igrib++      ;

/*       if sign bit set to 1 , values are negative. */

         if (ilat1 < 8388608) sec2[6] = ilat1;
         else                 sec2[6] = 8388608 - ilat1;
         if (ilat2 < 8388608) sec2[7] = ilat2;
         else                 sec2[7] = 8388608 - ilat2;

/*       direction increments / number of latitude lines. */

         sec2[8]  = *igrib++ << 8;
         sec2[8] += *igrib++;
         sec2[9]  = *igrib++ << 8;
         sec2[9] += *igrib++;

/*       scanning mode flags. */

         sec2[10] = *igrib++;

/*       4 reserved octets. */

         igrib += 4;

      }

/*    spherical harmonic data. */

      if (sec2[0] == 50)
      {
/*       pentagonal resolution parameters. */

         sec2[1]  = *igrib++ << 8;
         sec2[1] += *igrib++     ;
         sec2[2]  = *igrib++ << 8;
         sec2[2] += *igrib++     ;
         sec2[3]  = *igrib++ << 8;
         sec2[3] += *igrib++     ;

/*       representation type and mode. */

         sec2[4] = *igrib++;            sec2[5] = *igrib++;

/*       18 reserved octets. */

         igrib += 18;

      }

/*    get dimension of 2d-field */

      if (sec2[0] == 0)
      {
         nolat = (sec2[3] - sec2[6]);
         iwest = sec2[4];
         ieast = sec2[7];
         if (iwest <= ieast) iwest += 360000;
         nolng = iwest - ieast;
/*       if Di or Dj are missing */
         if (sec2[8] == 65535)
         {
            nolat = 1 + nolat / sec2[9];
            nolng = 1 + nolng / sec2[9];
         }
         else
         {
            nolat = 1 + nolat / sec2[9];
            nolng = 1 + nolng / sec2[8];
         }
         if (ReducedGrid) sec2[1] = nolng;
         if (ReducedGrid) sec2[2] = nolat;
         dim = sec2[1] * sec2[2];
      }
      if (sec2[0] == 4)
      {
         nolat = sec2[9] * 2;
         nolng = sec2[9] * 4;
         if (ReducedGrid) sec2[1] = nolng;
         if (ReducedGrid) sec2[2] = nolat;
         dim = sec2[1] * sec2[2];
      }
      if (sec2[0] == 50)
         dim = (sec2[1]+1) * (sec2[2]+2);


/*    vertical coordinate parameters for hybrid levels.     */
/*    get number of vertical coordinate parameters, if any. */

      if (ReducedGrid) jlenv = (lblk - 32) >> 1;
      else             jlenv = (lblk - 32) >> 2;
      if (jlenv > MAX_NVCT)
      {
         fprintf(stderr," No. of vertical coordinates: %d\n",jlenv);
         fprintf(stderr," Array size:                  %d\n",MAX_NVCT);
         exit(1);
      }
      if (jlenv)
      {
         nvcpr = (INT *) malloc(jlenv * sizeof(INT));
         if (ReducedGrid)
            for (i = 0 ; i < jlenv ; i++)
            {
                nvcpr[i]  = *igrib++ << 8;
                nvcpr[i] += *igrib++     ;
            }
         else
            for (i = 0 ; i < jlenv ; i++)
                igrib += 4;
      }
   }

/* Leave ungrib (decode only definition sections */
   if (sec4 == NULL) return;


/********************************************************************/
/* block 3 - bit map block.                                      */
/********************************************************************/

   if (sec1[4] == 64 || sec1[4] == 192)
   {
      lblk  = ((*igrib) << 16) + ((*(igrib+1)) << 8) + *(igrib+2);
      offset += lblk;
/*
      exit(1);
*/
      imiss  = *(igrib+3);
      imiss3 = imiss >> 3;
      igrib += 6;
      masklen = lblk - 6 - imiss3;
      if (masklen*8 - imiss != sec2[1]*sec2[2])
          { printf("gribin   : Mask dimension conflict !\n"); exit(1); }
      for (m = 0; m < masklen; m++)
      for (j = 7; j >= 0; j--)
      {
          mask[(m*8)+7-j] = ((igrib[m]) >> j) & 1;
      }
      igrib += masklen;
/*
      for (m = 0; m < masklen*8; m++)
      {
          printf("%1.1d",mask[m]);
          if ((m+1) % 128 == 0) printf("\n");
      }
*/

   }
   else
/*    preset mask */
      for (i = 0; i < dim; i++)
           mask[i] = 1;


/********************************************************************/
/* block 4 - binary data block.                                  */
/********************************************************************/

/* get length of binary data block. */

   lblk  = *igrib++ << 16;
   lblk += *igrib++ <<  8;
   lblk += *igrib++      ;

/* 4 bit flag / 4 bit count of unused bits at end of block octet. */

   iflag = *igrib++;

/* 0000---- grid point           */
/* 1000---- spherical harmonics  */

   irep = iflag >> 7;
   lnil = iflag & 127;

/* get scale factor */;

   jscale  = *igrib++ << 8;
   jscale += *igrib++     ;
   if (jscale > 32767) jscale = 32768 - jscale;

/* get reference value (fmin) in grib format (iexp,imant) */

   iexp   = *igrib++;
   imant  = *igrib++ << 16;
   imant += *igrib++ <<  8;
   imant += *igrib++      ;

/* check for missing data indicators. */

   imiss = (jscale == 65535 && iexp == 255 && imant == 16777215);

/* convert reference value and scale factor. */

   if (imiss == 0)
   {
      fmin = decfp(iexp,imant);
      zscale = pow(2.0,(REAL)jscale);
   }

/* get number of bits in each data value. */

   ibits = *igrib++;

/* if data is in spherical harmonic form, next 4 octets */
/* contain the real (0,0) coefficient.                  */

   if (irep == 1)
   {
/*    get real (0,0) coefficient in grib format and     */
/*    convert to floating point.                        */

      iexp   = *igrib++;
      imant  = *igrib++ << 16;
      imant += *igrib++ <<  8;
      imant += *igrib++      ;

      if (imiss) *sec4++ = 0.0;
      else       *sec4++ = decfp(iexp,imant);
   }

/* decode data values to floating point and store in sec4. */
/* first calculate the number of data values.                */

   jlenf = lblk - 11 - irep * 4 ;
   jlenf = (jlenf * 8 - lnil) / ibits ;

/* check length of output array. */

   if (jlenf+irep > MAX_DimGP)
   {
      fprintf(stderr," values to be  decoded are  %d\n",(jlenf)+1);
      fprintf(stderr," array size:                %d\n",MAX_DimGP);
      exit(1);
   }


   if (imiss) memset(sec4,0.0,dim * sizeof(REAL));
   else
   {
      switch (ibits)
      {
         case  8: for (i = 0; i < jlenf; i++)
                  {
                     if (mask[i] == 1)
                     {
                        *sec4 = fmin + zscale * *igrib ;
                        igrib++;
                     }
                     else *sec4 = *rmiss;
                     sec4++;
                  }
                  break;
         case 16: for (i = 0; i < jlenf; i++)
                  {
                     if (mask[i] == 1)
                     {
                        *sec4 = fmin + zscale *
                                    ((igrib[0] << 8) + igrib[1]);
                        igrib += 2;
                     }
                     else *sec4 = *rmiss;
                     sec4++;
                  }
                  break;
         case 32: for (i = 0; i < jlenf; i++)
                  {
                     if (mask[i] == 1)
                     {
                        *sec4 = fmin + zscale *
                                  ((igrib[0] << 24) +
                                   (igrib[1] << 16) +
                                   (igrib[2] <<  8) +
                                    igrib[3])       ;
                        igrib += 4;
                     }
                     else *sec4 = *rmiss;
                     sec4++;
                  }
                  break;
         default: fprintf(stderr,
                  " Unimplemented packing factor %d\n",ibits);
                  exit(1);
      }
   }
   if (ReducedGrid)
   {
      qu2reg2_(sec4-jlenf,nvcpr,&nolat,&nolng,&One,&rmiss,&kret);
      if (Debug) printf("ungrib   : free(nvcpr) at %8x\n",nvcpr);
      if (nvcpr) free(nvcpr);
   }
}

gribin_(unit, sec4, sec1, sec2, mask, dlen, keof, kret, fname, rmiss)
INT *unit, *sec1, *sec2, *mask, *dlen, *keof, *kret;
REAL *sec4, *rmiss;
char *fname;
{
   INT Count      ;
   INT BlockCount ;
   INT BlockLength;
   INT RecordBytes;
   INT maxbytes;
   int flen;

   char *mfile    ;
   CHAR *grib, *pgrib;

   flen = strlen(fname);

   maxbytes = MAX_DimGP * 5;
   grib = (CHAR *) malloc(maxbytes);
   pgrib = grib;
   if (Debug) {
       printf("gribin   : malloc grib at %8x\n",grib); }

   if (flen > 0)
   {
      mfile = malloc (flen+1);
      strncpy (mfile,fname,flen);
      *(mfile + flen) = '\040';
      *(strchr(mfile,'\040')) = '\0';
      if (fp == NULL)
      {
          ofile = malloc (128);
          strncpy (ofile,mfile,flen);
          printf("gribin   : Open %s\n",mfile);
      }
   }
   else {
      printf("gribin   : Invalid filename %s\n",mfile);
      *kret = 1; return(0);}

   if (strcmp(ofile,mfile) != 0)
   {
       fclose (fp); fp = NULL;
       printf("gribin   : Input file changed from %s to %s\n",ofile,mfile);
       strcpy (ofile,mfile);
   }
   if (fp == NULL) fp = fopen (mfile,"rb");
   if (fp == NULL) {
       printf("gribin   : Open %s failed\n",mfile);
       *kret = -1; return(0);}
   if (*keof == 1) {
       printf("gribin   : Rewound %s\n",mfile);
       rewind(fp); }

   if (fread(grib,1,4,fp) < 4) {
      if (feof(fp)) {
          printf("gribin   : EOF encountered in %s\n",mfile);
          *keof = 1; *kret = 0; return(0);}
      printf("gribin   : Read failed\n");
      *kret = 2; return(0);}

   if (strncmp((char *)grib,"GRIB",4))
   {  /* Try to synchronize with next GRIB record */
      Count = 0;
      while (++Count < 10240)
      {
         grib[0] = grib[1];
         grib[1] = grib[2];
         grib[2] = grib[3];
         if (fread(grib+3,1,1,fp) < 1)
             if (feof(fp)) { printf("gribin   : EOF encountered\n");
                            *keof = 1; *kret = 0; return(0);}
             else          { printf("gribin   : Read failed\n");
                            *keof = 1; *kret = 3; return(0);}
         if (strncmp((char *)grib,"GRIB",4) == 0) break;
      }
      if (Count > 10239) {
          printf("gribin   : Synchronization failed\n");
          *kret = 4; return(0);}
   }

   grib       += 4;
   fread(grib,1,4,fp);
   GribEdition = grib[3];
   if      (GribEdition == 0) {
      Grib1Offset = 0;
      RecordBytes = 8; fseek(fp,(long) -4,SEEK_CUR);
      for (BlockCount = 1 ; BlockCount < 7 ; BlockCount++) {
         if (fread(grib,1,4,fp) < 1) {
             printf("gribin   : Incomplete record\n");
             *kret = 6; return(0);}
         if (strncmp((char *)grib,"7777",4) == 0) break;
         BlockLength  = (grib[0] << 16) + (grib[1] << 8) + grib[2];
         RecordBytes += BlockLength;
         if (RecordBytes > maxbytes) {
             printf("gribin   : GRIB record too long\n");
             *kret = 7; return(0);}
         if (fread(grib+4,1,BlockLength-4,fp) < BlockLength-4) {
             printf("gribin   : Block read error\n");
             *kret = 8; return(0);}
         grib        += BlockLength;
      }
      RecordBytes += 4;
   }
   else if (GribEdition == 1) {
      Grib1Offset = 4;
      RecordBytes = (grib[0] << 16) + (grib[1] << 8) + grib[2];
      grib += 4;
      if (fread(grib,1,RecordBytes-8,fp) != RecordBytes-8) {
          printf("gribin   : Block read error\n");
          *kret = 8; return(0);}
   }
   else {
          printf("gribin   : GRIB Version not known\n");
          *kret = 5; return(0);}

   ungrib(pgrib,sec1,sec2,sec4,mask,rmiss);

   if (sec2[0] == 0 || sec2[0] == 4) *dlen = sec2[1]*sec2[2];
   if (sec2[0] == 50)  *dlen = (sec2[1]+1) * (sec2[1]+2);

   if (grib) {
       if (Debug) printf("gribin   : free(pgrib) at %8x\n",pgrib);
       free(pgrib); }

   *keof = 0; *kret = 0; return(0);
}

