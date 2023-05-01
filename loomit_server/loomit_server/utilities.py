''' 
@file: utilities.py
@author: Mark Newcomb
@date: 2/19/2018
@description: A set of common utilities used in the healthpub application
'''
 
def get_client_ip(request):
    '''
        Given a django request object, attempts to return the originating client's IP address
    '''
    x_fwd_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = ''
    if x_fwd_for:
        ip = x_fwd_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip
 