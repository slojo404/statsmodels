'''

from pystatsmodels mailinglist 20100524

Notes:
 - unfinished, unverified, but most parts seem to work in MonteCarlo
 - one example taken from lecture notes looks ok
 - needs cases with non-monotonic inequality for test to see difference between
   one-step, step-up and step-down procedures
 - FDR doesn't look really better then Bonferoni in the MC examples that I tried
update:
 - now tested against R, stats and multtest,
   I have all of their methods for p-value correction
 - getting Hommel was impossible until I found reference for pvalue correction
 - now, since I have p-values correction, some of the original tests (rej/norej)
   implementation is not really needed anymore. I think I keep it for reference.
   Test procedure for Hommel in development session log
 - I haven't updated other functions and classes in here.
   - multtest has some good helper function according to docs
 - still need to update references, the real papers
 - fdr with estimated true hypothesis still missing
 - multiple comparison procedures incomplete or missing
 - I will get multiple comparison for now only for independent case, which might
   be conservative in correlated case (?).


some References:

Gibbons, Jean Dickinson and Chakraborti Subhabrata, 2003, Nonparametric Statistical
Inference, Fourth Edition, Marcel Dekker
    p.363: 10.4 THE KRUSKAL-WALLIS ONE-WAY ANOVA TEST AND MULTIPLE COMPARISONS
    p.367: multiple comparison for kruskal formula used in multicomp.kruskal

Sheskin, David J., 2004, Handbook of Parametric and Nonparametric Statistical
Procedures, 3rd ed., Chapman&Hall/CRC
    Test 21: The Single-Factor Between-Subjects Analysis of Variance
    Test 22: The Kruskal-Wallis One-Way Analysis of Variance by Ranks Test

Zwillinger, Daniel and Stephen Kokoska, 2000, CRC standard probability and
statistics tables and formulae, Chapman&Hall/CRC
    14.9 WILCOXON RANKSUM (MANN WHITNEY) TEST


S. Paul Wright, Adjusted P-Values for Simultaneous Inference, Biometrics
    Vol. 48, No. 4 (Dec., 1992), pp. 1005-1013, International Biometric Society
    Stable URL: http://www.jstor.org/stable/2532694
 (p-value correction for Hommel in appendix)

for multicomparison

new book "multiple comparison in R"
Hsu is a good reference but I don't have it.


Author: Josef Pktd and example from H Raja and rewrite from Vincent Davis


TODO
----

* handle exception if empty, shows up only sometimes when running this
- DONE I think

Traceback (most recent call last):
  File "C:\Josef\eclipsegworkspace\statsmodels-josef-experimental-gsoc\scikits\statsmodels\sandbox\stats\multicomp.py", line 711, in <module>
    print 'sh', multipletests(tpval, alpha=0.05, method='sh')
  File "C:\Josef\eclipsegworkspace\statsmodels-josef-experimental-gsoc\scikits\statsmodels\sandbox\stats\multicomp.py", line 241, in multipletests
    rejectmax = np.max(np.nonzero(reject))
  File "C:\Programs\Python25\lib\site-packages\numpy\core\fromnumeric.py", line 1765, in amax
    return _wrapit(a, 'max', axis, out)
  File "C:\Programs\Python25\lib\site-packages\numpy\core\fromnumeric.py", line 37, in _wrapit
    result = getattr(asarray(obj),method)(*args, **kwds)
ValueError: zero-size array to ufunc.reduce without identity

* name of function multipletests, rename to something like pvalue_correction?


'''


#import xlrd
#import xlwt
import scipy.stats
import numpy
import numpy as np
import math
import copy
from scipy import stats
from statsmodels.iolib.table import SimpleTable
from numpy.testing import assert_almost_equal, assert_equal


qcrit = '''
	2 		3 		4 		5 		6 		7 		8 		9 		10
5 	3.64 5.70 	4.60 6.98 	5.22 7.80 	5.67 8.42 	6.03 8.91 	6.33 9.32 	6.58 9.67 	6.80 9.97 	6.99 10.24
6 	3.46 5.24 	4.34 6.33 	4.90 7.03 	5.30 7.56 	5.63 7.97 	5.90 8.32 	6.12 8.61 	6.32 8.87 	6.49 9.10
7 	3.34 4.95 	4.16 5.92 	4.68 6.54 	5.06 7.01 	5.36 7.37 	5.61 7.68 	5.82 7.94 	6.00 8.17 	6.16 8.37
8 	3.26 4.75 	4.04 5.64 	4.53 6.20 	4.89 6.62 	5.17 6.96 	5.40 7.24       5.60 7.47 	5.77 7.68 	5.92 7.86
9 	3.20 4.60 	3.95 5.43 	4.41 5.96 	4.76 6.35 	5.02 6.66 	5.24 6.91       5.43 7.13 	5.59 7.33 	5.74 7.49
10 	3.15 4.48 	3.88 5.27 	4.33 5.77 	4.65 6.14 	4.91 6.43 	5.12 6.67       5.30 6.87 	5.46 7.05 	5.60 7.21
11 	3.11 4.39 	3.82 5.15 	4.26 5.62 	4.57 5.97 	4.82 6.25 	5.03 6.48	5.20 6.67 	5.35 6.84 	5.49 6.99
12 	3.08 4.32 	3.77 5.05 	4.20 5.50 	4.51 5.84 	4.75 6.10 	4.95 6.32	5.12 6.51 	5.27 6.67 	5.39 6.81
13 	3.06 4.26 	3.73 4.96 	4.15 5.40 	4.45 5.73 	4.69 5.98 	4.88 6.19	5.05 6.37 	5.19 6.53 	5.32 6.67
14 	3.03 4.21 	3.70 4.89 	4.11 5.32 	4.41 5.63 	4.64 5.88 	4.83 6.08	4.99 6.26 	5.13 6.41 	5.25 6.54
15 	3.01 4.17 	3.67 4.84 	4.08 5.25 	4.37 5.56 	4.59 5.80 	4.78 5.99	4.94 6.16 	5.08 6.31 	5.20 6.44
16 	3.00 4.13 	3.65 4.79 	4.05 5.19 	4.33 5.49 	4.56 5.72 	4.74 5.92	4.90 6.08 	5.03 6.22 	5.15 6.35
17 	2.98 4.10 	3.63 4.74 	4.02 5.14 	4.30 5.43 	4.52 5.66 	4.70 5.85	4.86 6.01 	4.99 6.15 	5.11 6.27
18 	2.97 4.07 	3.61 4.70 	4.00 5.09 	4.28 5.38 	4.49 5.60 	4.67 5.79	4.82 5.94 	4.96 6.08 	5.07 6.20
19 	2.96 4.05 	3.59 4.67 	3.98 5.05 	4.25 5.33 	4.47 5.55 	4.65 5.73	4.79 5.89 	4.92 6.02 	5.04 6.14
20 	2.95 4.02 	3.58 4.64 	3.96 5.02 	4.23 5.29 	4.45 5.51 	4.62 5.69	4.77 5.84 	4.90 5.97 	5.01 6.09
24 	2.92 3.96 	3.53 4.55 	3.90 4.91 	4.17 5.17 	4.37 5.37 	4.54 5.54	4.68 5.69 	4.81 5.81 	4.92 5.92
30 	2.89 3.89 	3.49 4.45 	3.85 4.80 	4.10 5.05 	4.30 5.24 	4.46 5.40	4.60 5.54 	4.72 5.65 	4.82 5.76
40 	2.86 3.82 	3.44 4.37 	3.79 4.70 	4.04 4.93 	4.23 5.11 	4.39 5.26	4.52 5.39 	4.63 5.50 	4.73 5.60
60 	2.83 3.76 	3.40 4.28 	3.74 4.59 	3.98 4.82 	4.16 4.99 	4.31 5.13	4.44 5.25 	4.55 5.36 	4.65 5.45
120 	2.80 3.70 	3.36 4.20 	3.68 4.50 	3.92 4.71 	4.10 4.87 	4.24 5.01	4.36 5.12 	4.47 5.21 	4.56 5.30
infinity 	2.77 3.64 	3.31 4.12 	3.63 4.40 	3.86 4.60 	4.03 4.76 	4.17 4.88 	4.29 4.99 	4.39 5.08 	4.47 5.16
'''

res = [line.split() for line in qcrit.replace('infinity','9999').split('\n')]
c=np.array(res[2:-1]).astype(float)
#c[c==9999] = np.inf
ccols = np.arange(2,11)
crows = c[:,0]
cv005 = c[:, 1::2]
cv001 = c[:, 2::2]

from scipy import interpolate
def get_tukeyQcrit(k, df, alpha=0.05):
    '''
    return critical values for Tukey's HSD (Q)

    Parameters
    ----------
    k : int in {2, ..., 10}
        number of tests
    df : int
        degrees of freedom of error term
    alpha : {0.05, 0.01}
        type 1 error, 1-confidence level



    not enough error checking for limitations
    '''
    if alpha == 0.05:
        intp = interpolate.interp1d(crows, cv005[:,k-2])
    elif alpha == 0.01:
        intp = interpolate.interp1d(crows, cv001[:,k-2])
    return intp(df)


