import os
import pandas as pd


def main():
    df = pd.read_csv('bunruidb-fam.csv', encoding='shift-jis')
    print(df.columns)
    shitteiru = df.loc[df['知っている'] >= 1.9, ['見出し本体', '知っている', '話す', '類']]
    # shitteiru = shitteiru.loc[shitteiru['類'] == '用',  ['見出し本体', '知っている', '話す', '類']]
    shitteiru = shitteiru.loc[shitteiru['話す'] > 1.3 ,  ['見出し本体', '知っている', '話す', '類']]
    print(len(shitteiru))
    print(shitteiru.head())
    shitteiru = shitteiru.sort_values('知っている', ascending=False)
    print(shitteiru.head())
    record = list(shitteiru['見出し本体'])
    record_set = set()
    for rec in record:
        if '／' in rec:
            for r in rec.split('／'):
                record_set.add(r)
        elif '・' in rec:
            for r in rec.split('・'):
                record_set.add(r)
        else:
            record_set.add(rec)
    record = list(record_set)
    with open('Known_words.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(record))

if __name__=='__main__':
    main()