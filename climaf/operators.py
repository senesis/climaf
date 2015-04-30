"""

CliMAF handling of external scripts and binaries , and of internal operators (Python funcs)

"""

# Created : S.Senesi - 2014

import os, re, sys, subprocess
import driver
from clogging import clogger

# Next definition can be splitted in a set managed by an administrator, and
# other sets managed and fed by users. But it should be enforced that no redefinition
# occurs for some really basic operators (should it ?)
internals=[]
scripts=dict()
operators=dict()
derived_variables=dict()

class scriptFlags():
    def __init__(self,canOpendap=False, canSelectVar=False, 
                 canSelectTime=False, canSelectDomain=False, 
                 canAggregateTime=False, canAlias=False,
                 canMissing=False,
                 commuteWithTimeConcatenation=False,commuteWithSpaceConcatenation=False):
        self.canOpendap=canOpendap
        self.canSelectVar=canSelectVar
        self.canSelectTime=canSelectTime
        self.canSelectDomain=canSelectDomain
        self.canAggregateTime=canAggregateTime
        self.canAlias=canAlias
        self.canMissing=canMissing
        self.commuteWithTimeConcatenation=commuteWithTimeConcatenation
        self.commuteWithSpaceConcatenation=commuteWithSpaceConcatenation

class cscript():
    def __init__(self,name, command, format="nc", canOpendap=False, 
                 commuteWithTimeConcatenation=False, commuteWithSpaceConcatenation=False, **kwargs):
        """
        Declare a script or binary as a 'CliMAF operator', and define a Python function with the same name

        Args:
          name (str): name for the CliMAF operator.
          command (str): script calling sequence, according to the syntax described below.
          format (str): script outputs format -- either 'nc' or 'png' or 'None'; defaults to 'nc'
          canOpendap (bool, optional): is the script able to use OpenDAP URIs ? default to False
          commuteWithTimeConcatenation (bool, optional): can the operation commute with concatenation
            of time periods ? set it to true, if the operator can be applied on time
            chunks separately, in order to allow for incremental computation / time chunking;
            defaults to False
          commuteWithSpaceConcatenation (bool, optional): can the operation commute with concatenation
            of space domains ? defaults to False (see commuteWithTimeConcatenation)
          **kwargs : possible keyword arguments, with keys matching '<outname>_var', for providing
            a format string allowing to compute the variable name for output 'outname' (see below).
        
        Returns:
          None
          
        The script calling sequence pattern string (arg 'command') indicates how to build the system call
        which actually launches the script, with a match between python objects and formal arguments;

        For introducing the syntax, please consider this example, with the following commands::
        
        >>> cscript('mycdo','cdo ${operator} ${in} ${out}')
        >>> # Next line is necessary to ease reference to the new operator (rather than write 'climaf.operators.mycdo') :
        >>> from climaf.operators import mycdo     
        >>> # define some dataset
        >>> tas_ds = ds(project='example', experiment='AMIPV6', variable='tas', period='1980-1981')
        >>> # Apply operator 'mycdo' to dataset 'tas_ds', choosing a given 'operator' argument
        >>> tas_avg = mycdo(tas_ds,operator='timavg')
        
        CliMAF will later on launch this call behind the curtain::
        
        $ cdo tim_avg /home/my/tmp/climaf_cache/8a/5.nc /home/my/tmp/climaf_cache/4e/4.nc

        where :

        - the last filename is generated by CliMAF from the formal exprerssion describing 'tas_avg'
        - the first filename provide a file generated by CliMAF which includes the required data fot tas_ds

        **Detailed syntax**:

        -  formal arguments appear as : ``${argument}`` (in the example : ``${in}``, ``${out}``, ``${operator}`` )
        
        -  except for reserved keywords, arguments in the pattern will be
           replaced by the values for corresponding keywords used when invoking
           the diagnostic operator:

          - in the example above : argument ``operator`` is replaced by value ``timavg``,
            which is a keyword known to the external binary called, CDO  
        
        -  reserved argument keywords are :
        
         - **in, in_<digit>, ins, ins_<digit>** : they will be
           replaced by CliMAF managed filenames for input data, as
           deduced from dataset description or upstream computation; these
           filenames can actually be remote URLs (if the script can use
           OpenDAP, see args), local 'raw' data files, or CliMAF cache
           filenames
        
          -  **in** stands for the URL of the first dataset invoked in the
             operator call
        
          -  **in_<digit>** stands for the next ones, in the same order
        
          -  **ins** and **ins_<digit>** stand for the case where the script can
             select input from multiple input files or URLs (e.g. when the
             whole period to process spans over multiple files); in that case,
             a single string (surrounded with double quotes) will carry
             multiple URLs

         -  **var, var_<digit>** : when a script can select a variable in a
            multi-variable input stream, this is declared by adding this
            keyword in the calling sequence; CliMAF will replace it by the
            actual variable name to process; 'var' stands for first input
            stream, 'var_<digit>' for the next ones;

            - in the example above, we assume that external binary CDO is
              not tasked with selecting the variable, and that CliMAF must
              feed CDO with a datafile where it has already performed the
              selection
         
         
         - **period, period_<digit>** : when a script can select a time
           period in the content of a file or stream, it should declare it
           by putting this keyword in the pattern, which will be replaced at
           call time by the period written as <date1>-<date2>, where date is
           formated as YYYYMMDD ;

            - time intervals must be interpreted as [date1, date2[

            - 'period' stands for the first input_stream,

            - 'period_<n>' for the next ones, in the order of actual call;

           - in the example above, this keyword is not used, which means that
             CliMAF has to select the period upstream of feeding CDO with the
             data
         
         - **period_iso, period_iso_<digit>** : as for **period** above,
           except that the date formating fits CDO conventions : 

            - date format is ISO : YYYY-MM-DDTHH:MM:SS

            - interval is [date1,date2_iso], where date2_iso is 1 minute before
              date2

            - separator between dates is : ,  

         - **domain, domain_<digit>** : when a script can select a domain 
           in the input grid, this is declared by adding this
           keyword in the calling sequence; CliMAF will replace it by the
           domain definition if needed, as 'latmin,latmax,lonmin,lonmax' ;
           'domain' stands for first input stream, 'domain_<digit>' for the 
           next ones :

            - in the example above, we assume that external binary CDO is
              not tasked with selecting the domain, and that CliMAF must
              feed CDO with a datafile where it has already performed the
              selection
         
         - **out, out_<word>** : CliMAF provide file names for output
           files (if there is no such field, the script will have
           only 'side effects', e.g. launch a viewer). Main output
           file must be created by the script with the name provided
           at the location of argument ${out}. Using arguments like
           'out_<word>' tells CliMAF that the script provide some
           secondary output, which will be symbolically known in
           CliMAF syntax as an attribute of the main object; by
           default, the variable name of each output equals the name
           of the output (except for the main ouput, which variable
           name is supposed to be the same as for the first input);
           for other cases, see argument \*\*kwargs to provide a
           format string, used to derive the variable name from first
           input variable name as in e.g. :
           ``output2_var='std_dev(%s)'`` for the output labelled
           output2 (i.e. declared as '${out_output2}')

           - in the example above, we just apply the convention used by CDO,
             which expects that you provide an output filename as last
             argument on the command line. See example mean_and_sdev in doc
             for advanced usage.

         - **crs** : will be replaced by the CliMAF Reference Syntax expression
           describing the first input stream; can be useful for plot title
           or legend

         - **alias** : means that the script can make an on the fly re-scaling
           and renaming of a variable. Will be replaced by a string which pattern is :
           'new_varname,file_varname,scale,offset'. The script should then output
           a variable new_varname = file_varname * scale + offset

         - **missing** : means that the script can make an on-the-fly transformation
           of a givent constant to missing values

        """
        # Check that script name do not clash with an existing symbol 
        if name in dir() and name not in scripts :
            clogger.error("trying to redefine %s, which exists outside CliMAF"%name)
            return None
        if name in scripts : clogger.warning("Redefining CliMAF script %s"%name)
        #
        # Check now that script is executable
        scriptcommand=command.split(' ')[0].replace("(","")
        ex=subprocess.Popen(['which',scriptcommand], stdout=subprocess.PIPE)
        if ex.wait() != 0 :
            Climaf_Operator_Error("defining %s : command %s is not executable"%\
                              (name,scriptcommand))
        executable=ex.stdout.read().replace('\n','')
        #
        # Analyze inputs field keywords and populate dict attribute 'inputs' with some properties
        self.inputs=dict()
        it=re.finditer(r"\${(?P<keyw>(?P<mult>mm)?in(?P<serie>s)?(_(?P<n>([\d]+)))?)}",command)
        for oc in it : 
            if (oc.group("n") is not None) : rank=int(oc.group("n"))
            else : rank=0
            if rank in self.inputs :
                Climaf_Operator_Error("When defining %s : duplicate declaration for input #%d"%(name,rank))
            multiple=(oc.group("mult") is not None)
            serie=(oc.group("serie") is not None)
            self.inputs[rank]=(oc.group("keyw"),multiple,serie)
        if len(self.inputs)==0 : 
            Climaf_Operator_Error("When defining %s : command %s must include at least one of "
                                  "${in} ${ins} ${min} or ${in_..} for specifying how CliMAF will "
                                  "provide the input filename(s)"% (name,command))
        #print self.inputs
        for i in range(len(self.inputs)) :
            if i+1 not in self.inputs and not ( i == 0 and 0  in self.inputs) :
                Climaf_Operator_Error("When defining %s : error in input sequence for rank %d"%(name,i+1))
        #
        # Check if command includes an argument allowing for providing an output filename
        if command.find("${out") < 0 : format=None
        #
        # Search in call arguments for keywords matching "<output_name>_var" which may provide
        # format string for 'computing' outputs variable name from input variable name
        outvarnames=dict() ; pattern=r"^(.*)_var$"
        for p in kwargs : 
            if re.match(pattern,p):
                outvarnames[re.findall(pattern,p)[0]]=kwargs[p]
        #clogger.debug("outvarnames = "+`outvarnames`)
        #
        # Analyze outputs names , associated variable names (or format strings), and store 
        # it in attribute dict 'outputs' 
        self.outputs=dict()
        it=re.finditer(r"\${out(_(?P<outname>[\w-]*))?}",command)
        for occ in it :
            outname=occ.group("outname") 
            if outname is not None :
                if (outname in outvarnames) : 
                    self.outputs[outname]=outvarnames[outname]
                else :
                    self.outputs[outname]=outname
            else:
                self.outputs[None]="%s"
        #clogger.debug("outputs = "+`self.outputs`)
        #
        canSelectVar= (command.find("${var}") > 0 )
        canAggregateTime=(command.find("${ins}") > 0 or command.find("${ins_1}") > 0)
        canAlias= (command.find("${alias}") > 0 )
        canMissing= (command.find("${missing}") > 0 )
        canSelectTime=False
        if command.find("${period}") > 0  or command.find("${period_1}") > 0 :
            canSelectTime=True
        if command.find("${period_iso}") > 0  or command.find("${period_iso_1}") > 0 :
            canSelectTime=True
        canSelectDomain=(command.find("${domain}") > 0  or command.find("${domain_1}") > 0)
        #
        self.name=name
        self.command=command
        self.flags=scriptFlags(canOpendap, canSelectVar, canSelectTime, \
            canSelectDomain, canAggregateTime, canAlias, canAlias,\
            commuteWithTimeConcatenation, commuteWithSpaceConcatenation )
        self.outputFormat=format
        scripts[name]=self

        # Init doc string for the operator
        doc="CliMAF wrapper for command : %s"%self.command
        # try to get a better doc string from colocated doc/directory
        docfilename=os.path.dirname(__file__)+"/../doc/scripts/"+name+".rst"
        #print "docfilen= "+docfilename
        try:
            docfile=open(docfilename)
            doc=docfile.read()
            docfile.close()
        except:
            pass
        #
        # creates a function named as requested, which will invoke
        # capply with that name and same arguments
        defs='def %s(*args,**dic) :\n  """%s"""\n  return driver.capply("%s",*args,**dic)\n'\
             % (name,doc,name)
        exec defs in globals() #sys.modules['__main__'].__dict__
        clogger.debug("CliMAF script %s has been declared"%name)

    def __repr__(self):
        return "CliMAF operator : "+self.name

    def inputs_number(self):
        """ returns the number of distinct arguments of a script which are inputs 
        
        """
        l=re.findall(r"\$\{(mm)?ins?(_\d*)?\}",self.command)
        ls=[]; old=None
        for e in l :
            if e != old : ls.append(e)
            old=e
        return(len(ls))