def Tukeythreegene(first,second,third):
    #Performing the Tukey HSD post-hoc test for three genes
##   qwb = xlrd.open_workbook('F:/Lab/bioinformatics/qcrittable.xls')
##    #opening the workbook containing the q crit table
##   qwb.sheet_names()
##   qcrittable = qwb.sheet_by_name(u'Sheet1')

   firstmean = numpy.mean(first) #means of the three arrays
   secondmean = numpy.mean(second)
   thirdmean = numpy.mean(third)

   firststd = numpy.std(first) #standard deviations of the threearrays
   secondstd = numpy.std(second)
   thirdstd = numpy.std(third)

   firsts2 = math.pow(firststd,2) #standard deviation squared of the three arrays
   seconds2 = math.pow(secondstd,2)
   thirds2 = math.pow(thirdstd,2)

   mserrornum = firsts2*2+seconds2*2+thirds2*2 #numerator for mean square error
   mserrorden = (len(first)+len(second)+len(third))-3 #denominator for mean square error
   mserror = mserrornum/mserrorden #mean square error

   standarderror = math.sqrt(mserror/len(first))
   #standard error, which is square root of mserror and the number of samples in a group

   dftotal = len(first)+len(second)+len(third)-1 #various degrees of freedom
   dfgroups = 2
   dferror = dftotal-dfgroups

   qcrit = 0.5 # fix arbitrary#qcrittable.cell(dftotal, 3).value
   qcrit = get_tukeyQcrit(3, dftotal, alpha=0.05)
   #getting the q critical value, for degrees of freedom total and 3 groups

   qtest3to1 = (math.fabs(thirdmean-firstmean))/standarderror
    #calculating q test statistic values
   qtest3to2 = (math.fabs(thirdmean-secondmean))/standarderror
   qtest2to1 = (math.fabs(secondmean-firstmean))/standarderror

   conclusion = []

##    print qcrit
   print qtest3to1
   print qtest3to2
   print qtest2to1

   if(qtest3to1>qcrit): #testing all q test statistic values to q critical values
       conclusion.append('3to1null')
   else:
       conclusion.append('3to1alt')
   if(qtest3to2>qcrit):
       conclusion.append('3to2null')
   else:
       conclusion.append('3to2alt')
   if(qtest2to1>qcrit):
       conclusion.append('2to1null')
   else:
       conclusion.append('2to1alt')

   return conclusion


#rewrite by Vincent
def Tukeythreegene2(genes): #Performing the Tukey HSD post-hoc test for three genes
   """gend is a list, ie [first, second, third]"""
#   qwb = xlrd.open_workbook('F:/Lab/bioinformatics/qcrittable.xls')
    #opening the workbook containing the q crit table
#   qwb.sheet_names()
#   qcrittable = qwb.sheet_by_name(u'Sheet1')

   means = []
   stds = []
   for gene in genes:
      means.append(numpy.mean(gene))
      std.append(numpy.std(gene))

   #firstmean = numpy.mean(first) #means of the three arrays
   #secondmean = numpy.mean(second)
   #thirdmean = numpy.mean(third)

   #firststd = numpy.std(first) #standard deviations of the three arrays
   #secondstd = numpy.std(second)
   #thirdstd = numpy.std(third)

   stds2 = []
   for std in stds:
      stds2.append(math.pow(std,2))


   #firsts2 = math.pow(firststd,2) #standard deviation squared of the three arrays
   #seconds2 = math.pow(secondstd,2)
   #thirds2 = math.pow(thirdstd,2)

   #mserrornum = firsts2*2+seconds2*2+thirds2*2 #numerator for mean square error
   mserrornum = sum(stds2)*2
   mserrorden = (len(genes[0])+len(genes[1])+len(genes[2]))-3 #denominator for mean square error
   mserror = mserrornum/mserrorden #mean square error


def catstack(args):
    x = np.hstack(args)
    labels = np.hstack([k*np.ones(len(arr)) for k,arr in enumerate(args)])
    return x, labels

#==============================================
#
# Part 1: Multiple Tests and P-Value Correction
#
#==============================================


def multipletests(pvals, alpha=0.05, method='hs', returnsorted=False):
    '''test results and p-value correction for multiple tests


    Parameters
    ----------
    pvals : array_like
        uncorrected p-values
    alpha : float
        FWER, family-wise error rate, e.g. 0.1
    method : string
        Method used for testing and adjustment of pvalues. Can be either the
        full name or initial letters. Available methods are ::

        `bonferroni` : one-step correction
        `sidak` : on-step correction
        `holm-sidak` :
        `holm` :
        `simes-hochberg` :
        `hommel` :
        `fdr_bh` : Benjamini/Hochberg
        `fdr_by` : Benjamini/Yekutieli

    returnsorted : bool
         not tested, return sorted p-values instead of original sequence

    Returns
    -------
    reject : array, boolean
        true for hypothesis that can be rejected for given alpha
    pvals_corrected : array
        p-values corrected for multiple tests
    alphacSidak: float
        corrected pvalue with Sidak method
    alphacBonf: float
        corrected pvalue with Sidak method


    Notes
    -----
    all corrected pvalues now tested against R.
    insufficient "cosmetic" tests yet
    new procedure 'fdr_gbs' not verified yet, p-values derived from scratch not
    reference

    All procedures that are included, control FWER or FDR in the independent
    case, and most are robust in the positively correlated case.

    fdr_gbs: high power, fdr control for independent case and only small
    violation in positively correlated case


    there will be API changes.


    References
    ----------

    '''
    pvals = np.asarray(pvals)
    alphaf = alpha  # Notation ?
    sortind = np.argsort(pvals)
    pvals = pvals[sortind]
    sortrevind = sortind.argsort()
    ntests = len(pvals)
    alphacSidak = 1 - np.power((1. - alphaf), 1./ntests)
    alphacBonf = alphaf / float(ntests)
    if method.lower() in ['b', 'bonf', 'bonferroni']:
        reject = pvals < alphacBonf
        pvals_corrected = pvals * float(ntests)  # not sure

    elif method.lower() in ['s', 'sidak']:
        reject = pvals < alphacSidak
        pvals_corrected = 1 - np.power((1. - pvals), ntests)  # not sure

    elif method.lower() in ['hs', 'holm-sidak']:
        notreject = pvals > alphacSidak
        notrejectmin = np.min(np.nonzero(notreject))
        notreject[notrejectmin:] = True
        reject = ~notreject
        pvals_corrected = None  # not yet implemented
        #TODO: new not tested, mainly guessing by analogy
        pvals_corrected_raw = 1 - np.power((1. - pvals), np.arange(ntests, 0, -1))#ntests) # from "sidak" #pvals / alphacSidak * alphaf
        pvals_corrected = np.maximum.accumulate(pvals_corrected_raw)

    elif method.lower() in ['h', 'holm']:
        notreject = pvals > alphaf / np.arange(ntests, 0, -1) #alphacSidak
        notrejectmin = np.min(np.nonzero(notreject))
        notreject[notrejectmin:] = True
        reject = ~notreject
        pvals_corrected = None  # not yet implemented
        #TODO: new not tested, mainly guessing by analogy
        pvals_corrected_raw = pvals * np.arange(ntests, 0, -1) #ntests) # from "sidak" #pvals / alphacSidak * alphaf
        pvals_corrected = np.maximum.accumulate(pvals_corrected_raw)

    elif method.lower() in ['sh', 'simes-hochberg']:
        alphash = alphaf / np.arange(ntests, 0, -1)
        reject = pvals < alphash
        rejind = np.nonzero(reject)
        if rejind[0].size > 0:
            rejectmax = np.max(np.nonzero(reject))
            reject[:rejectmax] = True
        #check else
        pvals_corrected = None  # not yet implemented
        #TODO: new not tested, mainly guessing by analogy, looks ok in 1 example
        pvals_corrected_raw = np.arange(ntests, 0, -1) * pvals
        pvals_corrected = np.minimum.accumulate(pvals_corrected_raw[::-1])[::-1]

    elif method.lower() in ['ho', 'hommel']:
        a=pvals.copy()
        for m in range(ntests, 1, -1):
            cim = np.min(m * pvals[-m:] / np.arange(1,m+1.))
            a[-m:] = np.maximum(a[-m:], cim)
            a[:-m] = np.maximum(a[:-m], np.minimum(m * pvals[:-m], cim))
        pvals_corrected = a
        reject = a < alphaf

    elif method.lower() in ['fdr_bh', 'fdr_i', 'fdr_p', 'fdri', 'fdrp']:
        #delegate, call with sorted pvals
        reject, pvals_corrected = fdrcorrection0(pvals, alpha=alpha,
                                                 method='indep')
    elif method.lower() in ['fdr_by', 'fdr_n', 'fdr_c', 'fdrn', 'fdrcorr']:
        #delegate, call with sorted pvals
        reject, pvals_corrected = fdrcorrection0(pvals, alpha=alpha,
                                                 method='n')

    elif method.lower() in ['fdr_gbs']:
        #adaptive stepdown in Favrilov, Benjamini, Sarkar, Annals of Statistics 2009
