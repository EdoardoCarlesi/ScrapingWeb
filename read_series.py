

def return_series():

    years = [ 1990 + i for i in range(0, 34)]

    tags_file = open('series_names_ids.txt', 'r')
    all_nums = []
    number = []
    nstr = ''

    while (nstr != '3500'):
          
        # read by character
        char = tags_file.read(1)          
        if char == '"':
         
            if len(number) > 0:
                nstr = ''.join(number)
                #print(nstr)
                all_nums.append(int(nstr))

            number = []

        if char.isdigit():
            number.append(char)
    
    all_nums = set(all_nums)

    for yr in years:
        if (yr in all_nums):
            all_nums.remove(yr)

    all_nums = list(all_nums)
    all_nums.sort()

    return all_nums


if __name__ == '__main__':

    an = return_series()

    print(an)
