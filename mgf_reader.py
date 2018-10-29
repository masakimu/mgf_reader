'''
Copyright (c) 2018, Masaki Murase
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import sys
import re
import copy

ptn_comment=re.compile(r'^#|^[\s\t]?$')

class mz_intensity_charge():
    def __init__(self, mz=0.0, intensity=0.0, charge=-1):
        self.mz=mz
        self.intensity=intensity
        self.charge=charge

    def __str__(self):
        if self.charge==-1:
            return '\t'.join([str(self.mz), str(self.intensity)])
        else:
            return '\t'.join([str(self.mz), str(self.intensity), str(self.charge)])
        

def read_peaklist(file):
    '''
    mgf for MS1 and MSn
    '''

    with open(file, 'r')  as f:
        in_peaklist = False
        is_ms2_mgf = False
        in_spec_header = False
        in_spec_peaklist = False
        file_header = {}
        spec_header = {}
        list_mz_intensity_charge=[]
        spectrum={}
        
        for line in f:
            if ptn_comment.match(line) != None:
                continue
            
            if line.find('=')>-1:
                l=line.strip().split('=')
                if not(in_spec_header):
                    file_header[l[0].lower()] = l[1]
                else:
                    spec_header[l[0].lower()] = l[1]
                    
            elif line.strip() == 'BEGIN IONS':
                is_ms2_mgf = True
                in_spec_header = True
                continue
            
            elif line.strip() == 'END IONS':
                in_spec_peaklist = False
                spectrum['file_header']=file_header
                spectrum['header']=copy.deepcopy(spec_header)
                spectrum['mz_intensity_charge']=sorted(list_mz_intensity_charge, key=lambda x:x.mz)
                spec_header = {}
                list_mz_intensity_charge=[]
                
                if is_ms2_mgf:
                    yield spectrum
                    
            else:
                l=line.strip().split()
                if len(l)==2:
                    peak=mz_intensity_charge(mz=l[0], intensity=l[1])
                if len(l)==3:
                    peak=mz_intensity_charge(mz=l[0], intensity=l[1], charge=l[2])
                list_mz_intensity_charge.append(peak)
                        
        if not(is_ms2_mgf):
            spectrum['file_header']=file_header
            spectrum['header']=spec_header
            spec_header = {}
            spectrum['mz_intensity_charge']=sorted(list_mz_intensity_charge, key=lambda x:x.mz)
            yield spectrum

if __name__ == '__main__':
    argv=sys.argv
    argc=len(argv)

    if (argc!=2):
        print( 'Usage: python mgf_reader.py <Peaklist file>')
        quit()

    peaklist_file=argv[1]
    
    for spec in read_peaklist(peaklist_file):
        if spec['file_header']:
            print('File Header:')
            for key,val in spec['file_header'].items():
                print(key+':', val)
        if spec['header']:
            print('Spectrum Header:')
            for key,val in spec['header'].items():
                print(key+':', val)
        print('Peaklist:')
        for dat in spec['mz_intensity_charge']:
            print(dat)