##        notreject = pvals > alphaf / np.arange(ntests, 0, -1) #alphacSidak
##        notrejectmin = np.min(np.nonzero(notreject))
##        notreject[notrejectmin:] = True
##        reject = ~notreject

        ii = np.arange(1, ntests + 1)
        q = (ntests + 1. - ii)/ii * pvals / (1. - pvals)
        pvals_corrected_raw = np.maximum.accumulate(q) #up requirementd

        pvals_corrected = np.minimum.accumulate(pvals_corrected_raw[::-1])[::-1]
        reject = pvals_corrected < alpha

    else:
        raise ValueError('method not recognized')


    if not pvals_corrected is None: #not necessary anymore
        pvals_corrected[pvals_corrected>1] = 1
    if returnsorted:
        return reject, pvals_corrected, alphacSidak, alphacBonf
    else:
        if pvals_corrected is None:
            return reject[sortrevind], pvals_corrected, alphacSidak, alphacBonf
        else:
            return reject[sortrevind], pvals_corrected[sortrevind], alphacSidak, alphacBonf



def maxzero(x):
    '''find all up zero crossings and return the index of the highest

    Not used anymore


    >>> np.random.seed(12345)
    >>> x = np.random.randn(8)
    >>> x
    array([-0.20470766,  0.47894334, -0.51943872, -0.5557303 ,  1.96578057,
            1.39340583,  0.09290788,  0.28174615])
    >>> maxzero(x)
    (4, array([1, 4]))


    no up-zero-crossing at end

    >>> np.random.seed(0)
    >>> x = np.random.randn(8)
    >>> x
    array([ 1.76405235,  0.40015721,  0.97873798,  2.2408932 ,  1.86755799,
           -0.97727788,  0.95008842, -0.15135721])
    >>> maxzero(x)
    (None, array([6]))
    '''
    x = np.asarray(x)
    cond1 = x[:-1] < 0
    cond2 = x[1:] > 0
    #allzeros = np.nonzero(np.sign(x[:-1])*np.sign(x[1:]) <= 0)[0] + 1
    allzeros = np.nonzero((cond1 & cond2) | (x[1:]==0))[0] + 1
    if x[-1] >=0:
        maxz = max(allzeros)
    else:
        maxz = None
    return maxz, allzeros

def maxzerodown(x):
    '''find all up zero crossings and return the index of the highest

    Not used anymore

    >>> np.random.seed(12345)
    >>> x = np.random.randn(8)
    >>> x
    array([-0.20470766,  0.47894334, -0.51943872, -0.5557303 ,  1.96578057,
            1.39340583,  0.09290788,  0.28174615])
    >>> maxzero(x)
    (4, array([1, 4]))


    no up-zero-crossing at end

    >>> np.random.seed(0)
    >>> x = np.random.randn(8)
    >>> x
    array([ 1.76405235,  0.40015721,  0.97873798,  2.2408932 ,  1.86755799,
           -0.97727788,  0.95008842, -0.15135721])
    >>> maxzero(x)
    (None, array([6]))
'''
    x = np.asarray(x)
    cond1 = x[:-1] > 0
    cond2 = x[1:] < 0
    #allzeros = np.nonzero(np.sign(x[:-1])*np.sign(x[1:]) <= 0)[0] + 1
    allzeros = np.nonzero((cond1 & cond2) | (x[1:]==0))[0] + 1
    if x[-1] <=0:
        maxz = max(allzeros)
    else:
        maxz = None
    return maxz, allzeros

def ecdf(x):
    '''no frills empirical cdf used in fdrcorrection
    '''
    nobs = len(x)
    return np.arange(1,nobs+1)/float(nobs)

def rejectionline(n, alpha=0.5):
    '''reference line for rejection in multiple tests

    Not used anymore

    from: section 3.2, page 60
    '''
    t = np.arange(n)/float(n)
    frej = t/( t * (1-alpha) + alpha)
    return frej

#TODO: rename drop 0 at end
def fdrcorrection0(pvals, alpha=0.05, method='indep'):
    '''pvalue correction for false discovery rate

    This covers Benjamini/Hochberg for independent or positively correlated and
    Benjamini/Yekutieli for general or negatively correlated tests. Both are
    available in the function multipletests, as method=`fdr_bh`, resp. `fdr_by`.

    Parameters
    ----------
    pvals : array_like
        set of p-values of the individual tests.
    alpha : float
        error rate
    method : {'indep', 'negcorr')

    Returns
    -------
    rejected : array, bool
        True if a hypothesis is rejected, False if not
    pvalue-corrected : array
        pvalues adjusted for multiple hypothesis testing to limit FDR

    Notes
    -----

    If there is prior information on the fraction of true hypothesis, then alpha
    should be set to alpha * m/m_0 where m is the number of tests,
    given by the p-values, and m_0 is an estimate of the true hypothesis.
    (see Benjamini, Krieger and Yekuteli)

    The two-step method of Benjamini, Krieger and Yekutiel that estimates the number
    of false hypotheses will be available (soon).

    Method names can be abbreviated to first letter, 'i' or 'p' for fdr_bh and 'n' for
    fdr_by.



    '''
    pvals = np.asarray(pvals)

    pvals_sortind = np.argsort(pvals)
    pvals_sorted = pvals[pvals_sortind]
    sortrevind = pvals_sortind.argsort()

    if method in ['i', 'indep', 'p', 'poscorr']:
        ecdffactor = ecdf(pvals_sorted)
    elif method in ['n', 'negcorr']:
        cm = np.sum(1./np.arange(1, len(pvals_sorted)+1))   #corrected this
        ecdffactor = ecdf(pvals_sorted) / cm
##    elif method in ['n', 'negcorr']:
##        cm = np.sum(np.arange(len(pvals)))
##        ecdffactor = ecdf(pvals_sorted)/cm
    else:
        raise ValueError('only indep and necorr implemented')
    reject = pvals_sorted < ecdffactor*alpha
    if reject.any():
        rejectmax = max(np.nonzero(reject)[0])
    else:
        rejectmax = 0
    reject[:rejectmax] = True

    pvals_corrected_raw = pvals_sorted / ecdffactor
    pvals_corrected = np.minimum.accumulate(pvals_corrected_raw[::-1])[::-1]
    pvals_corrected[pvals_corrected>1] = 1
    return reject[sortrevind], pvals_corrected[sortrevind]
    #return reject[pvals_sortind.argsort()]

def fdrcorrection_twostage(pvals, alpha=0.05, iter=False):
    '''(iterated) two stage linear step-up procedure with estimation of number of true
    hypotheses

    Benjamini, Krieger and Yekuteli, procedure in Definition 6

    Parameters
    ----------
    pvals : array_like
        set of p-values of the individual tests.
    alpha : float
        error rate
    method : {'indep', 'negcorr')

    Returns
    -------
    rejected : array, bool
        True if a hypothesis is rejected, False if not
    pvalue-corrected : array
        pvalues adjusted for multiple hypotheses testing to limit FDR
    m0 : int
        ntest - rej, estimated number of true hypotheses
    alpha_stages : list of floats
        A list of alphas that have been used at each stage

    Notes
    -----
    The returned corrected p-values, are from the last stage of the fdr_bh linear step-up
    procedure (fdrcorrection0 with method='indep')

    BKY described several other multi-stage methods, which would be easy to implement.
    However, in their simulation the simple two-stage method (with iter=False) was the
    most robust to the presence of positive correlation

    TODO: What should be returned?

    '''
    ntests = len(pvals)
    alpha_prime = alpha/(1+alpha)
    rej, pvalscorr = fdrcorrection0(pvals, alpha=alpha_prime, method='indep')
    r1 = rej.sum()
    if (r1 == 0) or (r1 == ntests):
        return rej, pvalscorr, ntests - r1
    ri_old = r1
    alpha_stages = [alpha_prime]
    while 1:
        ntests0 = ntests - ri_old
        alpha_star = alpha_prime * ntests / ntests0
        alpha_stages.append(alpha_star)
        #print ntests0, alpha_star
        rej, pvalscorr = fdrcorrection0(pvals, alpha=alpha_star, method='indep')
        ri = rej.sum()
        if (not iter) or ri == ri_old:
            break
        elif ri < ri_old:
            raise RuntimeError(" oops - shouldn't be here")
        ri_old = ri

    return rej, pvalscorr, ntests - ri, alpha_stages





