import subprocess, sys, resource, time
t=time.time(); p=subprocess.run(sys.argv[1:], capture_output=True, text=True)
print(p.stdout.strip()[-400:]); print(p.stderr.strip()[-1500:] if p.returncode else "")
print(f"RC {p.returncode} WALL_s {time.time()-t:.1f} MAXRSS_MB {resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024:.0f}")
