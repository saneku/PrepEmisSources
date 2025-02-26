import numpy as np

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def erfc_num_recipes( x ):
  z = np.absolute(x)
  t = 1.0/(1.0 + 0.5*z)
  dum =  ( -z*z - 1.26551223 + t*(1.00002368 + t*(0.37409196 + t*(0.09678418 + t*(-0.18628806 + t*(0.27886807 + t*(-1.13520398 + t*(1.48851587 + t*(-0.82215223 + t*0.17087277 )))))))))
  erfc_dbl = t * np.exp(dum)
  if (x < 0.0):
    erfc_dbl = 2.0 - erfc_dbl

  return erfc_dbl


def sect02(dgnum,sigmag,xlo,xhi):
#   user specifies a single log-normal mode and a set of section boundaries
#   prog calculates mass and number for each section
  print("dgnum ",dgnum)
  print("sigmag ",sigmag)
  print("xlo ",xlo)
  print("xhi ",xhi)


  sx = np.log( sigmag )
  x0 = np.log( dgnum )      # Median diameter
  x3 = x0 + 3.*sx*sx        # Volume median diameter
  #dstar = dgnum * np.exp(1.5*sx*sx)

  sxroot2 = sx * np.sqrt( 2.0 )
  xlo = np.log(xlo)
  xhi = np.log(xhi)

  #Volume distrubution
  tlo = (xlo - x3)/sxroot2
  thi = (xhi - x3)/sxroot2

  if (tlo <= 0.0):
      vol = 0.5*( erfc_num_recipes(-thi) - erfc_num_recipes(-tlo) )
  else:
      vol = 0.5*( erfc_num_recipes(tlo) - erfc_num_recipes(thi) )


  #Size distribution
  tlo = (xlo - x0)/sxroot2
  thi = (xhi - x0)/sxroot2

  if (tlo <= 0.0):
      size = 0.5*( erfc_num_recipes(-thi) - erfc_num_recipes(-tlo) )
  else:
      size = 0.5*( erfc_num_recipes(tlo) - erfc_num_recipes(thi) )


  return vol,size

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------


dgnum_um=2.4
sginin=1.8
xlo=1.0
xhi=10.0

print(sect02(dgnum_um,sginin,xlo,xhi))