#I don't remember what I changed or why 2 versions,
#this follows german diss ???  with rline
#this might be useful if the null hypothesis is not "all effects are zero"
#rename to _bak and working again on fdrcorrection0
def fdrcorrection_bak(pvals, alpha=0.05, method='indep'):
    '''Reject False discovery rate correction for pvalues

    Old version, to be deleted


    missing: methods that estimate fraction of true hypotheses

    '''
    pvals = np.asarray(pvals)


    pvals_sortind = np.argsort(pvals)
    pvals_sorted = pvals[pvals_sortind]
    pecdf = ecdf(pvals_sorted)
    if method in ['i', 'indep', 'p', 'poscorr']:
        rline = pvals_sorted / alpha
    elif method in ['n', 'negcorr']:
        cm = np.sum(1./np.arange(1, len(pvals)))
        rline = pvals_sorted / alpha * cm
    elif method in ['g', 'onegcorr']:  #what's this ? german diss
        rline = pvals_sorted / (pvals_sorted*(1-alpha) + alpha)
    elif method in ['oth', 'o2negcorr']: # other invalid, cut-paste
        cm = np.sum(np.arange(len(pvals)))
        rline = pvals_sorted / alpha /cm
    else:
        raise ValueError('method not available')

    reject = pecdf >= rline
    if reject.any():
        rejectmax = max(np.nonzero(reject)[0])
    else:
        rejectmax = 0
    reject[:rejectmax] = True
    return reject[pvals_sortind.argsort()]

def mcfdr(nrepl=100, nobs=50, ntests=10, ntrue=6, mu=0.5, alpha=0.05, rho=0.):
    '''MonteCarlo to test fdrcorrection
    '''
    nfalse = ntests - ntrue
    locs = np.array([0.]*ntrue + [mu]*(ntests - ntrue))
    results = []
    for i in xrange(nrepl):
        #rvs = locs + stats.norm.rvs(size=(nobs, ntests))
        rvs = locs + randmvn(rho, size=(nobs, ntests))
        tt, tpval = stats.ttest_1samp(rvs, 0)
        res = fdrcorrection_bak(np.abs(tpval), alpha=alpha, method='i')
        res0 = fdrcorrection0(np.abs(tpval), alpha=alpha)
        #res and res0 give the same results
        results.append([np.sum(res[:ntrue]), np.sum(res[ntrue:])] +
                       [np.sum(res0[:ntrue]), np.sum(res0[ntrue:])] +
                       res.tolist() +
                       np.sort(tpval).tolist() +
                       [np.sum(tpval[:ntrue]<alpha),
                        np.sum(tpval[ntrue:]<alpha)] +
                       [np.sum(tpval[:ntrue]<alpha/ntests),
                        np.sum(tpval[ntrue:]<alpha/ntests)])
    return np.array(results)

def randmvn(rho, size=(1, 2), standardize=False):
    '''create random draws from equi-correlated multivariate normal distribution

    Parameters
    ----------
    rho : float
        correlation coefficient
    size : tuple of int
        size is interpreted (nobs, nvars) where each row


    Returns
    -------
    rvs : ndarray, (nobs, nvars)
        where each row is a independent random draw of nvars-dimensional correlated rvs

    '''
    nobs, nvars = size
    if 0 < rho and rho < 1:
        rvs = np.random.randn(nobs, nvars+1)
        rvs2 = rvs[:,:-1] * np.sqrt((1-rho)) + rvs[:,-1:] * np.sqrt(rho)
    elif rho ==0:
        rvs2 = np.random.randn(nobs, nvars)
    elif rho < 0:
        if rho < -1./(nvars-1):
            raise ValueError('rho has to be larger than -1./(nvars-1)')
        elif rho == -1./(nvars-1):
            rho = -1./(nvars-1+1e-10)  #barely positive definite
        #use Cholesky
        A = rho*np.ones((nvars,nvars))+(1-rho)*np.eye(nvars)
        rvs2 = np.dot(np.random.randn(nobs, nvars), np.linalg.cholesky(A).T)
    if standardize:
        rvs2 = stats.zscore(rvs2)
    return rvs2

#============================
#
# Part 2: Multiple comparisons and independent samples tests
#
#============================

def tiecorrect(xranks):
    '''

    should be equivalent of scipy.stats.tiecorrect

    '''
    #casting to int rounds down, but not relevant for this case
    rankbincount = np.bincount(np.asarray(xranks,dtype=int))
    nties = rankbincount[rankbincount > 1]
    ntot = float(len(xranks));
    tiecorrection = 1 - (nties**3 - nties).sum()/(ntot**3 - ntot)
    return tiecorrection


class GroupsStats(object):
    '''
    statistics by groups (another version)

    groupstats as a class with lazy evaluation (not yet - decorators are still
    missing)

    written this time as equivalent of scipy.stats.rankdata
    gs = GroupsStats(X, useranks=True)
    assert_almost_equal(gs.groupmeanfilter, stats.rankdata(X[:,0]), 15)

    TODO: incomplete doc strings

    '''

    def __init__(self, x, useranks=False, uni=None, intlab=None):
        '''descriptive statistics by groups

        Parameters
        ----------
        x : array, 2d
            first column data, second column group labels
        useranks : boolean
            if true, then use ranks as data corresponding to the
            scipy.stats.rankdata definition (start at 1, ties get mean)
        uni, intlab : arrays (optional)
            to avoid call to unique, these can be given as inputs


        '''
        self.x = np.asarray(x)
        if intlab is None:
            uni, intlab = np.unique(x[:,1], return_inverse=True)
        elif uni is None:
            uni = np.unique(x[:,1])

        self.useranks = useranks


        self.uni = uni
        self.intlab = intlab
        self.groupnobs = groupnobs = np.bincount(intlab)

        #temporary until separated and made all lazy
        self.runbasic(useranks=useranks)



    def runbasic_old(self, useranks=False):
        #check: refactoring screwed up case useranks=True

        #groupxsum = np.bincount(intlab, weights=X[:,0])
        #groupxmean = groupxsum * 1.0 / groupnobs
        x = self.x
        if useranks:
            self.xx = x[:,1].argsort().argsort() + 1  #rankraw
        else:
            self.xx = x[:,0]
        self.groupsum = groupranksum = np.bincount(self.intlab, weights=self.xx)
        #print 'groupranksum', groupranksum, groupranksum.shape, self.groupnobs.shape
        # start at 1 for stats.rankdata :
        self.groupmean = grouprankmean = groupranksum * 1.0 / self.groupnobs # + 1
        self.groupmeanfilter = grouprankmean[self.intlab]
        #return grouprankmean[intlab]

    def runbasic(self, useranks=False):
        #check: refactoring screwed up case useranks=True

        #groupxsum = np.bincount(intlab, weights=X[:,0])
        #groupxmean = groupxsum * 1.0 / groupnobs
        x = self.x
        if useranks:
            xuni, xintlab = np.unique(x[:,0], return_inverse=True)
            ranksraw = x[:,0].argsort().argsort() + 1  #rankraw
            self.xx = GroupsStats(np.column_stack([ranksraw, xintlab]),
                                  useranks=False).groupmeanfilter
        else:
            self.xx = x[:,0]
        self.groupsum = groupranksum = np.bincount(self.intlab, weights=self.xx)
        #print 'groupranksum', groupranksum, groupranksum.shape, self.groupnobs.shape
        # start at 1 for stats.rankdata :
        self.groupmean = grouprankmean = groupranksum * 1.0 / self.groupnobs # + 1
        self.groupmeanfilter = grouprankmean[self.intlab]
        #return grouprankmean[intlab]

    def groupdemean(self):
        return self.xx - self.groupmeanfilter

    def groupsswithin(self):
        xtmp = self.groupdemean()
        return np.bincount(self.intlab, weights=xtmp**2)

    def groupvarwithin(self):
        return self.groupsswithin()/(self.groupnobs-1).sum()


