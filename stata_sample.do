/*============================================================================================*
 This is a master file for the motivating analysis of one of my papers using survey data
 The original file called other do files. For showcasing purposes, I have pasted the code of 
 some of those at the end of the original file.

 Created by Daniel Díez Alonso, all rights reserved.
 Shared only for recruitment purposes. Please, do not circulate for any other purposes.
 
 Data sources:
	- GSS: https://gss.norc.org/get-the-data/stata [accessed 30/08/2019 21:00]
	- Census: https://www.census.gov/data/tables/time-series/demo/income-
			  poverty/historical-income-households.html [accessed 30/08/2019 21:00]
	- CPI: https://fred.stlouisfed.org/series/CPIAUCNS [accessed 30/08/2019 21:00]
*============================================================================================*/
set more off
clear all
set emptycells drop
set maxvar 10000
cap log close
set scheme s2color
grstyle init
grstyle set plain, grid


cd "C:\Users\UserName\Dropbox\PhD\project\"

*Main global macros:
	global dofiles = "dofiles/motivation"
	global data = "data/motivation"
	global figures = "figures/motivation"
	global tables = "tables/motivation"
		cap mkdir $figures
		cap mkdir $tables

* Parameters to define analysis: 
	global sheet "marjoint"		// Analysis by family income (married couple filed jointly)
	global base = 2000			// Base year for constant USD calculation

* Generate macros containing CPI values and income tax parameters (and produce tax summary graphs)
	qui do "${dofiles}/macros_cpi.do"
	qui do "${dofiles}/macros_tax.do"
		cap mkdir "${figures}/usahist"
		qui do "${dofiles}/graphs_tax.do"

* Generate macros containing reference income values (quintiles) from Census Data and produce summary graphs:
	qui do "${dofiles}/macros_income.do"
		qui do "${dofiles}/graphs_income.do"

* Analysis on GSS Data:
	global figures = "figures/motivation"
		cap mkdir "${figures}"
	qui do "${dofiles}/gss1_cleaning.do"	// calculation of taxes for each respondent
	qui do "${dofiles}/gss2_exploratory.do"
	qui do "${dofiles}/gss3_analysis.do"
	
/*================================================================================================*
* This section corresponds to the DO file "gss1_cleaning.do" called from the original master file
*
* Requires previously running all Macros from the Master file
*=================================================================================================*/

use "${data}/GSS7218_R1.dta", clear

keep year id wrkstat hrs1 hrs2 wrkslf occ10 prestg10 prestg105plus indus10 marital ///
	spwrksta sphrs1 sphrs2 spocc10 sppres10 sppres105plus spind10 age sibs childs educ ///
	speduc degree spdeg paeduc maeduc padeg madeg sex race born hompop teens adults earnrs ///
	income rincom* incom* finrela class* formwt oversamp incgap taxrich taxmid taxpoor taxshare

xtset id year	

label var wrkstat "Labor force status (last week)"
label var hrs1 "Hours worked all jobs (last week)"
label var hrs2 "Hours worked all jobs (usual week)"
label var wrkslf "Self-employed"
label var occ10 "R's occupation (2010 classification)"
label var prestg10 "R's occupation prestige (based on occ10)"
label var prestg105plus "R's occupation prestige (threshold method)"
label var indus10 "R's occupation industry (based on NAICS2007 & occ10)"
label var marital "Marital Status"
label var spwrksta "Spouse Labor force status (last week)"
label var sphrs1 "Spouse Hours worked all jobs (last week)"
label var sphrs2 "Spouse Hours worked all jobs (usual week)"
label var spocc10 "Spouse's occupation (2010 classification)"
label var sppres10 "Spouse's occupation prestige (based on occ10)"
label var sppres105plus "Spouse's occupation prestige (threshold method)"
label var spind10 "Spouse's occupation industry (based on NAICS2007 & occ10)"
label var age "Age of respondent"
label var sibs "Number of brothers and sisters"
label var childs "Number of children"
label var incom16 "R's family income at age 16"
label var born "Born in USA"
label var earnrs "People in household with earnings last year"
label var finrela "Family Income Rank"
label var sex "Female Dummy"

