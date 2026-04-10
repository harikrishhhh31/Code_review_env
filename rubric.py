
from typing import List, Dict, Any, Optional, Tuple
import re
from openenv.core.rubrics import Rubric

# IMPORTANT:
# Validator parses rewards/scores with 2 decimal places.
# Keep values away from endpoints even after rounding.
_EPS = 0.05


def _strict_unit_interval(x: float) -> float:
    """Clamp score to be strictly within (0, 1)."""
    if x <= _EPS:
        return _EPS
    if x >= 1.0 - _EPS:
        return 1.0 - _EPS
    return x


def _location_match(agent_loc: str, gt_loc: str) -> bool:
    if not agent_loc or not gt_loc:
        return True
    agent_tokens = [t for t in re.split(r"[^a-z0-9]+", agent_loc) if t]
    gt_tokens = [t for t in re.split(r"[^a-z0-9]+", gt_loc) if t]
    if not agent_tokens or not gt_tokens:
        return True
    return len(set(agent_tokens) & set(gt_tokens)) > 0


                                                                               
                                                       
                                                                               
                                                                       
                                                      

class CorrectnessRubric(Rubric):
    
    def __init__(self, weight: float = 1.0):
        super().__init__()
        self.weight = weight
        self.last_score = _EPS
    
    def forward(self, action, observation) -> float:
                              
        agent_findings = getattr(action, 'findings', [])
        
                                                       
        ground_truth = getattr(observation, 'metadata', {}).get(
            'ground_truth_issues', []
        )
        
                                                                        
        if not agent_findings:
            score = _strict_unit_interval(0.0 * self.weight)
            self.last_score = score
            return score
        
                                                 
        correct_count = 0
        for agent_finding in agent_findings:
                                                                     
            for gt_issue in ground_truth:
                if self._findings_match(agent_finding, gt_issue):
                    correct_count += 1
                    break                           
        
                                   
        precision = correct_count / len(agent_findings) if agent_findings else 0.0
        
                                 
        score = _strict_unit_interval(precision * self.weight)
        self.last_score = score
        return score
    
    def _findings_match(
        self, 
        agent_finding: Dict, 
        gt_issue: Dict
    ) -> bool:
        agent_type = agent_finding.get('type', '').lower()
        gt_type = gt_issue.get('type', '').lower()
        
        agent_desc = agent_finding.get('description', '').lower()
        gt_desc = gt_issue.get('description', '').lower()
        
                          
        type_match = agent_type == gt_type

        desc_match = (
            gt_desc in agent_desc or 
            agent_desc in gt_desc or
            any(word in agent_desc for word in gt_desc.split() if len(word) > 4)
        )

        if not (type_match and desc_match):
            return False

        agent_loc = str(agent_finding.get('location', '')).lower()
        gt_loc = str(gt_issue.get('location', '')).lower()
        return _location_match(agent_loc, gt_loc)


class CompletenessRubric(Rubric):
    
    def __init__(self, weight: float = 1.0):
        super().__init__()
        self.weight = weight
        self.last_score = _EPS
    
    def forward(self, action, observation) -> float:
        agent_findings = getattr(action, 'findings', [])
        ground_truth = getattr(observation, 'metadata', {}).get(
            'ground_truth_issues', []
        )
        
        if not ground_truth:
            score = _strict_unit_interval(1.0 * self.weight)
            self.last_score = score
            return score                                
        
                                                       
        found_count = 0
        for gt_issue in ground_truth:
            for agent_finding in agent_findings:
                if self._issue_found(agent_finding, gt_issue):
                    found_count += 1
                    break
        
                          
        recall = found_count / len(ground_truth)
        score = _strict_unit_interval(recall * self.weight)
        self.last_score = score
        return score
    
    def _issue_found(
        self, 
        agent_finding: Dict, 
        gt_issue: Dict
    ) -> bool:
                                                      
        agent_type = agent_finding.get('type', '').lower()
        gt_type = gt_issue.get('type', '').lower()
        
        gt_desc = gt_issue.get('description', '').lower()
        agent_desc = agent_finding.get('description', '').lower()
        
        type_match = agent_type == gt_type
        desc_match = any(
            word in agent_desc 
            for word in gt_desc.split() 
            if len(word) > 4
        )

        if not (type_match and desc_match):
            return False

        agent_loc = str(agent_finding.get('location', '')).lower()
        gt_loc = str(gt_issue.get('location', '')).lower()
        return _location_match(agent_loc, gt_loc)