class MultiComparison(object):
    '''Tests for multiple comparisons


    '''

    def __init__(self, x, groups):
        self.data = x
        self.groups = groups
        self.groupsunique, self.groupintlab = np.unique(groups, return_inverse=True)
        self.datali = [x[groups == k] for k in self.groupsunique]
        self.pairindices = np.triu_indices(len(self.groupsunique),1)  #tuple
        self.nobs = x.shape[0]

    def getranks(self):
        '''convert data to rankdata and attach


        This creates rankdata as it is used for non-parametric tests, where
        in the case of ties the average rank is assigned.


        '''
        #bug: the next should use self.groupintlab instead of self.groups
        #update: looks fixed
        #self.ranks = GroupsStats(np.column_stack([self.data, self.groups]),
        self.ranks = GroupsStats(np.column_stack([self.data, self.groupintlab]),
                                 useranks=True)
        self.rankdata = self.ranks.groupmeanfilter



    def kruskal(self, pairs=None, multimethod='T'):
        '''
        pairwise comparison for kruskal-wallis test

        This is just a reimplementation of scipy.stats.kruskal and does
        not yet use a multiple comparison correction.

        '''
        self.getranks()
        tot = self.nobs
        meanranks = self.ranks.groupmean
        groupnobs = self.ranks.groupnobs


        # simultaneous/separate treatment of multiple tests
        f=(tot*(tot+1.)/12.)/stats.tiecorrect(self.rankdata) #(xranks)
        print 'MultiComparison.kruskal'
        for i,j in zip(*self.pairindices):
            #pdiff = np.abs(mrs[i] - mrs[j])
            pdiff = np.abs(meanranks[i] - meanranks[j])
            se = np.sqrt(f * np.sum(1./groupnobs[[i,j]] )) #np.array([8,8]))) #Fixme groupnobs[[i,j]] ))
            Q = pdiff/se

            print i,j, pdiff, se, pdiff/se, pdiff/se>2.6310,
            print stats.norm.sf(Q)*2
            return stats.norm.sf(Q)*2


    def allpairtest(self, testfunc, alpha=0.05, method='bonf', pvalidx=1):
        '''run a pairwise test on all pairs with multiple test correction

        The statistical test given in testfunc is calculated for all pairs
        and the p-values are adjusted by methods in multipletests. The p-value
        correction is generic and based only on the p-values, and does not
        take any special structure of the hypotheses into account.

        Parameters
        ----------
        testfunc : function
            A test function for two (independent) samples. It is assumed that
            the return value on position pvalidx is the p-value.
        alpha : float
            familywise error rate
        method : string
            This specifies the method for the p-value correction. Any method
            of multipletests is possible.
        pvalidx : int (default: 1)
            position of the p-value in the return of testfunc

        Returns
        -------
        sumtab : SimpleTable instance
            summary table for printing

        errors:  TODO: check if this is still wrong, I think it's fixed.
        results from multipletests are in different order
        pval_corrected can be larger than 1 ???
        '''
        res = []
        for i,j in zip(*self.pairindices):
            res.append(testfunc(self.datali[i], self.datali[j]))
        res = np.array(res)
        reject, pvals_corrected, alphacSidak, alphacBonf = \
                multipletests(res[:,pvalidx], alpha=0.05, method=method)
        #print np.column_stack([res[:,0],res[:,1], reject, pvals_corrected])

        i1, i2 = self.pairindices
        if pvals_corrected is None:
            resarr = np.array(zip(i1, i2,
                                  np.round(res[:,0],4),
                                  np.round(res[:,1],4),
                                  reject),
                       dtype=[('group1', int),
                              ('group2', int),
                              ('stat',float),
                              ('pval',float),
                              ('reject', np.bool8)])
        else:
            resarr = np.array(zip(i1, i2,
                                  np.round(res[:,0],4),
                                  np.round(res[:,1],4),
                                  np.round(pvals_corrected,4),
                                  reject),
                       dtype=[('group1', int),
                              ('group2', int),
                              ('stat',float),
                              ('pval',float),
                              ('pval_corr',float),
                              ('reject', np.bool8)])
        from statsmodels.iolib.table import SimpleTable
        summtab = SimpleTable(resarr, headers=resarr.dtype.names)
        summtab.title = 'Test Multiple Comparison %s \n%s%4.2f method=%s' % (testfunc.__name__,
                        'FWER=', alpha, method) + \
                        '\nalphacSidak=%4.2f, alphacBonf=%5.3f' % (alphacSidak, alphacBonf)
        return summtab, (res, reject, pvals_corrected, alphacSidak, alphacBonf), resarr


    def tukeyhsd(self, alpha=0.05):
        #unfinished
        self.groupstats = GroupsStats(
                            np.column_stack([self.data, self.groupintlab]),
                            useranks=False)

        means = self.groupstats.groupmean
        nobs = self.groupstats.groupnobs
        #var_ = self.groupstats.groupvarwithin() #possibly an error in varcorrection in this case
        var_ = np.var(self.groupstats.groupdemean())
        res = tukeyhsd(means, nobs, var_, df=None, alpha=0.05, q_crit=None)

        resarr = np.array(zip(res[0][0], res[0][1],
                                  np.round(res[2],4),
                                  np.round(res[4][:,0],4),
                                  np.round(res[4][:,1],4),
                                  res[1]),
                       dtype=[('group1', int),
                              ('group2', int),
                              ('meandiff',float),
                              ('lower',float),
                              ('upper',float),
                              ('reject', np.bool8)])
        summtab = sm.iolib.SimpleTable(resarr, headers=resarr.dtype.names)
        summtab.title = 'Multiple Comparison of Means - Tukey HSD, FWER=%4.2f' % alpha

        return summtab, res









def rankdata(x):
    '''rankdata, equivalent to scipy.stats.rankdata

    just a different implementation, I have not yet compared speed

    '''
    uni, intlab = np.unique(x[:,0], return_inverse=True)
    groupnobs = np.bincount(intlab)
    groupxsum = np.bincount(intlab, weights=X[:,0])
    groupxmean = groupxsum * 1.0 / groupnobs

    rankraw = x[:,0].argsort().argsort()
    groupranksum = np.bincount(intlab, weights=rankraw)
    # start at 1 for stats.rankdata :
    grouprankmean = groupranksum * 1.0 / groupnobs + 1
    return grouprankmean[intlab]


#new

def compare_ordered(vals, alpha):
    '''simple ordered sequential comparison of means

    vals : array_like
        means or rankmeans for independent groups

    incomplete, no return, not used yet
    '''
    vals = np.asarray(vals)
    alphaf = alpha  # Notation ?
    sortind = np.argsort(vals)
    pvals = vals[sortind]
    sortrevind = sortind.argsort()
    ntests = len(vals)
    #alphacSidak = 1 - np.power((1. - alphaf), 1./ntests)
    #alphacBonf = alphaf / float(ntests)
    v1, v2 = np.triu_indices(ntests, 1)
    #v1,v2 have wrong sequence
    for i in range(4):
        for j in range(4,i, -1):
            print i,j



def varcorrection_unbalanced(nobs_all, srange=False):
    '''correction factor for variance with unequal sample sizes

    this is just a harmonic mean

    Parameters
    ----------
    nobs_all : array_like
        The number of observations for each sample
    srange : bool
        if true, then the correction is divided by the number of samples
        for the variance of the studentized range statistic

    Returns
    -------
    correction : float
        Correction factor for variance.


    Notes
    -----

    variance correction factor is

    1/k * sum_i 1/n_i

    where k is the number of samples and summation is over i=0,...,k-1.
    If all n_i are the same, then the correction factor is 1.

    This needs to be multiplied by the joint variance estimate, means square
    error, MSE. To obtain the correction factor for the standard deviation,
    square root needs to be taken.

    '''
    nobs_all = np.asarray(nobs_all)
    if not srange:
        return (1./nobs_all).sum()
    else:
        return (1./nobs_all).sum()/len(nobs_all)

def varcorrection_pairs_unbalanced(nobs_all, srange=False):
    '''correction factor for variance with unequal sample sizes for all pairs

    this is just a harmonic mean

    Parameters
    ----------
    nobs_all : array_like
        The number of observations for each sample
    srange : bool
        if true, then the correction is divided by 2 for the variance of
        the studentized range statistic

    Returns
    -------
    correction : array
        Correction factor for variance.


    Notes
    -----

    variance correction factor is

    1/k * sum_i 1/n_i

    where k is the number of samples and summation is over i=0,...,k-1.
    If all n_i are the same, then the correction factor is 1.

    This needs to be multiplies by the joint variance estimate, means square
    error, MSE. To obtain the correction factor for the standard deviation,
    square root needs to be taken.

    For the studentized range statistic, the resulting factor has to be
    divided by 2.

    '''
    #TODO: test and replace with broadcasting
    n1, n2 = np.meshgrid(nobs_all, nobs_all)
    if not srange:
        return (1./n1 + 1./n2)
    else:
        return (1./n1 + 1./n2) / 2.

def varcorrection_unequal(var_all, nobs_all, df_all):
    '''return joint variance from samples with unequal variances and unequal
    sample sizes

    something is wrong

    Parameters
    ----------
    var_all : array_like
        The variance for each sample
    nobs_all : array_like
        The number of observations for each sample
    df_all : array_like
        degrees of freedom for each sample

    Returns
    -------
    varjoint : float
        joint variance.
    dfjoint : float
        joint Satterthwait's degrees of freedom


    Notes
    -----
    (copy, paste not correct)
    variance is

    1/k * sum_i 1/n_i

    where k is the number of samples and summation is over i=0,...,k-1.
    If all n_i are the same, then the correction factor is 1/n.

    This needs to be multiplies by the joint variance estimate, means square
    error, MSE. To obtain the correction factor for the standard deviation,
    square root needs to be taken.

    This is for variance of mean difference not of studentized range.
    '''

    var_all = np.asarray(var_all)
    var_over_n = var_all *1./ nobs_all  #avoid integer division
    varjoint = var_over_n.sum()

    dfjoint = varjoint**2 / (var_over_n**2 * df_all).sum()

    return varjoint, dfjoint

