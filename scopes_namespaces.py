def scope_test():
    def do_local():
        spam = "local spam"

    def do_nonlocal():
        nonlocal spam
        spam = "nonlocal spam"

    def do_global():
        global spam
        spam = "global spam"

    spam = "test spam"
    do_local()
    # this will print "test spam", because ENCLOSED SCOPE - internal, i.e., do_local() - does not change ENCLOSING - external, i.e. scope_test()
    print("After local assignment:", spam)
    do_nonlocal()
    # this will print "non local spam", because setting scope to NONLOCAL binds definition to scope of ENCLOSING SCOPE - i.e., scope_test()
    print("After nonlocal assignment:", spam)
    # this will also print "non local spam", because setting scope to GLOBAL binds definition to scope outside both functions - i.e., module itself 
    do_global()
    print("After global assignment:", spam)

scope_test()
# this will print "global spam", because running scope_test() runs do_global(), which binds the definiton of spam to the whole module
print("In global scope:", spam)
# as a test, I can simply put a print(spam) before running scope_test(), and it would result in exception
# because spam is defined, albeit globally, from a "command" that runs inside scope_test()
# the same would happen if I commented out do_global(), because although ln 13 defines spam, it's only in the scope_test() namespace