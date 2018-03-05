import os
import pdb

import rdflib # May use faster rdf db instead.
import arrow

from ..db import *
from ..brick_parser import pointTagsetList
from ..common import *
from .. import plotter
#from ..brick_parser import g as brick_g 

def exec_measurement(func):
    def wrapped(*args, **kwargs):
        begin_time = arrow.get()
        res = func(*args, **kwargs)
        end_time = arrow.get()
        print('Execution Time: {0}'.format(end_time - begin_time))
        return res
    return wrapped
    

class FrameworkInterface(object):
    """
    # input parameters
    - target_building (str): name of the target building. this can be arbitrary later
    - source_buildings (list(str)): list of buildings already known.
    - exp_id: just for logging
    - conf: dictionary of other configuration parameters.
    """

    def __init__(self, 
                 target_building, 
                 source_buildings=[],
                 exp_id=0, 
                 framework_name=None, 
                 conf={}, 
                 ):
        super(FrameworkInterface, self).__init__()
        self.exp_id = exp_id
        self.framework_name = framework_name
        self.conf = conf
        self.infer_g = rdflib.Graph()
        self.used_srcids = set()
        #self.brick_g = brick_g
        self.point_tagsets = pointTagsetList
        self.pred = {
            'tagsets': dict(),
            'point': dict(),
            }
        self.target_srcids = []
        self.history = []

    # Interface functions 

    def learn(self, input_data):
        pass

    def active_learn(self, labeled_data):
        pass

    def infer(self):
        pass

    def result_summary(self):
        pass

    # helper functions
    def serialize_graph(self, g, filename='test.ttl'):
        if g:
            g.serialize(filename, format='turtle')
        else:
            print('no ground truth graph defined')

    def serialize_inferred_graph(self):
        self.serialize_graph(self.infer_g, 'infer.ttl')

    def serialize_true_graph(self):
        self.serialize_graph(self.true_g, 'true.ttl')

    # Update samples

    def register_fullparsing_samples(self, fullparsings, building=None):
        # fullparsings: {srcid: fullparsing}
        for srcid, fullparsing in fullparsings.items():
            point = LabeledMetadata.objects(srcid=srcid, building=building)\
                        .upsert_one(srcid=srcid, building=building)
            point.fullparsing = fullparsing
            point.save()

    def register_tagsets_samples(self, tagsets_dict, buliding=None):
        for srcid ,tagsets in tagsets_dict.items():
            point = LabeledMetadata.objects(srcid=srcid, building=building)\
                        .upsert_one(srcid=srcid, building=building)
            point.tagsts = tagsets 
            point.save()
    
    def evaluate_points(self):
        curr_log = {
            'learned_srcids': self.learned_srcids
        }
        score = 0
        for srcid, pred_tagsets in self.pred['tagsets'].items():
            true_tagsets = LabeledMetadata.objects(srcid=srcid)[0].tagsets
            true_point = sel_point_tagset(true_tagsets)
            pred_point = sel_point_tagset(pred_tagsets)
            if true_point == pred_point:
                score +=1 
        curr_log['accuracy'] = score / len(self.pred['point'])
        return curr_log

    def evaluate(self):
        points_log = self.evaluate_points()
        log = {
            'points': points_log
        }
        self.history.append(log)

    def plot_result_point(self):
        srcid_nums = [len(log['points']['learned_srcids']) for log in self.history]
        accs = [log['points']['accuracy'] for log in self.history]
        fig, _ = plotter.plot_multiple_2dline(srcid_nums, [accs])
        for ax in fig.axes:
            ax.set_grid(True)
        plot_name = '{0}_points_{1}.pdf'.format(self.framework_name, self.exp_id)
        plotter.save_fig(fig, plot_name)

    def learn_auto(self, iter_num=1):
        """Learn from the scratch to the end.

        This executes the learning mechanism from the ground truth.
        It iterates for the given amount of the number.
        Basic procedure is iterating this:
            ```python
            f = Framework()
            while not final_condition:
                new_srcids = f.select_informative_samples(10)
                f.update_model(new_srcids)
                self.pred['tagsets'] = XXX
                f.evaluate()
                final_condition = f.get_final_condition()
            ```

        Args:
            iter_num (int): total iteration number.

        Returns:
            None
            
        Byproduct:
            
            
        """
        pass

    def update_model(self, srcids):
        """Update model with given newly added srcids.

        This update the model based on the newly added srcids.
        Relevant data for the srcids are given from the ground truth data.
        We can later add an interactive function for users to manually add them

        Args:
            srcids (list(str)): The model will be updated based on the given
                                srcids.
        Returns:
            None

        Byproduct:
            The model will be updated, which can be used for predictions.
        """
        pass
    
    def select_informative_samples(self, sample_num):
        """Select the most informative N samples from the unlabeled data.

        This function is mainly used by active function frameworks to select
        the most informative samples to ask to the domain experts.
        The chosen samples are again fed back to the model updating mechanisms.

        Args:
            sample_num (int): The number of samples to be chosen

        Returns:
            new_srcids (list(str)): The list of srcids.

        Byproducts:
            None
        """
        pass