def varcorrection_pairs_unequal(var_all, nobs_all, df_all):
    '''return joint variance from samples with unequal variances and unequal
    sample sizes for all pairs

    something is wrong

    Parameters
    ----------
    var_all : array_like
        The variance for each sample
    nobs_all : array_like
        The number of observations for each sample
    df_all : array_like
        degrees of freedom for each sample

    Returns
    -------
    varjoint : array
        joint variance.
    dfjoint : array
        joint Satterthwait's degrees of freedom


    Notes
    -----

    (copy, paste not correct)
    variance is

    1/k * sum_i 1/n_i

    where k is the number of samples and summation is over i=0,...,k-1.
    If all n_i are the same, then the correction factor is 1.

    This needs to be multiplies by the joint variance estimate, means square
    error, MSE. To obtain the correction factor for the standard deviation,
    square root needs to be taken.

    TODO: something looks wrong with dfjoint, is formula from SPSS
    '''
    #TODO: test and replace with broadcasting
    v1, v2 = np.meshgrid(var_all, var_all)
    n1, n2 = np.meshgrid(nobs_all, nobs_all)
    df1, df2 = np.meshgrid(df_all, df_all)

    varjoint = v1/n1 + v2/n2

    dfjoint = varjoint**2 / (df1 * (v1/n1)**2 + df2 * (v2/n2)**2)

    return varjoint, dfjoint

def tukeyhsd(mean_all, nobs_all, var_all, df=None, alpha=0.05, q_crit=None):
    '''simultaneous Tukey HSD


    check: instead of sorting, I use absolute value of pairwise differences
    in means. That's irrelevant for the test, but maybe reporting actual
    differences would be better.
    CHANGED: meandiffs are with sign, studentized range uses abs

    q_crit added for testing

    TODO: error in variance calculation when nobs_all is scalar, missing 1/n

    '''
    mean_all = np.asarray(mean_all)
    #check if or when other ones need to be arrays

    n_means = len(mean_all)

    if df is None:
        df = nobs_all - 1

    if np.size(df) == 1:   # assumes balanced samples with df = n - 1, n_i = n
        df_total = n_means * df
        df = np.ones(n_means) * df
    else:
        df_total = np.sum(df)

    if (np.size(nobs_all) == 1) and (np.size(var_all) == 1):
        #balanced sample sizes and homogenous variance
        var_pairs = 1. * var_all / nobs_all * np.ones((n_means, n_means))

    elif np.size(var_all) == 1:
        #unequal sample sizes and homogenous variance
        var_pairs = var_all * varcorrection_pairs_unbalanced(nobs_all,
                                                             srange=True)
    elif np.size(var_all) > 1:
        var_pairs, df_sum = varcorrection_pairs_unequal(nobs_all, var_all, df)
        var_pairs /= 2.
        #check division by two for studentized range

    else:
        raise ValueError('not supposed to be here')

    #meandiffs_ = mean_all[:,None] - mean_all
    meandiffs_ = mean_all - mean_all[:,None]  #reverse sign, check with R example
    std_pairs_ = np.sqrt(var_pairs)

    #select all pairs from upper triangle of matrix
    idx1, idx2 = np.triu_indices(n_means, 1)
    meandiffs = meandiffs_[idx1, idx2]
    std_pairs = std_pairs_[idx1, idx2]

    st_range = np.abs(meandiffs) / std_pairs #studentized range statistic

    df_total_ = max(df_total, 5)  #TODO: smallest df in table
    if q_crit is None:
        q_crit = get_tukeyQcrit(n_means, df_total, alpha=alpha)

    reject = st_range > q_crit
    crit_int = std_pairs * q_crit
    reject2 = meandiffs > crit_int

    confint = np.column_stack((meandiffs - crit_int, meandiffs + crit_int))

    return (idx1, idx2), reject, meandiffs, std_pairs, confint, q_crit, \
           df_total, reject2

def distance_st_range(mean_all, nobs_all, var_all, df=None, triu=False):
    '''pairwise distance matrix, outsourced from tukeyhsd



    CHANGED: meandiffs are with sign, studentized range uses abs

    q_crit added for testing

    TODO: error in variance calculation when nobs_all is scalar, missing 1/n

    '''
    mean_all = np.asarray(mean_all)
    #check if or when other ones need to be arrays

    n_means = len(mean_all)

    if df is None:
        df = nobs_all - 1

    if np.size(df) == 1:   # assumes balanced samples with df = n - 1, n_i = n
        df_total = n_means * df
    else:
        df_total = np.sum(df)

    if (np.size(nobs_all) == 1) and (np.size(var_all) == 1):
        #balanced sample sizes and homogenous variance
        var_pairs = 1. * var_all / nobs_all * np.ones((n_means, n_means))

    elif np.size(var_all) == 1:
        #unequal sample sizes and homogenous variance
        var_pairs = var_all * varcorrection_pairs_unbalanced(nobs_all,
                                                             srange=True)
    elif np.size(var_all) > 1:
        var_pairs, df_sum = varcorrection_pairs_unequal(nobs_all, var_all, df)
        var_pairs /= 2.
        #check division by two for studentized range

    else:
        raise ValueError('not supposed to be here')

    #meandiffs_ = mean_all[:,None] - mean_all
    meandiffs = mean_all - mean_all[:,None]  #reverse sign, check with R example
    std_pairs = np.sqrt(var_pairs)

    idx1, idx2 = np.triu_indices(n_means, 1)
    if triu:
        #select all pairs from upper triangle of matrix
        meandiffs = meandiffs_[idx1, idx2]
        std_pairs = std_pairs_[idx1, idx2]

    st_range = np.abs(meandiffs) / std_pairs #studentized range statistic

    return st_range, meandiffs, std_pairs, (idx1,idx2)  #return square arrays


def contrast_allpairs(nm):
    '''contrast or restriction matrix for all pairs of nm variables

    Parameters
    ----------
    nm : int

    Returns
    -------
    contr : ndarray, 2d, (nm*(nm-1)/2, nm)
       contrast matrix for all pairwise comparisons

    '''
    contr = []
    for i in range(nm):
        for j in range(i+1, nm):
            contr_row = np.zeros(nm)
            contr_row[i] = 1
            contr_row[j] = -1
            contr.append(contr_row)
    return np.array(contr)

def contrast_all_one(nm):
    '''contrast or restriction matrix for all against first comparison

    Parameters
    ----------
    nm : int

    Returns
    -------
    contr : ndarray, 2d, (nm-1, nm)
       contrast matrix for all against first comparisons

    '''
    contr = np.column_stack((np.ones(nm-1), -np.eye(nm-1)))
    return contr

def contrast_diff_mean(nm):
    '''contrast or restriction matrix for all against mean comparison

    Parameters
    ----------
    nm : int

    Returns
    -------
    contr : ndarray, 2d, (nm-1, nm)
       contrast matrix for all against mean comparisons

    '''
    return np.eye(nm) - np.ones((nm,nm))/nm

def tukey_pvalues(std_range, nm, df):
    #corrected but very slow with warnings about integration
    from statsmodels.sandbox.distributions.multivariate import mvstdtprob
    #nm = len(std_range)
    contr = contrast_allpairs(nm)
    corr = np.dot(contr, contr.T)/2.
    tstat = std_range / np.sqrt(2) * np.ones(corr.shape[0]) #need len of all pairs
    return multicontrast_pvalues(tstat, corr, df=df)

def test_tukey_pvalues():
    #testcase with 3 is not good because all pairs has also 3*(3-1)/2=3 elements
    res = tukey_pvalues(3.649, 3, 16) #3.649*np.ones(3), 16)
    assert_almost_equal(0.05, res[0], 3)
    assert_almost_equal(0.05*np.ones(3), res[1], 3)


def multicontrast_pvalues(tstat, tcorr, df=None, dist='t', alternative='two-sided'):
    '''pvalues for simultaneous tests

    '''
    from statsmodels.sandbox.distributions.multivariate import mvstdtprob
    if (df is None) and (dist == 't'):
        raise ValueError('df has to be specified for the t-distribution')
    tstat = np.asarray(tstat)
    ntests = len(tstat)
    cc = np.abs(tstat)
    pval_global = 1 - mvstdtprob(-cc,cc, tcorr, df)
    pvals = []
    for ti in cc:
        limits = ti*np.ones(ntests)
        pvals.append(1 - mvstdtprob(-cc,cc, tcorr, df))

    return pval_global, np.asarray(pvals)





