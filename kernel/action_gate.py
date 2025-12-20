class ActionRequired(Exception):
    """
    Raised when an agent requests a system action
    that requires human approval.
    """
    def __init__(self, request):
        self.request = request
        super().__init__("Action requires approval")
