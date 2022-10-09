BEGIN {
    getline < (fn = "/proc/uptime")
    close(fn)
    print "The system was booted:",strftime("%c",t=systime()-$1)
}