class StepDown(object):
    '''a class for step down methods

    This is currently for simple tree subset descend, similar to homogeneous_subsets,
    but checks all leave-one-out subsets instead of assuming an ordered set.
    Comment in SAS manual:
    SAS only uses interval subsets of the sorted list, which is sufficient for range
    tests (maybe also equal variance and balanced sample sizes are required).
    For F-test based critical distances, the restriction to intervals is not sufficient.

    This version uses a single critical value of the studentized range distribution
    for all comparisons, and is therefore a step-down version of Tukey HSD.
    The class is written so it can be subclassed, where the get_distance_matrix and
    get_crit are overwritten to obtain other step-down procedures such as REGW.

    iter_subsets can be overwritten, to get a recursion as in the many to one comparison
    with a control such as in Dunnet's test.


    A one-sided right tail test is not covered because the direction of the inequality
    is hard coded in check_set.  Also Peritz's check of partitions is not possible, but
    I have not seen it mentioned in any more recent references.
    I have only partially read the step-down procedure for closed tests by Westfall.

    One change to make it more flexible, is to separate out the decision on a subset,
    also because the F-based tests, FREGW in SPSS, take information from all elements of
    a set and not just pairwise comparisons. I haven't looked at the details of
    the F-based tests such as Sheffe yet. It looks like running an F-test on equality
    of means in each subset. This would also outsource how pairwise conditions are
    combined, any larger or max. This would also imply that the distance matrix cannot
    be calculated in advance for tests like the F-based ones.


    '''

    def __init__(self, vals, nobs_all, var_all, df=None):
        self.vals = vals
        self.n_vals = len(vals)
        self.nobs_all = nobs_all
        self.var_all = var_all
        self.df = df
        # the following has been moved to run
        #self.cache_result = {}
        #self.crit = self.getcrit(0.5)   #decide where to set alpha, moved to run
        #self.accepted = []  #store accepted sets, not unique

    def get_crit(self, alpha):
        #currently tukey Q, add others
        q_crit = get_tukeyQcrit(self.n_vals, self.df, alpha=alpha)
        return q_crit * np.ones(self.n_vals)



    def get_distance_matrix(self):
        '''studentized range statistic'''
        #make into property, decorate
        dres = distance_st_range(self.vals, self.nobs_all, self.var_all, df=self.df)
        self.distance_matrix = dres[0]

    def iter_subsets(self, indices):
        for ii in range(len(indices)):
            idxsub = copy.copy(indices)
            idxsub.pop(ii)
            yield idxsub


    def check_set(self, indices):
        '''check whether pairwise distances of indices satisfy condition

        '''
        indtup = tuple(indices)
        if indtup in self.cache_result:
            return self.cache_result[indtup]
        else:
            set_distance_matrix = self.distance_matrix[np.asarray(indices)[:,None], indices]
            n_elements = len(indices)
            if np.any(set_distance_matrix > self.crit[n_elements-1]):
                res = True
            else:
                res = False
            self.cache_result[indtup] = res
            return res

    def stepdown(self, indices):
        print indices
        if self.check_set(indices): # larger than critical distance
            if (len(indices) > 2):  # step down into subsets if more than 2 elements
                for subs in self.iter_subsets(indices):
                    self.stepdown(subs)
            else:
                self.rejected.append(tuple(indices))
        else:
            self.accepted.append(tuple(indices))
            return indices

    def run(self, alpha):
        '''main function to run the test,

        could be done in __call__ instead
        this could have all the initialization code

        '''
        self.cache_result = {}
        self.crit = self.get_crit(alpha)   #decide where to set alpha, moved to run
        self.accepted = []  #store accepted sets, not unique
        self.rejected = []
        self.get_distance_matrix()
        self.stepdown(range(self.n_vals))

        return list(set(self.accepted)), list(set(sd.rejected))






def homogeneous_subsets(vals, dcrit):
    '''recursively check all pairs of vals for minimum distance

    step down method as in Newman-Keuls and Ryan procedures. This is not a
    closed procedure since not all partitions are checked.

    Parameters
    ----------
    vals : array_like
        values that are pairwise compared
    dcrit : array_like or float
        critical distance for rejecting, either float, or 2-dimensional array
        with distances on the upper triangle.

    Returns
    -------
    rejs : list of pairs
        list of pair-indices with (strictly) larger than critical difference
    nrejs : list of pairs
        list of pair-indices with smaller than critical difference
    lli : list of tuples
        list of subsets with smaller than critical difference
    res : tree
        result of all comparisons (for checking)


    this follows description in SPSS notes on Post-Hoc Tests

    Because of the recursive structure, some comparisons are made several
    times, but only unique pairs or sets are returned.

    Examples
    --------
    >>> m = [0, 2, 2.5, 3, 6, 8, 9, 9.5,10 ]
    >>> rej, nrej, ssli, res = homogeneous_subsets(m, 2)
    >>> set_partition(ssli)
    ([(5, 6, 7, 8), (1, 2, 3), (4,)], [0])
    >>> [np.array(m)[list(pp)] for pp in set_partition(ssli)[0]]
    [array([  8. ,   9. ,   9.5,  10. ]), array([ 2. ,  2.5,  3. ]), array([ 6.])]


    '''

    nvals = len(vals)
    indices_ = range(nvals)
    rejected = []
    subsetsli = []
    if np.size(dcrit) == 1:
        dcrit = dcrit*np.ones((nvals, nvals))  #example numbers for experimenting
    def subsets(vals, indices_):
        '''recursive function for constructing homogeneous subset

        registers rejected and subsetli in outer scope
        '''
        i, j = (indices_[0], indices_[-1])
        if vals[-1] - vals[0] > dcrit[i,j]:
            rejected.append((indices_[0], indices_[-1]))
            return [subsets(vals[:-1], indices_[:-1]),
                    subsets(vals[1:], indices_[1:]),
                    (indices_[0], indices_[-1])]
        else:
            subsetsli.append(tuple(indices_))
            return indices_
    res = subsets(vals, indices_)

    all_pairs = [(i,j) for i in range(nvals) for j in range(nvals-1,i,-1)]
    rejs = set(rejected)
    not_rejected = list(set(all_pairs) - rejs)

    return list(rejs), not_rejected, list(set(subsetsli)), res

def set_partition(ssli):
    '''extract a partition from a list of tuples

    this should be correctly called select largest disjoint sets.
    Begun and Gabriel 1981 don't seem to be bothered by sets of accepted
    hypothesis with joint elements,
    e.g. maximal_accepted_sets = { {1,2,3}, {2,3,4} }

    This creates a set partition from a list of sets given as tuples.
    It tries to find the partition with the largest sets. That is, sets are
    included after being sorted by length.

    If the list doesn't include the singletons, then it will be only a
    partial partition. Missing items are singletons (I think).

    Examples
    --------
    >>> li
    [(5, 6, 7, 8), (1, 2, 3), (4, 5), (0, 1)]
    >>> set_partition(li)
    ([(5, 6, 7, 8), (1, 2, 3)], [0, 4])

    '''
    part = []
    for s in sorted(list(set(ssli)), key=len)[::-1]:
        #print s,
        s_ = set(s).copy()
        if not any(set(s_).intersection(set(t)) for t in part):
            #print 'inside:', s
            part.append(s)
        #else: print part

    missing = list(set(i for ll in ssli for i in ll)
                   - set(i for ll in part for i in ll))
    return part, missing


def set_remove_subs(ssli):
    '''remove sets that are subsets of another set from a list of tuples

    Parameters
    ----------
    ssli : list of tuples
        each tuple is considered as a set

    Returns
    -------
    part : list of tuples
        new list with subset tuples removed, it is sorted by set-length of tuples. The
        list contains original tuples, duplicate elements are not removed.

    Examples
    --------
    >>> set_remove_subs([(0, 1), (1, 2), (1, 2, 3), (0,)])
    [(1, 2, 3), (0, 1)]
    >>> set_remove_subs([(0, 1), (1, 2), (1,1, 1, 2, 3), (0,)])
    [(1, 1, 1, 2, 3), (0, 1)]

    '''
    #TODO: maybe convert all tuples to sets immediately, but I don't need the extra efficiency
    part = []
    for s in sorted(list(set(ssli)), key=lambda x: len(set(x)))[::-1]:
        #print s,
        #s_ = set(s).copy()
        if not any(set(s).issubset(set(t)) for t in part):
            #print 'inside:', s
            part.append(s)
        #else: print part

##    missing = list(set(i for ll in ssli for i in ll)
##                   - set(i for ll in part for i in ll))
    return part