class coperator():
    def __init__(self,op, command, canOpendap=False, canSelectVar=False, 
	canSelectTime=False, canSelectDomain=False, canAggregateTime=False,
        canAlias=False, canMissing=False):
        clogger.error("Not yet developped")


def derive(project, derivedVar, Operator, *invars, **params) :
    """
    Define that 'derivedVar' is a derived variable in 'project', computed by
    applying 'Operator' to input streams which are datasets whose 
    variable names take the values in ``*invars`` and the parameter/arguments 
    of Operator take the values in ``**params``

    'project' may be the wildcard : '*'

    Example , assuming that operator 'minus' has been defined as ::
    
    >>> cscript('minus','cdo sub ${in_1} ${in_2} ${out}')
    
    which means that ``minus`` uses CDO for substracting the two datasets;
    you may define cloud radiative effect at the surface ('rscre')
    using the difference of values of all-sky and clear-sky net
    radiation at the surface by::
    
    >>> derive('*', 'rscre','minus','rs','rscs')

    You may then use this variable name at any location you would use any other variable name

    Another example is rescaling or renaming some variable; here, let us define how variable 'ta'
    can be derived from ERAI variable 't' :

    >>> derive('erai', 'ta','rescale', 't', scale=1., offset=0.)

    **However, this is not the most efficient way to do that**. See :py:func:`~climaf.classes.calias()`

    Expert use : argument 'derivedVar' may be a dictionnary, which key are derived variable
    names and values are scripts outputs names; example ::
    
    >>> cscript('vertical_interp', 'vinterp.sh ${in} surface_pressure=${in_2} ${out_l500} ${out_l850} method=${opt}')
    >>> derive('*', {'z500' : 'l500' , 'z850' : 'l850'},'vertical_interp', 'zg', 'ps', opt='log'}
    
    """
    # Action : register the information in a dedicated dict which keys
    # are single derived variable names, and which will be used at the
    # object evaluation step
    # Also : some consistency checks w.r.t. script definition
    if Operator in scripts :
        if not isinstance(derivedVar,dict) : derivedVar=dict(out=derivedVar)
        for outname in derivedVar :
            if (outname != 'out' and
                (not getattr(Operator,"outvarnames",None)  or outname not in Operator.outvarnames )):
                err="%s is not a named  ouput for operator %s; type help(%s)"%(outname,Operator,Operator)
                raise Climaf_Operator_Error(err)
            s=scripts[Operator]
            if s.inputs_number() != len(invars) :
                clogger.error("number of input variables for operator %s is %d, "
                              "which is inconsistent with script declaration : %s\
                              "%(s.name,len(invars),s.command))
                return
            # TBD : check parameters number  ( need to build its list in cscript.init() )
            if project not in derived_variables :  derived_variables[project]=dict()
            derived_variables[project][derivedVar[outname]]=(Operator, outname, list(invars), params)
    elif Operator in operators :
        clogger.warning("Cannot yet handle derived variables based on internal operators")
    else : 
        clogger.error("second argument must be a script or operator, already declared")