replace sex = sex-1
	label def SEX 0 "male" 1 "female", replace

xtset id year

bys year: egen totwt=total(formwt)
gen yweight = 2500*formwt/totwt
	label var yweight "Weight to normalise year sample to 2500"
	drop totwt
	
**********************
** INCOME VARIABLES **
**********************

gen fincome =.
label var fincome "Family Income (USD, nominal)"
forv yy=1972/2018{
	replace fincome = realinc/${cpi1986}*${cpi`yy'} if year==`yy'
	}

replace realinc = realinc/${cpi1986}*${cpi$base}		// transform to base year 2000 (from 1986)
	label var realinc "Family Income (constant USD 2000)"

gen lrealinc = ln(1+ realinc)
	label var lrealinc "Family Income (log, constant USD 2000)"
	
gen rinc = 0*(0<realinc & realinc<1000) + 1*(1000<=realinc & realinc<2000) + 2*(2000<=realinc & realinc<3000) + ///
	3*(3000<=realinc & realinc<4000) + 4*(4000<=realinc & realinc<5000) + 5*(5000<=realinc & realinc<6000) + ///
	6*(6000<=realinc & realinc<7000) + 7*(7000<=realinc & realinc<8000) + 8*(8000<=realinc & realinc<9000) + ///
	9*(9000<=realinc & realinc<10000) + 10*(10000<=realinc & realinc<11000) + 11*(11000<=realinc & realinc<12000) + ///
	12*(12000<=realinc & realinc<15000) + 15*(15000<=realinc & realinc<20000) + 20*(20000<=realinc & realinc<25000) + ///
	25*(25000<=realinc & realinc<30000) + 30*(30000<=realinc & realinc<40000) + 40*(40000<=realinc & realinc<50000) + ///
	50*(50000<=realinc & realinc<75000) + 75*(75000<=realinc & realinc<100000) + 100*(100000<=realinc) if realinc<999999
	replace rinc = rinc*1000
	label var rinc "Real Income Group, 2000 base (approx)"
	label define incomes 0 "$1-999" 1000 "$1,000-1,999" 2000 "$2,000-2,999" 3000 "$3,000-3,999" 4000 "$4,000-4,999" 5000 "$5,000-5,999" ///
		6000 "$6,000-6,999" 7000 "$7,000-7,999" 8000 "$8,000-8,999" 9000 "$9,000-9,999" 10000 "$10,000-10,999" 11000 "$11,000-11,999" ///
		12000 "$12,000-14,999" 15000 "$15,000-19,999" 20000 "$20,000-24,999" 25000 "$25,000-29,999" 30000 "$30,000-39,999" 40000 "$40,000-49,999" ///
		50000 "$50,000-74,999" 75000 "$75,000-99,999" 100000 "$100,000+"
	label val rinc incomes

gen incgroup = 0 if rinc==0									// $0-999 USD
	replace incgroup = 1 if rinc>0 & rinc<8000				// $1,000-7,999 USD
	replace incgroup = 2 if rinc>=8000 & rinc<20000		// $8,000-19,999 USD
	replace incgroup = 3 if rinc>=20000 & rinc<50000		// $20,000-49,999 USD
	replace incgroup = 4 if rinc>=50000 & rinc<100000	// $50,000-99,999 USD
	replace incgroup = 5 if rinc>=100000					// >$100,000 USD

*********************************
** Corresponding Tax Variables **
*********************************

gen mtr =.
	label var mtr "Marginal Tax Rate"
gen band =.
	label var band "Income Tax Band in tax scheme"
gen above =.
	label var above "Tax Bands above"
gen mtrel =.
gen bandrel=.
gen atr =0 if fincome!=.
	label var atr "Average Tax Rate"
gen taxfree =.
	label var taxfree "Distance from tax free allowance (thousand USD)"
gen rtaxfree =.
	label var rtaxfree "Distance from tax free allowance (thousand USD, real)"
gen taxrel =.
	label var taxrel "Tax burden relative to top MTR"

forv yy=1972/2018{
	local bb = ${bands`yy'}-1
		replace mtr = ${mtr${bands`yy'}_`yy'} if year==`yy' & fincome>${band`bb'_`yy'} & fincome!=.
		replace band = ${bands`yy'} if year==`yy' & fincome>${band`bb'_`yy'} & fincome!=.
		replace above = 0 if year==`yy' & fincome>${band`bb'_`yy'} & fincome!=.
	forv i=1/${bands`yy'}{
		local cc = ${bands`yy'}-`i'
		local dd = `cc'+1
		if `i'==1 {
			replace atr = atr + (fincome - ${band`cc'_`yy'})*${mtr`cc'_`yy'} if year==`yy' & fincome>${band`cc'_`yy'} & fincome!=.
		}
		if `i'>1 {
			replace atr = atr + max(0,min(fincome,${band`dd'_`yy'})-${band`cc'_`yy'})*${mtr`dd'_`yy'} if year==`yy' & fincome!=.
		}
		if `cc'==0{
			replace mtr = 0 if year==`yy' & fincome<=${band0_`yy'} & fincome!=.
			replace band = 0 if year==`yy' & fincome<=${band0_`yy'} & fincome!=.
			replace above = ${bands`yy'} if year==`yy' & fincome<=${band0_`yy'} & fincome!=.
			continue, break
		}
		replace mtr = ${mtr`cc'_`yy'} if year==`yy' & fincome<${band`cc'_`yy'} & fincome!=.
		replace band = `cc' if year==`yy' & fincome<${band`cc'_`yy'} & fincome!=.
		replace above = `i' if year==`yy' & fincome<${band`cc'_`yy'} & fincome!=.
	}
	replace mtrel = mtr/${mtr${bands`yy'}_`yy'} if year==`yy' & fincome!=.
	replace bandrel = band/${bands`yy'} if year==`yy' & fincome!=.
	replace atr = atr/fincome if year==`yy' & fincome!=.
	replace taxfree = round(fincome - ${band0_`yy'},1000)/1000 if year==`yy'
	replace rtaxfree = round(taxfree/${cpi`yy'}*${cpi$base},1) if year==`yy'
	replace taxrel = atr/${mtr${bands`yy'}_`yy'} if year==`yy'
}

******************************
** Income Related Variables **
******************************

gen finchange = -(finalter==2) + (finalter==1) if finalter<99
	label var finchange "Change in financial situation"
	label define fchange -1 "worse" 0 "same" 1 "better"
	label val finchange fchange
	drop finalter

replace finrela = finrela-3	if finrela<99		 	// rescaled so that 0 = around the mean
	label var finrela "Perceived distance from mean (-2: far below, +2 far above)"
	label define FINRELA -2 "far below average" -1 "below average" 0 "average" 1 "above average" 2 "far above average" .d "DK" .i "IAP" .n "NA", replace
	
replace rank = 11-rank	if rank<99					// reversed order so that 10 = top
	label var rank "Perceived rank, 1 Bottom - 10 Top"
	label define RANK 10 "top" 1 "bottom" .d "DK" .i "IAP" .n "NA", replace
	
gen mdistance =.
	label var mdistance "Distance from mean (proportional measure)"
gen position =.
	label var position "Income Rank (0 to 10 scale)"
gen rmeaninc =.
	label var rmeaninc "Average Income (real terms)"
gen allowance =.
	label var allowance "Tax Free Allowance (real terms)"
	
forv yr=1972/2018{
    replace rmeaninc = ${meaninc_`yr'}/${cpi`yr'}*${cpi$base} if year==`yr'
	replace allowance = ${band0_`yr'}/${cpi`yr'}*${cpi$base} if year==`yr'
	*replace mdistance = (fincome - ${meaninc_`yr'})*3/(fincome+2*${meaninc_`yr'}) if year==`yr' & finrela!=.
	replace mdistance = 2*((fincome-${meaninc_`yr'})/${meaninc_`yr'}*(${meaninc_`yr'}>fincome) + (fincome-${meaninc_`yr'})/fincome*(${meaninc_`yr'}<fincome)) if year==`yr' & finrela!=.
	replace position = 2*	((fincome>0)*(fincome<=${lim1_`yr'})*(fincome/${lim1_`yr'}) + ///
		(fincome>${lim1_`yr'})*(fincome<=${lim2_`yr'})*(1 + (fincome-${lim1_`yr'})/(${lim2_`yr'}-${lim1_`yr'})) + ///
		(fincome>${lim2_`yr'})*(fincome<=${lim3_`yr'})*(2 + (fincome-${lim2_`yr'})/(${lim3_`yr'}-${lim2_`yr'})) + ///
		(fincome>${lim3_`yr'})*(fincome<=${lim4_`yr'})*(3 + (fincome-${lim3_`yr'})/(${lim4_`yr'}-${lim3_`yr'})) + ///
		(fincome>${lim4_`yr'})*(fincome<=${limtop_`yr'})*(4 + .75*(fincome-${lim4_`yr'})/(${limtop_`yr'}-${lim4_`yr'})) + ///
		(fincome>${limtop_`yr'})*(4.75 + .25*min(1,(fincome-${limtop_`yr'})/${limtop_`yr'}))) if year==`yr'
	}

sort id year
compress
save "${data}/gssclean.dta", replace

/*================================================================================================*
* This section corresponds to the DO file "gss3_analysis.do" called from the original master file
*
* Requires previously running all Macros from the Master file
*=================================================================================================*/

/* If not running after gss2_exploratory
	use "${data}/gssclean.dta", clear
	keep if year>=1984 & year<=2018
*/

*Generate measure of ATR relative to its maximum possible in a given year:
gen atrel = taxrel*100
	label var atrel "Tax Burden (as % of potential maximum)"
	
*Change scale of preferences for redistribution (0=lower, 6=max)
	replace eqwlth = (7-eqwlth)/6*100
		label def redist 0 "None" 6 "Max"
		label val eqwlth redist

**************************	
** ADDITIONAL VARIABLES **
**************************
// Generate change in taxes paid wrt tax system in place 2 years before
gen atrinst =0
gen relinst =.
gen mtr2=.

forv yy=1972/2018{
	local yr = `yy'+2
	local bb = ${bands`yy'}-1
		replace mtr2 = ${mtr${bands`yy'}_`yy'} if year==`yr' & fincome>${band`bb'_`yy'} & fincome!=.
	forv i=1/${bands`yy'}{
		local cc = ${bands`yy'}-`i'
		local dd = `cc'+1
		if `i'==1 {
			replace atrinst = atrinst + (fincome - ${band`cc'_`yy'})*${mtr`cc'_`yy'} if year==`yr' & fincome>${band`cc'_`yy'} & fincome!=.
		}
		if `i'>1 {
			replace atrinst = atrinst + max(0,min(fincome,${band`dd'_`yy'})-${band`cc'_`yy'})*${mtr`dd'_`yy'} if year==`yr' & fincome!=.
		}
		if `cc'==0{
			replace mtr2 = 0 if year==`yr' & fincome<=${band0_`yy'} & fincome!=.
			continue, break
		}
		replace mtr2 = ${mtr`cc'_`yy'} if year==`yr' & fincome<${band`cc'_`yy'} & fincome!=.
	}
	replace atrinst = atrinst/fincome if year==`yr' & fincome!=.
	replace relinst = atrinst/${mtr${bands`yy'}_`yy'} if year==`yr'
}

replace finrela = finrela+3 // change to avoid zeros and negative numbers

gen taxchange = ln(atr/atrinst)
gen relchange = ln(atrel/relinst)		

gen cfinrela = ln(finrela/l2.finrela)
gen crealinc = lrealinc - l2.lrealinc

*********************	
** REGRESSIONS **
*********************
* Main regressions:
foreach var in finrela rank eqwlth{
	oprobit `var' atrel [iw=yweight] if position<9, vce(cluster id)
		if "`var'"=="finrela"{
			outreg2 using "${tables}/gss_regs.xls", bdec(3) label excel replace ctitle("`var'") nocons ///
				title("Ordered Probit Regressions") addtext(Year FE, NO, Demographic Controls, NO, Household FE, NO) ///
				keep(atrel) nor2 addstat(Pseudo R-squared, e(r2_p))
		}
		else{
			outreg2 using "${tables}/gss_regs.xls", bdec(3) label excel ctitle("`var'") nocons ///
				addtext(Year FE, NO, Demographic Controls, NO, Household FE, NO) keep(atrel) ///
				nor2 addstat(Pseudo R-squared, e(r2_p))
		}
	oprobit `var' atrel lrealinc [iw=yweight] if position<9, vce(cluster id)
		outreg2 using "${tables}/gss_regs.xls", bdec(3) label excel ctitle("`var'") nocons ///
			addtext(Year FE, NO, Demographic Controls, NO, Household FE, NO) keep(atrel lrealinc finchange) ///
			nor2 addstat(Pseudo R-squared, e(r2_p))
	oprobit `var' atrel lrealinc finchange age sex i.degree i.year [iw=yweight] if position<9, vce(cluster id)
		outreg2 using "${tables}/gss_regs.xls", bdec(3) label excel ctitle("`var'") nocons ///						SEX, AGE and EDUC CNTRLS
			addtext(Year FE, YES, Demographic Controls, YES, Household FE, NO) keep(atrel lrealinc finchange) ///
			nor2 addstat(Pseudo R-squared, e(r2_p))
	xtoprobit `var', vce(robust)  iterate(20)
		local r0 = `e(ll)'
	xtoprobit `var' atrel lrealinc finchange i.year if position<9, vce(robust)  iterate(20)
		local r2 = round((`e(ll)' - `r0')/(-`r0'),.001)
		outreg2 using "${tables}/gss_regs.xls", bdec(3) label excel ctitle("`var'") nocons ///
			addtext(Year FE, YES, Demographic Controls, NO, Household FE, YES) keep(atrel lrealinc finchange) ///
			nor2 addstat(Pseudo R-squared, `r2')
}
	rm "${tables}/gss_regs.txt"

ivprobit eqwlth (finrela = atrel) lrealinc finchange age sex educ year year2 year3, vce(cluster id) iterate(20)

	
	
* 2SLS regressions:
	ivreg eqwlth (finrela = atrel), r cluster(id) first
		outreg2 using "${tables}/gss_ivregs.xls", bdec(3) label excel replace ctitle("2SLS") nocons ///
			title("IV Regressions") addtext(Year FE, NO, Demographic controls, NO, Household FE, NO) keep(finrela)
	ivreg eqwlth (finrela = atrel) lrealinc finchange, r cluster(id)
		outreg2 using "${tables}/gss_ivregs.xls", bdec(3) label excel ctitle("2SLS") nocons ///
			addtext(Year FE, NO, Demographic controls, NO, Household FE, NO) keep(finrela lrealinc finchange)
	gen year2 = year^2
	gen year3 = year^3
	ivreg eqwlth (finrela = atrel) lrealinc finchange year year2 year3, r cluster(id)
		outreg2 using "${tables}/gss_ivregs.xls", bdec(3) label excel ctitle("2SLS") nocons ///
			addtext(Year FE, YES, Demographic controls, NO, Household FE, NO) keep(finrela lrealinc finchange)
	ivreg eqwlth (finrela = atrel) lrealinc finchange age sex educ year year2 year3, r cluster(id)
		outreg2 using "${tables}/gss_ivregs.xls", bdec(3) label excel ctitle("2SLS") nocons ///
			addtext(Year FE, YES, Demographic controls, YES, Household FE, NO) keep(finrela lrealinc finchange)
	ivprobit eqwlth (finrela = atrel) lrealinc finchange age sex educ year year2 year3, vce(cluster id)
		outreg2 using "${tables}/gss_ivregs.xls", bdec(3) label excel ctitle("Probit") nocons ///
			addtext(Year FE, YES, Demographic controls, YES, Household FE, NO) keep(finrela lrealinc finchange)
	xtivreg eqwlth (finrela = atrel) lrealinc finchange year year2 year3, fe
		outreg2 using "${tables}/gss_ivregs.xls", bdec(3) label excel ctitle("Panel") nocons ///
			addtext(Year FE, YES, Demographic controls, NO, Household FE, YES) keep(finrela lrealinc finchange) nor2 addstat(R-squared, e(r2_o))
	drop year2 year3
	rm "${tables}/gss_ivregs.txt"