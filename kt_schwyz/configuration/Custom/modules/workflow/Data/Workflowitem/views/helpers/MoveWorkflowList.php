<?php

class Zend_View_Helper_MoveWorkflowList extends Zend_View_Helper_Abstract {

	/**
	 * Generates the first level of the list.
	 *
	 * @return string
	 */
	public function moveWorkflowList() {
		$workflowListMapper = new Workflow_Model_Mapper_WorkflowItem();
		$workflowListItems  = $workflowListMapper->getAllWorkflows();

		$output = '';

		if ($workflowListItems) {

			$i = 0;
			$last = count($workflowListItems);
			$output .= '<div class="row">';
			foreach ($workflowListItems as $workflowListItem) {

				$output .= '<div class="row-container' . ($workflowListItem->workflowItemID == $this->view->workflowListId ? ' current' : '') . '">
								<div class="content-row">
									<div class="column column-100">
										<a class="move-item" href="' . $this->view->url(array(
														'action' => 'move',
														'workflow-list-id' => $this->view->workflowListId,
														'target-id' => $workflowListItem->workflowItemID,
														'mode' => 'before')) . '"
											>
											<span>
											' . $this->view->translate('Move here') . '
											</span>
										</a>
									</div>
								</div>
								<div class="content-row item">
									<div class="column column-100">
									' ./* $this->view->()->questionType($this->view->questionTypeId) .*/ '
										<span>' . $this->view->escape($workflowListItem->name) . '</span>
									</div>
								</div>';
				$i++;
				if ($i == $last) {
					$output .= '<div class="content-row">
									<div class="column column-100">
										<a class="move-item" href="' . $this->view->url(array(
													'action' => 'move',
													'workflow-list-id' => $this->view->workflowListId,
													'target-id' => $workflowListItem->workflowItemID,
													'mode' => 'after')) .
											'">
											<span>
											' . $this->view->translate('Move here') . '
											</span>
										</a>
									</div>
								</div>';
				}
				$output .= '</div>';
			}
			$output .= '</div>';
		}
		else {
			$output.='<div class="row-container">
								<div class="content-row">
									<div class="column column-100">
										<a class="move-item" href="' . $this->view->url(array('action' => 'move', 'workflow-list-id' => $this->view->workflowListId, 'target-workflow-list-id' => NULL, 'mode' => 'before')) . '">
											<span>
											' . $this->view->translate('Move here') . '
											</span>
										</a>
									</div>
								</div>';
		}

		return $output;

	}

}