if __name__ == '__main__':

    examples = ['tukey', 'tukeycrit', 'fdr', 'fdrmc', 'bonf', 'randmvn',
                'multicompdev', 'None']#[-1]

    if 'tukey' in examples:
        #Example Tukey
        x = np.array([[0,0,1]]).T + np.random.randn(3, 20)
        print Tukeythreegene(*x)

        #Example FDR
        #------------

    if ('fdr' in examples) or ('bonf' in examples):
        x1 = [1,1,1,0,-1,-1,-1,0,1,1,-1,1]
        print zip(np.arange(len(x1)), x1)
        print maxzero(x1)
        #[(0, 1), (1, 1), (2, 1), (3, 0), (4, -1), (5, -1), (6, -1), (7, 0), (8, 1), (9, 1), (10, -1), (11, 1)]
        #(11, array([ 3,  7, 11]))

        print maxzerodown(-np.array(x1))

        locs = np.linspace(0,1,10)
        locs = np.array([0.]*6 + [0.75]*4)
        rvs = locs + stats.norm.rvs(size=(20,10))
        tt, tpval = stats.ttest_1samp(rvs, 0)
        tpval_sortind = np.argsort(tpval)
        tpval_sorted = tpval[tpval_sortind]

        reject = tpval_sorted < ecdf(tpval_sorted)*0.05
        reject2 = max(np.nonzero(reject))
        print reject

        res = np.array(zip(np.round(rvs.mean(0),4),np.round(tpval,4),
                           reject[tpval_sortind.argsort()]),
                       dtype=[('mean',float),
                              ('pval',float),
                              ('reject', np.bool8)])
        #from statsmodels.iolib import SimpleTable
        print SimpleTable(res, headers=res.dtype.names)
        print fdrcorrection_bak(tpval, alpha=0.05)
        print reject

        print '\nrandom example'
        print 'bonf', multipletests(tpval, alpha=0.05, method='bonf')
        print 'sidak', multipletests(tpval, alpha=0.05, method='sidak')
        print 'hs', multipletests(tpval, alpha=0.05, method='hs')
        print 'sh', multipletests(tpval, alpha=0.05, method='sh')
        pvals = np.array('0.0020 0.0045 0.0060 0.0080 0.0085 0.0090 0.0175 0.0250 '
                 '0.1055 0.5350'.split(), float)
        print '\nexample from lecturnotes'
        for meth in ['bonf', 'sidak', 'hs', 'sh']:
            print meth, multipletests(pvals, alpha=0.05, method=meth)

    if 'fdrmc' in examples:
        mcres = mcfdr(nobs=100, nrepl=1000, ntests=30, ntrue=30, mu=0.1, alpha=0.05, rho=0.3)
        mcmeans = np.array(mcres).mean(0)
        print mcmeans
        print mcmeans[0]/6., 1-mcmeans[1]/4.
        print mcmeans[:4], mcmeans[-4:]


    if 'randmvn' in examples:
        rvsmvn = randmvn(0.8, (5000,5))
        print np.corrcoef(rvsmvn, rowvar=0)
        print rvsmvn.var(0)


    if 'tukeycrit' in examples:
        print get_tukeyQcrit(8, 8, alpha=0.05), 5.60
        print get_tukeyQcrit(8, 8, alpha=0.01), 7.47


    if 'multicompdev' in examples:
        #development of kruskal-wallis multiple-comparison
        #example from matlab file exchange

        X = np.array([[7.68, 1], [7.69, 1], [7.70, 1], [7.70, 1], [7.72, 1],
                      [7.73, 1], [7.73, 1], [7.76, 1], [7.71, 2], [7.73, 2],
                      [7.74, 2], [7.74, 2], [7.78, 2], [7.78, 2], [7.80, 2],
                      [7.81, 2], [7.74, 3], [7.75, 3], [7.77, 3], [7.78, 3],
                      [7.80, 3], [7.81, 3], [7.84, 3], [7.71, 4], [7.71, 4],
                      [7.74, 4], [7.79, 4], [7.81, 4], [7.85, 4], [7.87, 4],
                      [7.91, 4]])
        xli = [X[X[:,1]==k,0] for k in range(1,5)]
        xranks = stats.rankdata(X[:,0])
        xranksli = [xranks[X[:,1]==k] for k in range(1,5)]
        xnobs = np.array([len(x) for x in xli])
        meanranks = [item.mean() for item in xranksli]
        sumranks = [item.sum() for item in xranksli]
        # equivalent function
        #from scipy import special
        #-np.sqrt(2.)*special.erfcinv(2-0.5) == stats.norm.isf(0.25)
        stats.norm.sf(0.67448975019608171)
        stats.norm.isf(0.25)

        mrs = np.sort(meanranks)
        v1, v2 = np.triu_indices(4,1)
        print '\nsorted rank differences'
        print mrs[v2] - mrs[v1]
        diffidx = np.argsort(mrs[v2] - mrs[v1])[::-1]
        mrs[v2[diffidx]] - mrs[v1[diffidx]]

        print '\nkruskal for all pairs'
        for i,j in zip(v2[diffidx], v1[diffidx]):
            print i,j, stats.kruskal(xli[i], xli[j]),
            mwu, mwupval = stats.mannwhitneyu(xli[i], xli[j], use_continuity=False)
            print mwu, mwupval*2, mwupval*2<0.05/6., mwupval*2<0.1/6.





        uni, intlab = np.unique(X[:,0], return_inverse=True)
        groupnobs = np.bincount(intlab)
        groupxsum = np.bincount(intlab, weights=X[:,0])
        groupxmean = groupxsum * 1.0 / groupnobs

        rankraw = X[:,0].argsort().argsort()
        groupranksum = np.bincount(intlab, weights=rankraw)
        # start at 1 for stats.rankdata :
        grouprankmean = groupranksum * 1.0 / groupnobs + 1
        assert_almost_equal(grouprankmean[intlab], stats.rankdata(X[:,0]), 15)
        gs = GroupsStats(X, useranks=True)
        print '\ngroupmeanfilter and grouprankmeans'
        print gs.groupmeanfilter
        print grouprankmean[intlab]
        #the following has changed
        #assert_almost_equal(gs.groupmeanfilter, stats.rankdata(X[:,0]), 15)

        xuni, xintlab = np.unique(X[:,0], return_inverse=True)
        gs2 = GroupsStats(np.column_stack([X[:,0], xintlab]), useranks=True)
        #assert_almost_equal(gs2.groupmeanfilter, stats.rankdata(X[:,0]), 15)

        rankbincount = np.bincount(xranks.astype(int))
        nties = rankbincount[rankbincount > 1]
        ntot = float(len(xranks));
        tiecorrection = 1 - (nties**3 - nties).sum()/(ntot**3 - ntot)
        assert_almost_equal(tiecorrection, stats.tiecorrect(xranks),15)
        print '\ntiecorrection for data and ranks'
        print tiecorrection
        print tiecorrect(xranks)

        tot = X.shape[0]
        t=500 #168
        f=(tot*(tot+1.)/12.)-(t/(6.*(tot-1.)))
        f=(tot*(tot+1.)/12.)/stats.tiecorrect(xranks)
        print '\npairs of mean rank differences'
        for i,j in zip(v2[diffidx], v1[diffidx]):
            #pdiff = np.abs(mrs[i] - mrs[j])
            pdiff = np.abs(meanranks[i] - meanranks[j])
            se = np.sqrt(f * np.sum(1./xnobs[[i,j]] )) #np.array([8,8]))) #Fixme groupnobs[[i,j]] ))
            print i,j, pdiff, se, pdiff/se, pdiff/se>2.6310

        multicomp = MultiComparison(*X.T)
        multicomp.kruskal()
        gsr = GroupsStats(X, useranks=True)

        print '\nexamples for kruskal multicomparison'
        for i in range(10):
            x1, x2 = (np.random.randn(30,2) + np.array([0, 0.5])).T
            skw = stats.kruskal(x1, x2)
            mc2=MultiComparison(np.r_[x1, x2], np.r_[np.zeros(len(x1)), np.ones(len(x2))])
            newskw = mc2.kruskal()
            print skw, np.sqrt(skw[0]), skw[1]-newskw, (newskw/skw[1]-1)*100

        tablett, restt, arrtt = multicomp.allpairtest(stats.ttest_ind)
        tablemw, resmw, arrmw = multicomp.allpairtest(stats.mannwhitneyu)
        print
        print tablett
        print
        print tablemw
        tablemwhs, resmw, arrmw = multicomp.allpairtest(stats.mannwhitneyu, method='hs')
        print
        print tablemwhs

    if 'last' in examples:
        xli = (np.random.randn(60,4) + np.array([0, 0, 0.5, 0.5])).T
        #Xrvs = np.array(catstack(xli))
        xrvs, xrvsgr = catstack(xli)
        multicompr = MultiComparison(xrvs, xrvsgr)
        tablett, restt, arrtt = multicompr.allpairtest(stats.ttest_ind)
        print tablett


        xli=[[8,10,9,10,9],[7,8,5,8,5],[4,8,7,5,7]]
        x,l = catstack(xli)
        gs4 = GroupsStats(np.column_stack([x,l]))
        print gs4.groupvarwithin()


    #test_tukeyhsd() #moved to test_multi.py

    gmeans = np.array([ 7.71375,  7.76125,  7.78428571,  7.79875])
    gnobs = np.array([8, 8, 7, 8])
    sd = StepDown(gmeans, gnobs, 0.001, [27])

    #example from BKY
    pvals = [0.0001, 0.0004, 0.0019, 0.0095, 0.0201, 0.0278, 0.0298, 0.0344, 0.0459,
             0.3240, 0.4262, 0.5719, 0.6528, 0.7590, 1.000 ]

    #same number of rejection as in BKY paper:
    #single step-up:4, two-stage:8, iterated two-step:9
    #also alpha_star is the same as theirs for TST
    print fdrcorrection0(pvals, alpha=0.05, method='indep')
    print fdrcorrection_twostage(pvals, alpha=0.05, iter=False)
    res_tst = fdrcorrection_twostage(pvals, alpha=0.05, iter=False)
    assert_almost_equal([0.047619, 0.0649], res_tst[-1][:2],3) #alpha_star for stage 2
    assert_equal(8, res_tst[0].sum())
    print fdrcorrection_twostage(pvals, alpha=0.05, iter=True)
    print 'fdr_gbs', multipletests(pvals, alpha=0.05, method='fdr_gbs')
    #multicontrast_pvalues(tstat, tcorr, df)
    test_tukey_pvalues()
    tukey_pvalues(3.649, 3, 16)