def is_derived_variable(variable,project):
    """ True if the variable is a derived variable, either in provided project
    or in wildcard project '*'
    """
    rep= (project in derived_variables and variable in derived_variables[project] or \
            "*"     in derived_variables and variable in derived_variables["*"])
    clogger.debug("Checking if variable %s is derived for project %s : %s"%(variable,project,rep))
    return(rep)
    

def derived_variable(variable,project):
    """ Returns the entry defining a derived variable in requested project or in wildcard project '*'
    """
    if project in derived_variables and variable in derived_variables[project] :
        rep=derived_variables[project][variable]
    elif "*"   in derived_variables and variable in derived_variables["*"] :
        rep=derived_variables['*'][variable]
    else : rep=None
    clogger.debug("Derived variable %s for project %s is %s"%(variable,project,rep))
    return(rep)
    

class Climaf_Operator_Error(Exception):
    def __init__(self, valeur):
        self.valeur = valeur
        clogger.error(self.__str__())
        dedent(100)
    def __str__(self):
        return `self.valeur`


if __name__ == "__main__":
    def ceval(script_name,*args,**dic) :
        print script_name, " has been called with args=",args, " and dic=",dic
        print "Command would be:",
    cscript('test_script' ,'echo $*')
    test_script(arg1=1,arg2='two')

#scripts['eof']='eof "${in}" ${out_eof} ${out_cp}'
#scripts['regress']='regress ${in_1} ${in_2} ${out_regress} ${out_correl}'
#scripts['spatial_average']="cdo fldavg ${datain} ${dataout} ${box} ${dataout2}"
#scripts['eof']="eof ${datain} ${out1} ${dataout2}"

