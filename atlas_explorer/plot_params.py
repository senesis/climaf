# -- Import the dictionnaries of plot params:
from climaf.site_settings import *

if atCNRM:


# --> for LMDZ
import lmdz_dict_plot_params
# --> for NEMO
import nemo_dict_plot_params

def plot_params(variable,context, custom_plot_params=None) :
    """
    Return plot parameters as a dict(), according to LMDZ habits , for a given
    variable and a context (among full_field, bias, model_model)
    
    The user can pass his own custom dictionnary of plot parameters with custom_plot_params.

    """

    defaults = { 
        'contours' : 1 ,
        'color'    :'temp_19lev',
    }

    per_variable = {}
    # --> Adding the LMDZ plot params 
    per_variable.update(lmdz_dict_plot_params.dict_plot_params)
    # --> Adding the NEMO plot params
    per_variable.update(nemo_dict_plot_params.dict_plot_params)
    # --> If needed, adding a custom dictionnary of plot params
    if custom_plot_params:
       per_variable.update(custom_plot_params)
    #
    rep=defaults.copy()
    if variable in per_variable : 
        var_entry=per_variable[variable]
        for cont in [ 'default', context ] :
            if cont in var_entry : rep.update(var_entry[cont])
    return rep
        