class SeverityRubric(Rubric):
    
    def __init__(self, weight: float = 0.5):
        super().__init__()
        self.weight = weight
        self.last_score = _EPS
    
    def forward(self, action, observation) -> float:
        agent_findings = getattr(action, 'findings', [])
        
        if not agent_findings:
            score = _strict_unit_interval(0.0 * self.weight)
            self.last_score = score
            return score
        
        ground_truth = getattr(observation, 'metadata', {}).get(
            'ground_truth_issues', []
        )
        
                                           
        severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        
        correct_severity = 0
        total_severity_issues = 0
        
        for agent_finding in agent_findings:
            agent_severity = agent_finding.get('severity', 'medium')
            agent_type = agent_finding.get('type', '')
            
                                        
            for gt_issue in ground_truth:
                if gt_issue.get('type', '') == agent_type:
                    total_severity_issues += 1
                    gt_severity = gt_issue.get('severity', 'medium')
                    
                                                                 
                    diff = abs(
                        severity_order.get(agent_severity, 1) - 
                        severity_order.get(gt_severity, 1)
                    )
                    if diff <= 1:
                        correct_severity += 1
                    break
        
        if total_severity_issues == 0:
            score = _strict_unit_interval(1.0 * self.weight)
            self.last_score = score
            return score                              
        
        computed_score = correct_severity / total_severity_issues
        score = _strict_unit_interval(computed_score * self.weight)
        self.last_score = score
        return score


class DescriptionMatchRubric(Rubric):
    
    def __init__(self, weight: float = 1.0):
        super().__init__()
        self.weight = weight
        self.last_score = _EPS
    
    def forward(self, action, observation) -> float:
        pr_info = getattr(observation, 'pr_info', {})
        expected_match = pr_info.get('description_match', True)
        
                                                  
                                                                           
        agent_assessment_correct = True               
        
        computed_score = 1.0 if agent_assessment_correct else 0.0
        score = _strict_unit_interval(computed_score * self.weight)
        self.last_score = score
        return score


                                                                               
                                                       
                                                                               
                                                             

class ReadabilityRubric(Rubric):
    
    def __init__(self):
        super().__init__()
        self.last_score = _EPS
        self.correctness = CorrectnessRubric(weight=0.5)
        self.completeness = CompletenessRubric(weight=0.5)
    
    def forward(self, action, observation) -> float:
        c_score = self.correctness(action, observation)
        comp_score = self.completeness(action, observation)
        
                              
        total = c_score + comp_score
        
        score = _strict_unit_interval(min(total, 1.0))
        self.last_score = score
        return score              


class BugLogicRubric(Rubric):
    
    def __init__(self):
        super().__init__()
        self.last_score = _EPS
        self.correctness = CorrectnessRubric(weight=0.4)
        self.completeness = CompletenessRubric(weight=0.4)
        self.severity = SeverityRubric(weight=0.2)
    
    def forward(self, action, observation) -> float:
        c_score = self.correctness(action, observation)
        comp_score = self.completeness(action, observation)
        sev_score = self.severity(action, observation)
        
        total = c_score + comp_score + sev_score
        
        score = _strict_unit_interval(min(total, 1.0))
        self.last_score = score
        return score


class FullReviewRubric(Rubric):
    
    def __init__(self):
        super().__init__()
        self.last_score = _EPS
        self.readability = ReadabilityRubric()
        self.bug_logic = BugLogicRubric()
        self.description_match = DescriptionMatchRubric(weight=0.2)
    
    def forward(self, action, observation) -> float:
        read_score = self.readability(action, observation)
        bug_score = self.bug_logic(action, observation)
        desc_score = self.description_match(action, observation)
        
                              
        total = (
            read_score * 0.25 +
            bug_score * 0.35 +
            desc_score * 0.40                                     
        )
        
        score = _strict_unit_interval(min(total, 1.0))
        self.last_score = score
        return score


                                                                               
                                                     
                                                                               

class RubricFactory:
    
                                    
    RUBRIC_MAP = {
        "readability": ReadabilityRubric,
        "bug_logic": BugLogicRubric,
        "full_review": FullReviewRubric,
    }
    
    @classmethod
    def create(cls, task_id: str) -> Rubric:
        rubric_class = cls.RUBRIC_MAP.get(task_id)
        if rubric_class is None:
            raise ValueError(f"Unknown task: {task_id}")
        return rubric_class()


                                                                               
         
                                                                               

__all__ = [
                  
    "CorrectnessRubric",
    "CompletenessRubric", 
    "SeverityRubric",
    "DescriptionMatchRubric",
                       
    "ReadabilityRubric",
    "BugLogicRubric",
    "FullReviewRubric",
             
    "RubricFactory",
]
