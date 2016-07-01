import cProfile, pstats, io
pr = cProfile.Profile()
pr.enable()

print("Profiling this haan")

pr.disable()
s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())