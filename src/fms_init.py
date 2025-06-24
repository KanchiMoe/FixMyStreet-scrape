import src

def fms_init_main():
    # Do a DB integrity check before continuing
    src.integrity_check()

    # Do autofind the highest report ID
    src.autofind_highest_report_id()