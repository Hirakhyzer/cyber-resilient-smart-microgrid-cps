import numpy as np

def cyber_metrics(labels, alarms):
    y=np.asarray(labels, dtype=bool); a=np.asarray(alarms, dtype=bool)
    tp=int(np.sum(y & a)); fp=int(np.sum(~y & a)); fn=int(np.sum(y & ~a)); tn=int(np.sum(~y & ~a))
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"tp":tp,"fp":fp,"fn":fn,"tn":tn,"precision":precision,"recall":recall,"f1":f1}
