import pandas as pd
feature_names = ['checkingstatus', 'duration', 'history', 'purpose', 'amount', 'savings', 'employ', 'installment', 'status', 'others', 'residence', 'property', 'age', 'otherplans', 'housing', 'cards', 'job', 'liable', 'telephone', 'foreign']

var_xwalk = {'checkingstatus':{
'A11' : '... < 0 DM',
'A12' : '0 <= ... < 200 DM',
'A13' : '... >= 200 DM / salary assignments for at least 1 year',
'A14' : 'no checking account'},
'history':{
'A30' : 'no credits taken/ all credits paid back duly',
'A31' : 'all credits at this bank paid back duly',
'A32' : 'existing credits paid back duly till now',
'A33' : 'delay in paying off in the past',
'A34' : 'critical account/ other credits existing (not at this bank)'},
'purpose':{ 
'A40' : 'car (new)',
'A41' : 'car (used)',
'A42' : 'furniture/equipment',
'A43' : 'radio/television',
'A44' : 'domestic appliances',
'A45' : 'repairs',
'A46' : 'education',
'A47' : 'vacation',
'A48' : 'retraining',
'A49' : 'business',
'A410' : 'purpose - others'},
'savings' : {
'A61' : '... < 100 DM',
'A62' : '100 <= ... < 500 DM',
'A63' : '500 <= ... < 1000 DM',
'A64' : '.. >= 1000 DM',
'A65' : 'unknown/ no savings account'},
'employ' : {
'A71' : 'unemployed',
'A72' : '... < 1 year',
'A73' : '1 <= ... < 4 years',
'A74' : '4 <= ... < 7 years',
'A75' : '.. >= 7 years'},
'status' : {
'A91' : 'male : divorced/separated',
'A92' : 'female : divorced/separated/married',
'A93' : 'male : single',
'A94' : 'male : married/widowed',
'A95' : 'female : single (does not exist)'},
'age' : {'> 25 years' : '> 25 years',
        '<= 25 years' : '<= 25 years'},
'others' : {
'A101' : 'others - none',
'A102' : 'co-applicant',
'A103' : 'guarantor'},
'property' : {
'A121' : 'real estate',
'A122' : 'building society savings agreement/ life insurance',
'A123' : 'car or other, not in attribute 6',
'A124' : 'unknown / no property'},
'otherplans' : {
'A141' : 'bank',
'A142' : 'stores',
'A143' : 'none'},
'housing' : {
'A151' : 'rent',
'A152' : 'own',
'A153' : 'for free'},
'job' : {
'A171' : 'unemployed/ unskilled - non-resident',
'A172' : 'unskilled - resident',
'A173' : 'skilled employee / official',
'A174' : 'management/ self-employed/highly qualified employee/ officer'},
'telephone' : {
'A191' : 'phone - none',
'A192' : 'phone - yes, registered under the customers name'},
'foreign' : {
'A201' : 'foreign - yes',
'A202' : 'foreign - no'},
'outcome' : {
1 : 'Good',
2 : 'Bad'}}

import pandas as pd


def load_german_dict():
    german_dict = {0: ['... < 0 DM',
      '0 <= ... < 200 DM',
      '... >= 200 DM / salary assignments for at least 1 year',
      'no checking account'],
     1: ['duration'],
     2: ['no credits taken/ all credits paid back duly',
      'all credits at this bank paid back duly',
      'existing credits paid back duly till now',
      'delay in paying off in the past',
      'critical account/ other credits existing (not at this bank)'],
     3: ['car (new)',
      'car (used)',
      'furniture/equipment',
      'radio/television',
      'domestic appliances',
      'repairs',
      'education',
      'retraining',
      'business',
      'purpose - others'],
     4: ['amount'],
     5: ['... < 100 DM',
      '100 <= ... < 500 DM',
      '500 <= ... < 1000 DM',
      '.. >= 1000 DM',
      'unknown/ no savings account'],
     6: ['unemployed',
      '... < 1 year',
      '1 <= ... < 4 years',
      '4 <= ... < 7 years',
      '.. >= 7 years'],
     7: ['installment'],
     8: ['male : divorced/separated',
      'female : divorced/separated/married',
      'male : single',
      'male : married/widowed'],
     9: ['others - none', 'co-applicant', 'guarantor'],
     10: ['residence'],
     11: ['real estate',
      'building society savings agreement/ life insurance',
      'car or other, not in attribute 6',
      'unknown / no property'],
     12: ['<= 25 years', '> 25 years'],
     13: ['bank', 'stores', 'none'],
     14: ['rent', 'own', 'for free'],
     15: ['cards'],
     16: ['unemployed/ unskilled - non-resident',
      'unskilled - resident',
      'skilled employee / official',
      'management/ self-employed/highly qualified employee/ officer'],
     17: ['liable'],
     18: ['phone - none', 'phone - yes, registered under the customers name'],
     19: ['foreign - yes', 'foreign - no']
    }
    return german_dict
  

def get_feature_name(idx):
    return feature_names[idx]

def map_german_encoding_to_label(german_dict):
    new_german_dict = {}
    for i in range(len(feature_names)):
        if feature_names[i] in var_xwalk:
            input_keys = list(german_dict.keys())
            
            if input_keys[0] in var_xwalk[feature_names[i]].keys(): 
                #populate new dictionary
                for x in german_dict:
                    new_german_dict[var_xwalk[feature_names[i]][x]] = german_dict[x]
    return new_german_dict

def convert_all_encoding_to_label(encoded_df):
    decoded_df = pd.DataFrame().reindex_like(encoded_df)

    for header in feature_names:
        if header in var_xwalk: 
            decoded_df[header] = encoded_df[header].map(var_xwalk[header]) 
        else:
            decoded_df[header] = encoded_df[header]
    return decoded_df

def make_decoded_data():
   data = pd.read_csv('./data/german_credit.csv')
   feature_names = list(data)
   X = data.drop('outcome',axis=1) 
   y = data['outcome']
   
   new_df = convert_all_encoding_to_label(X)
   new_df['outcome'] = y
   
   new_df['age_cat'] = "> 25 years"
   new_df.loc[new_df.age <= 25,['age_cat']] = "<= 25 years"
   
   new_df = new_df.drop(['age'],axis = 1)
   new_df.columns = [x if x != "age_cat" else "age" for x in new_df.columns ] # change name
   new_df = new_df[feature_names] # reorder

   new_df.to_csv('./data/german_credit-decoded.csv', index=False)

