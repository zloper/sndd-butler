def parse(txt):
    txt_lst = txt.split('"""info')
    result = ''
    for elem in txt_lst:
        if 'info"""' in elem:
            info = elem.split('info"""')[0]
            result += '- ' + info.strip() + '\n'
    return result
