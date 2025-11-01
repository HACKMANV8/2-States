"""
MCDC (Modified Condition/Decision Coverage) Analyzer.

Analyzes complex boolean conditions to determine minimum test cases needed
for MCDC coverage criteria.

MCDC Requirements:
- Every condition in a decision independently affects the outcome
- Each condition must be shown to affect the decision's outcome
"""

import re
import ast
import itertools
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ConditionOperator(str, Enum):
    """Boolean operators in conditions."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


@dataclass
class Condition:
    """A single boolean condition."""
    id: str
    expression: str
    variable_name: Optional[str] = None


@dataclass
class Decision:
    """A decision containing multiple conditions."""
    decision_id: str
    file_path: str
    line_number: int
    full_expression: str
    conditions: List[Condition]
    operators: List[ConditionOperator]
    complexity: int = 1


@dataclass
class TruthTableRow:
    """A row in the truth table."""
    condition_values: Dict[str, bool]
    decision_outcome: bool
    test_number: int


@dataclass
class MCDCTestCase:
    """A test case required for MCDC."""
    test_id: str
    condition_values: Dict[str, bool]
    expected_outcome: bool
    independent_condition: str  # Which condition this test verifies
    pair_with: Optional[str] = None  # Paired test case ID


@dataclass
class MCDCResult:
    """Result of MCDC analysis."""
    decision: Decision
    truth_table: List[TruthTableRow]
    required_test_cases: List[MCDCTestCase]
    minimum_test_count: int
    is_achievable: bool
    reason: Optional[str] = None


class MCDCAnalyzer:
    """
    Analyzes boolean conditions for MCDC coverage requirements.

    Implements:
    - Condition parsing and decomposition
    - Truth table generation
    - Independence analysis
    - Minimum test set calculation
    """

    def __init__(self, max_conditions: int = 8):
        """
        Initialize MCDC analyzer.

        Args:
            max_conditions: Maximum conditions to analyze (prevents explosion)
        """
        self.max_conditions = max_conditions

    def analyze_decision(
        self,
        expression: str,
        file_path: str,
        line_number: int
    ) -> MCDCResult:
        """
        Analyze a boolean decision for MCDC requirements.

        Args:
            expression: Boolean expression (e.g., "a && (b || c)")
            file_path: File containing the decision
            line_number: Line number of decision

        Returns:
            MCDCResult with analysis
        """
        print(f" Analyzing MCDC for: {expression}")

        # Parse decision into conditions
        decision = self._parse_decision(expression, file_path, line_number)

        # Check if analyzable
        if len(decision.conditions) > self.max_conditions:
            print(f"     Too many conditions ({len(decision.conditions)} > {self.max_conditions})")
            return MCDCResult(
                decision=decision,
                truth_table=[],
                required_test_cases=[],
                minimum_test_count=0,
                is_achievable=False,
                reason=f"Too many conditions ({len(decision.conditions)})"
            )

        # Generate truth table
        truth_table = self._generate_truth_table(decision)
        print(f"   Truth table: {len(truth_table)} rows")

        # Find MCDC test cases
        test_cases = self._find_mcdc_test_cases(decision, truth_table)
        print(f"   Required tests: {len(test_cases)}")

        return MCDCResult(
            decision=decision,
            truth_table=truth_table,
            required_test_cases=test_cases,
            minimum_test_count=len(test_cases),
            is_achievable=True
        )

    def analyze_file(
        self,
        file_path: str,
        code: str,
        language: str = "python"
    ) -> List[MCDCResult]:
        """
        Analyze all decisions in a file.

        Args:
            file_path: Path to file
            code: Source code content
            language: Programming language

        Returns:
            List of MCDC results for each decision
        """
        print(f" Analyzing MCDC in file: {file_path}")

        results = []

        if language == "python":
            decisions = self._extract_python_decisions(code, file_path)
        elif language in ["javascript", "typescript"]:
            decisions = self._extract_js_decisions(code, file_path)
        else:
            print(f"     Unsupported language: {language}")
            return []

        print(f"   Found {len(decisions)} decisions")

        for decision in decisions:
            result = self.analyze_decision(
                decision.full_expression,
                decision.file_path,
                decision.line_number
            )
            results.append(result)

        return results

    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================

    def _parse_decision(
        self,
        expression: str,
        file_path: str,
        line_number: int
    ) -> Decision:
        """Parse boolean expression into Decision object."""
        # Normalize expression
        normalized = self._normalize_expression(expression)

        # Extract conditions
        conditions = self._extract_conditions(normalized)

        # Extract operators
        operators = self._extract_operators(normalized)

        # Calculate complexity
        complexity = len(conditions) + len(operators)

        decision_id = f"{file_path}:{line_number}"

        return Decision(
            decision_id=decision_id,
            file_path=file_path,
            line_number=line_number,
            full_expression=expression,
            conditions=conditions,
            operators=operators,
            complexity=complexity
        )

    def _normalize_expression(self, expression: str) -> str:
        """Normalize boolean expression to standard form."""
        # Remove whitespace
        normalized = ' '.join(expression.split())

        # Convert language-specific operators to standard
        replacements = {
            '&&': 'AND',
            '||': 'OR',
            '!': 'NOT ',
            ' and ': ' AND ',
            ' or ': ' OR ',
            ' not ': ' NOT ',
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        return normalized

    def _extract_conditions(self, expression: str) -> List[Condition]:
        """Extract individual conditions from expression."""
        # Split by AND/OR operators
        parts = re.split(r'\s+(AND|OR)\s+', expression)

        conditions = []
        condition_id = 1

        for part in parts:
            if part in ['AND', 'OR']:
                continue

            # Remove NOT prefix
            clean_part = part.replace('NOT ', '').strip('() ')

            if clean_part and not clean_part in ['AND', 'OR']:
                conditions.append(Condition(
                    id=f"C{condition_id}",
                    expression=clean_part,
                    variable_name=self._extract_variable_name(clean_part)
                ))
                condition_id += 1

        return conditions

    def _extract_operators(self, expression: str) -> List[ConditionOperator]:
        """Extract operators from expression."""
        operators = []

        if 'AND' in expression:
            operators.append(ConditionOperator.AND)
        if 'OR' in expression:
            operators.append(ConditionOperator.OR)
        if 'NOT' in expression:
            operators.append(ConditionOperator.NOT)

        return operators

    def _extract_variable_name(self, condition: str) -> Optional[str]:
        """Extract variable name from condition."""
        # Simple extraction: first identifier
        match = re.search(r'\b([a-zA-Z_]\w*)\b', condition)
        if match:
            return match.group(1)
        return None

    def _generate_truth_table(self, decision: Decision) -> List[TruthTableRow]:
        """Generate complete truth table for decision."""
        num_conditions = len(decision.conditions)
        truth_table = []

        # Generate all possible combinations
        for i, combination in enumerate(itertools.product([False, True], repeat=num_conditions)):
            # Create condition values map
            condition_values = {
                cond.id: value
                for cond, value in zip(decision.conditions, combination)
            }

            # Evaluate decision outcome
            outcome = self._evaluate_decision(decision, condition_values)

            truth_table.append(TruthTableRow(
                condition_values=condition_values,
                decision_outcome=outcome,
                test_number=i + 1
            ))

        return truth_table

    def _evaluate_decision(
        self,
        decision: Decision,
        condition_values: Dict[str, bool]
    ) -> bool:
        """Evaluate decision outcome given condition values."""
        # Build evaluation expression
        expr = decision.full_expression

        # Replace each condition with its value
        for condition in decision.conditions:
            # Replace condition expression with True/False
            value = condition_values[condition.id]
            expr = expr.replace(condition.expression, str(value))

        # Normalize operators for Python eval
        expr = expr.replace('AND', 'and')
        expr = expr.replace('OR', 'or')
        expr = expr.replace('NOT', 'not')

        try:
            # Safely evaluate
            return eval(expr, {"__builtins__": {}}, {})
        except:
            # Default to False if evaluation fails
            return False

    def _find_mcdc_test_cases(
        self,
        decision: Decision,
        truth_table: List[TruthTableRow]
    ) -> List[MCDCTestCase]:
        """
        Find minimum test cases for MCDC coverage.

        For each condition, find pair of test cases where:
        - Only that condition changes
        - Decision outcome changes
        """
        test_cases = []

        for condition in decision.conditions:
            # Find test pair for this condition
            pair = self._find_independent_pair(
                condition.id, decision, truth_table
            )

            if pair:
                test1, test2 = pair

                # Add both tests to test set
                test_cases.append(MCDCTestCase(
                    test_id=f"T{test1.test_number}",
                    condition_values=test1.condition_values,
                    expected_outcome=test1.decision_outcome,
                    independent_condition=condition.id,
                    pair_with=f"T{test2.test_number}"
                ))

                test_cases.append(MCDCTestCase(
                    test_id=f"T{test2.test_number}",
                    condition_values=test2.condition_values,
                    expected_outcome=test2.decision_outcome,
                    independent_condition=condition.id,
                    pair_with=f"T{test1.test_number}"
                ))

        # Remove duplicates (same test can verify multiple conditions)
        unique_tests = {}
        for test in test_cases:
            if test.test_id not in unique_tests:
                unique_tests[test.test_id] = test

        return list(unique_tests.values())

    def _find_independent_pair(
        self,
        condition_id: str,
        decision: Decision,
        truth_table: List[TruthTableRow]
    ) -> Optional[Tuple[TruthTableRow, TruthTableRow]]:
        """
        Find a pair of test cases where only the given condition changes
        and the decision outcome changes.
        """
        for i, row1 in enumerate(truth_table):
            for row2 in truth_table[i+1:]:
                # Check if only target condition differs
                differing_conditions = [
                    cond_id for cond_id in row1.condition_values.keys()
                    if row1.condition_values[cond_id] != row2.condition_values[cond_id]
                ]

                if len(differing_conditions) == 1 and differing_conditions[0] == condition_id:
                    # Check if outcome differs
                    if row1.decision_outcome != row2.decision_outcome:
                        return (row1, row2)

        return None

    def _extract_python_decisions(
        self,
        code: str,
        file_path: str
    ) -> List[Decision]:
        """Extract decisions from Python code using AST."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        visitor = PythonDecisionVisitor(file_path)
        visitor.visit(tree)

        return visitor.decisions

    def _extract_js_decisions(
        self,
        code: str,
        file_path: str
    ) -> List[Decision]:
        """Extract decisions from JavaScript code (simplified)."""
        decisions = []

        # Simple regex-based extraction for if statements
        pattern = r'if\s*\((.*?)\)'
        matches = re.finditer(pattern, code)

        for match in matches:
            expression = match.group(1)

            # Estimate line number
            line_number = code[:match.start()].count('\n') + 1

            # Only analyze if contains logical operators
            if any(op in expression for op in ['&&', '||', '!']):
                decisions.append(self._parse_decision(
                    expression, file_path, line_number
                ))

        return decisions


class PythonDecisionVisitor(ast.NodeVisitor):
    """AST visitor to extract boolean decisions from Python code."""

    def __init__(self, file_path: str):
        """Initialize visitor."""
        self.file_path = file_path
        self.decisions: List[Decision] = []

    def visit_If(self, node: ast.If):
        """Visit if statement."""
        # Extract condition
        if isinstance(node.test, ast.BoolOp):
            # Complex boolean expression
            expression = ast.unparse(node.test)

            decision_id = f"{self.file_path}:{node.lineno}"

            # Parse into decision
            analyzer = MCDCAnalyzer()
            decision = analyzer._parse_decision(
                expression, self.file_path, node.lineno
            )

            self.decisions.append(decision)

        # Continue traversing
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        """Visit while loop."""
        if isinstance(node.test, ast.BoolOp):
            expression = ast.unparse(node.test)

            analyzer = MCDCAnalyzer()
            decision = analyzer._parse_decision(
                expression, self.file_path, node.lineno
            )

            self.decisions.append(decision)

        self.generic_visit(node)
