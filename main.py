from parser import token_list, get_env, parse
from interp import interp

if __name__ == "__main__":
    #take in input as string
    input_str = "[hello, there]\nSET hi 3\nADD hi 6 2\nPRINT &hi"

    #seperate program into individual lines
    splt_line_lst = token_list(input_str)

    #get env from first line
    env = get_env(splt_line_lst)

    #parse program
    ast = parse(splt_line_lst)

    #interp ast with given env
    interp(ast, env)
