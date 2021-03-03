from qlib.workflow import R
import pandas as pd
from typing import Union
from tqdm.auto import tqdm


class RollingCollector:
    """
    Rolling Models Ensemble based on (R)ecord

    This shares nothing with Ensemble
    """

    # TODO: speed up this class
    def __init__(self, get_key_func, flt_func=None):
        self.get_key_func = get_key_func  # user need to implement this method to get the key of a task based on task config
        self.flt_func = flt_func  # determine whether a task can be retained based on task config

    def __call__(self, exp_name) -> Union[pd.Series, dict]:
        # TODO;
        # Should we split the scripts into several sub functions?
        exp = R.get_exp(experiment_name=exp_name)

        # filter records
        recs = exp.list_recorders()

        recs_flt = {}
        for rid, rec in tqdm(recs.items(), desc="Loading data"):
            params = rec.load_object("param")
            if rec.status == rec.STATUS_FI:
                if self.flt_func is None or self.flt_func(params):
                    rec.params = params
                    recs_flt[rid] = rec

        # group
        recs_group = {}
        for _, rec in recs_flt.items():
            params = rec.params
            group_key = self.get_key_func(params)
            recs_group.setdefault(group_key, []).append(rec)

        # reduce group
        reduce_group = {}
        for k, rec_l in recs_group.items():
            pred_l = []
            for rec in rec_l:
                pred_l.append(rec.load_object("pred.pkl").iloc[:, 0])
            pred = pd.concat(pred_l).sort_index()
            reduce_group[k] = pred

        return reduce_group
